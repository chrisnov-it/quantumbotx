# /core/strategies/ma_crossover.py
import pandas_ta as ta
import MetaTrader5 as mt5
from .base_strategy import BaseStrategy
from core.data.fetch import get_rates

class MACrossoverStrategy(BaseStrategy):
    name = 'Moving Average Crossover'
    description = 'Sinyal berdasarkan persilangan antara dua Moving Averages (misal, 20 & 50). Cocok untuk pasar trending.'

    def analyze(self):
        """
        Menganalisis pasar menggunakan strategi Moving Average Crossover (20/50).
        Ideal untuk pasar dengan tren kuat seperti XAUUSD.
        """
        # Mengakses properti dari instance bot yang tersimpan
        tf_const = self.bot.tf_map.get(self.bot.timeframe, mt5.TIMEFRAME_H1)
        
        # Butuh data yang cukup untuk MA 50
        df = get_rates(self.bot.market_for_mt5, tf_const, 52)

        if df is None or df.empty or len(df) < 51:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup untuk MA Crossover."}

        # --- Hitung Indikator ---
        df["ma_fast"] = ta.sma(df["close"], length=20)
        df["ma_slow"] = ta.sma(df["close"], length=50)
        df.dropna(inplace=True)
        
        if len(df) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        prev = df.iloc[-2]

        price = last["close"]
        signal = "HOLD"
        explanation = f"MA(20): {last['ma_fast']:.2f}, MA(50): {last['ma_slow']:.2f}. Tidak ada sinyal."

        # --- Logika Sinyal ---
        # Golden Cross (Sinyal Beli)
        if prev["ma_fast"] <= prev["ma_slow"] and last["ma_fast"] > last["ma_slow"]:
            signal = "BUY"
            explanation = f"Golden Cross: MA(20) [{last['ma_fast']:.2f}] memotong ke atas MA(50) [{last['ma_slow']:.2f}]"
        # Death Cross (Sinyal Jual)
        elif prev["ma_fast"] >= prev["ma_slow"] and last["ma_fast"] < last["ma_slow"]:
            signal = "SELL"
            explanation = f"Death Cross: MA(20) [{last['ma_fast']:.2f}] memotong ke bawah MA(50) [{last['ma_slow']:.2f}]"

        return {
            "signal": signal, "price": price, "explanation": explanation,
            "ma_fast": last['ma_fast'], "ma_slow": last['ma_slow']
        }