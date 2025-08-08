# /core/strategies/rsi_breakout.py
import pandas_ta as ta
import numpy as np
from .base_strategy import BaseStrategy

class RSIBreakoutStrategy(BaseStrategy):
    name = 'RSI Breakout'
    description = 'Sinyal berdasarkan RSI yang keluar dari zona jenuh beli (overbought) atau jenuh jual (oversold).'

    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "rsi_period", "label": "Periode RSI", "type": "number", "default": 14},
            {"name": "overbought_level", "label": "Level Overbought", "type": "number", "default": 70},
            {"name": "oversold_level", "label": "Level Oversold", "type": "number", "default": 30}
        ]

    def analyze(self, df):
        """Metode untuk LIVE TRADING."""
        rsi_period = self.params.get('rsi_period', 14)
        overbought_level = self.params.get('overbought_level', 70)
        oversold_level = self.params.get('oversold_level', 30)

        if df is None or df.empty or len(df) < rsi_period + 2:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup."}

        df['RSI'] = ta.rsi(df['close'], length=rsi_period)
        df.dropna(inplace=True)

        if len(df) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        prev = df.iloc[-2]
        price = last["close"]
        signal = "HOLD"
        explanation = f"RSI ({last['RSI']:.2f}) netral."

        if prev['RSI'] < oversold_level and last['RSI'] >= oversold_level:
            signal = "BUY"
            explanation = f"RSI Breakout NAIK!"
        elif prev['RSI'] > overbought_level and last['RSI'] <= overbought_level:
            signal = "SELL"
            explanation = f"RSI Breakout TURUN!"

        return {"signal": signal, "price": price, "explanation": explanation}

    def analyze_df(self, df):
        """Metode untuk BACKTESTING."""
        rsi_period = self.params.get('rsi_period', 14)
        overbought_level = self.params.get('overbought_level', 70)
        oversold_level = self.params.get('oversold_level', 30)

        df['RSI'] = ta.rsi(df['close'], length=rsi_period)

        buy_signal = (df['RSI'].shift(1) < oversold_level) & (df['RSI'] >= oversold_level)
        sell_signal = (df['RSI'].shift(1) > overbought_level) & (df['RSI'] <= overbought_level)

        df['signal'] = np.where(buy_signal, 'BUY', np.where(sell_signal, 'SELL', 'HOLD'))

        return df
