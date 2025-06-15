import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, Holt
from statsmodels.tsa.seasonal import seasonal_decompose
import streamlit as st
from datetime import datetime, timedelta
from config import PREDICTION_CONFIG

class TimeSeriesAnalyzer:
    def __init__(self, data):
        """
        Inisialisasi analyzer dengan data time series
        
        Args:
            data (pd.DataFrame): DataFrame dengan kolom tanggal dan nilai penjualan
        """
        self.data = data
        self.forecast_periods = PREDICTION_CONFIG['forecast_periods']
        self.confidence_level = PREDICTION_CONFIG['confidence_level']
        
    def prepare_data(self, date_column='tanggal', value_column='jumlah_penjualan'):
        """Mempersiapkan data untuk analisis time series"""
        try:
            # Konversi kolom tanggal
            self.data[date_column] = pd.to_datetime(self.data[date_column])
            
            # Set tanggal sebagai index
            self.data = self.data.set_index(date_column)
            
            # Sort berdasarkan tanggal
            self.data = self.data.sort_index()
            
            # Ambil kolom nilai yang akan dianalisis
            self.series = self.data[value_column]
            
            return True
        except Exception as e:
            st.error(f"Error dalam mempersiapkan data: {e}")
            return False
    
    def simple_exponential_smoothing(self, smoothing_level=None):
        """
        Melakukan prediksi menggunakan Simple Exponential Smoothing
        
        Args:
            smoothing_level (float): Level smoothing (alpha)
            
        Returns:
            dict: Hasil prediksi dan metrik
        """
        try:
            if smoothing_level is None:
                smoothing_level = PREDICTION_CONFIG['smoothing_level']
            
            # Fit model
            model = SimpleExpSmoothing(self.series, initialization_method="estimated")
            fitted_model = model.fit(smoothing_level=smoothing_level)
            
            # Prediksi
            forecast = fitted_model.forecast(self.forecast_periods)
            
            # Hitung confidence interval (estimasi sederhana)
            residuals = fitted_model.resid
            std_error = np.std(residuals)
            z_score = 1.96  # untuk 95% confidence interval
            
            confidence_interval = {
                'lower': forecast - (z_score * std_error),
                'upper': forecast + (z_score * std_error)
            }
            
            # Hitung MAPE
            mape = self.calculate_mape(self.series, fitted_model.fittedvalues)
            
            return {
                'method': 'Simple Exponential Smoothing',
                'forecast': forecast,
                'confidence_interval': confidence_interval,
                'mape': mape,
                'fitted_values': fitted_model.fittedvalues,
                'model': fitted_model
            }
            
        except Exception as e:
            st.error(f"Error dalam Simple Exponential Smoothing: {e}")
            return None
    
    def holt_linear_trend(self, smoothing_level=None, trend_level=None):
        """
        Melakukan prediksi menggunakan Holt's Linear Trend
        
        Args:
            smoothing_level (float): Level smoothing (alpha)
            trend_level (float): Trend smoothing (beta)
            
        Returns:
            dict: Hasil prediksi dan metrik
        """
        try:
            if smoothing_level is None:
                smoothing_level = PREDICTION_CONFIG['smoothing_level']
            if trend_level is None:
                trend_level = PREDICTION_CONFIG['trend_level']
            
            # Fit model
            model = Holt(self.series, initialization_method="estimated")
            fitted_model = model.fit(
                smoothing_level=smoothing_level,
                smoothing_trend=trend_level
            )
            
            # Prediksi
            forecast = fitted_model.forecast(self.forecast_periods)
            
            # Hitung confidence interval
            residuals = fitted_model.resid
            std_error = np.std(residuals)
            z_score = 1.96  # untuk 95% confidence interval
            
            confidence_interval = {
                'lower': forecast - (z_score * std_error),
                'upper': forecast + (z_score * std_error)
            }
            
            # Hitung MAPE
            mape = self.calculate_mape(self.series, fitted_model.fittedvalues)
            
            return {
                'method': 'Holt Linear Trend',
                'forecast': forecast,
                'confidence_interval': confidence_interval,
                'mape': mape,
                'fitted_values': fitted_model.fittedvalues,
                'model': fitted_model
            }
            
        except Exception as e:
            st.error(f"Error dalam Holt Linear Trend: {e}")
            return None
    
    def calculate_mape(self, actual, predicted):
        """
        Menghitung Mean Absolute Percentage Error (MAPE)
        
        Args:
            actual (pd.Series): Nilai aktual
            predicted (pd.Series): Nilai prediksi
            
        Returns:
            float: Nilai MAPE dalam persen
        """
        try:
            # Hapus nilai yang tidak valid
            mask = (actual != 0) & (~np.isnan(actual)) & (~np.isnan(predicted))
            actual_clean = actual[mask]
            predicted_clean = predicted[mask]
            
            if len(actual_clean) == 0:
                return np.nan
            
            mape = np.mean(np.abs((actual_clean - predicted_clean) / actual_clean)) * 100
            return mape
            
        except Exception as e:
            st.error(f"Error dalam menghitung MAPE: {e}")
            return np.nan
    
    def decompose_series(self, model='additive', period=12):
        """
        Melakukan dekomposisi time series
        
        Args:
            model (str): Model dekomposisi ('additive' atau 'multiplicative')
            period (int): Periode musiman
            
        Returns:
            dict: Komponen dekomposisi
        """
        try:
            if len(self.series) < 2 * period:
                st.warning("Data tidak cukup untuk dekomposisi musiman")
                return None
            
            decomposition = seasonal_decompose(
                self.series, 
                model=model, 
                period=period
            )
            
            return {
                'trend': decomposition.trend,
                'seasonal': decomposition.seasonal,
                'residual': decomposition.resid,
                'observed': decomposition.observed
            }
            
        except Exception as e:
            st.error(f"Error dalam dekomposisi: {e}")
            return None
    
    def generate_forecast_dates(self, start_date=None):
        """
        Menghasilkan tanggal untuk periode prediksi
        
        Args:
            start_date (datetime): Tanggal mulai prediksi
            
        Returns:
            list: Daftar tanggal prediksi
        """
        if start_date is None:
            start_date = self.series.index[-1] + timedelta(days=1)
        
        forecast_dates = []
        for i in range(self.forecast_periods):
            # Asumsi prediksi bulanan
            next_month = start_date + timedelta(days=30 * i)
            forecast_dates.append(next_month)
        
        return forecast_dates
    
    def get_trend_analysis(self):
        """
        Menganalisis tren data
        
        Returns:
            dict: Analisis tren
        """
        try:
            # Hitung perubahan rata-rata
            changes = self.series.diff().dropna()
            avg_change = changes.mean()
            
            # Tentukan arah tren
            if avg_change > 0:
                trend_direction = "Naik"
                trend_strength = "Kuat" if avg_change > self.series.std() else "Lemah"
            elif avg_change < 0:
                trend_direction = "Turun"
                trend_strength = "Kuat" if abs(avg_change) > self.series.std() else "Lemah"
            else:
                trend_direction = "Stabil"
                trend_strength = "Netral"
            
            # Hitung volatilitas
            volatility = self.series.std() / self.series.mean() * 100
            
            return {
                'direction': trend_direction,
                'strength': trend_strength,
                'avg_change': avg_change,
                'volatility': volatility,
                'min_value': self.series.min(),
                'max_value': self.series.max(),
                'mean_value': self.series.mean()
            }
            
        except Exception as e:
            st.error(f"Error dalam analisis tren: {e}")
            return None

