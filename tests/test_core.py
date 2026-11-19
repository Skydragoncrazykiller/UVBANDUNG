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
    assert core.hi_level(26.6)[1] == 0 and core.hi_level(26.7)[1] == 1 and core.hi_level(32.3)[1] == 2
    assert core.hi_level(39.4)[1] == 3 and core.hi_level(51.7)[1] == 4
    # contoh di draf materi: 30 °C, RH 49% -> sekitar 31 °C (Waspada)
    h = float(core.heat_index_c(30, 49)); assert abs(h - 31) < 0.5 and core.hi_level(h)[2] == "Waspada"

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


def test_jendela_proteksi_dan_pesan():
    import pandas as pd
    d = pd.DataFrame({"jam": range(24), "uv_index": [0]*6 + [1, 2, 4, 7, 9, 10, 9, 7, 4, 2, 1, 0] + [0]*6})
    assert core.jendela_proteksi_uv(d) == [(8, 15)]
    m = core.pesan_mahasiswa(10, 11, "08:00–15:00", 28)
    assert len(m) == 3 and "sunscreen" in m[0] and "8 gelas" in m[1]


def _base_hari():
    import pandas as pd
    t = pd.date_range("2026-01-01", periods=24, freq="h")
    return core.add_indices(pd.DataFrame({
        "time": t, "temperature_2m": 28.0, "relative_humidity_2m": 60.0, "apparent_temperature": 29.0,
        "uv_index": [0]*6 + [2, 4, 6, 7, 8, 8, 7, 6, 4, 2, 1, 0] + [0]*6, "uv_index_clear_sky": 9.0,
        "cloud_cover": 20.0, "precipitation": 0.0}))


def test_cams_dan_ensemble_memberi_pembanding_independen():
    import pandas as pd
    base = _base_hari()
    seg = core.ringkas_segmen(base[base.tanggal == "2026-01-01"])
    ens = base[["time", "temperature_2m", "relative_humidity_2m", "uv_index"]].copy()
    ens["temperature_2m_spread"] = 0.6
    ens["relative_humidity_2m_spread"] = 4.0
    ens["uv_index_spread"] = 0.5
    cams = base[["time"]].copy(); cams["uv_cams"] = base["uv_index"] * 1.5
    out = core.tambah_ketidakpastian(seg, {"kembar": base.copy()}, "2026-01-01", ens={"e": ens}, cams=cams)
    s = out[out.segmen == "Pagi"].iloc[0]           # UV maks 7 (Tinggi), CAMS 10,5 (Sangat tinggi)
    assert s.keyakinan != "Tidak dapat dinilai"
    assert s.uv_cams == 10.5 and abs(s.uv_sd - 0.5) < 1e-9 and s.sd_sumber == "ensemble"
    assert s.uv_hi >= 10.5 and bool(s.skenario_terburuk)
    assert "CAMS" in core.teks_kepastian(s)


def test_tanpa_sumber_tambahan_jatuh_ke_asumsi():
    base = _base_hari()
    seg = core.ringkas_segmen(base[base.tanggal == "2026-01-01"])
    out = core.tambah_ketidakpastian(seg, {"kembar": base.copy()}, "2026-01-01", ens={}, cams=None)
    assert (out.sd_sumber == "asumsi").all()
    assert out[out.segmen == "Siang"].iloc[0].keyakinan == "Tidak dapat dinilai"
