# /core/strategies/ma_crossover.py
import pandas_ta as ta
import numpy as np
from .base_strategy import BaseStrategy

class MACrossoverStrategy(BaseStrategy):
    name = 'Moving Average Crossover'
    description = 'Sinyal berdasarkan persilangan antara dua Moving Averages (misal, 20 & 50). Cocok untuk pasar trending.'

    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "fast_period", "label": "Periode MA Cepat", "type": "number", "default": 20},
            {"name": "slow_period", "label": "Periode MA Lambat", "type": "number", "default": 50}
        ]

    def analyze(self, df):
        """Metode untuk LIVE TRADING. Menganalisis beberapa bar data terakhir."""
        if df is None or df.empty or len(df) < self.params.get('slow_period', 50) + 1:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup."}

        fast_period = self.params.get('fast_period', 20)
        slow_period = self.params.get('slow_period', 50)

        df["ma_fast"] = ta.sma(df["close"], length=fast_period)
        df["ma_slow"] = ta.sma(df["close"], length=slow_period)
        df.dropna(inplace=True)
        
        if len(df) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        prev = df.iloc[-2]

        price = last["close"]
        signal = "HOLD"
        explanation = f"MA({fast_period}): {last['ma_fast']:.2f}, MA({slow_period}): {last['ma_slow']:.2f}. Tidak ada sinyal."

        if prev["ma_fast"] <= prev["ma_slow"] and last["ma_fast"] > last["ma_slow"]:
            signal = "BUY"
            explanation = f"Golden Cross: MA({fast_period}) memotong ke atas MA({slow_period})"
        elif prev["ma_fast"] >= prev["ma_slow"] and last["ma_fast"] < last["ma_slow"]:
            signal = "SELL"
            explanation = f"Death Cross: MA({fast_period}) memotong ke bawah MA({slow_period})"

        return {"signal": signal, "price": price, "explanation": explanation}

    def analyze_df(self, df):
        """Metode untuk BACKTESTING. Menganalisis seluruh DataFrame."""
        fast_period = self.params.get('fast_period', 20)
        slow_period = self.params.get('slow_period', 50)

        df["ma_fast"] = ta.sma(df["close"], length=fast_period)
        df["ma_slow"] = ta.sma(df["close"], length=slow_period)
        
        golden_cross = (df["ma_fast"].shift(1) <= df["ma_slow"].shift(1)) & (df["ma_fast"] > df["ma_slow"])
        death_cross = (df["ma_fast"].shift(1) >= df["ma_slow"].shift(1)) & (df["ma_fast"] < df["ma_slow"])

        df['signal'] = np.where(golden_cross, 'BUY', np.where(death_cross, 'SELL', 'HOLD'))
        
        return df