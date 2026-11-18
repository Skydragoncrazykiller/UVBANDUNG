"""Ambil data terbaru, perbarui riwayat, dan hasilkan README/HTML/grafik.

Pakai:  python scripts/update.py
Tes offline:  python scripts/update.py --fixture
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from uvheat import core, render  # noqa: E402

DATA, DOCS = ROOT / "data", ROOT / "docs"
HOURLY_CSV, LOG_CSV = DATA / "hourly.csv", DATA / "forecast_log.csv"
START, END = "<!-- TODAY:START -->", "<!-- TODAY:END -->"
HSTART, HEND = "<!-- HOURLY:START -->", "<!-- HOURLY:END -->"


def fixture_df(now: pd.Timestamp) -> pd.DataFrame:
    """Data sintetis untuk uji offline (BUKAN data nyata)."""
    import numpy as np
    t = pd.date_range(now.normalize() - pd.Timedelta(days=2), periods=24 * 5, freq="h")
    h = t.hour.values + t.minute.values / 60
    sun = np.clip(np.sin((h - 6) / 12 * np.pi), 0, None)
    rng = np.random.default_rng(1)
    cloud = np.clip(40 + 30 * np.sin(h / 24 * 2 * np.pi * 2) + rng.normal(0, 10, len(t)), 0, 100)
    return core.add_indices(pd.DataFrame({
        "time": t, "temperature_2m": 20 + 8 * sun, "relative_humidity_2m": 90 - 35 * sun,
        "apparent_temperature": 21 + 8 * sun, "uv_index": 11 * sun * (1 - cloud / 220),
        "uv_index_clear_sky": 11 * sun, "cloud_cover": cloud,
        "precipitation": np.where((h > 14) & (h < 16), 1.2, 0.0),
    }))


def upsert_hourly(new: pd.DataFrame, updated: pd.Timestamp) -> pd.DataFrame:
    cols = ["time"] + core.HOURLY_VARS + ["heat_index"]
    new = new[cols].copy()
    if HOURLY_CSV.exists():
        old = pd.read_csv(HOURLY_CSV, parse_dates=["time"])
        new = pd.concat([old[cols], new]).drop_duplicates("time", keep="last")
    new = new.sort_values("time")
    new.to_csv(HOURLY_CSV, index=False, float_format="%.2f")
    return core.add_indices(new)


def append_log(seg: pd.DataFrame, date: pd.Timestamp, updated: pd.Timestamp) -> None:
    """Catat perubahan prakiraan hari ini; hanya baris yang nilainya berubah dari catatan terakhir."""
    cur = seg[["segmen", "uv_max", "hi_max"]].copy()
    cur.insert(0, "tanggal", date.date().isoformat())
    cur.insert(0, "dicatat_wib", updated.strftime("%Y-%m-%d %H:%M"))
    if LOG_CSV.exists():
        log = pd.read_csv(LOG_CSV)
        last = log[log["tanggal"] == date.date().isoformat()].drop_duplicates("segmen", keep="last")
        merged = cur.merge(last[["segmen", "uv_max", "hi_max"]], on="segmen", how="left", suffixes=("", "_prev"))
        changed = merged[(merged["uv_max"] != merged["uv_max_prev"]) | (merged["hi_max"] != merged["hi_max_prev"])]
        cur = cur[cur["segmen"].isin(changed["segmen"])]
        if cur.empty:
            return
        cur.to_csv(LOG_CSV, mode="a", header=False, index=False)
    else:
        cur.to_csv(LOG_CSV, index=False)


def replace_block(text: str, start: str, end: str, body: str) -> str:
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    return pat.sub(lambda _m: f"{start}\n{body}\n{end}", text)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", action="store_true", help="pakai data sintetis (uji offline)")
    args = ap.parse_args()

    now = pd.Timestamp.now(tz=core.TZ).tz_localize(None)
    df = fixture_df(now) if args.fixture else core.fetch_forecast(past_days=2, forecast_days=3)

    DATA.mkdir(exist_ok=True); DOCS.mkdir(exist_ok=True)
    hist = upsert_hourly(df, now)

    hari = df[df["tanggal"] == now.normalize()]
    if hari.empty:
        raise SystemExit("Data hari ini tidak ditemukan di respons API")
    seg = core.ringkas_segmen(hari, now)
    if args.fixture:
        per_model = {}
        for k, f in (("fixture_a", 0.85), ("fixture_b", 1.1)):
            m = df.copy(); m["uv_index"] = m["uv_index"] * f
            per_model[k] = m
    else:
        per_model = core.fetch_models(past_days=0, forecast_days=1)
    seg = core.tambah_ketidakpastian(seg, per_model, now.normalize())
    append_log(seg, now.normalize(), now)

    (DATA / "today.json").write_text(json.dumps({
        "updated_wib": now.strftime("%Y-%m-%d %H:%M"), "lokasi": core.LOKASI,
        "tanggal": now.date().isoformat(), "segmen": seg.to_dict("records"),
    }, ensure_ascii=False, indent=2))

    render.plot_today(hari, str(DOCS / "today.png"), now)
    render.plot_trend(hist, str(DOCS / "trend.png"))
    (DOCS / "index.html").write_text(render.html_page(seg, hari, now), encoding="utf-8")

    readme = ROOT / "README.md"
    txt = readme.read_text(encoding="utf-8")
    txt = replace_block(txt, START, END, render.markdown_today(seg, hari, now))
    txt = replace_block(txt, HSTART, HEND, render.markdown_hourly(hari))
    readme.write_text(txt, encoding="utf-8")
    print("OK", now)


if __name__ == "__main__":
    main()
