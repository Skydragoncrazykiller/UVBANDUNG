# UV dan Heat Index Bandung (ITB)

[![Update data](https://github.com/Skydragoncrazykiller/UVBANDUNG/actions/workflows/update.yml/badge.svg)](https://github.com/Skydragoncrazykiller/UVBANDUNG/actions/workflows/update.yml)
[![Buka di Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Skydragoncrazykiller/UVBANDUNG/blob/main/notebook/Bandung_UV_HeatIndex.ipynb)

Pemantauan intensitas sinar UV dan heat index di kampus ITB Ganesha, Bandung, per segmen waktu dalam sehari. Data diambil dari Open-Meteo setiap jam melalui GitHub Actions, lalu diterjemahkan menjadi tindakan praktis untuk setiap segmen waktu.

**Dasbor:** <https://skydragoncrazykiller.github.io/UVBANDUNG/> · **Notebook analisis:** [`notebook/Bandung_UV_HeatIndex.ipynb`](notebook/Bandung_UV_HeatIndex.ipynb) · **Metodologi:** [`METODOLOGI.md`](METODOLOGI.md)

## Kondisi hari ini

<!-- TODAY:START -->
**Kamis, 19 November 2026** · ITB Ganesha, Bandung · diperbarui 06:23 WIB

| Ringkasan hari ini | |
|---|---|
| Puncak UV | **8,6** (Sangat tinggi) pukul 11:00 WIB |
| Jam perlu proteksi (UV ≥ 3) | 09:00–16:00 |
| Jendela UV aman (< 3) | 06:00–09:00, 16:00–18:00 |
| Heat index tertinggi | **26,8 °C** (Waspada) |

| Segmen | Jam (WIB) | UV maks | Heat index maks | Kepastian | Tindakan |
|---|---|---|---|---|---|
| **Dini hari** | 00:00–06:00 | Tidak ada | **23,1 °C** Aman | Tinggi · HI 22–24 °C | Tabir surya tidak diperlukan. |
| **Pagi** (berlangsung) | 06:00–10:00 | **5,3** Sedang (09:00) | **26,8 °C** Waspada | Tidak dapat dinilai (model memberi UV identik) · HI 24–29 °C | SPF 30+ dan kacamata hitam; cari teduh saat terik. Bawa botol minum; minum sebelum haus. Mendung tidak mengurangi risiko UV. |
| **Siang** | 10:00–15:00 | **8,6** Sangat tinggi (11:00) | **26,8 °C** Waspada | Tinggi · UV 8,6–8,6 · HI 24–29 °C · 2 model | Hindari luar ruang tanpa naungan; bila perlu SPF 50+, topi, pakaian menutup. Bawa botol minum; minum sebelum haus. Mendung tidak mengurangi risiko UV. Bawa payung. |
| **Sore** | 15:00–18:00 | **3,4** Sedang (15:00) | **24,6 °C** Aman | Tinggi · UV 3,4–3,4 · HI 24–26 °C · 2 model | SPF 30+ dan kacamata hitam; cari teduh saat terik. Mendung tidak mengurangi risiko UV. Bawa payung. |
| **Malam** | 18:00–24:00 | Tidak ada | **23,6 °C** Aman | Tinggi · HI 22–25 °C | Tabir surya tidak diperlukan. |

**Pesan hari ini untuk mahasiswa**

- UV hari ini mencapai 8,6 (sangat tinggi) sekitar pukul 11:00. Pakai sunscreen dan cari tempat teduh pada 09:00–16:00.
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
| 05:00 | 0,0 | 22,2 | 21,7 | 86 | 92 |
| 06:00 | 0,1 | 22,6 | 22,1 | 85 | 98 |
| 07:00 | 1,1 | 23,6 | 23,1 | 83 | 75 |
| 08:00 | 3,0 | 25,1 | 24,5 | 79 | 64 |
| 09:00 | 5,3 | 26,8 | 26,2 | 72 | 90 |
| 10:00 | 7,5 | 26,8 | 26,3 | 70 | 95 |
| 11:00 | 8,6 | 26,1 | 25,6 | 74 | 99 |
| 12:00 | 6,4 | 26,4 | 25,8 | 75 | 98 |
| 13:00 | 6,3 | 25,1 | 24,5 | 80 | 100 |
| 14:00 | 6,2 | 25,1 | 24,4 | 83 | 100 |
| 15:00 | 3,4 | 24,3 | 23,7 | 85 | 100 |
| 16:00 | 0,9 | 24,6 | 24,0 | 84 | 96 |
| 17:00 | 0,1 | 24,0 | 23,3 | 90 | 99 |
| 18:00 | 0,0 | 23,6 | 22,8 | 94 | 98 |
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

Kolom **Kepastian** membandingkan beberapa model cuaca Open-Meteo dan memperhitungkan galat input heat index. Bila kisarannya melewati kategori yang lebih berat, tindakan mengikuti skenario terburuk.

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
