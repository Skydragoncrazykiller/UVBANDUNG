"""Render hasil ke Markdown (README), HTML (GitHub Pages) dan grafik PNG."""
from __future__ import annotations

import html
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .core import (LOKASI, SEGMEN, SEGMEN_ORDER, estimasi_menit_aman, fmt_jendela,
                   jendela_aman_uv, teks_kepastian, uv_level)

BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus",
         "September", "Oktober", "November", "Desember"]
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


def tanggal_id(ts: pd.Timestamp) -> str:
    return f"{HARI[ts.weekday()]}, {ts.day} {BULAN[ts.month - 1]} {ts.year}"


def headline(seg_df: pd.DataFrame, df_hari: pd.DataFrame) -> list[str]:
    i = df_hari["uv_index"].idxmax()
    uv_max, jam = float(df_hari.loc[i, "uv_index"]), int(df_hari.loc[i, "jam"])
    lvl = uv_level(uv_max)
    menit = estimasi_menit_aman(uv_max)
    lines = [f"{lvl[3]} **UV puncak hari ini {uv_max:.1f} ({lvl[2]}) pukul {jam:02d}:00 WIB.**"]
    if menit:
        lines.append(f"Pada puncak itu, kulit sensitif bisa mulai memerah dalam ± {menit} menit tanpa perlindungan (perkiraan kasar).")
    lines.append(f"Jendela aman UV (< 3) di siang hari: **{fmt_jendela(jendela_aman_uv(df_hari))}**.")
    hi = float(df_hari["heat_index"].max())
    lines.append(f"Heat index tertinggi hari ini {hi:.1f} °C.")
    return lines


def markdown_today(seg_df: pd.DataFrame, df_hari: pd.DataFrame, updated: pd.Timestamp) -> str:
    tgl = tanggal_id(df_hari["time"].iloc[0])
    out = [f"### {tgl} — {LOKASI}", ""]
    out += [f"- {l}" for l in headline(seg_df, df_hari)]
    out += ["", "| Segmen (WIB) | Status | UV maks | Heat index maks | Suhu / RH | Kepastian (kisaran) | Yang sebaiknya dilakukan |",
            "|---|---|---|---|---|---|---|"]
    for r in seg_df.itertuples():
        uv = f"{r.uv_emoji} **{r.uv_max:.1f}** {r.uv_label}" + (f" ({int(r.jam_uv_max):02d}:00)" if pd.notna(r.jam_uv_max) and r.uv_max >= 0.5 else "")
        hi = f"{r.hi_emoji} **{r.hi_max:.1f} °C** {r.hi_label}"
        out.append(f"| **{r.segmen}**<br>{r.jam} | {r.status} | {uv} | {hi} | {r.suhu_mean:.0f} °C / {r.rh_mean}% | {teks_kepastian(r)} | {r.tindakan} |")
    out += ["", f"<sub>Diperbarui otomatis: {updated:%d-%m-%Y %H:%M} WIB · Sumber: Open-Meteo</sub>"]
    return "\n".join(out)


def markdown_hourly(df_hari: pd.DataFrame) -> str:
    d = df_hari[(df_hari["jam"] >= 5) & (df_hari["jam"] <= 18)]
    out = ["| Jam | UV | Heat index | Suhu | RH | Awan |", "|---|---|---|---|---|---|"]
    for r in d.itertuples():
        lv = uv_level(r.uv_index)
        out.append(f"| {r.jam:02d}:00 | {lv[3] if r.uv_index >= .5 else '⚫'} {r.uv_index:.1f} | {r.heat_index:.1f} °C | {r.temperature_2m:.1f} °C | {r.relative_humidity_2m:.0f}% | {r.cloud_cover:.0f}% |")
    return "\n".join(out)


def html_page(seg_df: pd.DataFrame, df_hari: pd.DataFrame, updated: pd.Timestamp) -> str:
    esc = html.escape
    rows = []
    for r in seg_df.itertuples():
        cls = {"▶ Sekarang": "now", "Sudah lewat": "past"}.get(r.status, "")
        uv = f"{r.uv_emoji} <b>{r.uv_max:.1f}</b> {esc(r.uv_label)}"
        hi = f"{r.hi_emoji} <b>{r.hi_max:.1f} °C</b> {esc(r.hi_label)}"
        rows.append(f"<tr class='{cls}'><td><b>{r.segmen}</b><br><small>{r.jam}</small></td><td>{esc(r.status)}</td>"
                    f"<td>{uv}</td><td>{hi}</td><td>{r.suhu_mean:.0f} °C / {r.rh_mean}%</td><td>{esc(teks_kepastian(r))}</td><td>{esc(r.tindakan)}</td></tr>")
    head = "".join(f"<li>{esc(l).replace('**', '')}</li>" for l in headline(seg_df, df_hari))
    return f"""<!doctype html><html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>UV &amp; Heat Index Hari Ini — {esc(LOKASI)}</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:1100px;margin:1.5rem auto;padding:0 1rem;color:#1f2933}}
table{{border-collapse:collapse;width:100%}} th,td{{border:1px solid #d5dbe1;padding:.5rem .6rem;vertical-align:top;text-align:left}}
th{{background:#f1f4f7}} tr.now{{background:#fff8e1}} tr.past{{opacity:.6}} small{{color:#667}}
img{{max-width:100%}} @media(prefers-color-scheme:dark){{body{{background:#121417;color:#e6e9ec}}th{{background:#1e2329}}td,th{{border-color:#333b44}}tr.now{{background:#3a3213}}}}
</style></head><body>
<h1>UV &amp; Heat Index — {esc(LOKASI)}</h1>
<h2>{esc(tanggal_id(df_hari['time'].iloc[0]))}</h2><ul>{head}</ul>
<table><thead><tr><th>Segmen (WIB)</th><th>Status</th><th>UV maks</th><th>Heat index maks</th><th>Suhu / RH</th><th>Kepastian (kisaran)</th><th>Yang sebaiknya dilakukan</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<p><img src="today.png" alt="Grafik hari ini"></p><p><img src="trend.png" alt="Tren 14 hari"></p>
<h3>Cara membaca ketidakpastian</h3>
<p><small>Data adalah keluaran model numerik Open-Meteo, bukan pengukuran sensor di ITB. "Kepastian" membandingkan beberapa model cuaca (kisaran UV) dan galat input heat index (suhu ±1 °C, RH ±10%). Bila model tidak sepakat atau kisaran melintasi kategori, tindakan memakai <b>skenario terburuk</b> (⚠️). Detail: METODOLOGI.md di repo.</small></p>
<p><small>Diperbarui otomatis {updated:%d-%m-%Y %H:%M} WIB · Data: Open-Meteo (CC BY 4.0). Heat index: NWS/NOAA. UV: skala WHO.</small></p>
</body></html>"""


# ---------------------------------------------------------------- grafik
UV_BANDS = [(0, 3, "#9be29b"), (3, 6, "#ffe680"), (6, 8, "#ffb366"), (8, 11, "#ff7f7f"), (11, 16, "#c9a0ff")]


def plot_today(df_hari: pd.DataFrame, path: str, now: pd.Timestamp | None = None) -> None:
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.2), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
    x = df_hari["jam"] + 0.5
    for lo, hi, c in UV_BANDS:
        a1.axhspan(lo, hi, color=c, alpha=.35, lw=0)
    a1.plot(x, df_hari["uv_index"], color="#1f2933", lw=2.2, label="UV (aktual/prakiraan)")
    a1.plot(x, df_hari["uv_index_clear_sky"], color="#1f2933", lw=1, ls="--", alpha=.6, label="UV langit cerah")
    a1.set_ylim(0, max(12, df_hari["uv_index"].max() + 1)); a1.set_ylabel("Indeks UV"); a1.legend(loc="center right", fontsize=8)
    a2.plot(x, df_hari["heat_index"], color="#d9480f", lw=2, label="Heat index")
    a2.plot(x, df_hari["temperature_2m"], color="#1c7ed6", lw=1.5, label="Suhu udara")
    a2.plot(x, df_hari["apparent_temperature"], color="#2f9e44", lw=1.2, ls=":", label="Suhu terasa (Open-Meteo)")
    a2.set_ylabel("°C"); a2.legend(loc="upper left", fontsize=8, ncol=3)
    for ax in (a1, a2):
        for seg, (a, b) in SEGMEN.items():
            ax.axvline(a, color="gray", lw=.6, ls="--")
        ax.grid(alpha=.2)
        if now is not None and df_hari["time"].iloc[0].normalize() == now.normalize():
            ax.axvline(now.hour + now.minute / 60, color="crimson", lw=1.5)
    ymax = a1.get_ylim()[1]
    for seg, (a, b) in SEGMEN.items():
        a1.text((a + b) / 2, ymax * .93, seg, ha="center", fontsize=9, weight="bold")
    a2.set_xticks(range(0, 25, 3)); a2.set_xlim(0, 24); a2.set_xlabel("Jam (WIB)")
    a1.set_title(f"UV & heat index — {LOKASI} — {tanggal_id(df_hari['time'].iloc[0])}")
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def plot_trend(hourly: pd.DataFrame, path: str, days: int = 14) -> None:
    d = hourly[hourly["tanggal"] >= hourly["tanggal"].max() - pd.Timedelta(days=days - 1)]
    piv_uv = d.pivot_table(index="segmen", columns="tanggal", values="uv_index", aggfunc="max").reindex(SEGMEN_ORDER)
    piv_hi = d.pivot_table(index="segmen", columns="tanggal", values="heat_index", aggfunc="max").reindex(SEGMEN_ORDER)
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.6))
    for ax, piv, cmap, title, vmax in ((axs[0], piv_uv, "YlOrRd", "UV maksimum per segmen", 12),
                                       (axs[1], piv_hi, "YlOrBr", "Heat index maksimum per segmen (°C)", None)):
        im = ax.imshow(piv.values.astype(float), aspect="auto", cmap=cmap, vmin=0 if vmax else None, vmax=vmax)
        ax.set_yticks(range(len(piv.index)), piv.index)
        ax.set_xticks(range(len(piv.columns)), [c.strftime("%d/%m") for c in piv.columns], rotation=60, fontsize=8)
        for (i, j), v in np.ndenumerate(piv.values.astype(float)):
            if not np.isnan(v):
                lo, hi = np.nanmin(piv.values.astype(float)), np.nanmax(piv.values.astype(float))
                top = (v - (0 if vmax else lo)) / ((vmax or hi) - (0 if vmax else lo) or 1)
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7, color="white" if top > .6 else "black")
        ax.set_title(title, fontsize=10); fig.colorbar(im, ax=ax, fraction=.04)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)
