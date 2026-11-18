# Metodologi, sumber, asumsi, dan ketidakpastian

## 1. Sumber
| No | Sumber | Dipakai untuk |
|---|---|---|
| 1 | [Open-Meteo Forecast API](https://open-meteo.com/en/docs) | UV, suhu 2 m, RH, awan, hujan per jam (hari ini & prakiraan) |
| 2 | [Open-Meteo Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api) | Riwayat per jam untuk notebook |
| 3 | WHO/WMO/UNEP/ICNIRP (2002), *Global Solar UV Index: A Practical Guide* | Kategori UV |
| 4 | [US NWS Heat Index](https://www.weather.gov/ama/heatindex); Rothfusz (1990), NWS TA SR 90-23; Steadman (1979), *J. Appl. Meteor.* 18 | Rumus & ambang heat index |

Sitasi Open-Meteo: Zippenfenig, P. (2023). *Open-Meteo.com Weather API*. Zenodo. <https://doi.org/10.5281/zenodo.7970649>. Lisensi data CC BY 4.0 (non-komersial).

## 2. Pengolahan
1. Data per jam diambil dalam zona `Asia/Jakarta` (WIB, UTC+7) untuk titik ITB Ganesha (−6,8915; 107,6107).
2. Heat index dihitung dari suhu 2 m & RH (NWS Rothfusz + koreksi; di bawah ±27 °C hasilnya ≈ suhu udara).
3. Hari dibagi ke segmen: Dini hari 00–06, Pagi 06–10, Siang 10–15, Sore 15–18, Malam 18–24 (`SEGMEN` di `uvheat/core.py`).
4. Per segmen diambil **nilai maksimum** UV dan HI (kondisi terburuk dalam segmen), lalu diklasifikasi dan diterjemahkan ke tindakan dengan aturan tetap (`UV_TINDAKAN`, `HI_TINDAKAN`).

## 3. Asumsi
- **A1** Satu titik; iklim mikro kampus (bayangan gedung, aspal, pohon) tidak tertangkap model.
- **A2** Data adalah keluaran model, bukan sensor di ITB; model dasar "best match" Open-Meteo dapat berubah.
- **A3** Historical Forecast API merekam prakiraan model per waktu, bukan reanalisis homogen.
- **A4** UV diperlakukan apa adanya (permukaan, langit dengan awan); tanpa koreksi albedo/halangan lokal.
- **A5** Heat index = kondisi teduh & angin ringan; tidak memasukkan radiasi langsung, sehingga di bawah terik terasa lebih panas.
- **A6** Batas segmen adalah pilihan analis; hasil sensitif terhadapnya (lihat notebook 11D).
- **A7** Teks tindakan adalah pedoman umum, bukan nasihat medis. Estimasi "menit sebelum kulit memerah" ≈ 200/UVI — sangat kasar, bergantung tipe kulit.
- **A8** Galat input heat index: 1 simpangan baku = suhu 1 °C, RH 8% (asumsi, belum divalidasi lokal); kisaran HI = nilai ± simpangan baku hasil propagasi galat.

## 4. Ketidakpastian
| Jenis | Sumber | Penanganan |
|---|---|---|
| Variabilitas alami | Awan & cuaca antarhari | Persentil P10–P90; bootstrap antarhari (notebook 11A) |
| Galat model | Model numerik berbeda | Tiap jam, tabel "Kepastian" membandingkan model (`MODELS` di `core.py`): kisaran UV = min–maks antar-model termasuk "best match"; label **Tinggi** (satu kategori & selisih ≤ 1,5 UVI), **Sedang** (beda 1 kategori), **Rendah** (beda >1 kategori), **Tidak diketahui** (hanya 1 model), **Tidak dapat dinilai** (model "berbeda" memberi UV identik → kemungkinan sumber UV sama, bukan kesepakatan independen) |
| Galat input & rumus HI | Suhu/RH tidak sempurna; regresi NWS ±1,3 °F | Kisaran HI = nilai ± 1 simpangan baku propagasi galat (T 1 °C, RH 8%) dan antar-model; Monte Carlo di notebook 11C |
| Pilihan analis | Batas segmen, ambang | Uji sensitivitas notebook 11D |

**Aturan keputusan:** bila kisaran melintasi kategori yang lebih berat dari nilai utama, kolom tindakan memakai **skenario terburuk** dan diberi tanda ⚠️.

**Batasan utama:** belum ada validasi terhadap alat ukur UV/stasiun cuaca di ITB; hasil bersifat indikatif. Model yang tidak menyediakan `uv_index` otomatis dilewati; bila hanya satu model tersedia, kepastian ditulis "Tidak diketahui", bukan "Tinggi".
