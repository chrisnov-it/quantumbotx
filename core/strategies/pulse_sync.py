# core/strategies/pulse_sync.py
import pandas_ta as ta
import numpy as np
from .base_strategy import BaseStrategy

class PulseSyncStrategy(BaseStrategy):
    name = 'Pulse Sync'
    description = 'Strategi responsif yang menggunakan filter tren jangka menengah (SMA 100) dengan konfirmasi MACD dan Stochastic.'

    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "trend_period", "label": "Periode Filter Tren", "type": "number", "default": 100},
            {"name": "macd_fast", "label": "MACD Fast", "type": "number", "default": 12},
            {"name": "macd_slow", "label": "MACD Slow", "type": "number", "default": 26},
            {"name": "macd_signal", "label": "MACD Signal", "type": "number", "default": 9},
            {"name": "stoch_k", "label": "Stoch %K", "type": "number", "default": 14},
            {"name": "stoch_d", "label": "Stoch %D", "type": "number", "default": 3},
            {"name": "stoch_smooth", "label": "Stoch Smooth", "type": "number", "default": 3},
        ]

    def analyze(self, df_h1):
        """Metode untuk LIVE TRADING. Disesuaikan agar 100% konsisten dengan logika backtesting (analyze_df)."""
        # Ambil parameter atau gunakan default
        trend_period = self.params.get('trend_period', 100)
        macd_fast = self.params.get('macd_fast', 12)
        macd_slow = self.params.get('macd_slow', 26)
        macd_signal_p = self.params.get('macd_signal', 9)
        stoch_k = self.params.get('stoch_k', 14)
        stoch_d = self.params.get('stoch_d', 3)
        stoch_smooth = self.params.get('stoch_smooth', 3)

        # Pastikan data cukup untuk semua indikator
        if df_h1 is None or len(df_h1) < trend_period + 1:
            return {"signal": "HOLD", "price": None, "explanation": f"Data tidak cukup untuk SMA({trend_period})."}

        # 1. Hitung semua indikator pada data yang diterima
        df_h1['trend_proxy_sma'] = ta.sma(df_h1['close'], length=trend_period)
        df_h1.ta.macd(fast=macd_fast, slow=macd_slow, signal=macd_signal_p, append=True)
        df_h1.ta.stoch(k=stoch_k, d=stoch_d, smooth_k=stoch_smooth, append=True)
        
        df_h1.dropna(inplace=True)
        if len(df_h1) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        # Nama kolom indikator untuk referensi
        macd_hist_col = f'MACDh_{macd_fast}_{macd_slow}_{macd_signal_p}'
        stoch_k_col = f'STOCHk_{stoch_k}_{stoch_d}_{stoch_smooth}'
        stoch_d_col = f'STOCHd_{stoch_k}_{stoch_d}_{stoch_smooth}'

        # Ambil data bar terakhir dan sebelumnya
        last = df_h1.iloc[-1]
        prev = df_h1.iloc[-2]
        price = last["close"]

        # 2. Definisikan kondisi sinyal berdasarkan data terakhir
        is_uptrend = last['close'] > last['trend_proxy_sma']
        is_downtrend = last['close'] < last['trend_proxy_sma']
        h1_macd_bullish = last[macd_hist_col] > 0
        h1_macd_bearish = last[macd_hist_col] < 0
        stoch_bullish_cross = (prev[stoch_k_col] <= prev[stoch_d_col]) and (last[stoch_k_col] > last[stoch_d_col])
        stoch_bearish_cross = (prev[stoch_k_col] >= prev[stoch_d_col]) and (last[stoch_k_col] < last[stoch_d_col])

        # 3. Gabungkan semua kondisi untuk sinyal final
        signal = "HOLD"
        explanation = "Tidak ada sinyal yang memenuhi syarat."

        if is_uptrend and h1_macd_bullish and stoch_bullish_cross:
            signal = "BUY"
            explanation = f"Tren Naik (SMA{trend_period}) & Momentum Bullish (MACD) & Stoch Cross."
        elif is_downtrend and h1_macd_bearish and stoch_bearish_cross:
            signal = "SELL"
            explanation = f"Tren Turun (SMA{trend_period}) & Momentum Bearish (MACD) & Stoch Cross."

        return {"signal": signal, "price": price, "explanation": explanation}

    def analyze_df(self, df):
        """
        Metode untuk BACKTESTING.
        Menerjemahkan logika multi-timeframe (D1+H1) ke dalam satu DataFrame H1.
        - Tren D1 disimulasikan dengan SMA pada data H1.
        - Sinyal MACD H1 dan Stochastic H1 dihitung secara normal.
        """
        # Ambil parameter atau gunakan default
        trend_period = self.params.get('trend_period', 100)
        macd_fast = self.params.get('macd_fast', 12)
        macd_slow = self.params.get('macd_slow', 26)
        macd_signal_p = self.params.get('macd_signal', 9)
        stoch_k = self.params.get('stoch_k', 14)
        stoch_d = self.params.get('stoch_d', 3)
        stoch_smooth = self.params.get('stoch_smooth', 3)
        
        # 1. Hitung semua indikator
        # Proksi Tren D1: SMA pada data H1
        df['trend_proxy_sma'] = ta.sma(df['close'], length=trend_period)

        # Indikator H1
        df.ta.macd(fast=macd_fast, slow=macd_slow, signal=macd_signal_p, append=True)
        df.ta.stoch(k=stoch_k, d=stoch_d, smooth_k=stoch_smooth, append=True)
        
        # Nama kolom indikator untuk referensi
        macd_hist_col = f'MACDh_{macd_fast}_{macd_slow}_{macd_signal_p}'
        stoch_k_col = f'STOCHk_{stoch_k}_{stoch_d}_{stoch_smooth}'
        stoch_d_col = f'STOCHd_{stoch_k}_{stoch_d}_{stoch_smooth}'

        # 2. Definisikan kondisi sinyal
        # Kondisi Tren (simulasi D1)
        is_uptrend = df['close'] > df['trend_proxy_sma']
        is_downtrend = df['close'] < df['trend_proxy_sma']

        # Kondisi Momentum (H1 MACD)
        h1_macd_bullish = df[macd_hist_col] > 0
        h1_macd_bearish = df[macd_hist_col] < 0

        # Kondisi Entry (H1 Stochastic Crossover)
        stoch_bullish_cross = (df[stoch_k_col].shift(1) <= df[stoch_d_col].shift(1)) & (df[stoch_k_col] > df[stoch_d_col])
        stoch_bearish_cross = (df[stoch_k_col].shift(1) >= df[stoch_d_col].shift(1)) & (df[stoch_k_col] < df[stoch_d_col])

        # 3. Gabungkan semua kondisi
        buy_signal = is_uptrend & h1_macd_bullish & stoch_bullish_cross
        sell_signal = is_downtrend & h1_macd_bearish & stoch_bearish_cross

        # 4. Hasilkan sinyal final
        df['signal'] = np.where(buy_signal, 'BUY', np.where(sell_signal, 'SELL', 'HOLD'))
        
        return df