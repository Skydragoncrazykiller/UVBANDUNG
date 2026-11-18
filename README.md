# UV dan Heat Index Bandung (ITB)

[![Update data](https://github.com/Skydragoncrazykiller/UVBANDUNG/actions/workflows/update.yml/badge.svg)](https://github.com/Skydragoncrazykiller/UVBANDUNG/actions/workflows/update.yml)
[![Buka di Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Skydragoncrazykiller/UVBANDUNG/blob/main/notebook/Bandung_UV_HeatIndex.ipynb)

Pemantauan intensitas sinar UV dan heat index di kampus ITB Ganesha, Bandung, per segmen waktu dalam sehari. Data diambil dari Open-Meteo setiap jam melalui GitHub Actions, lalu diterjemahkan menjadi tindakan praktis untuk setiap segmen waktu.

**Dasbor:** <https://skydragoncrazykiller.github.io/UVBANDUNG/> · **Notebook analisis:** [`notebook/Bandung_UV_HeatIndex.ipynb`](notebook/Bandung_UV_HeatIndex.ipynb) · **Metodologi:** [`METODOLOGI.md`](METODOLOGI.md)

## Kondisi hari ini

<!-- TODAY:START -->
**Rabu, 18 November 2026** · ITB Ganesha, Bandung · diperbarui 23:27 WIB

| Ringkasan hari ini | |
|---|---|
| Puncak UV | **8,3** (Sangat tinggi) pukul 13:00 WIB |
| Jam perlu proteksi (UV ≥ 3) | 08:00–17:00 |
| Jendela UV aman (< 3) | 06:00–08:00, 17:00–18:00 |
| Heat index tertinggi | **32,3 °C** (Sangat waspada) |

| Segmen | Jam (WIB) | UV maks | Heat index maks | Kepastian | Tindakan |
|---|---|---|---|---|---|
| **Dini hari** | 00:00–06:00 | Tidak ada | **24,4 °C** Aman | Tinggi · HI 23–26 °C | Tabir surya tidak diperlukan. |
| **Pagi** | 06:00–10:00 | **4,8** Sedang (09:00) | **29,2 °C** Waspada | Tidak dapat dinilai (model memberi UV identik) · HI 27–31 °C | SPF 30+ dan kacamata hitam; cari teduh saat terik. Bawa botol minum; minum sebelum haus. Mendung tidak mengurangi risiko UV. |
| **Siang** | 10:00–15:00 | **8,3** Sangat tinggi (13:00) | **32,3 °C** Sangat waspada | Tinggi · UV 8,3–8,3 · HI 30–35 °C · 2 model | Hindari luar ruang tanpa naungan; bila perlu SPF 50+, topi, pakaian menutup. Minum ±250 ml tiap jam secara perlahan; kurangi aktivitas berat. Mendung tidak mengurangi risiko UV. Bawa payung. |
| **Sore** | 15:00–18:00 | **5,1** Sedang (15:00) | **26,6 °C** Aman | Tidak dapat dinilai (model memberi UV identik) · HI 24–29 °C | SPF 30+ dan kacamata hitam; cari teduh saat terik. Bawa botol minum; minum sebelum haus. Mendung tidak mengurangi risiko UV. Bawa payung. |
| **Malam** (berlangsung) | 18:00–24:00 | Tidak ada | **24,4 °C** Aman | Tinggi · HI 23–26 °C | Tabir surya tidak diperlukan. Bawa payung. |

**Pesan hari ini untuk mahasiswa**

- UV hari ini mencapai 8,3 (sangat tinggi) sekitar pukul 13:00. Pakai sunscreen dan cari tempat teduh pada 08:00–17:00.
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
| 05:00 | 0,0 | 22,2 | 21,6 | 91 | 92 |
| 06:00 | 0,1 | 22,1 | 21,5 | 92 | 86 |
| 07:00 | 1,1 | 24,1 | 23,6 | 80 | 97 |
| 08:00 | 3,0 | 26,2 | 25,7 | 72 | 97 |
| 09:00 | 4,8 | 29,2 | 27,5 | 65 | 95 |
| 10:00 | 6,8 | 30,7 | 28,9 | 59 | 85 |
| 11:00 | 8,3 | 32,3 | 30,0 | 57 | 92 |
| 12:00 | 7,5 | 32,2 | 30,1 | 56 | 100 |
| 13:00 | 8,3 | 25,8 | 25,2 | 77 | 100 |
| 14:00 | 7,1 | 24,4 | 23,7 | 86 | 99 |
| 15:00 | 5,1 | 26,1 | 25,4 | 80 | 63 |
| 16:00 | 3,4 | 26,6 | 26,0 | 75 | 54 |
| 17:00 | 0,8 | 25,4 | 24,8 | 80 | 72 |
| 18:00 | 0,1 | 24,4 | 23,8 | 84 | 84 |
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
