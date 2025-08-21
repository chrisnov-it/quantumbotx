# core/strategies/ichimoku_cloud.py
import numpy as np
import pandas_ta as ta
from .base_strategy import BaseStrategy

class IchimokuCloudStrategy(BaseStrategy):
    name = 'Ichimoku Cloud'
    description = 'Sistem trading komprehensif berdasarkan Ichimoku Cloud untuk mengidentifikasi tren dan sinyal momentum.'

    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "tenkan_period", "label": "Periode Tenkan-sen", "type": "number", "default": 9},
            {"name": "kijun_period", "label": "Periode Kijun-sen", "type": "number", "default": 26},
            {"name": "senkou_period", "label": "Periode Senkou Span B", "type": "number", "default": 52},
            {"name": "use_cloud_filter", "label": "Gunakan Filter Awan", "type": "boolean", "default": True}
        ]

    def analyze(self, df):
        """Metode untuk LIVE TRADING."""
        tenkan_period = self.params.get('tenkan_period', 9)
        kijun_period = self.params.get('kijun_period', 26)
        senkou_period = self.params.get('senkou_period', 52)
        use_cloud_filter = str(self.params.get('use_cloud_filter', True)).lower() != 'false'

        min_len = max(tenkan_period, kijun_period, senkou_period) + kijun_period
        if df is None or df.empty or len(df) < min_len:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup."}

        # Hitung Indikator Ichimoku
        df.ta.ichimoku(tenkan=tenkan_period, kijun=kijun_period, senkou=senkou_period, append=True)
        df.dropna(inplace=True)
        
        if len(df) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        prev = df.iloc[-2]
        price = last["close"]
        signal = "HOLD"
        explanation = "Tidak ada sinyal Ichimoku."

        # Nama kolom dari pandas_ta:
        tenkan_col = f'ITS_{tenkan_period}'
        kijun_col = f'IKS_{kijun_period}'
        span_a_col = f'ISA_{tenkan_period}'
        span_b_col = f'ISB_{kijun_period}' # DIPERBAIKI: Nama kolom dinamis

        # Pastikan kolom ada sebelum digunakan
        if not all(col in df.columns for col in [tenkan_col, kijun_col, span_a_col, span_b_col]):
            return {"signal": "HOLD", "price": None, "explanation": "Kolom Ichimoku tidak ditemukan."}

        # Kondisi Awan (Filter Utama)
        is_above_cloud = price > last[span_a_col] and price > last[span_b_col]
        is_below_cloud = price < last[span_a_col] and price < last[span_b_col]
        
        # Kondisi Persilangan Tenkan/Kijun (Pemicu)
        tk_cross_up = prev[tenkan_col] <= prev[kijun_col] and last[tenkan_col] > last[kijun_col]
        tk_cross_down = prev[tenkan_col] >= prev[kijun_col] and last[tenkan_col] < last[kijun_col]

        # Logika Entry
        if tk_cross_up:
            if use_cloud_filter and is_above_cloud:
                signal = "BUY"
                explanation = "Harga di atas Awan & Tenkan/Kijun Golden Cross."
            elif not use_cloud_filter:
                signal = "BUY"
                explanation = "Tenkan/Kijun Golden Cross (Filter Awan Dinonaktifkan)."
        elif tk_cross_down:
            if use_cloud_filter and is_below_cloud:
                signal = "SELL"
                explanation = "Harga di bawah Awan & Tenkan/Kijun Death Cross."
            elif not use_cloud_filter:
                signal = "SELL"
                explanation = "Tenkan/Kijun Death Cross (Filter Awan Dinonaktifkan)."

        return {"signal": signal, "price": price, "explanation": explanation}

    def analyze_df(self, df):
        """Metode untuk BACKTESTING (vectorized)."""
        tenkan_period = self.params.get('tenkan_period', 9)
        kijun_period = self.params.get('kijun_period', 26)
        senkou_period = self.params.get('senkou_period', 52)
        use_cloud_filter = str(self.params.get('use_cloud_filter', True)).lower() != 'false'

        min_len = max(tenkan_period, kijun_period, senkou_period) + kijun_period
        if df is None or df.empty or len(df) < min_len:
            df['signal'] = 'HOLD'
            return df

        # Hitung Indikator Ichimoku
        df.ta.ichimoku(tenkan=tenkan_period, kijun=kijun_period, senkou=senkou_period, append=True)
        df.dropna(inplace=True)
        df = df.reset_index(drop=True)

        # Nama kolom dari pandas_ta:
        tenkan_col = f'ITS_{tenkan_period}'
        kijun_col = f'IKS_{kijun_period}'
        span_a_col = f'ISA_{tenkan_period}'
        span_b_col = f'ISB_{kijun_period}' # DIPERBAIKI: Nama kolom dinamis

        required_cols = [tenkan_col, kijun_col, span_a_col, span_b_col]
        if not all(col in df.columns for col in required_cols):
            df['signal'] = 'HOLD'
            return df

        # Kondisi Awan (Filter Utama) - DIPERBAIKI: Logika konsisten dengan 'analyze'
        is_above_cloud = (df['close'] > df[span_a_col]) & (df['close'] > df[span_b_col])
        is_below_cloud = (df['close'] < df[span_a_col]) & (df['close'] < df[span_b_col])

        # Kondisi Persilangan Tenkan/Kijun (Pemicu)
        tk_cross_up = (df[tenkan_col].shift(1) <= df[kijun_col].shift(1)) & (df[tenkan_col] > df[kijun_col])
        tk_cross_down = (df[tenkan_col].shift(1) >= df[kijun_col].shift(1)) & (df[tenkan_col] < df[kijun_col])

        # Gabungkan sinyal
        buy_signal = tk_cross_up
        sell_signal = tk_cross_down

        if use_cloud_filter:
            buy_signal = buy_signal & is_above_cloud
            sell_signal = sell_signal & is_below_cloud

        df['signal'] = np.where(buy_signal, 'BUY', np.where(sell_signal, 'SELL', 'HOLD'))
        
        return df