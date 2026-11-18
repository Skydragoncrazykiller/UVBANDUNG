# ☀️ UV & Heat Index Bandung (ITB) — pantauan harian otomatis

Data **Open-Meteo** diambil otomatis tiap jam oleh GitHub Actions, dibagi per segmen waktu harian (WIB), lalu diterjemahkan menjadi **tindakan yang perlu dilakukan**, bukan sekadar angka.
Dasbor web: aktifkan GitHub Pages (Settings → Pages → Branch `main`, folder `/docs`).

## 📌 Hari ini

<!-- TODAY:START -->
### Rabu, 18 November 2026 — ITB Ganesha, Bandung

- 🔴 **UV puncak hari ini 8.3 (Sangat tinggi) pukul 13:00 WIB.**
- Pada puncak itu, kulit sensitif bisa mulai memerah dalam ± 20 menit tanpa perlindungan (perkiraan kasar).
- Jendela aman UV (< 3) di siang hari: **06:00–08:00, 17:00–18:00**.
- Heat index tertinggi hari ini 32.1 °C.

| Segmen (WIB) | Status | UV maks | Heat index maks | Suhu / RH | Kepastian (kisaran) | Yang sebaiknya dilakukan |
|---|---|---|---|---|---|---|
| **Dini hari**<br>00:00–06:00 | Sudah lewat | ⚫ **0.0** Tidak ada | 🟢 **24.4 °C** Nyaman/normal | 23 °C / 88% | Tinggi. HI 23–26 °C | Tidak ada paparan UV berarti; tabir surya tidak diperlukan. |
| **Pagi**<br>06:00–10:00 | Sudah lewat | 🟡 **4.8** Sedang (09:00) | 🟡 **28.8 °C** Waspada (caution) | 24 °C / 78% | Tinggi. UV 4.8–4.8, HI 26–32 °C (2 model) | Oleskan tabir surya SPF 30+ 15–30 menit sebelum keluar. Pakai kacamata hitam; cari teduh saat terik. Suhu terasa hangat: bawa air minum, istirahat di tempat teduh tiap ±1 jam. Meski berawan/mendung, UV tetap menembus awan — tetap pakai perlindungan. |
| **Siang**<br>10:00–15:00 | ▶ Sekarang | 🔴 **8.3** Sangat tinggi (13:00) | 🟠 **32.1 °C** Sangat waspada | 27 °C / 69% | Tinggi. UV 8.3–8.3, HI 29–36 °C (2 model) | Hindari aktivitas luar ruang tanpa perlindungan penuh (SPF 50+, topi, kacamata UV, pakaian menutup). Tunda kegiatan lapangan/olahraga ke segmen lain. Minum 1 gelas (±250 ml) tiap 20–30 menit; kurangi aktivitas berat; istirahat teduh tiap 30 menit. Meski berawan/mendung, UV tetap menembus awan — tetap pakai perlindungan. Ada potensi hujan; bawa payung/jas hujan. |
| **Sore**<br>15:00–18:00 | Berikutnya | 🟡 **5.6** Sedang (15:00) | 🟢 **24.5 °C** Nyaman/normal | 24 °C / 87% | Tinggi. UV 5.6–5.6, HI 23–29 °C (2 model) | ⚠️ Prakiraan tidak pasti; memakai skenario terburuk. Oleskan tabir surya SPF 30+ 15–30 menit sebelum keluar. Pakai kacamata hitam; cari teduh saat terik. Suhu terasa hangat: bawa air minum, istirahat di tempat teduh tiap ±1 jam. Meski berawan/mendung, UV tetap menembus awan — tetap pakai perlindungan. Ada potensi hujan; bawa payung/jas hujan. |
| **Malam**<br>18:00–24:00 | Berikutnya | ⚫ **0.2** Tidak ada | 🟢 **23.6 °C** Nyaman/normal | 22 °C / 95% | Tinggi. HI 22–25 °C | Tidak ada paparan UV berarti; tabir surya tidak diperlukan. Ada potensi hujan; bawa payung/jas hujan. |

<sub>Diperbarui otomatis: 18-11-2026 13:45 WIB · Sumber: Open-Meteo</sub>
<!-- TODAY:END -->

![Grafik hari ini](docs/today.png)

<details><summary>Rincian per jam hari ini</summary>

<!-- HOURLY:START -->
| Jam | UV | Heat index | Suhu | RH | Awan |
|---|---|---|---|---|---|
| 05:00 | ⚫ 0.0 | 22.2 °C | 21.6 °C | 91% | 92% |
| 06:00 | ⚫ 0.1 | 22.1 °C | 21.5 °C | 92% | 86% |
| 07:00 | 🟢 1.1 | 24.3 °C | 23.7 °C | 82% | 99% |
| 08:00 | 🟡 3.0 | 26.0 °C | 25.5 °C | 73% | 100% |
| 09:00 | 🟡 4.8 | 28.8 °C | 27.2 °C | 66% | 100% |
| 10:00 | 🟠 6.8 | 30.3 °C | 28.4 °C | 62% | 99% |
| 11:00 | 🔴 8.3 | 32.1 °C | 29.8 °C | 58% | 99% |
| 12:00 | 🟠 7.5 | 30.9 °C | 29.1 °C | 58% | 100% |
| 13:00 | 🔴 8.3 | 26.3 °C | 25.6 °C | 81% | 100% |
| 14:00 | 🟠 6.8 | 24.8 °C | 24.1 °C | 84% | 100% |
| 15:00 | 🟡 5.6 | 24.3 °C | 23.6 °C | 87% | 100% |
| 16:00 | 🟡 3.6 | 24.5 °C | 23.8 °C | 85% | 100% |
| 17:00 | 🟢 1.5 | 23.8 °C | 23.1 °C | 90% | 100% |
| 18:00 | ⚫ 0.2 | 23.6 °C | 22.9 °C | 91% | 100% |
<!-- HOURLY:END -->

</details>

## 📈 Perkembangan 14 hari terakhir

![Tren](docs/trend.png)

Riwayat per jam: [`data/hourly.csv`](data/hourly.csv) · Perubahan prakiraan hari ini sepanjang waktu: [`data/forecast_log.csv`](data/forecast_log.csv) · Ringkasan terbaru (JSON): [`data/today.json`](data/today.json)

## Cara baca
Kolom **Kepastian (kisaran)** menunjukkan seberapa sepakat beberapa model cuaca Open-Meteo (kisaran UV) dan galat input heat index (±1 simpangan baku: suhu 1 °C, RH 8%). Jika kisaran melintasi kategori yang lebih berat, tindakan memakai **skenario terburuk** (⚠️).

| Segmen | Jam (WIB) |
|---|---|
| Dini hari | 00:00–06:00 |
| Pagi | 06:00–10:00 |
| Siang | 10:00–15:00 |
| Sore | 15:00–18:00 |
| Malam | 18:00–24:00 |

- **UV**: skala WHO — 🟢 Rendah (<3) · 🟡 Sedang (3–5) · 🟠 Tinggi (6–7) · 🔴 Sangat tinggi (8–10) · 🟣 Ekstrem (≥11).
- **Heat index**: rumus NWS/NOAA (suhu + kelembapan), dalam °C — 🟢 <27 · 🟡 27–32 · 🟠 32–41 · 🔴 41–54 · 🟣 ≥54. Bandung berada di ±770 mdpl dan sejuk, sehingga heat index umumnya mendekati suhu udara dan jarang melewati ambang waspada; **UV adalah faktor risiko utama**.
- Perkiraan "menit sebelum kulit sensitif memerah" (≈ 200/UVI) hanya patokan kasar, bukan saran medis.
- Batas segmen bisa diubah di `SEGMEN` pada `uvheat/core.py`; koordinat di `LAT, LON`.

## Sumber, asumsi, dan ketidakpastian (ringkas)

- **Sumber:** Open-Meteo (Forecast & Historical Forecast API, CC BY 4.0); kategori UV WHO/WMO/UNEP/ICNIRP (2002); heat index NWS/NOAA (Rothfusz 1990, Steadman 1979).
- **Data adalah keluaran model, bukan sensor ITB** — iklim mikro kampus tidak tertangkap; belum divalidasi dengan alat ukur lokal.
- **Asumsi utama:** satu titik di ITB Ganesha; batas segmen adalah pilihan (hasil sensitif terhadapnya); heat index kondisi teduh; galat input (1 simpangan baku) suhu 1 °C, RH 8%; tindakan = pedoman umum, bukan nasihat medis.
- **Ketidakpastian:** variabilitas antarhari, selisih antar-model, galat input/rumus heat index, dan pilihan batas segmen — dihitung di notebook (bootstrap, antar-model, Monte Carlo, uji sensitivitas).
- Rincian lengkap: [`METODOLOGI.md`](METODOLOGI.md).

## Menjalankan sendiri

```bash
pip install -r requirements.txt
python scripts/update.py            # ambil data nyata & perbarui semua keluaran
python -m pytest -q tests           # tes unit
```

Notebook Colab penjelasan lengkap: `notebook/Bandung_UV_HeatIndex.ipynb`.

Data: [Open-Meteo.com](https://open-meteo.com/) (CC BY 4.0, non-komersial).
