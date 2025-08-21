# /core/strategies/dynamic_breakout.py
import pandas_ta as ta
import numpy as np
from .base_strategy import BaseStrategy

class DynamicBreakoutStrategy(BaseStrategy):
    name = 'Dynamic Breakout'
    description = 'Strategi breakout dinamis menggunakan Donchian Channels, dengan filter tren EMA dan filter volatilitas ATR.'

    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "donchian_period", "label": "Periode Donchian Channel", "type": "number", "default": 20},
            {"name": "ema_filter_period", "label": "Periode EMA Filter Tren", "type": "number", "default": 50},
            {"name": "atr_period", "label": "Periode ATR", "type": "number", "default": 14},
            {"name": "atr_multiplier", "label": "Pengali ATR untuk Volatilitas", "type": "number", "default": 0.8, "step": 0.1},
        ]

    def analyze(self, df):
        """Metode untuk LIVE TRADING. (PERLU PENYEMPURNAAN SETELAH BACKTEST VALID)"""
        # TODO: Adaptasi logika dari analyze_df yang sudah valid untuk live trading.
        return {"signal": "HOLD", "price": df.iloc[-1]['close'] if not df.empty else None, "explanation": "Live logic needs to be implemented."}

    def analyze_df(self, df):
        """Metode untuk BACKTESTING (vectorized)."""
        donchian_period = self.params.get('donchian_period', 20)
        ema_filter_period = self.params.get('ema_filter_period', 50)
        atr_period = self.params.get('atr_period', 14)
        atr_multiplier = self.params.get('atr_multiplier', 0.8)

        # --- 1. Hitung Indikator ---
        # Donchian Channels
        df.ta.donchian(lower_length=donchian_period, upper_length=donchian_period, append=True)
        donchian_upper_col = f'DCU_{donchian_period}_{donchian_period}'
        donchian_lower_col = f'DCL_{donchian_period}_{donchian_period}'

        # EMA Trend Filter
        ema_filter_col = f'EMA_{ema_filter_period}'
        df[ema_filter_col] = ta.ema(df['close'], length=ema_filter_period)

        # ATR Volatility Filter
        atr_col = f'ATRr_{atr_period}'
        df.ta.atr(length=atr_period, append=True)

        # --- 2. Tentukan Kondisi & Filter ---
        # Kondisi Breakout: harga menembus channel dari bar sebelumnya
        breakout_up = df['close'] > df[donchian_upper_col].shift(1)
        breakout_down = df['close'] < df[donchian_lower_col].shift(1)

        # Filter Tren
        is_uptrend = df['close'] > df[ema_filter_col]
        is_downtrend = df['close'] < df[ema_filter_col]

        # Filter Volatilitas: range bar saat ini harus lebih besar dari ATR * pengali
        bar_range = df['high'] - df['low']
        is_volatile_enough = bar_range > (df[atr_col] * atr_multiplier)

        # --- 3. Hasilkan Sinyal ---
        buy_signal = is_uptrend & breakout_up & is_volatile_enough
        sell_signal = is_downtrend & breakout_down & is_volatile_enough

        df['signal'] = np.where(buy_signal, 'BUY', np.where(sell_signal, 'SELL', 'HOLD'))

        return df