# UV dan Heat Index Bandung (ITB)

[![Update data](https://github.com/Skydragoncrazykiller/UVBANDUNG/actions/workflows/update.yml/badge.svg)](https://github.com/Skydragoncrazykiller/UVBANDUNG/actions/workflows/update.yml)
[![Buka di Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Skydragoncrazykiller/UVBANDUNG/blob/main/notebook/Bandung_UV_HeatIndex.ipynb)

Pemantauan intensitas sinar UV dan heat index di kampus ITB Ganesha, Bandung, per segmen waktu dalam sehari. Data diambil dari Open-Meteo setiap jam melalui GitHub Actions, lalu diterjemahkan menjadi tindakan praktis untuk setiap segmen waktu.

**Dasbor:** <https://skydragoncrazykiller.github.io/UVBANDUNG/> · **Notebook analisis:** [`notebook/Bandung_UV_HeatIndex.ipynb`](notebook/Bandung_UV_HeatIndex.ipynb) · **Metodologi:** [`METODOLOGI.md`](METODOLOGI.md)

## Kondisi hari ini

<!-- TODAY:START -->
**Selasa, 24 November 2026** · ITB Ganesha, Bandung · diperbarui 03:11 WIB

| Ringkasan hari ini | |
|---|---|
| Puncak UV | **7,8** (Tinggi) pukul 14:00 WIB |
| Jam perlu proteksi (UV ≥ 3) | 08:00–17:00 |
| Jendela UV aman (< 3) | 06:00–08:00, 17:00–18:00 |
| Heat index tertinggi | **29,7 °C** (Waspada) |

| Segmen | Jam (WIB) | UV maks | Heat index maks | Kepastian | Tindakan |
|---|---|---|---|---|---|
| **Dini hari** (berlangsung) | 00:00–06:00 | Tidak ada | **24,2 °C** Aman | Tinggi · HI 24–25 °C | Tabir surya tidak diperlukan. |
| **Pagi** | 06:00–10:00 | **5,3** Sedang (09:00) | **28,6 °C** Waspada | Tinggi · UV 5,3–5,5 · HI 26–31 °C · CAMS 5,5 | SPF 30+ dan kacamata hitam; cari teduh saat terik. Bawa botol minum; minum sebelum haus. Mendung tidak mengurangi risiko UV. |
| **Siang** | 10:00–15:00 | **7,8** Tinggi (14:00) | **29,7 °C** Waspada | Tinggi · UV 6,6–7,8 · HI 28–32 °C · CAMS 6,6 | SPF 50+, topi, lengan panjang; ulangi tiap 2 jam. Bawa botol minum; minum sebelum haus. Mendung tidak mengurangi risiko UV. Bawa payung. |
| **Sore** | 15:00–18:00 | **5,7** Sedang (15:00) | **25,4 °C** Aman | Sedang · UV 1,6–5,7 · HI 24–29 °C · CAMS 1,6 · skenario terburuk | SPF 30+ dan kacamata hitam; cari teduh saat terik. Bawa botol minum; minum sebelum haus. Mendung tidak mengurangi risiko UV. Bawa payung. |
| **Malam** | 18:00–24:00 | Tidak ada | **23,9 °C** Aman | Tinggi · HI 23–25 °C | Tabir surya tidak diperlukan. |

**Pesan hari ini untuk mahasiswa**

- UV hari ini mencapai 7,8 (tinggi) sekitar pukul 14:00. Pakai sunscreen dan cari tempat teduh pada 08:00–17:00.
- Target minimal 8 gelas air putih sehari. Kalau kamu banyak di luar ruang, minum ±250 ml tiap jam secara perlahan. Cek warna pipis: kuning pucat berarti cukup.
- Kombo hari ini: minum cukup + sunscreen + berteduh di jam puncak.

<sub>Sumber: Open-Meteo. Angka adalah keluaran model, bukan pengukuran sensor di ITB; lihat [METODOLOGI.md](METODOLOGI.md) untuk asumsi dan ketidakpastian.</sub>
<!-- TODAY:END -->

![UV dan heat index per jam hari ini](docs/today.png)

<details>
<summary>Rincian per jam</summary>

<!-- HOURLY:START -->
| Jam | UV | Heat index (°C) | Suhu (°C) | RH (%) | Awan (%) |
|---:|---:|---:|---:|---:|---:|
| 05:00 | 0,0 | 22,1 | 21,5 | 90 | 92 |
| 06:00 | 0,1 | 22,3 | 21,7 | 90 | 99 |
| 07:00 | 1,2 | 24,0 | 23,4 | 83 | 95 |
| 08:00 | 3,2 | 25,6 | 25,0 | 78 | 88 |
| 09:00 | 5,3 | 28,6 | 26,8 | 71 | 66 |
| 10:00 | 6,9 | 29,7 | 27,6 | 68 | 67 |
| 11:00 | 7,8 | 25,5 | 24,9 | 80 | 88 |
| 12:00 | 7,5 | 26,0 | 25,4 | 76 | 98 |
| 13:00 | 6,8 | 25,5 | 25,0 | 76 | 95 |
| 14:00 | 7,8 | 24,3 | 23,6 | 88 | 88 |
| 15:00 | 5,7 | 25,4 | 24,7 | 83 | 100 |
| 16:00 | 3,2 | 24,3 | 23,6 | 89 | 99 |
| 17:00 | 0,5 | 24,3 | 23,5 | 90 | 98 |
| 18:00 | 0,1 | 23,9 | 23,1 | 93 | 98 |
<!-- HOURLY:END -->

</details>

## Tren 14 hari terakhir

![UV dan heat index maksimum per segmen](docs/trend.png)

## Cara membaca

Hari dibagi menjadi lima segmen (WIB). Untuk tiap segmen diambil nilai **maksimum** UV dan heat index, yaitu kondisi terburuk dalam segmen tersebut.

| Segmen | Jam |
|---|---|
| Dini hari | 00:00–06:00 |
| Pagi | 06:00–10:00 |
| Siang | 10:00–15:00 |
| Sore | 15:00–18:00 |
| Malam | 18:00–24:00 |

| Indeks UV (WHO) | Kategori | Heat index (NWS) | Kategori |
|---|---|---|---|
| < 3 | Rendah | < 27 °C (80 °F) | Aman |
| 3–5 | Sedang | 27–32 °C (80–90 °F) | Waspada |
| 6–7 | Tinggi | 32–39 °C (90–103 °F) | Sangat waspada |
| 8–10 | Sangat tinggi | 39–52 °C (103–125 °F) | Bahaya |
| ≥ 11 | Ekstrem | ≥ 52 °C (≥ 125 °F) | Sangat bahaya |

Ambang tepatnya adalah 26,7 / 32,2 / 39,4 / 51,7 °C (konversi dari °F). WHO menganjurkan perlindungan dari matahari saat UV ≥ 3, sehingga dasbor menampilkan "jam perlu proteksi" (UV ≥ 3) dan "jendela aman" (UV < 3).

Ringkasan harian juga memuat **pesan untuk mahasiswa** (UV, hidrasi, dan "kombo" minum cukup + sunscreen + berteduh) yang diselaraskan dengan materi poster Diseminasi Informasi Meteorologi.

Kolom **Kepastian** memakai pembanding UV independen (UV CAMS dan spread ensemble) serta galat input heat index; spread ensemble menunjukkan sebaran prakiraan, bukan galat terhadap pengamatan. Bila kisarannya melewati kategori yang lebih berat, tindakan mengikuti skenario terburuk.

Bandung berada di sekitar 770 mdpl dan relatif sejuk, sehingga heat index umumnya mendekati suhu udara; UV cenderung menjadi faktor risiko yang lebih menentukan.

## Sumber, asumsi, dan batasan

- Data adalah keluaran model numerik Open-Meteo, **bukan pengukuran sensor di ITB**, dan belum divalidasi dengan alat ukur lokal. Hasil bersifat indikatif.
- Satu titik lokasi (−6,8915; 107,6107); iklim mikro kampus tidak tertangkap.
- Batas segmen adalah pilihan analis; hasil sensitif terhadapnya (lihat analisis di notebook).
- Tindakan adalah pedoman umum, bukan nasihat medis. Estimasi waktu kulit memerah (sekitar 200/UVI menit) sangat kasar.
- Asumsi lengkap, sumber, dan metode ketidakpastian: [`METODOLOGI.md`](METODOLOGI.md).

## Struktur repositori

```
uvheat/core.py            pengambilan data, heat index, klasifikasi, rekomendasi, ketidakpastian
uvheat/render.py          keluaran Markdown, HTML, dan grafik
scripts/update.py         pembaruan data dan keluaran (dijalankan Actions tiap jam)
notebook/                 notebook Colab dan skrip pembangunnya
data/hourly.csv           riwayat per jam (UV, suhu, RH, awan, heat index)
data/forecast_log.csv     catatan perubahan prakiraan hari ini
data/uncertainty_log.csv  UV utama vs CAMS dan SD ensemble per jam (riwayat pembanding)
data/sumber_status.json   status pengambilan Ensemble Mean dan CAMS pada run terakhir
data/today.json           ringkasan terbaru (JSON)
docs/                     dasbor web (GitHub Pages) dan grafik
tests/                    tes unit
```

## Menjalankan secara lokal

```bash
pip install -r requirements.txt
python scripts/update.py      # ambil data dan perbarui semua keluaran
python -m pytest -q tests     # tes unit
```

Notebook dibangun ulang dari `uvheat/core.py` dengan `python notebook/build_notebook.py`.

## Data dan atribusi

Data cuaca: [Open-Meteo.com](https://open-meteo.com/) (CC BY 4.0, penggunaan non-komersial). Skala UV: WHO/WMO/UNEP/ICNIRP (2002). Heat index: US National Weather Service (Rothfusz, 1990).
