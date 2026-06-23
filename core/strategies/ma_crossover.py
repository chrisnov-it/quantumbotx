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

        # Market context: price position vs MAs
        price_vs_fast = price - last['ma_fast']
        price_vs_slow = price - last['ma_slow']
        ma_gap = last['ma_fast'] - last['ma_slow']
        ma_gap_pct = abs(ma_gap) / last['ma_slow'] * 100

        # Determine trend strength from MA separation
        if ma_gap > 0:
            trend_side = "bullish"
            if ma_gap_pct > 0.5:
                trend_strength = "kuat"
            elif ma_gap_pct > 0.2:
                trend_strength = "moderat"
            else:
                trend_strength = "lemah"
        else:
            trend_side = "bearish"
            if ma_gap_pct > 0.5:
                trend_strength = "kuat"
            elif ma_gap_pct > 0.2:
                trend_strength = "moderat"
            else:
                trend_strength = "lemah"

        # Price position context
        if price_vs_fast > 0 and price_vs_slow > 0:
            position = "di atas kedua MA"
        elif price_vs_fast < 0 and price_vs_slow < 0:
            position = "di bawah kedua MA"
        elif price_vs_fast > 0 and price_vs_slow < 0:
            position = "di antara MA (sideways)"
        else:
            position = "di antara MA (sideways)"

        signal = "HOLD"
        explanation = (
            f"Tren {trend_side} {trend_strength} | "
            f"MA({fast_period}) {last['ma_fast']:.5f}, MA({slow_period}) {last['ma_slow']:.5f} | "
            f"Harga {position}. "
            f"Menunggu persilangan MA untuk sinyal entry."
        )

        if prev["ma_fast"] <= prev["ma_slow"] and last["ma_fast"] > last["ma_slow"]:
            signal = "BUY"
            explanation = f"Golden Cross: MA({fast_period})={last['ma_fast']:.5f} memotong ke atas MA({slow_period})={last['ma_slow']:.5f}. Tren {trend_side} {trend_strength}."
        elif prev["ma_fast"] >= prev["ma_slow"] and last["ma_fast"] < last["ma_slow"]:
            signal = "SELL"
            explanation = f"Death Cross: MA({fast_period})={last['ma_fast']:.5f} memotong ke bawah MA({slow_period})={last['ma_slow']:.5f}. Tren {trend_side} {trend_strength}."

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