import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import numpy as np
from uvheat import core

def test_heat_index_reference_values():
    # Tabel NWS: 90 °F (32.2 °C) & 70% RH -> ~106 °F (41 °C)
    hi = float(core.heat_index_c((90 - 32) * 5 / 9, 70))
    assert abs(hi * 9 / 5 + 32 - 105.9) < 1.0
    # Suhu rendah: HI ≈ suhu udara
    assert abs(float(core.heat_index_c(24, 70)) - 24) < 1.5

def test_levels():
    assert core.uv_level(2.9)[2] == "Rendah"
    assert core.uv_level(3.0)[2] == "Sedang"
    assert core.uv_level(8.0)[2] == "Sangat tinggi"
    assert core.uv_level(11.0)[2] == "Ekstrem"
    assert core.hi_level(26.9)[1] == 0 and core.hi_level(27)[1] == 1 and core.hi_level(41)[1] == 3

def test_segmen_covers_24h():
    assert sorted(core.segmen_of_hour(h) for h in range(24)) == sorted(
        n for n, (a, b) in core.SEGMEN.items() for _ in range(b - a))

def test_jendela():
    import pandas as pd
    d = pd.DataFrame({"jam": range(24), "uv_index": [0]*6 + [1, 2, 4, 7, 9, 10, 9, 7, 4, 2, 1, 0] + [0]*6})
    assert core.jendela_aman_uv(d) == [(6, 8), (15, 18)]

def test_ketidakpastian():
    import pandas as pd
    t = pd.date_range("2026-01-01", periods=24, freq="h")
    base = core.add_indices(pd.DataFrame({
        "time": t, "temperature_2m": 25.0, "relative_humidity_2m": 70.0, "apparent_temperature": 26.0,
        "uv_index": [0]*6 + [2, 4, 6, 7, 8, 8, 7, 6, 4, 2, 1, 0] + [0]*6, "uv_index_clear_sky": 9.0,
        "cloud_cover": 20.0, "precipitation": 0.0}))
    seg = core.ringkas_segmen(base[base.tanggal == "2026-01-01"])
    hi = base.copy(); hi["uv_index"] = hi["uv_index"] * 1.4
    out = core.tambah_ketidakpastian(seg, {"a": base, "b": hi}, "2026-01-01")
    s = out[out.segmen == "Pagi"].iloc[0]   # UV maks 7 (Tinggi) -> model tinggi 9.8 (Sangat tinggi)
    assert s.uv_hi > s.uv_max and s.n_model == 3
    assert s.keyakinan in ("Sedang", "Rendah")
    assert bool(s.skenario_terburuk)
    solo = core.tambah_ketidakpastian(seg, {}, "2026-01-01")
    assert (solo.keyakinan == "Tidak diketahui").all()


def test_model_identik_tidak_dianggap_sepakat():
    import pandas as pd
    t = pd.date_range("2026-01-01", periods=24, freq="h")
    base = core.add_indices(pd.DataFrame({
        "time": t, "temperature_2m": 22.0, "relative_humidity_2m": 80.0, "apparent_temperature": 22.0,
        "uv_index": [0]*6 + [2, 4, 6, 7, 8, 8, 7, 6, 4, 2, 1, 0] + [0]*6, "uv_index_clear_sky": 9.0,
        "cloud_cover": 20.0, "precipitation": 0.0}))
    seg = core.ringkas_segmen(base[base.tanggal == "2026-01-01"])
    out = core.tambah_ketidakpastian(seg, {"kembar": base.copy()}, "2026-01-01")
    assert (out[out.segmen == "Siang"].keyakinan == "Tidak dapat dinilai").all()
    # HI 22 °C tidak boleh memicu peringatan skenario terburuk hanya karena galat input
    assert not out.skenario_terburuk.any()
