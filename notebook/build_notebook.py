"""Membangun Bandung_UV_HeatIndex.ipynb dari uvheat/core.py (supaya notebook & repo selalu sinkron).
Jalankan:  python notebook/build_notebook.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = (ROOT / "uvheat" / "core.py").read_text(encoding="utf-8")

cells = []
md = lambda t: cells.append(("markdown", t.strip("\n")))
code = lambda t: cells.append(("code", t.strip("\n")))

md("""
# ☀️ UV & Heat Index Bandung (ITB) menurut Segmen Waktu Harian

**Tujuan:** menjelaskan bagaimana intensitas sinar UV dan heat index di Bandung (ITB Ganesha) berubah menurut waktu dalam sehari (dini hari, pagi, siang, sore, malam), lalu menerjemahkannya menjadi **tindakan** yang masuk akal.

**Sumber data:** [Open-Meteo](https://open-meteo.com/) saja (Historical Forecast API untuk riwayat per jam, Forecast API untuk hari ini). Tidak perlu API key.

**Alur notebook**
1. Konsep dasar (UV index, heat index, kenapa segmen waktu)
2. Pengambilan data & pemeriksaan kualitas
3. Profil harian rata-rata
4. Statistik per segmen waktu (inti analisis)
5. Pola musiman, pengaruh awan, jendela aman
6. Prakiraan **hari ini** → tabel tindakan
7. Kesimpulan otomatis & ekspor

> Catatan zona waktu: Bandung seluruhnya berada di **WIB (UTC+7)**, jadi "zona waktu" di sini dibaca sebagai **segmen waktu dalam sehari**. Batas jam segmen dapat diubah pada variabel `SEGMEN`.
""")

md("""
## 1. Konsep dasar

**Indeks UV (UVI)** — ukuran intensitas UV yang berpengaruh pada kulit (eritema). UVI 1 ≈ 25 mW/m². Skala WHO:

| UVI | Kategori | Makna singkat |
|---|---|---|
| 0–2 | Rendah 🟢 | Aman |
| 3–5 | Sedang 🟡 | Perlu perlindungan |
| 6–7 | Tinggi 🟠 | Perlu perlindungan ekstra |
| 8–10 | Sangat tinggi 🔴 | Hindari paparan tanpa naungan |
| ≥11 | Ekstrem 🟣 | Hindari luar ruang |

UV ditentukan terutama oleh **sudut matahari** (jam), lalu **awan**, **ozon**, dan **ketinggian** (Bandung ±770 mdpl → UV sedikit lebih kuat dibanding permukaan laut). Bandung di ±6,9° LS sehingga matahari hampir selalu tinggi: UV bisa mencapai kategori "sangat tinggi–ekstrem" sepanjang tahun.

**Heat index (HI)** — "suhu terasa" dari kombinasi suhu udara & kelembapan (rumus NWS/NOAA, Rothfusz). Ambang (°C): <27 nyaman · 27–32 waspada · 32–41 sangat waspada · 41–54 bahaya · ≥54 sangat bahaya. Di bawah ±27 °C rumusnya praktis sama dengan suhu udara, sehingga di kota sejuk seperti Bandung HI sering **tidak melampaui ambang**. Sebagai pembanding, Open-Meteo juga menyediakan `apparent_temperature` (memperhitungkan angin & radiasi).

**Kenapa segmen waktu?** UV dan suhu mengikuti siklus matahari: UV nyaris nol malam hari, mulai naik ±06:00, puncak sekitar tengah hari (kira-kira 11:30–12:10 WIB di Bandung), lalu turun. Kebiasaan manusia (kuliah, olahraga, makan siang, pulang) juga mengikuti segmen — jadi rekomendasi paling berguna jika dikaitkan ke segmen.
""")

md("## 2. Setup & fungsi inti\nSel berikut berisi konfigurasi lokasi, pemanggilan Open-Meteo, rumus heat index, klasifikasi, segmen waktu, dan aturan rekomendasi. (Isinya sama persis dengan `uvheat/core.py` di repo GitHub.)")
code(CORE)

code("""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display, Markdown

pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", 200)
plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": .25})

SEKARANG = pd.Timestamp.now(tz=TZ).tz_localize(None)
HARI_INI = SEKARANG.normalize()
print("Lokasi :", LOKASI, (LAT, LON))
print("Sekarang (WIB):", SEKARANG.strftime("%Y-%m-%d %H:%M"))
print("Segmen :", {k: f"{a:02d}-{b:02d}" for k, (a, b) in SEGMEN.items()})
""")

md("## 3. Ambil data historis per jam\nDefault: 1 Jan 2023 s.d. kemarin. Jika UV kosong di tahun awal (lihat pemeriksaan di bawah), geser `AWAL` ke tahun yang datanya lengkap.")
code("""
AWAL = "2023-01-01"
AKHIR = (HARI_INI - pd.Timedelta(days=1)).date().isoformat()

hist = fetch_historical(AWAL, AKHIR)
print(f"{len(hist):,} baris per jam · {hist['time'].min()} → {hist['time'].max()}")
hist.head()
""")

md("### Pemeriksaan kualitas data")
code("""
cek = hist.groupby(hist["time"].dt.year)[HOURLY_VARS + ["heat_index"]].agg(lambda s: s.isna().mean() * 100).round(1)
cek.columns = [c.replace("_2m", "") for c in cek.columns]
print("Persentase data KOSONG per tahun (%):")
display(cek)
if hist["uv_index"].isna().mean() > 0.2:
    print("⚠️ UV kosong >20%. Naikkan AWAL ke tahun yang datanya terisi.")
hist = hist.dropna(subset=["uv_index", "temperature_2m", "relative_humidity_2m"]).reset_index(drop=True)
print("Baris dipakai:", f"{len(hist):,}")
display(hist[["temperature_2m", "relative_humidity_2m", "apparent_temperature", "heat_index", "uv_index", "cloud_cover"]].describe().round(1))
""")

md("""
## 4. Profil harian rata-rata
Garis = rata-rata semua hari; area = rentang persentil 10–90 (variasi cuaca antarhari, terutama awan).
""")
code("""
prof = hist.groupby("jam").agg(
    uv_mean=("uv_index", "mean"), uv_p10=("uv_index", lambda s: s.quantile(.1)), uv_p90=("uv_index", lambda s: s.quantile(.9)),
    hi_mean=("heat_index", "mean"), hi_p10=("heat_index", lambda s: s.quantile(.1)), hi_p90=("heat_index", lambda s: s.quantile(.9)),
    t_mean=("temperature_2m", "mean"), rh_mean=("relative_humidity_2m", "mean"))

fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
for lo, hi, c in [(0, 3, "#9be29b"), (3, 6, "#ffe680"), (6, 8, "#ffb366"), (8, 11, "#ff7f7f"), (11, 16, "#c9a0ff")]:
    a1.axhspan(lo, hi, color=c, alpha=.3, lw=0)
a1.fill_between(prof.index, prof.uv_p10, prof.uv_p90, color="gray", alpha=.3, label="P10–P90")
a1.plot(prof.index, prof.uv_mean, "k", lw=2, label="rata-rata")
a1.set_ylabel("Indeks UV"); a1.legend(); a1.set_ylim(0, max(12, prof.uv_p90.max() + 1))
a2.fill_between(prof.index, prof.hi_p10, prof.hi_p90, color="#d9480f", alpha=.2, label="Heat index P10–P90")
a2.plot(prof.index, prof.hi_mean, color="#d9480f", lw=2, label="Heat index rata-rata")
a2.plot(prof.index, prof.t_mean, color="#1c7ed6", lw=1.5, label="Suhu udara rata-rata")
a2.axhline(27, color="gray", ls="--", lw=1); a2.text(0.2, 27.2, "ambang waspada HI 27 °C", fontsize=8)
a2.set_ylabel("°C"); a2.set_xlabel("Jam (WIB)"); a2.legend(); a2.set_xticks(range(0, 24, 2))
for ax in (a1, a2):
    for a, _ in SEGMEN.values(): ax.axvline(a, color="gray", lw=.6, ls="--")
for nama, (a, b) in SEGMEN.items():
    a1.text((a + b) / 2, a1.get_ylim()[1] * .94, nama, ha="center", fontsize=9, weight="bold")
fig.suptitle(f"Profil harian UV & heat index — {LOKASI} ({AWAL[:4]}–{AKHIR[:4]})"); fig.tight_layout(); plt.show()

jam_puncak = int(prof.uv_mean.idxmax())
print(f"Jam dengan rata-rata UV tertinggi: {jam_puncak:02d}:00 WIB (UV rata-rata {prof.uv_mean.max():.1f})")
print(f"Jam dengan rata-rata heat index tertinggi: {int(prof.hi_mean.idxmax()):02d}:00 WIB ({prof.hi_mean.max():.1f} °C)")
""")

md("""
## 5. Statistik per segmen waktu (inti analisis)
Untuk setiap hari & segmen diambil nilai **maksimum** (kondisi terburuk dalam segmen itu), lalu dihitung sebarannya di semua hari. Kolom `%hari UV≥6` = persentase hari ketika UV segmen itu mencapai kategori Tinggi atau lebih.
""")
code("""
harian = (hist.groupby(["tanggal", "segmen"])
          .agg(uv_max=("uv_index", "max"), hi_max=("heat_index", "max"), t_max=("temperature_2m", "max"),
               awan=("cloud_cover", "mean"), hujan=("precipitation", "sum"))
          .reset_index())

def pct(s, cond): return round(100 * cond(s).mean(), 1)
ringkas = harian.groupby("segmen").apply(lambda d: pd.Series({
    "UV maks rata-rata": d.uv_max.mean(), "UV maks median": d.uv_max.median(), "UV maks P90": d.uv_max.quantile(.9),
    "%hari UV≥3": pct(d.uv_max, lambda s: s >= 3), "%hari UV≥6": pct(d.uv_max, lambda s: s >= 6),
    "%hari UV≥8": pct(d.uv_max, lambda s: s >= 8), "%hari UV≥11": pct(d.uv_max, lambda s: s >= 11),
    "HI maks rata-rata": d.hi_max.mean(), "HI maks P90": d.hi_max.quantile(.9),
    "%hari HI≥27": pct(d.hi_max, lambda s: s >= 27), "%hari HI≥32": pct(d.hi_max, lambda s: s >= 32),
    "Awan rata-rata %": d.awan.mean()}), include_groups=False).reindex(SEGMEN_ORDER).round(1)
display(ringkas)
""")

code("""
fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
data_uv = [harian.loc[harian.segmen == s, "uv_max"] for s in SEGMEN_ORDER]
data_hi = [harian.loc[harian.segmen == s, "hi_max"] for s in SEGMEN_ORDER]
axs[0].boxplot(data_uv, tick_labels=SEGMEN_ORDER, showfliers=False)
for y in (3, 6, 8, 11): axs[0].axhline(y, color="gray", ls="--", lw=.8)
axs[0].set_title("UV maksimum per segmen (semua hari)"); axs[0].set_ylabel("UVI")
axs[1].boxplot(data_hi, tick_labels=SEGMEN_ORDER, showfliers=False)
for y in (27, 32): axs[1].axhline(y, color="gray", ls="--", lw=.8)
axs[1].set_title("Heat index maksimum per segmen (semua hari)"); axs[1].set_ylabel("°C")
fig.tight_layout(); plt.show()

# komposisi kategori UV per segmen
bins, labels = [-.01, 2.95, 5.95, 7.95, 10.95, 99], ["Rendah", "Sedang", "Tinggi", "Sangat tinggi", "Ekstrem"]
harian["kategori_uv"] = pd.cut(harian.uv_max.round(1), bins=bins, labels=labels)
komp = (harian.groupby(["segmen", "kategori_uv"], observed=False).size().unstack(fill_value=0)
        .reindex(SEGMEN_ORDER)); komp = komp.div(komp.sum(axis=1), axis=0) * 100
ax = komp.plot(kind="bar", stacked=True, figsize=(9, 4), color=["#9be29b", "#ffe680", "#ffb366", "#ff7f7f", "#c9a0ff"], width=.75)
ax.set_ylabel("% hari"); ax.set_title("Komposisi kategori UV maksimum per segmen"); ax.legend(ncol=5, fontsize=8, loc="upper center", bbox_to_anchor=(.5, -.12))
plt.xticks(rotation=0); plt.tight_layout(); plt.show()
""")

md("## 6. Pola musiman: rata-rata UV dan heat index menurut bulan × jam")
code("""
fig, axs = plt.subplots(1, 2, figsize=(13, 4.2))
for ax, col, cmap, ttl in ((axs[0], "uv_index", "YlOrRd", "UV rata-rata"), (axs[1], "heat_index", "YlOrBr", "Heat index rata-rata (°C)")):
    pv = hist.assign(bulan=hist.time.dt.month).pivot_table(index="bulan", columns="jam", values=col, aggfunc="mean")
    im = ax.imshow(pv.values, aspect="auto", cmap=cmap, origin="lower")
    ax.set_yticks(range(len(pv)), [["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"][m - 1] for m in pv.index])
    ax.set_xticks(range(0, 24, 2), range(0, 24, 2)); ax.set_xlabel("Jam (WIB)"); ax.set_title(ttl); fig.colorbar(im, ax=ax)
fig.tight_layout(); plt.show()

per_bulan = harian[harian.segmen == "Siang"].assign(bulan=lambda d: d.tanggal.dt.month).groupby("bulan").agg(
    uv_siang_rata2=("uv_max", "mean"), hari_uv_ge8_pct=("uv_max", lambda s: 100 * (s >= 8).mean()),
    hi_siang_rata2=("hi_max", "mean"), awan_siang=("awan", "mean")).round(1)
print("Segmen SIANG per bulan:"); display(per_bulan)
""")

md("""
## 7. Pengaruh awan terhadap UV
`uv_index_clear_sky` = UV jika langit cerah. Rasio `UV aktual / UV cerah` menunjukkan seberapa besar awan meredam UV. Kalau rasio tetap tinggi saat mendung, "mendung = aman" adalah mitos.
""")
code("""
d = hist[(hist.uv_index_clear_sky >= 3)].copy()
d["rasio"] = (d.uv_index / d.uv_index_clear_sky).clip(0, 1.2)
d["awan_bin"] = pd.cut(d.cloud_cover, [-1, 25, 50, 75, 100], labels=["0–25%", "25–50%", "50–75%", "75–100%"])
efek = d.groupby("awan_bin", observed=False).agg(rasio_UV_persen=("rasio", lambda s: 100 * s.mean()), n_jam=("rasio", "size")).round(0)
display(efek)
ax = efek.rasio_UV_persen.plot(kind="bar", figsize=(6, 3.5), color="#f08c00"); ax.set_ylabel("% dari UV langit cerah"); ax.set_xlabel("Tutupan awan")
ax.set_title("UV yang tembus menurut tutupan awan"); plt.xticks(rotation=0); plt.tight_layout(); plt.show()
""")

md("## 8. Seberapa sering heat index benar-benar melewati ambang di Bandung?")
code("""
delta = (hist.heat_index - hist.temperature_2m)
print(f"Selisih rata-rata HI − suhu udara: {delta.mean():.2f} °C (maks {delta.max():.1f} °C)")
tot = len(hist)
for batas, nama in ((27, "waspada"), (32, "sangat waspada"), (41, "bahaya")):
    print(f"Jam dengan HI ≥ {batas} °C ({nama}): {100 * (hist.heat_index >= batas).sum() / tot:.2f}% dari semua jam")
tab = (hist[hist.heat_index >= 27].groupby("segmen").size().reindex(SEGMEN_ORDER).fillna(0).astype(int))
print("\\nJam HI ≥ 27 °C per segmen:"); display(tab.to_frame("jumlah jam"))
""")

md("""
## 9. Jendela aman UV (< 3)
Peluang UV < 3 untuk setiap jam siang (06–17 WIB) — jam dengan peluang tinggi aman untuk aktivitas luar ruang tanpa perlindungan khusus.
""")
code("""
aman = hist[(hist.jam >= 6) & (hist.jam < 18)].groupby("jam").apply(lambda d: 100 * (d.uv_index < 3).mean(), include_groups=False)
ax = aman.plot(kind="bar", figsize=(9, 3.5), color=["#2f9e44" if v >= 80 else "#f59f00" if v >= 40 else "#e03131" for v in aman])
ax.set_ylabel("% hari dengan UV < 3"); ax.set_xlabel("Jam (WIB)"); ax.axhline(80, color="gray", ls="--", lw=1)
ax.set_title("Peluang jam aman UV"); plt.xticks(rotation=0); plt.tight_layout(); plt.show()
jam_aman = [int(j) for j, v in aman.items() if v >= 80]
print("Jam dengan ≥80% hari UV<3:", ", ".join(f"{j:02d}:00" for j in jam_aman) or "tidak ada")
""")

md("""
## 10. Prakiraan HARI INI → tabel tindakan
Data langsung dari Open-Meteo Forecast API. Tindakan disusun dari aturan di `UV_TINDAKAN` dan `HI_TINDAKAN` pada sel inti (bisa Anda ubah). Kolom **Kepastian** membandingkan beberapa model Open-Meteo dan memperhitungkan galat input heat index; bila kisarannya melintasi kategori yang lebih berat, tindakan memakai **skenario terburuk** (tanda ⚠️).
""")
code("""
live = fetch_forecast(past_days=1, forecast_days=2)
hari = live[live.tanggal == HARI_INI].reset_index(drop=True)
seg = ringkas_segmen(hari, SEKARANG)
per_model = fetch_models(past_days=0, forecast_days=1)          # model pembanding untuk kisaran ketidakpastian
print("Model pembanding yang menyediakan UV:", list(per_model) or "tidak ada (kepastian = 'Tidak diketahui')")
seg = tambah_ketidakpastian(seg, per_model, HARI_INI)

i = hari.uv_index.idxmax(); uv_p = hari.loc[i, "uv_index"]; lv = uv_level(uv_p)
display(Markdown(f"### {HARI_INI:%A, %d %B %Y} — {LOKASI}\\n"
                 f"{lv[3]} **UV puncak {uv_p:.1f} ({lv[2]}) pukul {int(hari.loc[i, 'jam']):02d}:00 WIB** · "
                 f"estimasi kulit sensitif mulai memerah ± {estimasi_menit_aman(uv_p)} menit pada puncak (kasar) · "
                 f"jendela aman UV<3: **{fmt_jendela(jendela_aman_uv(hari))}** · heat index tertinggi {hari.heat_index.max():.1f} °C"))

tabel = seg.assign(
    UV=lambda d: d.uv_emoji + " " + d.uv_max.astype(str) + " " + d.uv_label,
    HeatIndex=lambda d: d.hi_emoji + " " + d.hi_max.astype(str) + " °C " + d.hi_label,
    SuhuRH=lambda d: d.suhu_mean.astype(int).astype(str) + " °C / " + d.rh_mean.astype(str) + "%",
    Kepastian=lambda d: [teks_kepastian(r) for r in d.itertuples()],
)[["segmen", "jam", "status", "UV", "HeatIndex", "SuhuRH", "Kepastian", "tindakan"]]
tabel.columns = ["Segmen", "Jam (WIB)", "Status", "UV maks", "Heat index maks", "Suhu / RH", "Kepastian (kisaran)", "Yang sebaiknya dilakukan"]
display(tabel.style.hide(axis="index").set_properties(subset=["Yang sebaiknya dilakukan"], **{"text-align": "left", "white-space": "normal"}))

fig, ax = plt.subplots(figsize=(10, 3.8))
for lo, hi, c in [(0, 3, "#9be29b"), (3, 6, "#ffe680"), (6, 8, "#ffb366"), (8, 11, "#ff7f7f"), (11, 16, "#c9a0ff")]:
    ax.axhspan(lo, hi, color=c, alpha=.3, lw=0)
ax.plot(hari.jam + .5, hari.uv_index, "k", lw=2, label="UV"); ax.plot(hari.jam + .5, hari.uv_index_clear_sky, "k--", lw=1, alpha=.6, label="UV langit cerah")
ax.axvline(SEKARANG.hour + SEKARANG.minute / 60, color="crimson", lw=1.5, label="sekarang")
for a, _ in SEGMEN.values(): ax.axvline(a, color="gray", lw=.6, ls="--")
ax.set_xlim(0, 24); ax.set_ylim(0, max(12, hari.uv_index.max() + 1)); ax.set_xlabel("Jam (WIB)"); ax.set_ylabel("UVI"); ax.legend(loc="upper left"); ax.set_title("UV hari ini")
plt.tight_layout(); plt.show()
""")


md("""
## 11. Analisis ketidakpastian
Ketidakpastian dalam analisis ini berasal dari dua jenis sumber yang berbeda sifatnya:

| Jenis | Sumber | Bagaimana ditangani di notebook ini |
|---|---|---|
| **Variabilitas alami** (aleatorik) | Cuaca/awan berbeda tiap hari | Persentil P10–P90 (seksi 4–5) dan *bootstrap* untuk kepastian statistik (11A) |
| **Galat model** (epistemik) | Data Open-Meteo = keluaran model, bukan sensor ITB; tiap model berbeda | Perbandingan antar-model (11B) |
| **Galat input & rumus** | Heat index dihitung dari suhu & RH yang masing-masing punya galat; rumus regresi punya galat sendiri | Simulasi Monte Carlo (11C) |
| **Pilihan analis** | Batas jam segmen, ambang kategori | Uji sensitivitas batas segmen (11D) |
""")

md("### 11A. Seberapa pasti statistik per segmen? (bootstrap antarhari)\nHari diambil ulang secara acak dengan pengembalian (1.000×) untuk mendapat selang kepercayaan 95%. *Asumsi: hari-hari saling bebas; kenyataannya cuaca berautokorelasi sehingga selang ini cenderung sedikit **terlalu sempit**. Rentang data juga hanya beberapa tahun, jadi bukan klimatologi jangka panjang.*")
code("""
rng = np.random.default_rng(42)
def boot(vals, fn, n=1000):
    idx = rng.integers(0, len(vals), (n, len(vals)))
    est = fn(vals[idx])
    return np.percentile(est, [2.5, 97.5])

baris = []
for sg in ("Pagi", "Siang", "Sore"):
    v = harian.loc[harian.segmen == sg, "uv_max"].to_numpy()
    m, lo_hi = v.mean(), boot(v, lambda a: a.mean(1))
    p6, c6 = 100 * (v >= 6).mean(), boot(v, lambda a: 100 * (a >= 6).mean(1))
    p8, c8 = 100 * (v >= 8).mean(), boot(v, lambda a: 100 * (a >= 8).mean(1))
    baris.append({"Segmen": sg, "n hari": len(v),
                  "UV maks rata-rata": f"{m:.1f} ({lo_hi[0]:.1f}–{lo_hi[1]:.1f})",
                  "%hari UV≥6": f"{p6:.0f} ({c6[0]:.0f}–{c6[1]:.0f})",
                  "%hari UV≥8": f"{p8:.0f} ({c8[0]:.0f}–{c8[1]:.0f})"})
ci_tab = pd.DataFrame(baris).set_index("Segmen")
print("Nilai (selang kepercayaan 95%):"); display(ci_tab)
""")

md("### 11B. Seberapa setuju model-model cuaca? (30 hari terakhir)\nUV segmen dihitung dari tiap model Open-Meteo secara terpisah. **Spread** = selisih UV maksimum antara model tertinggi dan terendah pada hari & segmen yang sama; `% beda kategori` = persentase hari ketika model-model jatuh ke kelompok tindakan yang berbeda.")
code("""
pm30 = fetch_models(past_days=30, forecast_days=1)
print("Model yang tersedia:", list(pm30))
spread_tab = None
if len(pm30) >= 2:
    frames = [d.groupby(["tanggal", "segmen"]).uv_index.max().rename(m) for m, d in pm30.items()]
    tab = pd.concat(frames, axis=1).dropna()
    tab["spread"] = tab.max(axis=1) - tab.min(axis=1)
    tab["beda_kategori"] = tab[list(pm30)].apply(lambda r: len({uv_bucket(v) for v in r}) > 1, axis=1)
    day = tab.reset_index()
    day = day[day.segmen.isin(["Pagi", "Siang", "Sore"])]
    spread_tab = day.groupby("segmen").agg(spread_rata2=("spread", "mean"), spread_P90=("spread", lambda s: s.quantile(.9)),
                                           pct_beda_kategori=("beda_kategori", lambda s: 100 * s.mean())).reindex(["Pagi", "Siang", "Sore"]).round(1)
    spread_tab.columns = ["Spread UV rata-rata", "Spread UV P90", "% hari beda kategori"]
    display(spread_tab)
    ax = day.boxplot(column="spread", by="segmen", figsize=(6, 3.5)); ax.set_ylabel("Spread UV antar-model"); plt.suptitle(""); ax.set_title("Perbedaan UV antar-model per segmen"); plt.tight_layout(); plt.show()
else:
    print("Kurang dari 2 model menyediakan UV; perbandingan antar-model dilewati.")
""")

md("### 11C. Ketidakpastian heat index (Monte Carlo)\nSuhu udara diganggu *N(0, 1 °C)* dan RH *N(0, 8 %)* (asumsi galat model; ubah sesuai kebutuhan), lalu heat index dihitung ulang 200 kali pada jam 09–15. Selain itu, NWS menyatakan regresi Rothfusz sendiri punya galat sekitar ±1,3 °F (≈ ±0,7 °C) — **tidak** disertakan dalam simulasi sehingga ketidakpastian total sedikit lebih besar.")
code("""
rng = np.random.default_rng(1)
ds = hist[hist.jam.between(9, 14)]
T0, RH0 = ds.temperature_2m.to_numpy(), ds.relative_humidity_2m.to_numpy()
mc = np.array([heat_index_c(T0 + rng.normal(0, 1.0, len(ds)), np.clip(RH0 + rng.normal(0, 8, len(ds)), 1, 100)) for _ in range(200)])
base = ds.heat_index.to_numpy()
print(f"Simpangan baku HI akibat galat input (rata-rata jam 09–14): {mc.std(0).mean():.2f} °C")
for batas in (27, 32):
    frac = 100 * (mc >= batas).mean(1)
    print(f"Jam dengan HI ≥ {batas} °C: basis {100 * (base >= batas).mean():.1f}% → dengan galat input {frac.mean():.1f}% (95%: {np.percentile(frac, 2.5):.1f}–{np.percentile(frac, 97.5):.1f}%)")
""")

md("### 11D. Sensitivitas terhadap pilihan batas segmen\nSegmen \"Siang\" didefinisikan 10:00–15:00. Berikut hasilnya bila batas digeser — menunjukkan seberapa besar kesimpulan bergantung pada pilihan analis.")
code("""
alt = {"Baku 10–15": (10, 15), "Geser −1 jam (09–14)": (9, 14), "Geser +1 jam (11–16)": (11, 16), "Lebih lebar (09–16)": (9, 16), "Lebih sempit (11–14)": (11, 14)}
rows = []
for nama, (a, b) in alt.items():
    mx = hist[(hist.jam >= a) & (hist.jam < b)].groupby("tanggal").uv_index.max()
    rows.append({"Definisi Siang": nama, "UV maks rata-rata": round(mx.mean(), 1), "%hari UV≥8": round(100 * (mx >= 8).mean(), 1), "%hari UV≥11": round(100 * (mx >= 11).mean(), 1)})
sens = pd.DataFrame(rows).set_index("Definisi Siang"); display(sens)
""")

md("""
### 11E. Ringkasan ketidakpastian & cara menyikapinya
*Pola umum yang diharapkan secara fisis — cocokkan dengan angka pada tabel 11A–11D di atas sebelum dipakai sebagai kesimpulan.*
- **Pagi/sore** diperkirakan paling tidak pasti: UV berada di lereng kurva harian (±1 jam saja bisa mengubah kategori) dan sensitif terhadap awan.
- **Siang** diperkirakan paling stabil secara kategori, tetapi bila sedikit di bawah ambang (mis. UV 7,6 vs ambang 8) kategorinya mudah berubah antarmodel.
- **Heat index** di Bandung biasanya jauh di bawah ambang sehingga galat input jarang mengubah kesimpulan; ia hanya relevan saat siang cerah-kering dengan suhu mendekati 27 °C ke atas.
- **Aturan keputusan:** bila model tidak sepakat atau kisaran melintasi kategori yang lebih berat, ikuti **skenario terburuk** (biaya perlindungan ekstra kecil dibanding risiko kulit terbakar).
""")

md("## 12. Kesimpulan otomatis (dibangkitkan dari data di atas)")
code("""
seg_uv = ringkas["%hari UV≥6"].drop("Dini hari").drop("Malam")
terburuk = seg_uv.idxmax()
pagi_aman = aman[aman >= 80].index.tolist()
lines = [
    f"- **Puncak UV rata-rata** terjadi sekitar **{jam_puncak:02d}:00 WIB** (rata-rata UVI {prof.uv_mean.max():.1f}).",
    f"- Segmen paling berisiko: **{terburuk}** — pada {seg_uv.max():.0f}% hari UV maksimumnya ≥ 6 (Tinggi), dan {ringkas.loc[terburuk, '%hari UV≥8']:.0f}% hari ≥ 8 (Sangat tinggi).",
    f"- Jam relatif aman (UV<3 di ≥80% hari): {', '.join(f'{j:02d}:00' for j in pagi_aman) or 'tidak ada'}.",
    f"- Heat index ≥ 27 °C terjadi pada {100 * (hist.heat_index >= 27).mean():.1f}% jam dan ≥ 32 °C pada {100 * (hist.heat_index >= 32).mean():.1f}% jam"
    + (" → di Bandung heat index jarang jadi masalah dibanding UV." if (hist.heat_index >= 32).mean() < 0.02 else " → heat index perlu diperhatikan, terutama di segmen siang."),
    f"- Saat awan 75–100%, UV masih ±{efek.rasio_UV_persen.iloc[-1]:.0f}% dari kondisi langit cerah"
    + (" → mendung bukan jaminan aman." if efek.rasio_UV_persen.iloc[-1] >= 30 else " → awan tebal meredam UV cukup besar."),
    f"- **Ketidakpastian statistik (95%)**: UV maks rata-rata segmen Siang {ci_tab.loc['Siang', 'UV maks rata-rata']}; %hari UV≥8 {ci_tab.loc['Siang', '%hari UV≥8']}.",
]
if spread_tab is not None:
    lines.append(f"- **Ketidakpastian antar-model (30 hari terakhir)**: spread UV rata-rata Siang {spread_tab.loc['Siang'].iloc[0]:.1f} UVI; "
                 f"model berbeda kategori pada {spread_tab.loc['Siang'].iloc[2]:.0f}% hari (Pagi {spread_tab.loc['Pagi'].iloc[2]:.0f}%, Sore {spread_tab.loc['Sore'].iloc[2]:.0f}%).")
display(Markdown("\\n".join(lines)))

display(Markdown("**Matriks tindakan (aturan yang dipakai)**"))
for nama, kunci in (("UV < 0,5", 0), ("UV 0,5–2,9", 1), ("UV 3–5,9", 2), ("UV 6–7,9", 3), ("UV ≥ 8", 4)):
    print(f"{nama:12s} → {' '.join(UV_TINDAKAN[kunci])}")
""")

md("""
## 13. Sumber data, asumsi, dan batasan

**Sumber**
1. Open-Meteo — Forecast API (`api.open-meteo.com/v1/forecast`) & Historical Forecast API (`historical-forecast-api.open-meteo.com`). Lisensi data CC BY 4.0, gratis untuk non-komersial. Sitasi: Zippenfenig, P. (2023). *Open-Meteo.com Weather API*. Zenodo. https://doi.org/10.5281/zenodo.7970649 · dokumentasi: https://open-meteo.com/en/docs
2. Skala indeks UV & kategori: WHO/WMO/UNEP/ICNIRP (2002), *Global Solar UV Index: A Practical Guide*.
3. Heat index: US National Weather Service, https://www.weather.gov/ama/heatindex ; regresi Rothfusz (1990), NWS Technical Attachment SR 90-23; dasar: Steadman (1979), *J. Applied Meteorology* 18.
4. Ambang kategori heat index (°C): tabel NWS/NOAA yang dikonversi ke Celsius.

**Asumsi**
- **A1 Lokasi:** satu titik (−6,8915; 107,6107) = ITB Ganesha; resolusi model ≫ kampus, jadi iklim mikro (bayangan gedung, aspal, pepohonan) tidak tertangkap.
- **A2 Data = model:** nilai UV, suhu, RH, awan adalah keluaran model/analisis, bukan sensor di kampus. Model dasar pada "best match" Open-Meteo dapat berubah seiring waktu.
- **A3 Riwayat:** Historical Forecast API merekam prakiraan model terbaik per waktu, bukan reanalisis homogen; tidak ada jaminan kontinuitas antar-versi model.
- **A4 UV:** nilai UV Open-Meteo diperlakukan sebagai indeks UV permukaan langit-ada-awan; tidak ada koreksi lokal terhadap albedo/halangan.
- **A5 Heat index:** rumus NWS (kondisi teduh, angin ringan). Di bawah ±27 °C ≈ suhu udara. Tidak memasukkan radiasi matahari langsung, sehingga di bawah terik terasa lebih panas dari nilainya (lihat `apparent_temperature`).
- **A6 Segmen:** batas jam adalah pilihan analis (WIB). Hasil per segmen memakai nilai **maksimum** dalam segmen (kondisi terburuk).
- **A7 Kategori & tindakan:** mengikuti WHO untuk UV dan NWS untuk HI; teks tindakan adalah pedoman umum, bukan nasihat medis. Estimasi waktu memerah (≈ 200/UVI menit) sangat kasar dan bergantung tipe kulit.
- **A8 Galat input HI:** suhu ±1 °C dan RH ±8–10% (asumsi, belum divalidasi dengan sensor lokal).
- **A9 Statistik:** hari dianggap independen pada bootstrap; periode data beberapa tahun sehingga variasi antartahun (mis. El Niño/La Niña) hanya sebagian tertangkap.

**Batasan utama:** tanpa validasi terhadap alat ukur UV/AWS di ITB (mis. stasiun BMKG/kampus) hasil ini bersifat indikatif. Langkah berikutnya yang paling berharga adalah membandingkan keluaran model dengan pengukuran lokal.
""")

md("## 14. Ekspor data")
code("""
hist.drop(columns=["tanggal"]).to_csv("bandung_uv_hi_per_jam.csv", index=False)
ringkas.to_csv("ringkasan_per_segmen.csv")
seg.to_csv("tindakan_hari_ini.csv", index=False)
try:
    from google.colab import files
    for f in ("bandung_uv_hi_per_jam.csv", "ringkasan_per_segmen.csv", "tindakan_hari_ini.csv"): files.download(f)
except ImportError:
    print("Berkas tersimpan di folder kerja.")
""")

md("""
---
**Batasan:** data Open-Meteo adalah keluaran model (analisis/prakiraan), bukan pengukuran sensor di ITB; UV model dapat berbeda dari alat ukur lokal. Heat index berlaku untuk kondisi teduh & angin ringan. Estimasi waktu memerah hanyalah patokan kasar, bukan saran medis.
**Data:** Open-Meteo.com (CC BY 4.0, non-komersial).
""")

nb = {
    "cells": [
        {"cell_type": t, "id": f"c{i:02d}", "metadata": {}, "source": src.splitlines(True),
         **({"outputs": [], "execution_count": None} if t == "code" else {})}
        for i, (t, src) in enumerate(cells)
    ],
    "metadata": {"colab": {"provenance": []}, "kernelspec": {"display_name": "Python 3", "name": "python3"},
                 "language_info": {"name": "python"}},
    "nbformat": 4, "nbformat_minor": 5,
}
out = ROOT / "notebook" / "Bandung_UV_HeatIndex.ipynb"
out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("ditulis:", out, len(cells), "sel")
