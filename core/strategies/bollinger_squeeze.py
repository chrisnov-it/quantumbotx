# /core/strategies/bollinger_squeeze.py
import pandas_ta as ta
import numpy as np
from .base_strategy import BaseStrategy

class BollingerSqueezeStrategy(BaseStrategy):
    name = 'Bollinger Squeeze Breakout'
    description = 'Mencari periode volatilitas rendah (squeeze) sebagai sinyal potensi breakout harga yang kuat.'

    @classmethod
    def get_definable_params(cls):
        """Mengembalikan parameter yang bisa diatur untuk strategi ini."""
        return [
            {"name": "bb_length", "label": "Panjang BB", "type": "number", "default": 20},
            {"name": "bb_std", "label": "Std Dev BB", "type": "number", "default": 2.0, "step": 0.1},
            {"name": "squeeze_window", "label": "Window Squeeze", "type": "number", "default": 10},
            {"name": "squeeze_factor", "label": "Faktor Squeeze", "type": "number", "default": 0.7, "step": 0.1},
            {"name": "rsi_period", "label": "Periode RSI", "type": "number", "default": 14},
            {"name": "volume_factor", "label": "Faktor Volume", "type": "number", "default": 1.5, "step": 0.1}
        ]

    def analyze(self, df):
        """
        Menganalisis pasar menggunakan strategi Bollinger Band Squeeze.
        Strategi ini menunggu periode volatilitas rendah ("squeeze") lalu 
        masuk saat harga breakout.
        """
        if df is None or df.empty or len(df) < 121:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup untuk Bollinger Squeeze."}

        # --- Hitung Indikator ---
        bb_length = self.params.get('bb_length', 20)
        bb_std = self.params.get('bb_std', 2.0)
        squeeze_window = self.params.get('squeeze_window', 10)
        squeeze_factor = self.params.get('squeeze_factor', 0.7)
        rsi_period = self.params.get('rsi_period', 14)
        volume_factor = self.params.get('volume_factor', 1.5)

        # PERBAIKAN: Paksa format float dengan satu desimal pada nama kolom
        # untuk mencegah KeyError (misal: 'BBU_20_2' vs 'BBU_20_2.0')
        bbu_col = f'BBU_{bb_length}_{bb_std:.1f}'
        bbm_col = f'BBM_{bb_length}_{bb_std:.1f}'
        bbl_col = f'BBL_{bb_length}_{bb_std:.1f}'

        df.ta.bbands(length=bb_length, std=bb_std, append=True)
        df['BB_WIDTH'] = df[bbu_col] - df[bbl_col]
        
        # FIX 1: Mencegah ZeroDivisionError dengan pembagian yang aman
        df['BB_BANDWIDTH'] = np.where(
            df[bbm_col] != 0,
            (df[bbu_col] - df[bbl_col]) / df[bbm_col] * 100,
            0  # Jika middle band 0, anggap bandwidth 0
        )

        df['AVG_BANDWIDTH'] = df['BB_BANDWIDTH'].rolling(window=squeeze_window).mean()
        df['SQUEEZE_LEVEL'] = df['AVG_BANDWIDTH'] * squeeze_factor
        df['SQUEEZE'] = df['BB_BANDWIDTH'] < df['SQUEEZE_LEVEL']
        df['RSI'] = ta.rsi(df['close'], length=rsi_period)

        # FIX 2: Menggunakan nama kolom volume yang benar ('tick_volume')
        if 'tick_volume' in df.columns:
            df['AVG_VOLUME'] = df['tick_volume'].rolling(window=squeeze_window).mean()
            df['VOLUME_SURGE'] = df['tick_volume'] > df['AVG_VOLUME'] * volume_factor
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
            if last['close'] > prev[bbu_col] and last['RSI'] < 70:
                signal = "BUY"
                explanation = f"Squeeze & Breakout NAIK! Harga [{last['close']:.2f}] > Band Atas [{prev[bbu_col]:.2f}]"
            elif last['close'] < prev[bbl_col] and last['RSI'] > 30:
                signal = "SELL"
                explanation = f"Squeeze & Breakout TURUN! Harga [{last['close']:.2f}] < Band Bawah [{prev[bbl_col]:.2f}]"
        else:
            # Kondisi 3: Post-Squeeze Momentum
            if prev['BB_BANDWIDTH'] > prev['AVG_BANDWIDTH'] * 1.2:  # Bands expanding
                if last['close'] > prev[bbu_col] and last['VOLUME_SURGE']:
                    signal = 'BUY'
                    explanation = f"Momentum NAIK! Harga [{last['close']:.2f}] > Band Atas [{prev[bbu_col]:.2f}] dengan volume"
                elif last['close'] < prev[bbl_col] and last['VOLUME_SURGE']:
                    signal = 'SELL'
                    explanation = f"Momentum TURUN! Harga [{last['close']:.2f}] < Band Bawah [{prev[bbl_col]:.2f}] dengan volume"

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