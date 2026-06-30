# Telco Observability Platform: Play Store Review Analytics

Repositori ini mengimplementasikan *pipeline* analisis deret waktu (*time-series*) dan pemrosesan bahasa alami (NLP) untuk mengekstrak metrik operasional publik dari ulasan aplikasi Google Play Store. Proyek ini membandingkan pemetaan performa antar-operator seluler menggunakan dua metrik diagnostik utama: **Telco Friction Index (TFI)** dan **Z-Score Anomaly Detection**.

## 1. Arsitektur Proyek & Struktur Direktori

```text
.
├── dashboard_output/
│   └── indosat_portfolio_dashboard.png # Artefak visual 
├── dataset_indosat/
│   ├── im3_master_catalog.csv          # Metadata katalog hasil klasifikasi
│   ├── im3_tfi_analysis.csv            # Agregasi metrik TFI harian
│   ├── im3_tfi_multidimensional.csv    # Matriks TFI berbasis versi aplikasi
│   ├── myim3_reviews_raw.csv           # Hasil scraping mentah dari Google Play API
│   ├── myim3_reviews_tagged.csv        # Dataset hasil tagging kategori NLP
├── calculate_tfi_isat.ipynb            # Pipeline pemrosesan data Indosat
├── nlp_processor.py                    # Modul klasifikasi teks (reusable)
├── parse_har.py                        # Parser untuk log lalu lintas jaringan
└── README.md                           # Dokumentasi sistem
```

## 2. Metodologi Diagnostik

Sistem ini memecah analisis menjadi dua dimensi independen untuk memangkas *Mean Time to Detect* (MTTD).

### A. Telco Friction Index (TFI)

Mengukur rasio konsentrasi kegagalan fungsional pada layer *client* (aplikasi) berdasarkan versi rilis tertentu.

**TFI = (Volume Keluhan App/System / Total Keluhan) × 100**

- **Aplikasi:** Isolasi kegagalan regresi kode atau *deployment bug* pada versi spesifik.
- **Mitigasi Bias:** Menggunakan *Dynamic Thresholding* berbasis Kuartil Atas Ekstrem (Persentil 95) untuk mengeliminasi varians sampel kecil (*Small Sample Variance*) pada versi aplikasi usang.

### B. Z-Score Operational Event Detection

Mengukur magnitudo lonjakan volume keluhan harian untuk mendeteksi gangguan pada layer infrastruktur (*backend/network outage*).

**Z = (X − μ) / σ**

- **Konfigurasi:** *Rolling window* sepanjang 14 hari digunakan untuk mengamankan 2 siklus musiman mingguan penuh (*weekly seasonality bias*).
- **Ambang Batas:** Z-Score > 2.0 mendeklarasikan insiden operasional massal (Harga atau Jaringan).

## 3. Ringkasan Temuan Kritis (Indosat)

- **Insiden Infrastruktur Terparah:** Terdeteksi pada **2026-06-07** untuk kategori *Network/QoS* dengan volume mencapai **115** keluhan dalam satu hari, mencatatkan deviasi ekstrem sebesar **Z-Score: 3.08** (*3-sigma event*).
- **Kegagalan Rilis Aplikasi:** Terdeteksi anomali fungsional nyata pada aplikasi **versi 82.15.0** pada **2026-06-23** dengan skor TFI puncak **37.78**.

---
