import mysql.connector
from mysql.connector import Error
import streamlit as st
from config import DATABASE_CONFIG

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Membuat koneksi ke database MySQL"""
        try:
            # Coba menggunakan konfigurasi dari Streamlit secrets terlebih dahulu
            if hasattr(st, 'secrets') and 'mysql' in st.secrets:
                config = {
                    'host': st.secrets['mysql']['host'],
                    'user': st.secrets['mysql']['user'],
                    'password': st.secrets['mysql']['password'],
                    'database': st.secrets['mysql']['database'],
                    'port': st.secrets['mysql']['port']
                }
            else:
                # Fallback ke konfigurasi default
                config = DATABASE_CONFIG
            
            self.connection = mysql.connector.connect(**config)
            self.cursor = self.connection.cursor(dictionary=True)
            return True
            
        except Error as e:
            st.error(f"Error koneksi database: {e}")
            return False
    
    def disconnect(self):
        """Menutup koneksi database"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query, params=None):
        """Menjalankan query SELECT"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            st.error(f"Error menjalankan query: {e}")
            return None
    
    def execute_insert(self, query, params=None):
        """Menjalankan query INSERT/UPDATE/DELETE"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Error as e:
            st.error(f"Error menjalankan insert: {e}")
            return False
    
    def create_tables(self):
        """Membuat tabel-tabel yang diperlukan"""
        tables = {
            'sales_data': """
                CREATE TABLE IF NOT EXISTS sales_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tanggal DATE NOT NULL,
                    kategori_produk ENUM('kopi_susu', 'non_kopi') NOT NULL,
                    nama_produk VARCHAR(255) NOT NULL,
                    jumlah_penjualan INT NOT NULL,
                    harga_satuan DECIMAL(10,2) NOT NULL,
                    total_penjualan DECIMAL(12,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """,
            'predictions': """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tanggal_prediksi DATE NOT NULL,
                    kategori_produk ENUM('kopi_susu', 'non_kopi') NOT NULL,
                    metode_prediksi VARCHAR(100) NOT NULL,
                    nilai_prediksi DECIMAL(12,2) NOT NULL,
                    confidence_interval_lower DECIMAL(12,2),
                    confidence_interval_upper DECIMAL(12,2),
                    mape DECIMAL(5,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'insights': """
                CREATE TABLE IF NOT EXISTS insights (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    kategori_insight ENUM('inventory', 'marketing', 'production', 'financial') NOT NULL,
                    judul VARCHAR(255) NOT NULL,
                    deskripsi TEXT NOT NULL,
                    prioritas ENUM('high', 'medium', 'low') NOT NULL,
                    status ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        }
        
        for table_name, query in tables.items():
            if self.execute_insert(query):
                st.success(f"Tabel {table_name} berhasil dibuat/diverifikasi")
            else:
                st.error(f"Gagal membuat tabel {table_name}")

# Fungsi helper untuk mendapatkan koneksi database
def get_database_connection():
    """Mendapatkan instance koneksi database"""
    db = DatabaseConnection()
    if db.connect():
        return db
    return None

