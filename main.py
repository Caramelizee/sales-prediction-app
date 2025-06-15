import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io
import xlsxwriter

# Import modul dari folder src
from src.config import APP_CONFIG, PRODUCT_CATEGORIES, EXPORT_CONFIG
from src.connection import get_database_connection
from src.time_series import TimeSeriesAnalyzer

# Konfigurasi halaman
st.set_page_config(
    page_title=APP_CONFIG['title'],
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_sample_data():
    """Memuat data contoh untuk demonstrasi"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    
    # Data kopi susu
    kopi_susu_base = 1000
    kopi_susu_trend = np.linspace(0, 200, len(dates))
    kopi_susu_seasonal = 100 * np.sin(2 * np.pi * np.arange(len(dates)) / 12)
    kopi_susu_noise = np.random.normal(0, 50, len(dates))
    kopi_susu_sales = kopi_susu_base + kopi_susu_trend + kopi_susu_seasonal + kopi_susu_noise
    
    # Data non-kopi
    non_kopi_base = 800
    non_kopi_trend = np.linspace(0, 150, len(dates))
    non_kopi_seasonal = 80 * np.sin(2 * np.pi * np.arange(len(dates)) / 12 + np.pi/4)
    non_kopi_noise = np.random.normal(0, 40, len(dates))
    non_kopi_sales = non_kopi_base + non_kopi_trend + non_kopi_seasonal + non_kopi_noise
    
    # Gabungkan data
    data = []
    for i, date in enumerate(dates):
        data.append({
            'tanggal': date,
            'kategori_produk': 'kopi_susu',
            'nama_produk': 'Kopi Susu Botolan',
            'jumlah_penjualan': max(0, int(kopi_susu_sales[i])),
            'harga_satuan': 15000,
            'total_penjualan': max(0, int(kopi_susu_sales[i])) * 15000
        })
        data.append({
            'tanggal': date,
            'kategori_produk': 'non_kopi',
            'nama_produk': 'Non-Kopi Botolan',
            'jumlah_penjualan': max(0, int(non_kopi_sales[i])),
            'harga_satuan': 12000,
            'total_penjualan': max(0, int(non_kopi_sales[i])) * 12000
        })
    
    return pd.DataFrame(data)

def create_visualization(data, chart_type="line", product_filter="all"):
    """Membuat visualisasi data penjualan"""
    
    # Filter data berdasarkan produk
    if product_filter != "all":
        data = data[data['kategori_produk'] == product_filter]
    
    # Agregasi data bulanan
    monthly_data = data.groupby(['tanggal', 'kategori_produk']).agg({
        'jumlah_penjualan': 'sum',
        'total_penjualan': 'sum'
    }).reset_index()
    
    if chart_type == "line":
        fig = px.line(
            monthly_data, 
            x='tanggal', 
            y='jumlah_penjualan',
            color='kategori_produk',
            title='Tren Penjualan Bulanan',
            labels={
                'tanggal': 'Tanggal',
                'jumlah_penjualan': 'Jumlah Penjualan (Unit)',
                'kategori_produk': 'Kategori Produk'
            }
        )
    elif chart_type == "bar":
        fig = px.bar(
            monthly_data, 
            x='tanggal', 
            y='jumlah_penjualan',
            color='kategori_produk',
            title='Penjualan Bulanan',
            labels={
                'tanggal': 'Tanggal',
                'jumlah_penjualan': 'Jumlah Penjualan (Unit)',
                'kategori_produk': 'Kategori Produk'
            }
        )
    elif chart_type == "area":
        fig = px.area(
            monthly_data, 
            x='tanggal', 
            y='jumlah_penjualan',
            color='kategori_produk',
            title='Area Penjualan Bulanan',
            labels={
                'tanggal': 'Tanggal',
                'jumlah_penjualan': 'Jumlah Penjualan (Unit)',
                'kategori_produk': 'Kategori Produk'
            }
        )
    
    fig.update_layout(
        xaxis_title="Tanggal",
        yaxis_title="Jumlah Penjualan (Unit)",
        legend_title="Kategori Produk",
        hovermode='x unified'
    )
    
    return fig

def perform_prediction(data, category):
    """Melakukan prediksi untuk kategori produk tertentu"""
    
    # Filter data berdasarkan kategori
    category_data = data[data['kategori_produk'] == category].copy()
    
    # Agregasi bulanan
    monthly_data = category_data.groupby('tanggal').agg({
        'jumlah_penjualan': 'sum'
    }).reset_index()
    
    # Inisialisasi analyzer
    analyzer = TimeSeriesAnalyzer(monthly_data)
    
    if not analyzer.prepare_data():
        return None
    
    # Lakukan prediksi dengan kedua metode
    ses_result = analyzer.simple_exponential_smoothing()
    holt_result = analyzer.holt_linear_trend()
    
    # Analisis tren
    trend_analysis = analyzer.get_trend_analysis()
    
    return {
        'ses': ses_result,
        'holt': holt_result,
        'trend': trend_analysis,
        'historical_data': monthly_data
    }

def generate_business_insights(predictions):
    """Menghasilkan insight bisnis berdasarkan prediksi"""
    
    insights = {
        'inventory': [],
        'marketing': [],
        'production': [],
        'financial': []
    }
    
    for category, pred_data in predictions.items():
        if pred_data and pred_data['holt']:
            forecast = pred_data['holt']['forecast']
            trend = pred_data['trend']
            
            category_name = PRODUCT_CATEGORIES[category]
            
            # Inventory Management
            avg_forecast = forecast.mean()
            if trend['direction'] == 'Naik':
                insights['inventory'].append(
                    f"Tingkatkan stok {category_name} sebesar 20-30% untuk mengantisipasi peningkatan permintaan"
                )
            elif trend['direction'] == 'Turun':
                insights['inventory'].append(
                    f"Kurangi stok {category_name} dan fokus pada produk dengan performa lebih baik"
                )
            
            # Marketing Strategy
            if trend['volatilitas'] > 20:
                insights['marketing'].append(
                    f"Implementasikan strategi pemasaran yang lebih agresif untuk {category_name} karena volatilitas tinggi"
                )
            
            # Production Planning
            insights['production'].append(
                f"Rencanakan produksi {category_name} sebesar {int(avg_forecast)} unit per bulan untuk 2 bulan ke depan"
            )
            
            # Financial Forecasting
            if category == 'kopi_susu':
                revenue_forecast = avg_forecast * 15000
            else:
                revenue_forecast = avg_forecast * 12000
            
            insights['financial'].append(
                f"Proyeksi pendapatan {category_name}: Rp {revenue_forecast:,.0f} per bulan"
            )
    
    return insights

def export_to_excel(data, predictions, insights):
    """Export data ke Excel"""
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet 1: Data Historis
        data.to_excel(writer, sheet_name='Data Historis', index=False)
        
        # Sheet 2: Hasil Prediksi
        prediction_data = []
        for category, pred_data in predictions.items():
            if pred_data and pred_data['holt']:
                forecast = pred_data['holt']['forecast']
                dates = pd.date_range(start='2025-04-01', periods=len(forecast), freq='M')
                
                for i, (date, value) in enumerate(zip(dates, forecast)):
                    prediction_data.append({
                        'Tanggal': date,
                        'Kategori': PRODUCT_CATEGORIES[category],
                        'Prediksi (Unit)': int(value),
                        'Metode': 'Holt Linear Trend'
                    })
        
        pd.DataFrame(prediction_data).to_excel(writer, sheet_name='Hasil Prediksi', index=False)
        
        # Sheet 3: Insight Bisnis
        insight_data = []
        for category, insight_list in insights.items():
            for insight in insight_list:
                insight_data.append({
                    'Kategori': category.title(),
                    'Insight': insight
                })
        
        pd.DataFrame(insight_data).to_excel(writer, sheet_name='Insight Bisnis', index=False)
    
    output.seek(0)
    return output

def main():
    """Fungsi utama aplikasi"""
    
    # Header
    st.title(APP_CONFIG['title'])
    st.markdown(f"**Versi:** {APP_CONFIG['version']} | **Penulis:** {APP_CONFIG['author']}")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("Pengaturan")
    
    # Pilihan sumber data
    data_source = st.sidebar.selectbox(
        "Sumber Data",
        ["Data Contoh", "Database MySQL"]
    )
    
    # Load data
    if data_source == "Data Contoh":
        data = load_sample_data()
        st.sidebar.success("Data contoh berhasil dimuat")
    else:
        # Coba koneksi database
        db = get_database_connection()
        if db:
            st.sidebar.success("Koneksi database berhasil")
            # Di sini bisa ditambahkan query untuk mengambil data dari database
            data = load_sample_data()  # Sementara gunakan data contoh
            db.disconnect()
        else:
            st.sidebar.error("Gagal terhubung ke database. Menggunakan data contoh.")
            data = load_sample_data()
    
    # Filter dan kontrol visualisasi
    st.sidebar.subheader("Kontrol Visualisasi")
    
    chart_type = st.sidebar.selectbox(
        "Tipe Grafik",
        ["line", "bar", "area"],
        format_func=lambda x: {"line": "Garis", "bar": "Batang", "area": "Area"}[x]
    )
    
    product_filter = st.sidebar.selectbox(
        "Filter Produk",
        ["all", "kopi_susu", "non_kopi"],
        format_func=lambda x: {
            "all": "Semua Produk",
            "kopi_susu": "Kopi Susu",
            "non_kopi": "Non-Kopi"
        }[x]
    )
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Visualisasi Data Penjualan")
        
        # Buat dan tampilkan grafik
        fig = create_visualization(data, chart_type, product_filter)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tampilkan data dalam tabel
        st.subheader("📋 Data Historis")
        st.dataframe(data.tail(10), use_container_width=True)
    
    with col2:
        st.subheader("🔮 Prediksi Permintaan")
        
        # Lakukan prediksi untuk setiap kategori
        predictions = {}
        
        for category in ['kopi_susu', 'non_kopi']:
            with st.expander(f"Prediksi {PRODUCT_CATEGORIES[category]}"):
                pred_result = perform_prediction(data, category)
                
                if pred_result:
                    predictions[category] = pred_result
                    
                    # Tampilkan hasil prediksi Holt
                    if pred_result['holt']:
                        holt_forecast = pred_result['holt']['forecast']
                        mape = pred_result['holt']['mape']
                        
                        st.metric(
                            "Prediksi April 2025",
                            f"{int(holt_forecast.iloc[0])} unit"
                        )
                        st.metric(
                            "Prediksi Mei 2025",
                            f"{int(holt_forecast.iloc[1])} unit"
                        )
                        st.metric(
                            "Akurasi (MAPE)",
                            f"{mape:.2f}%"
                        )
                        
                        # Analisis tren
                        trend = pred_result['trend']
                        st.write(f"**Tren:** {trend['direction']} ({trend['strength']})")
                        st.write(f"**Volatilitas:** {trend['volatility']:.1f}%")
                else:
                    st.error(f"Gagal melakukan prediksi untuk {PRODUCT_CATEGORIES[category]}")
    
    # Insight Bisnis
    st.markdown("---")
    st.subheader("💡 Insight Bisnis Strategis")
    
    if predictions:
        insights = generate_business_insights(predictions)
        
        insight_tabs = st.tabs(["📦 Inventory", "📈 Marketing", "🏭 Produksi", "💰 Keuangan"])
        
        with insight_tabs[0]:
            for insight in insights['inventory']:
                st.write(f"• {insight}")
        
        with insight_tabs[1]:
            for insight in insights['marketing']:
                st.write(f"• {insight}")
        
        with insight_tabs[2]:
            for insight in insights['production']:
                st.write(f"• {insight}")
        
        with insight_tabs[3]:
            for insight in insights['financial']:
                st.write(f"• {insight}")
    
    # Export data
    st.markdown("---")
    st.subheader("📥 Export Data")
    
    if st.button("Download Laporan Excel"):
        if predictions:
            excel_data = export_to_excel(data, predictions, insights)
            st.download_button(
                label="📊 Download Laporan Lengkap",
                data=excel_data,
                file_name=EXPORT_CONFIG['excel_filename'],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Tidak ada data prediksi untuk di-export")

if __name__ == "__main__":
    main()

