# Metodologi, sumber, asumsi, dan ketidakpastian

## 1. Sumber
| No | Sumber | Dipakai untuk |
|---|---|---|
| 1 | [Open-Meteo Forecast API](https://open-meteo.com/en/docs) | UV, suhu 2 m, RH, awan, hujan per jam (hari ini & prakiraan) |
| 2 | [Open-Meteo Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api) | Riwayat per jam untuk notebook |
| 3 | WHO/WMO/UNEP/ICNIRP (2002), *Global Solar UV Index: A Practical Guide* | Kategori UV |
| 4 | [US NWS Heat Index](https://www.weather.gov/ama/heatindex); Rothfusz (1990), NWS TA SR 90-23; Steadman (1979), *J. Appl. Meteor.* 18 | Rumus & ambang heat index: 80/90/103/125 °F = 26,7/32,2/39,4/51,7 °C |
| 5 | [Open-Meteo Ensemble Mean API](https://open-meteo.com/en/docs/ensemble-mean-api) | Spread (simpangan baku antar-anggota ensemble) suhu, RH, awan, UV |
| 6 | [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) (CAMS global, ~40 km) | UV prakiraan independen dari UV berbasis GFS |
| 7 | Kemenkes RI, Permenkes No. 28 Tahun 2019 (AKG); imbauan BMKG tentang cuaca panas (rujukan dari draf materi kelompok, URL belum diverifikasi ulang) | Pesan hidrasi: target minimal 8 gelas/hari, ±250 ml tiap jam saat aktivitas panas di luar ruang |

Sitasi Open-Meteo: Zippenfenig, P. (2023). *Open-Meteo.com Weather API*. Zenodo. <https://doi.org/10.5281/zenodo.7970649>. Lisensi data CC BY 4.0 (non-komersial).

## 2. Pengolahan
1. Data per jam diambil dalam zona `Asia/Jakarta` (WIB, UTC+7) untuk titik ITB Ganesha (−6,8915; 107,6107).
2. Heat index dihitung dari suhu 2 m & RH (NWS Rothfusz + koreksi; di bawah ±27 °C hasilnya ≈ suhu udara).
3. Hari dibagi ke segmen: Dini hari 00–06, Pagi 06–10, Siang 10–15, Sore 15–18, Malam 18–24 (`SEGMEN` di `uvheat/core.py`).
4. Ambang heat index (°C) berasal dari konversi ambang NWS dalam °F: Waspada ≥ 26,7; Sangat waspada ≥ 32,2; Bahaya ≥ 39,4; Sangat bahaya ≥ 51,7.
5. Per segmen diambil **nilai maksimum** UV dan HI (kondisi terburuk dalam segmen), lalu diklasifikasi dan diterjemahkan ke tindakan dengan aturan tetap (`UV_TINDAKAN`, `HI_TINDAKAN`). "Jam perlu proteksi" adalah jam dengan UV ≥ 3 (anjuran WHO); pesan untuk mahasiswa dibangkitkan dari aturan di `pesan_mahasiswa()`.

## 3. Asumsi
- **A1** Satu titik; iklim mikro kampus (bayangan gedung, aspal, pohon) tidak tertangkap model.
- **A2** Data adalah keluaran model, bukan sensor di ITB; model dasar "best match" Open-Meteo dapat berubah.
- **A3** Historical Forecast API merekam prakiraan model per waktu, bukan reanalisis homogen.
- **A4** UV diperlakukan apa adanya (permukaan, langit dengan awan); tanpa koreksi albedo/halangan lokal.
- **A5** Heat index = kondisi teduh & angin ringan; tidak memasukkan radiasi langsung, sehingga di bawah terik terasa lebih panas.
- **A6** Batas segmen adalah pilihan analis; hasil sensitif terhadapnya (lihat notebook 11D).
- **A7** Teks tindakan adalah pedoman umum, bukan nasihat medis. Estimasi "menit sebelum kulit memerah" ≈ 200/UVI — sangat kasar, bergantung tipe kulit.
- **A8** Galat input heat index: bila spread ensemble tersedia, SD suhu dan RH diambil dari spread ensemble pada jam heat index maksimum; bila tidak, dipakai asumsi 1 simpangan baku = suhu 1 °C, RH 8% (belum divalidasi lokal). Kisaran HI = nilai ± simpangan baku hasil propagasi galat. Kolom `sd_sumber` mencatat asal angkanya.
- **A9** Spread ensemble adalah sebaran prakiraan, bukan galat terhadap pengamatan; ensemble cenderung kurang menyebar sehingga kisaran sebenarnya dapat lebih lebar.
- **A10** UV di Forecast API Open-Meteo berbasis GFS untuk semua pilihan model, sehingga selisih "antar-model" UV tidak dipakai sebagai bukti kesepakatan. Pembanding independen: UV CAMS dan spread ensemble. Nama model Ensemble Mean selain `dwd_icon_eps_ensemble_mean_seamless` belum terkonfirmasi; yang ditolak API dilewati dan dicatat di `data/sumber_status.json`.

## 4. Ketidakpastian
| Jenis | Sumber | Penanganan |
|---|---|---|
| Variabilitas alami | Awan & cuaca antarhari | Persentil P10–P90; bootstrap antarhari (notebook 11A) |
| Galat model | Model numerik berbeda | Tiap jam, kisaran UV = min–maks dari UV utama, model lain, UV utama ± 1 SD ensemble, dan UV CAMS (`fetch_ensemble_mean`, `fetch_cams_uv` di `core.py`); label **Tinggi** (satu kategori & selisih ≤ 1,5 UVI), **Sedang** (beda 1 kategori), **Rendah** (beda >1 kategori), **Tidak diketahui** (hanya 1 model dan tanpa pembanding independen), **Tidak dapat dinilai** (tanpa CAMS maupun spread ensemble, dan model "berbeda" memberi UV identik) |
| Galat input & rumus HI | Suhu/RH tidak sempurna; regresi NWS ±1,3 °F | Kisaran HI = nilai ± 1 simpangan baku propagasi galat (SD dari spread ensemble, atau asumsi T 1 °C / RH 8%) dan antar-model; Monte Carlo di notebook 11C |
| Pilihan analis | Batas segmen, ambang | Uji sensitivitas notebook 11D |

**Aturan keputusan:** bila kisaran melintasi kategori yang lebih berat dari nilai utama, kolom tindakan memakai **skenario terburuk** dan diberi tanda ⚠️.

**Batasan utama:** belum ada validasi terhadap alat ukur UV/stasiun cuaca di ITB; hasil bersifat indikatif. Model atau sumber yang gagal diambil otomatis dilewati dan dicatat (`data/sumber_status.json`); tanpa pembanding, kepastian ditulis "Tidak diketahui" atau "Tidak dapat dinilai", bukan "Tinggi". Riwayat perbandingan UV utama vs CAMS dan SD ensemble tiap jam disimpan di `data/uncertainty_log.csv` untuk dianalisis kemudian.
