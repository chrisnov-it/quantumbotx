# /core/strategies/bollinger_squeeze.py
import pandas_ta as ta
import numpy as np
import MetaTrader5 as mt5
from .base_strategy import BaseStrategy
from core.data.fetch import get_rates # <-- PERBAIKAN: Impor dari lokasi yang benar

class BollingerSqueezeStrategy(BaseStrategy):
    name = 'Bollinger Squeeze Breakout'
    description = 'Mencari periode volatilitas rendah (squeeze) sebagai sinyal potensi breakout harga yang kuat.'

    def analyze(self):
        """
        Menganalisis pasar menggunakan strategi Bollinger Band Squeeze.
        Strategi ini menunggu periode volatilitas rendah ("squeeze") lalu 
        masuk saat harga breakout.
        """
        tf_const = self.bot.tf_map.get(self.bot.timeframe, mt5.TIMEFRAME_H1)
        
        # Butuh data yang cukup untuk rolling window squeeze (120) + BBands (20)
        df = get_rates(self.bot.market_for_mt5, tf_const, 150) # <-- PERBAIKAN: Gunakan fungsi yang benar

        if df is None or df.empty or len(df) < 121:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup untuk Bollinger Squeeze."}

        # --- Hitung Indikator ---
        df.ta.bbands(length=20, std=2.0, append=True)
        df['BB_WIDTH'] = df['BBU_20_2.0'] - df['BBL_20_2.0']
        
        # FIX 1: Mencegah ZeroDivisionError dengan pembagian yang aman
        df['BB_BANDWIDTH'] = np.where(
            df['BBM_20_2.0'] != 0,
            (df['BBU_20_2.0'] - df['BBL_20_2.0']) / df['BBM_20_2.0'] * 100,
            0  # Jika middle band 0, anggap bandwidth 0
        )

        df['AVG_BANDWIDTH'] = df['BB_BANDWIDTH'].rolling(window=10).mean()
        df['SQUEEZE_LEVEL'] = df['AVG_BANDWIDTH'] * 0.7
        df['SQUEEZE'] = df['BB_BANDWIDTH'] < df['SQUEEZE_LEVEL']
        df['RSI'] = ta.rsi(df['close'], length=14)

        # FIX 2: Menggunakan nama kolom volume yang benar ('tick_volume')
        if 'tick_volume' in df.columns:
            df['AVG_VOLUME'] = df['tick_volume'].rolling(window=10).mean()
            df['VOLUME_SURGE'] = df['tick_volume'] > df['AVG_VOLUME'] * 1.5
            df['VOLUME_SURGE'] = df['VOLUME_SURGE'].astype(int)
        else:
            df['VOLUME_SURGE'] = 0

        df.dropna(inplace=True)
        
        if len(df) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        prev = df.iloc[-2]

        price = last["close"]
        signal = "HOLD"
        explanation = "Tidak ada kondisi Squeeze & Breakout yang terdeteksi."

        # --- Logika Sinyal ---
        
        # Kondisi 1: Apakah candle SEBELUMNYA berada dalam kondisi "Squeeze"?
        is_in_squeeze = prev['SQUEEZE']
                    
        if is_in_squeeze:
            explanation = f"Squeeze terdeteksi (Lebar: {prev['BB_WIDTH']:.4f}). Menunggu breakout."
                
            # Kondisi 2: Jika ya, apakah candle SEKARANG breakout dari Bands SEBELUMNYA?
            if last['close'] > prev['BBU_20_2.0'] and last['RSI'] < 70:
                signal = "BUY"
                explanation = f"Squeeze & Breakout NAIK! Harga [{last['close']:.2f}] > Band Atas [{prev['BBU_20_2.0']:.2f}]"
            elif last['close'] < prev['BBL_20_2.0'] and last['RSI'] > 30:
                signal = "SELL"
                explanation = f"Squeeze & Breakout TURUN! Harga [{last['close']:.2f}] < Band Bawah [{prev['BBL_20_2.0']:.2f}]"
        else:
            # Kondisi 3: Post-Squeeze Momentum
            if prev['BB_BANDWIDTH'] > prev['AVG_BANDWIDTH'] * 1.2:  # Bands expanding
                if last['close'] > prev['BBU_20_2.0'] and last['VOLUME_SURGE']:
                    signal = 'BUY'
                    explanation = f"Momentum NAIK! Harga [{last['close']:.2f}] > Band Atas [{prev['BBU_20_2.0']:.2f}] dengan volume"
                elif last['close'] < prev['BBL_20_2.0'] and last['VOLUME_SURGE']:
                    signal = 'SELL'
                    explanation = f"Momentum TURUN! Harga [{last['close']:.2f}] < Band Bawah [{prev['BBL_20_2.0']:.2f}] dengan volume"

        # --- PERBAIKAN: Kembalikan semua data analisis yang relevan ---
        analysis_data = {
            "signal": signal,
            "price": price,
            "explanation": explanation,
            "RSI": last.get('RSI'),
            "BB_Width": last.get('BB_WIDTH'),
            "BB_Bandwidth": last.get('BB_BANDWIDTH'),
            "Is_Squeeze": bool(last.get('SQUEEZE', False)), # FIX: Konversi numpy.bool_ ke bool standar
            "Volume_Surge": bool(last.get('VOLUME_SURGE', 0))
        }

        return analysis_data