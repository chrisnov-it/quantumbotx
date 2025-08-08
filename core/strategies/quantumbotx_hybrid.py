# /core/strategies/quantumbotx_hybrid.py
import pandas_ta as ta
import numpy as np
from .base_strategy import BaseStrategy

class QuantumBotXHybridStrategy(BaseStrategy):
    name = 'QuantumBotX Hybrid'
    description = 'Strategi eksklusif yang menggabungkan beberapa indikator untuk performa optimal, kini dengan filter tren jangka panjang.'

    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "adx_period", "label": "Periode ADX", "type": "number", "default": 14},
            {"name": "adx_threshold", "label": "Ambang ADX", "type": "number", "default": 25},
            {"name": "ma_fast_period", "label": "Periode MA Cepat", "type": "number", "default": 20},
            {"name": "ma_slow_period", "label": "Periode MA Lambat", "type": "number", "default": 50},
            {"name": "bb_length", "label": "Panjang BB", "type": "number", "default": 20},
            {"name": "bb_std", "label": "Std Dev BB", "type": "number", "default": 2.0, "step": 0.1},
            {"name": "trend_filter_period", "label": "Periode Filter Tren (SMA)", "type": "number", "default": 200}
        ]

    def analyze(self, df):
        """Metode untuk LIVE TRADING."""
        trend_filter_period = self.params.get('trend_filter_period', 200)
        if df is None or df.empty or len(df) < trend_filter_period:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup untuk filter tren."}

        adx_period = self.params.get('adx_period', 14)
        adx_threshold = self.params.get('adx_threshold', 25)
        ma_fast_period = self.params.get('ma_fast_period', 20)
        ma_slow_period = self.params.get('ma_slow_period', 50)
        bb_length = self.params.get('bb_length', 20)
        bb_std = self.params.get('bb_std', 2.0)

        bbu_col = f'BBU_{bb_length}_{bb_std:.1f}'
        bbl_col = f'BBL_{bb_length}_{bb_std:.1f}'
        trend_filter_col = f'SMA_{trend_filter_period}'

        df.ta.adx(length=adx_period, append=True)
        df[f'SMA_{ma_fast_period}'] = ta.sma(df['close'], length=ma_fast_period)
        df[f'SMA_{ma_slow_period}'] = ta.sma(df['close'], length=ma_slow_period)
        df.ta.bbands(length=bb_length, std=bb_std, append=True)
        df[trend_filter_col] = ta.sma(df['close'], length=trend_filter_period)
        
        df.dropna(inplace=True)
        
        if len(df) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        prev = df.iloc[-2]
        price = last["close"]
        signal = "HOLD"
        explanation = "Kondisi pasar tidak memenuhi syarat."

        is_uptrend = price > last[trend_filter_col]
        is_downtrend = price < last[trend_filter_col]
        adx_value = last[f'ADX_{adx_period}']

        if adx_value > adx_threshold: # Mode Trending
            if is_uptrend and prev[f'SMA_{ma_fast_period}'] <= prev[f'SMA_{ma_slow_period}'] and last[f'SMA_{ma_fast_period}'] > last[f'SMA_{ma_slow_period}']:
                signal = "BUY"
                explanation = f"Uptrend & Trending: Golden Cross."
            elif is_downtrend and prev[f'SMA_{ma_fast_period}'] >= prev[f'SMA_{ma_slow_period}'] and last[f'SMA_{ma_fast_period}'] < last[f'SMA_{ma_slow_period}']:
                signal = "SELL"
                explanation = f"Downtrend & Trending: Death Cross."
        else: # Mode Ranging
            if is_uptrend and last['low'] <= last[bbl_col]:
                signal = "BUY"
                explanation = f"Uptrend & Ranging: Oversold."
            elif is_downtrend and last['high'] >= last[bbu_col]:
                signal = "SELL"
                explanation = f"Downtrend & Ranging: Overbought."

        return {"signal": signal, "price": price, "explanation": explanation}

    def analyze_df(self, df):
        """Metode untuk BACKTESTING."""
        adx_period = self.params.get('adx_period', 14)
        adx_threshold = self.params.get('adx_threshold', 25)
        ma_fast_period = self.params.get('ma_fast_period', 20)
        ma_slow_period = self.params.get('ma_slow_period', 50)
        bb_length = self.params.get('bb_length', 20)
        bb_std = self.params.get('bb_std', 2.0)
        trend_filter_period = self.params.get('trend_filter_period', 200)

        bbu_col = f'BBU_{bb_length}_{bb_std:.1f}'
        bbl_col = f'BBL_{bb_length}_{bb_std:.1f}'
        trend_filter_col = f'SMA_{trend_filter_period}'

        df.ta.adx(length=adx_period, append=True)
        df[f'SMA_{ma_fast_period}'] = ta.sma(df['close'], length=ma_fast_period)
        df[f'SMA_{ma_slow_period}'] = ta.sma(df['close'], length=ma_slow_period)
        df.ta.bbands(length=bb_length, std=bb_std, append=True)
        df[trend_filter_col] = ta.sma(df['close'], length=trend_filter_period)

        is_trending = df[f'ADX_{adx_period}'] > adx_threshold
        is_ranging = ~is_trending
        is_uptrend = df['close'] > df[trend_filter_col]
        is_downtrend = df['close'] < df[trend_filter_col]

        golden_cross = (df[f'SMA_{ma_fast_period}'].shift(1) <= df[f'SMA_{ma_slow_period}'].shift(1)) & (df[f'SMA_{ma_fast_period}'] > df[f'SMA_{ma_slow_period}'])
        death_cross = (df[f'SMA_{ma_fast_period}'].shift(1) >= df[f'SMA_{ma_slow_period}'].shift(1)) & (df[f'SMA_{ma_fast_period}'] < df[f'SMA_{ma_slow_period}'])
        
        trending_buy = is_uptrend & is_trending & golden_cross
        trending_sell = is_downtrend & is_trending & death_cross

        ranging_buy = is_uptrend & is_ranging & (df['low'] <= df[bbl_col])
        ranging_sell = is_downtrend & is_ranging & (df['high'] >= df[bbu_col])

        df['signal'] = np.where(trending_buy | ranging_buy, 'BUY', np.where(trending_sell | ranging_sell, 'SELL', 'HOLD'))

        return df
