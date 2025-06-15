import os

# Database Configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'sales_prediction'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# Application Configuration
APP_CONFIG = {
    'title': 'Sistem Prediksi Permintaan Produk Kopi Susu dan Non-Kopi Botolan',
    'version': '1.0.0',
    'author': 'Mahasiswa Skripsi',
    'description': 'Aplikasi prediksi permintaan menggunakan metode Exponential Smoothing'
}

# Prediction Configuration
PREDICTION_CONFIG = {
    'forecast_periods': 2,  # Prediksi untuk 2 bulan ke depan (April dan Mei 2025)
    'confidence_level': 0.95,
    'smoothing_level': 0.3,
    'trend_level': 0.1
}

# Product Categories
PRODUCT_CATEGORIES = {
    'kopi_susu': 'Kopi Susu Botolan',
    'non_kopi': 'Non-Kopi Botolan'
}

# Export Configuration
EXPORT_CONFIG = {
    'excel_filename': 'laporan_prediksi_permintaan.xlsx',
    'sheets': {
        'data_historis': 'Data Historis',
        'prediksi': 'Hasil Prediksi',
        'insight': 'Insight Bisnis',
        'risiko': 'Analisis Risiko',
        'rencana_aksi': 'Rencana Aksi'
    }
}

