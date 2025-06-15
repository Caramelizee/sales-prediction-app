# Sistem Prediksi Permintaan Produk Kopi Susu dan Non-Kopi Botolan

Aplikasi web berbasis Streamlit untuk memprediksi permintaan produk kopi susu dan non-kopi botolan menggunakan metode Exponential Smoothing.

## Fitur Utama

- 📊 **Dashboard Visualisasi Interaktif**: Grafik tren penjualan dengan berbagai tipe visualisasi
- 🔮 **Prediksi Permintaan**: Menggunakan Simple Exponential Smoothing dan Holt's Linear Trend
- 💡 **Insight Bisnis Strategis**: Rekomendasi untuk inventory, marketing, produksi, dan keuangan
- 📥 **Export Data**: Download laporan lengkap dalam format Excel
- 🗄️ **Integrasi Database**: Dukungan MySQL dengan fallback ke data contoh

## Teknologi yang Digunakan

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: MySQL
- **Analisis**: Statsmodels, Pandas, NumPy
- **Visualisasi**: Plotly
- **Export**: OpenPyXL, XlsxWriter

## Instalasi dan Deployment

### Prasyarat
- Python 3.8+
- MySQL (opsional)

### Langkah Instalasi
1. Clone repository ini
2. Install dependencies: `pip install -r requirements.txt`
3. Jalankan aplikasi: `streamlit run main.py`

### Deployment di Streamlit Sharing
1. Fork repository ini ke akun GitHub Anda
2. Daftar di [Streamlit Sharing](https://streamlit.io/sharing)
3. Deploy dengan mengatur:
   - Repository: `your-username/sales-prediction-app`
   - Branch: `main`
   - Main file path: `main.py`

## Struktur Proyek

```
sales-prediction-app/
├── main.py                    # File utama aplikasi Streamlit
├── requirements.txt           # Dependencies
├── README.md                  # Dokumentasi
└── src/
    ├── __init__.py           # Python package marker
    ├── config.py             # Konfigurasi aplikasi
    ├── connection.py         # Koneksi database
    └── time_series.py        # Analisis time series
```

## Konfigurasi Database (Opsional)

Jika ingin menggunakan MySQL, tambahkan secrets di Streamlit Sharing:

```toml
[mysql]
host = "your-mysql-host"
user = "your-username"
password = "your-password"
database = "sales_prediction"
port = 3306
```

## Kontribusi

Aplikasi ini dikembangkan sebagai bagian dari skripsi tentang sistem prediksi permintaan produk menggunakan metode Exponential Smoothing.

## Lisensi

MIT License

