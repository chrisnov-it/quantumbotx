# /core/strategies/bollinger_reversion.py
import pandas_ta as ta
import numpy as np
from .base_strategy import BaseStrategy

class BollingerBandsStrategy(BaseStrategy):
    name = 'Bollinger Bands Reversion'
    description = 'Sinyal berdasarkan harga yang menyentuh atau melintasi batas atas atau bawah Bollinger Bands (Mean Reversion), dengan filter tren jangka panjang.'

    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "bb_length", "label": "Panjang BB", "type": "number", "default": 20},
            {"name": "bb_std", "label": "Standar Deviasi BB", "type": "number", "default": 2.0, "step": 0.1},
            {"name": "trend_filter_period", "label": "Periode Filter Tren (SMA)", "type": "number", "default": 200}
        ]

    def analyze(self, df):
        """Metode untuk LIVE TRADING."""
        bb_length = self.params.get('bb_length', 20)
        trend_filter_period = self.params.get('trend_filter_period', 200)

        if df is None or df.empty or len(df) < trend_filter_period:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup untuk filter tren."}

        bb_std = self.params.get('bb_std', 2.0)
        bbu_col = f'BBU_{bb_length}_{bb_std:.1f}'
        bbl_col = f'BBL_{bb_length}_{bb_std:.1f}'
        trend_filter_col = f'SMA_{trend_filter_period}'

        df.ta.bbands(length=bb_length, std=bb_std, append=True)
        df[trend_filter_col] = ta.sma(df['close'], length=trend_filter_period)
        df.dropna(inplace=True)
        
        if df.empty:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        price = last["close"]
        signal = "HOLD"
        explanation = f"Harga di dalam Bands atau tren tidak sesuai."
        
        is_uptrend = price > last[trend_filter_col]
        is_downtrend = price < last[trend_filter_col]

        if is_uptrend and last['low'] <= last[bbl_col]:
            signal = "BUY"
            explanation = f"Uptrend & Oversold: Harga menyentuh Band Bawah."
        elif is_downtrend and last['high'] >= last[bbu_col]:
            signal = "SELL"
            explanation = f"Downtrend & Overbought: Harga menyentuh Band Atas."

        return {"signal": signal, "price": price, "explanation": explanation}

    def analyze_df(self, df):
        """Metode untuk BACKTESTING."""
        bb_length = self.params.get('bb_length', 20)
        bb_std = self.params.get('bb_std', 2.0)
        trend_filter_period = self.params.get('trend_filter_period', 200)

        bbu_col = f'BBU_{bb_length}_{bb_std:.1f}'
        bbl_col = f'BBL_{bb_length}_{bb_std:.1f}'
        trend_filter_col = f'SMA_{trend_filter_period}'

        df.ta.bbands(length=bb_length, std=bb_std, append=True)
        df[trend_filter_col] = ta.sma(df['close'], length=trend_filter_period)

        is_uptrend = df['close'] > df[trend_filter_col]
        is_downtrend = df['close'] < df[trend_filter_col]

        buy_signal = is_uptrend & (df['low'] <= df[bbl_col])
        sell_signal = is_downtrend & (df['high'] >= df[bbu_col])

        df['signal'] = np.where(buy_signal, 'BUY', np.where(sell_signal, 'SELL', 'HOLD'))

        return df