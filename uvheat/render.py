"""Render hasil ke Markdown (README), HTML (GitHub Pages) dan grafik PNG."""
from __future__ import annotations

import html

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .core import (LOKASI, SEGMEN, SEGMEN_ORDER, estimasi_menit_aman, fmt_id,
                   fmt_jendela, hi_level, jendela_aman_uv, jendela_proteksi_uv, pesan_mahasiswa,
                   teks_kepastian, uv_level)

BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus",
         "September", "Oktober", "November", "Desember"]
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
REPO_URL = "https://github.com/Skydragoncrazykiller/UVBANDUNG"


def tanggal_id(ts: pd.Timestamp) -> str:
    return f"{HARI[ts.weekday()]}, {ts.day} {BULAN[ts.month - 1]} {ts.year}"


def ringkasan(df_hari: pd.DataFrame) -> dict:
    i = df_hari["uv_index"].idxmax()
    uv, jam = float(df_hari.loc[i, "uv_index"]), int(df_hari.loc[i, "jam"])
    hi = float(df_hari["heat_index"].max())
    lv = uv_level(uv)
    k = {
        "uv": uv, "uv_jam": jam, "uv_label": lv[2], "uv_bg": lv[3], "uv_fg": lv[4],
        "menit": estimasi_menit_aman(uv),
        "aman": fmt_jendela(jendela_aman_uv(df_hari)),
        "proteksi": fmt_jendela(jendela_proteksi_uv(df_hari)),
        "hi": hi, "hi_label": hi_level(hi)[2], "hi_bg": hi_level(hi)[3], "hi_fg": hi_level(hi)[4],
    }
    k["pesan"] = pesan_mahasiswa(uv, jam, k["proteksi"], hi)
    return k


def _uv_cell(r) -> str:
    jam = f" ({int(r.jam_uv_max):02d}:00)" if pd.notna(r.jam_uv_max) and r.uv_max >= 0.5 else ""
    return f"**{fmt_id(r.uv_max)}** {r.uv_label}{jam}" if r.uv_max >= 0.5 else r.uv_label


# --------------------------------------------------------------------- Markdown
def markdown_today(seg_df: pd.DataFrame, df_hari: pd.DataFrame, updated: pd.Timestamp) -> str:
    k = ringkasan(df_hari)
    out = [f"**{tanggal_id(df_hari['time'].iloc[0])}** · {LOKASI} · diperbarui {updated:%H:%M} WIB", "",
           "| Ringkasan hari ini | |", "|---|---|",
           f"| Puncak UV | **{fmt_id(k['uv'])}** ({k['uv_label']}) pukul {k['uv_jam']:02d}:00 WIB |",
           f"| Jam perlu proteksi (UV ≥ 3) | {k['proteksi']} |",
           f"| Jendela UV aman (< 3) | {k['aman']} |",
           f"| Heat index tertinggi | **{fmt_id(k['hi'])} °C** ({k['hi_label']}) |", "",
           "| Segmen | Jam (WIB) | UV maks | Heat index maks | Kepastian | Tindakan |",
           "|---|---|---|---|---|---|"]
    for r in seg_df.itertuples():
        nama = f"**{r.segmen}**" + (" (berlangsung)" if r.status == "Berlangsung" else "")
        out.append(f"| {nama} | {r.jam} | {_uv_cell(r)} | **{fmt_id(r.hi_max)} °C** {r.hi_label} | {teks_kepastian(r)} | {r.tindakan} |")
    out += ["", "**Pesan hari ini untuk mahasiswa**", ""] + [f"- {m}" for m in k["pesan"]]
    out += ["", "<sub>Sumber: Open-Meteo. Angka adalah keluaran model, bukan pengukuran sensor di ITB; "
                "lihat [METODOLOGI.md](METODOLOGI.md) untuk asumsi dan ketidakpastian.</sub>"]
    return "\n".join(out)


def markdown_hourly(df_hari: pd.DataFrame) -> str:
    d = df_hari[(df_hari["jam"] >= 5) & (df_hari["jam"] <= 18)]
    out = ["| Jam | UV | Heat index (°C) | Suhu (°C) | RH (%) | Awan (%) |", "|---:|---:|---:|---:|---:|---:|"]
    for r in d.itertuples():
        out.append(f"| {r.jam:02d}:00 | {fmt_id(r.uv_index)} | {fmt_id(r.heat_index)} | {fmt_id(r.temperature_2m)} | {r.relative_humidity_2m:.0f} | {r.cloud_cover:.0f} |")
    return "\n".join(out)


# --------------------------------------------------------------------- HTML
_CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#17212b;--mut:#5b6773;--line:#dfe3e8;--accent:#0b5cad}
@media(prefers-color-scheme:dark){:root{--bg:#0f1318;--card:#171d24;--ink:#e8ecf0;--mut:#9aa6b2;--line:#2a323b;--accent:#6fb1f0}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1120px;margin:0 auto;padding:32px 20px 48px}
header h1{font-size:1.55rem;margin:0 0 4px;font-weight:650;letter-spacing:-.01em}
header p{margin:0;color:var(--mut)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin:24px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px}
.kpi .l{font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;color:var(--mut)}
.kpi .v{font-size:1.9rem;font-weight:650;line-height:1.2;margin:4px 0;font-variant-numeric:tabular-nums}
.kpi .s{color:var(--mut);font-size:.86rem}
.pill{display:inline-block;white-space:nowrap;padding:1px 9px;border-radius:999px;font-size:.78rem;font-weight:600;vertical-align:middle}
h2{font-size:1.05rem;margin:32px 0 10px;font-weight:650}
.tablewrap{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:860px}
th,td{padding:11px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}
th{font-size:.76rem;text-transform:uppercase;letter-spacing:.05em;color:var(--mut);font-weight:600}
tr:last-child td{border-bottom:0}
tr.now td:first-child{box-shadow:inset 3px 0 0 var(--accent)}
tr.past td{opacity:.62}
td .n{font-variant-numeric:tabular-nums;font-weight:650}
td small{color:var(--mut);font-size:.82rem}
.charts{display:grid;gap:14px}
.charts img{width:100%;border:1px solid var(--line);border-radius:10px;background:#fff}
details{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 18px;margin-top:14px}
summary{cursor:pointer;font-weight:600}
details ul{margin:10px 0 2px;padding-left:20px}
footer{margin-top:32px;color:var(--mut);font-size:.82rem}
footer a,details a{color:var(--accent)}
"""


def _pill(text: str, bg: str, fg: str) -> str:
    return f'<span class="pill" style="background:{bg};color:{fg}">{html.escape(text)}</span>'


def html_page(seg_df: pd.DataFrame, df_hari: pd.DataFrame, updated: pd.Timestamp) -> str:
    esc, k = html.escape, ringkasan(df_hari)
    rows = []
    for r in seg_df.itertuples():
        cls = {"Berlangsung": "now", "Selesai": "past"}.get(r.status, "")
        if r.uv_max >= 0.5:
            uv = f'<span class="n">{fmt_id(r.uv_max)}</span> {_pill(r.uv_label, r.uv_bg, r.uv_fg)}'
            if pd.notna(r.jam_uv_max):
                uv += f"<br><small>puncak {int(r.jam_uv_max):02d}:00</small>"
        else:
            uv = _pill(r.uv_label, r.uv_bg, r.uv_fg)
        hi = (f'<span class="n">{fmt_id(r.hi_max)} °C</span> {_pill(r.hi_label, r.hi_bg, r.hi_fg)}'
              f"<br><small>suhu rata-rata {fmt_id(r.suhu_mean, 0)} °C, RH {r.rh_mean}%</small>")
        stat = f"<br><small>{esc(r.status)}</small>" if r.status else ""
        rows.append(f"<tr class='{cls}'><td><b>{esc(r.segmen)}</b><br><small>{r.jam}</small>{stat}</td>"
                    f"<td>{uv}</td><td>{hi}</td><td><small>{esc(teks_kepastian(r))}</small></td><td>{esc(r.tindakan)}</td></tr>")
    menit = f"Perkiraan kasar: kulit sensitif mulai memerah dalam ±{k['menit']} menit tanpa perlindungan" if k["menit"] else ""
    return f"""<!doctype html><html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>UV dan Heat Index {esc(LOKASI)}</title><style>{_CSS}</style></head><body><div class="wrap">
<header><h1>UV dan Heat Index — {esc(LOKASI)}</h1>
<p>{esc(tanggal_id(df_hari['time'].iloc[0]))} · diperbarui {updated:%H:%M} WIB · data Open-Meteo</p></header>
<section class="kpis">
<div class="kpi"><div class="l">Puncak UV</div><div class="v">{fmt_id(k['uv'])}</div>
<div class="s">{_pill(k['uv_label'], k['uv_bg'], k['uv_fg'])} pukul {k['uv_jam']:02d}:00 WIB</div><div class="s">{esc(menit)}</div></div>
<div class="kpi"><div class="l">Jam perlu proteksi (UV ≥ 3)</div><div class="v" style="font-size:1.35rem">{esc(k['proteksi'])}</div><div class="s">Jendela aman (UV &lt; 3): {esc(k['aman'])}</div></div>
<div class="kpi"><div class="l">Heat index tertinggi</div><div class="v">{fmt_id(k['hi'])} °C</div><div class="s">{_pill(k['hi_label'], k['hi_bg'], k['hi_fg'])}</div></div>
</section>
<h2>Ringkasan dan tindakan per segmen waktu</h2>
<div class="tablewrap"><table><thead><tr><th>Segmen (WIB)</th><th>UV maks</th><th>Heat index maks</th><th>Kepastian</th><th>Tindakan</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<h2>Pesan hari ini untuk mahasiswa</h2>
<div class="tablewrap" style="padding:6px 20px"><ul style="padding-left:18px;margin:10px 0">{''.join(f"<li>{esc(m)}</li>" for m in k["pesan"])}</ul></div>
<h2>Grafik</h2><div class="charts"><img src="today.png" alt="UV, heat index, dan suhu per jam hari ini"><img src="trend.png" alt="UV dan heat index maksimum per segmen, 14 hari"></div>
<details><summary>Cara membaca, asumsi, dan ketidakpastian</summary><ul>
<li>Nilai per segmen adalah <b>maksimum</b> dalam segmen tersebut (kondisi terburuk). Batas segmen: Dini hari 00–06, Pagi 06–10, Siang 10–15, Sore 15–18, Malam 18–24 WIB.</li>
<li>UV mengikuti skala WHO (rendah &lt; 3, sedang 3–5, tinggi 6–7, sangat tinggi 8–10, ekstrem ≥ 11). Heat index mengikuti ambang NWS (waspada ≥ 26,7 °C, sangat waspada ≥ 32,2 °C, bahaya ≥ 39,4 °C, sangat bahaya ≥ 51,7 °C; setara 80/90/103/125 °F).</li>
<li>Data adalah keluaran model numerik Open-Meteo, bukan pengukuran sensor di ITB, dan belum divalidasi dengan alat ukur lokal.</li>
<li>Kolom Kepastian membandingkan beberapa model cuaca dan memperhitungkan galat input heat index (1 simpangan baku: suhu 1 °C, RH 8%). Jika kisarannya melewati kategori yang lebih berat, tindakan mengikuti skenario terburuk.</li>
<li>Tindakan adalah pedoman umum, bukan nasihat medis.</li>
<li>Rincian lengkap: <a href="{REPO_URL}/blob/main/METODOLOGI.md">METODOLOGI.md</a>.</li></ul></details>
<footer>Sumber data: <a href="https://open-meteo.com/">Open-Meteo.com</a> (CC BY 4.0, non-komersial) · Kode dan data: <a href="{REPO_URL}">GitHub</a></footer>
</div></body></html>"""


# --------------------------------------------------------------------- grafik
UV_BANDS = [(0, 3, "#2e8b3d"), (3, 6, "#f2d600"), (6, 8, "#f28a00"), (8, 11, "#d62f2f"), (11, 16, "#6a4bc4")]
_STYLE = {"axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#8a949e",
          "axes.labelcolor": "#33404d", "xtick.color": "#33404d", "ytick.color": "#33404d"}


def plot_today(df_hari: pd.DataFrame, path: str, now: pd.Timestamp | None = None) -> None:
    with plt.rc_context(_STYLE):
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.2), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
        x = df_hari["jam"] + 0.5
        for lo, hi, c in UV_BANDS:
            a1.axhspan(lo, hi, color=c, alpha=.16, lw=0)
        a1.plot(x, df_hari["uv_index"], color="#17212b", lw=2.2, label="Indeks UV")
        a1.plot(x, df_hari["uv_index_clear_sky"], color="#17212b", lw=1, ls="--", alpha=.55, label="UV bila langit cerah")
        a1.set_ylim(0, max(12, df_hari["uv_index"].max() + 1)); a1.set_ylabel("Indeks UV")
        a1.legend(loc="center right", fontsize=8, frameon=False)
        a2.plot(x, df_hari["heat_index"], color="#c2410c", lw=2, label="Heat index")
        a2.plot(x, df_hari["temperature_2m"], color="#1c5fa8", lw=1.5, label="Suhu udara")
        a2.plot(x, df_hari["apparent_temperature"], color="#2f7d4a", lw=1.2, ls=":", label="Suhu terasa (Open-Meteo)")
        a2.axhline(26.7, color="#8a949e", lw=.8, ls="--"); a2.text(23.9, 27.15, "ambang waspada 27 °C", ha="right", fontsize=7.5, color="#5b6773")
        a2.set_ylabel("°C"); a2.legend(loc="upper left", fontsize=8, ncol=3, frameon=False)
        for ax in (a1, a2):
            for a, _ in SEGMEN.values():
                ax.axvline(a, color="#8a949e", lw=.6, ls="--")
            ax.grid(alpha=.18)
            if now is not None and df_hari["time"].iloc[0].normalize() == now.normalize():
                ax.axvline(now.hour + now.minute / 60, color="#d62f2f", lw=1.4)
        ymax = a1.get_ylim()[1]
        for seg, (a, b) in SEGMEN.items():
            a1.text((a + b) / 2, ymax * .93, seg, ha="center", fontsize=9, weight="bold", color="#33404d")
        a2.set_xticks(range(0, 25, 3)); a2.set_xlim(0, 24); a2.set_xlabel("Jam (WIB)")
        a1.set_title(f"UV dan heat index per jam · {LOKASI} · {tanggal_id(df_hari['time'].iloc[0])}", fontsize=11, loc="left")
        fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def plot_trend(hourly: pd.DataFrame, path: str, days: int = 14) -> None:
    d = hourly[hourly["tanggal"] >= hourly["tanggal"].max() - pd.Timedelta(days=days - 1)]
    piv_uv = d.pivot_table(index="segmen", columns="tanggal", values="uv_index", aggfunc="max").reindex(SEGMEN_ORDER)
    piv_hi = d.pivot_table(index="segmen", columns="tanggal", values="heat_index", aggfunc="max").reindex(SEGMEN_ORDER)
    with plt.rc_context(_STYLE):
        fig, axs = plt.subplots(1, 2, figsize=(12, 3.7))
        for ax, piv, cmap, title, vmax in ((axs[0], piv_uv, "YlOrRd", "UV maksimum per segmen", 12),
                                           (axs[1], piv_hi, "YlOrBr", "Heat index maksimum per segmen (°C)", None)):
            vals = piv.values.astype(float)
            im = ax.imshow(vals, aspect="auto", cmap=cmap, vmin=0 if vmax else None, vmax=vmax)
            ax.set_yticks(range(len(piv.index)), piv.index)
            ax.set_xticks(range(len(piv.columns)), [c.strftime("%d/%m") for c in piv.columns], rotation=60, fontsize=8)
            lo, hi = np.nanmin(vals), np.nanmax(vals)
            for (i, j), v in np.ndenumerate(vals):
                if not np.isnan(v):
                    top = (v - (0 if vmax else lo)) / ((vmax or hi) - (0 if vmax else lo) or 1)
                    ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7, color="white" if top > .6 else "black")
            ax.set_title(title, fontsize=10, loc="left"); fig.colorbar(im, ax=ax, fraction=.04)
        fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)
