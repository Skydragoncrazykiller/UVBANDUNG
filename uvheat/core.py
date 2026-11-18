"""Inti logika: ambil data Open-Meteo, hitung heat index, klasifikasi, segmen waktu, rekomendasi.

File ini sengaja SELF-CONTAINED (hanya butuh requests, numpy, pandas) supaya
bisa dipakai langsung oleh skrip GitHub Actions dan disalin utuh ke Google Colab.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import requests

# ----------------------------------------------------------------------------
# 1. KONFIGURASI
# ----------------------------------------------------------------------------
LAT, LON = -6.8915, 107.6107          # Kampus ITB Ganesha, Bandung
LOKASI = "ITB Ganesha, Bandung"
TZ = "Asia/Jakarta"                    # WIB (UTC+7)

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HISTORICAL_URL = "https://historical-forecast-api.open-meteo.com/v1/forecast"  # ada uv_index (sejak 2022)

HOURLY_VARS = [
    "temperature_2m", "relative_humidity_2m", "apparent_temperature",
    "uv_index", "uv_index_clear_sky", "cloud_cover", "precipitation",
]

# Segmen waktu harian (jam lokal WIB). Format: nama -> (jam_mulai, jam_selesai_eksklusif)
# Ubah di sini jika ingin pembagian lain.
SEGMEN = {
    "Dini hari": (0, 6),
    "Pagi":      (6, 10),
    "Siang":     (10, 15),
    "Sore":      (15, 18),
    "Malam":     (18, 24),
}
SEGMEN_ORDER = list(SEGMEN.keys())

# Model cuaca Open-Meteo yang dibandingkan untuk menaksir ketidakpastian antar-model.
# Model yang tidak menyediakan uv_index otomatis dilewati.
MODELS = ["ecmwf_ifs025", "gfs_seamless", "icon_seamless", "gem_seamless"]
# Asumsi galat input untuk heat index (suhu udara °C, kelembapan %), dipakai untuk kisaran HI.
HI_ERR_T, HI_ERR_RH = 1.0, 10.0

# ----------------------------------------------------------------------------
# 2. AMBIL DATA
# ----------------------------------------------------------------------------
def _to_df(payload: dict) -> pd.DataFrame:
    h = payload["hourly"]
    df = pd.DataFrame(h)
    df["time"] = pd.to_datetime(df["time"])           # sudah jam lokal (timezone=Asia/Jakarta)
    return df


def fetch_forecast(past_days: int = 2, forecast_days: int = 3, session=None) -> pd.DataFrame:
    """Data per jam: past_days ke belakang + forecast_days ke depan (termasuk hari ini)."""
    s = session or requests
    r = s.get(FORECAST_URL, timeout=30, params={
        "latitude": LAT, "longitude": LON, "hourly": ",".join(HOURLY_VARS),
        "timezone": TZ, "past_days": past_days, "forecast_days": forecast_days,
    })
    r.raise_for_status()
    return add_indices(_to_df(r.json()))


def fetch_historical(start: str, end: str, session=None) -> pd.DataFrame:
    """Data per jam rentang tanggal (YYYY-MM-DD) dari Historical Forecast API.
    Dipecah per ~6 bulan agar request ringan."""
    s = session or requests
    out = []
    for a, b in _chunks(pd.Timestamp(start), pd.Timestamp(end)):
        r = s.get(HISTORICAL_URL, timeout=60, params={
            "latitude": LAT, "longitude": LON, "hourly": ",".join(HOURLY_VARS),
            "timezone": TZ, "start_date": a.date().isoformat(), "end_date": b.date().isoformat(),
        })
        r.raise_for_status()
        out.append(_to_df(r.json()))
    return add_indices(pd.concat(out, ignore_index=True).drop_duplicates("time"))


def fetch_model(model: str, past_days: int = 0, forecast_days: int = 2, session=None) -> pd.DataFrame:
    """Data per jam dari SATU model tertentu (untuk membandingkan antar-model)."""
    s = session or requests
    r = s.get(FORECAST_URL, timeout=30, params={
        "latitude": LAT, "longitude": LON, "hourly": ",".join(HOURLY_VARS), "models": model,
        "timezone": TZ, "past_days": past_days, "forecast_days": forecast_days,
    })
    r.raise_for_status()
    df = _to_df(r.json())
    df.columns = [c[: -len(model) - 1] if c.endswith("_" + model) else c for c in df.columns]
    if "uv_index" not in df or df["uv_index"].isna().all():
        raise ValueError(f"model {model} tidak menyediakan uv_index")
    for c in HOURLY_VARS:
        if c not in df:
            df[c] = np.nan
    return add_indices(df)


def fetch_models(models=None, **kw) -> dict:
    """Ambil beberapa model; yang gagal/tanpa UV dilewati (dicetak sebagai peringatan)."""
    out = {}
    for m in (models or MODELS):
        try:
            out[m] = fetch_model(m, **kw)
        except Exception as e:  # noqa: BLE001
            print(f"[lewati model {m}] {type(e).__name__}: {e}")
    return out


def _chunks(start: pd.Timestamp, end: pd.Timestamp, days: int = 180):
    cur = start
    while cur <= end:
        nxt = min(cur + pd.Timedelta(days=days - 1), end)
        yield cur, nxt
        cur = nxt + pd.Timedelta(days=1)

# ----------------------------------------------------------------------------
# 3. INDEKS & KLASIFIKASI
# ----------------------------------------------------------------------------
def heat_index_c(t_c, rh):
    """Heat Index (NWS Rothfusz + koreksi), input suhu udara °C & RH %, output °C.

    Di bawah ~27 °C rumus ini praktis ≈ suhu udara (memang demikian definisinya).
    """
    t_c = np.asarray(t_c, dtype=float)
    rh = np.asarray(rh, dtype=float)
    t = t_c * 9 / 5 + 32
    simple = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + rh * 0.094)
    full = (-42.379 + 2.04901523 * t + 10.14333127 * rh - 0.22475541 * t * rh
            - 0.00683783 * t * t - 0.05481717 * rh * rh + 0.00122874 * t * t * rh
            + 0.00085282 * t * rh * rh - 0.00000199 * t * t * rh * rh)
    adj1 = np.where((rh < 13) & (t >= 80) & (t <= 112),
                    -((13 - rh) / 4) * np.sqrt(np.clip((17 - np.abs(t - 95)) / 17, 0, None)), 0.0)
    adj2 = np.where((rh > 85) & (t >= 80) & (t <= 87), ((rh - 85) / 10) * ((87 - t) / 5), 0.0)
    hi_f = np.where((simple + t) / 2 < 80, simple, full + adj1 + adj2)
    return (hi_f - 32) * 5 / 9


def add_indices(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["heat_index"] = heat_index_c(df["temperature_2m"], df["relative_humidity_2m"]).round(1)
    df["tanggal"] = df["time"].dt.normalize()
    df["jam"] = df["time"].dt.hour
    df["segmen"] = df["jam"].map(segmen_of_hour)
    return df


def segmen_of_hour(h: int) -> str:
    for nama, (a, b) in SEGMEN.items():
        if a <= h < b:
            return nama
    raise ValueError(h)


# WHO / WMO UV index
UV_LEVELS = [  # (batas_bawah, kode, label, emoji)
    (0.0, 0, "Rendah", "🟢"),      # 0–2.9 (0 = tidak ada sinar)
    (3.0, 1, "Sedang", "🟡"),
    (6.0, 2, "Tinggi", "🟠"),
    (8.0, 3, "Sangat tinggi", "🔴"),
    (11.0, 4, "Ekstrem", "🟣"),
]

# Heat index NOAA/NWS (°C)
HI_LEVELS = [
    (-99.0, 0, "Nyaman/normal", "🟢"),
    (27.0, 1, "Waspada (caution)", "🟡"),
    (32.0, 2, "Sangat waspada", "🟠"),
    (41.0, 3, "Bahaya", "🔴"),
    (54.0, 4, "Sangat bahaya", "🟣"),
]


def _level(value: float, table):
    chosen = table[0]
    for row in table:
        if value >= row[0]:
            chosen = row
    return chosen  # (batas, kode, label, emoji)


def uv_level(v: float):
    return _level(round(float(v), 1), UV_LEVELS)


def hi_level(v: float):
    return _level(float(v), HI_LEVELS)

# ----------------------------------------------------------------------------
# 4. RINGKASAN SEGMEN & REKOMENDASI TINDAKAN
# ----------------------------------------------------------------------------
UV_TINDAKAN = {
    0: ["Tidak ada paparan UV berarti; tabir surya tidak diperlukan."],
    1: ["Aman beraktivitas di luar ruang.", "Tabir surya opsional (SPF 30 jika >1 jam)."],
    2: ["Oleskan tabir surya SPF 30+ 15–30 menit sebelum keluar.", "Pakai kacamata hitam; cari teduh saat terik."],
    3: ["Tabir surya SPF 50+, topi lebar, lengan panjang; ulangi oles tiap 2 jam.",
        "Batasi di luar ruang tanpa naungan; pindahkan kegiatan ke ruang teduh atau segmen UV lebih rendah."],
    4: ["Hindari aktivitas luar ruang tanpa perlindungan penuh (SPF 50+, topi, kacamata UV, pakaian menutup).",
        "Tunda kegiatan lapangan/olahraga ke segmen lain."],
}
HI_TINDAKAN = {
    0: [],
    1: ["Suhu terasa hangat: bawa air minum, istirahat di tempat teduh tiap ±1 jam."],
    2: ["Minum 1 gelas (±250 ml) tiap 20–30 menit; kurangi aktivitas berat; istirahat teduh tiap 30 menit."],
    3: ["Hindari aktivitas fisik berat di luar ruang; risiko kram/heat exhaustion."],
    4: ["Tunda semua aktivitas luar ruang; risiko heat stroke."],
}


def uv_bucket(uv: float) -> int:
    """Kelompok tindakan UV: 0 (<0,5) · 1 (<3) · 2 (<6) · 3 (<8) · 4 (>=8)."""
    return 0 if uv < 0.5 else 1 if uv < 3 else 2 if uv < 6 else 3 if uv < 8 else 4


def estimasi_menit_aman(uv: float) -> int | None:
    """Perkiraan kasar waktu sebelum kulit sensitif mulai memerah (~200/UVI menit)."""
    return None if uv < 1 else int(round(200 / uv, -1)) or 10


def rekomendasi(seg: str, uv_max: float, hi_max: float, cloud_mean: float, rain_sum: float) -> str:
    parts = list(_uv_actions(uv_max)) + HI_TINDAKAN[hi_level(hi_max)[1]]
    if uv_max >= 3 and cloud_mean >= 60:
        parts.append("Meski berawan/mendung, UV tetap menembus awan — tetap pakai perlindungan.")
    if rain_sum >= 1:
        parts.append("Ada potensi hujan; bawa payung/jas hujan.")
    return " ".join(parts)


def _uv_actions(uv_max: float) -> list[str]:
    if uv_max < 0.5:
        return UV_TINDAKAN[0]
    if uv_max < 3:
        return UV_TINDAKAN[1]
    if uv_max < 6:
        return UV_TINDAKAN[2]
    if uv_max < 8:
        return UV_TINDAKAN[3]
    return UV_TINDAKAN[4]


def ringkas_segmen(df_hari: pd.DataFrame, now: pd.Timestamp | None = None) -> pd.DataFrame:
    """Ringkasan per segmen untuk SATU hari (df_hari = baris jam-jam di hari itu)."""
    rows = []
    for seg in SEGMEN_ORDER:
        a, b = SEGMEN[seg]
        d = df_hari[df_hari["segmen"] == seg]
        if d.empty:
            continue
        i_uv = d["uv_index"].idxmax()
        uv_max = float(d.loc[i_uv, "uv_index"])
        i_hi = d["heat_index"].idxmax()
        hi_max = float(d.loc[i_hi, "heat_index"])
        status = ""
        if now is not None:
            start = d["time"].min().normalize() + pd.Timedelta(hours=a)
            end = d["time"].min().normalize() + pd.Timedelta(hours=b)
            status = "▶ Sekarang" if start <= now < end else ("Berikutnya" if now < start else "Sudah lewat")
        rows.append({
            "segmen": seg, "jam": f"{a:02d}:00–{b % 24:02d}:00" if b < 24 else f"{a:02d}:00–24:00",
            "status": status,
            "uv_max": round(uv_max, 1), "jam_uv_max": int(d.loc[i_uv, "jam"]) if uv_max > 0 else None,
            "uv_label": uv_level(uv_max)[2] if uv_max >= 0.5 else "Tidak ada",
            "uv_emoji": uv_level(uv_max)[3] if uv_max >= 0.5 else "⚫",
            "hi_max": round(hi_max, 1), "jam_hi_max": int(d.loc[i_hi, "jam"]),
            "hi_label": hi_level(hi_max)[2], "hi_emoji": hi_level(hi_max)[3],
            "t_hi": float(d.loc[i_hi, "temperature_2m"]), "rh_hi": float(d.loc[i_hi, "relative_humidity_2m"]),
            "suhu_mean": round(float(d["temperature_2m"].mean()), 1),
            "rh_mean": round(float(d["relative_humidity_2m"].mean())),
            "awan_mean": round(float(d["cloud_cover"].mean())),
            "hujan_mm": round(float(d["precipitation"].sum()), 1),
            "tindakan": rekomendasi(seg, uv_max, hi_max, float(d["cloud_cover"].mean()), float(d["precipitation"].sum())),
        })
    return pd.DataFrame(rows)


def jendela_aman_uv(df_hari: pd.DataFrame, batas: float = 3.0, jam_awal: int = 6, jam_akhir: int = 18) -> list[tuple[int, int]]:
    """Rentang jam siang (06–18) saat UV < batas, berupa [(jam_mulai, jam_selesai_eksklusif), ...]."""
    d = df_hari[(df_hari["jam"] >= jam_awal) & (df_hari["jam"] < jam_akhir)].sort_values("jam")
    ok = (d["uv_index"] < batas).tolist()
    jam = d["jam"].tolist()
    out, start = [], None
    for h, flag in zip(jam, ok):
        if flag and start is None:
            start = h
        if not flag and start is not None:
            out.append((start, h)); start = None
    if start is not None:
        out.append((start, jam[-1] + 1))
    return out


def fmt_jendela(w: list[tuple[int, int]]) -> str:
    return ", ".join(f"{a:02d}:00–{b:02d}:00" for a, b in w) if w else "tidak ada"


# ----------------------------------------------------------------------------
# 5. KETIDAKPASTIAN
# ----------------------------------------------------------------------------
def kisaran_model(per_model: dict, tanggal) -> pd.DataFrame:
    """Maks UV & HI per segmen untuk tiap model pada satu tanggal."""
    rows = []
    for m, df in per_model.items():
        d = df[df["tanggal"] == pd.Timestamp(tanggal).normalize()]
        if d.empty:
            continue
        g = d.groupby("segmen").agg(uv=("uv_index", "max"), hi=("heat_index", "max")).reset_index()
        g["model"] = m
        rows.append(g)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["segmen", "uv", "hi", "model"])


def label_keyakinan(uv_lo: float, uv_hi: float, n_model: int) -> str:
    if n_model < 2:
        return "Tidak diketahui"
    if uv_bucket(uv_lo) == uv_bucket(uv_hi) and (uv_hi - uv_lo) <= 1.5:
        return "Tinggi"
    if abs(uv_bucket(uv_hi) - uv_bucket(uv_lo)) <= 1:
        return "Sedang"
    return "Rendah"


def tambah_ketidakpastian(seg: pd.DataFrame, per_model: dict, tanggal) -> pd.DataFrame:
    """Tambahkan kisaran UV/HI (antar-model + galat input HI), label keyakinan, dan tindakan skenario terburuk."""
    seg = seg.copy()
    kis = kisaran_model(per_model, tanggal)
    cols = {k: [] for k in ("uv_lo", "uv_hi", "hi_lo", "hi_hi", "n_model", "keyakinan")}
    tind = []
    for r in seg.itertuples():
        k = kis[kis["segmen"] == r.segmen]
        uvs = [r.uv_max] + k["uv"].dropna().tolist()
        his = [r.hi_max] + k["hi"].dropna().tolist()
        # galat input: T ± HI_ERR_T, RH ± HI_ERR_RH di jam HI maksimum
        his += [float(heat_index_c(r.t_hi - HI_ERR_T, max(r.rh_hi - HI_ERR_RH, 1))),
                float(heat_index_c(r.t_hi + HI_ERR_T, min(r.rh_hi + HI_ERR_RH, 100)))]
        n = 1 + k["model"].nunique()
        uv_lo, uv_hi = min(uvs), max(uvs)
        cols["uv_lo"].append(round(uv_lo, 1)); cols["uv_hi"].append(round(uv_hi, 1))
        cols["hi_lo"].append(round(min(his), 1)); cols["hi_hi"].append(round(max(his), 1))
        cols["n_model"].append(int(n)); cols["keyakinan"].append(label_keyakinan(uv_lo, uv_hi, n))
        if uv_bucket(uv_hi) > uv_bucket(r.uv_max) or hi_level(max(his))[1] > hi_level(r.hi_max)[1]:
            tind.append("⚠️ Prakiraan tidak pasti; memakai skenario terburuk. "
                        + rekomendasi(r.segmen, uv_hi, max(his), r.awan_mean, r.hujan_mm))
        else:
            tind.append(r.tindakan)
    for k_, v in cols.items():
        seg[k_] = v
    seg["tindakan"] = tind
    return seg


def teks_kepastian(r) -> str:
    """Satu baris ringkas untuk tabel: keyakinan + kisaran."""
    if getattr(r, "uv_hi", 0) < 0.5 and r.uv_max < 0.5:
        return f"{r.keyakinan}. HI {r.hi_lo:.0f}–{r.hi_hi:.0f} °C"
    return f"{r.keyakinan}. UV {r.uv_lo:.1f}–{r.uv_hi:.1f}, HI {r.hi_lo:.0f}–{r.hi_hi:.0f} °C ({r.n_model} model)"
