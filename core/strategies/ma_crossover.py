# /core/strategies/ma_crossover.py
import pandas_ta as ta
import MetaTrader5 as mt5
from .base_strategy import BaseStrategy
from core.data.fetch import get_rates

class MACrossoverStrategy(BaseStrategy):
    name = 'Moving Average Crossover'
    description = 'Sinyal berdasarkan persilangan antara dua Moving Averages (misal, 20 & 50). Cocok untuk pasar trending.'

    @classmethod
    def get_definable_params(cls):
        """Mengembalikan parameter yang bisa diatur untuk strategi ini."""
        return [
            {"name": "fast_period", "label": "Periode MA Cepat", "type": "number", "default": 20},
            {"name": "slow_period", "label": "Periode MA Lambat", "type": "number", "default": 50}
        ]

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
        # Gunakan parameter dinamis, dengan fallback ke nilai default
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

        # --- Logika Sinyal ---
        # Golden Cross (Sinyal Beli)
        if prev["ma_fast"] <= prev["ma_slow"] and last["ma_fast"] > last["ma_slow"]:
            signal = "BUY"
            explanation = f"Golden Cross: MA({fast_period}) [{last['ma_fast']:.2f}] memotong ke atas MA({slow_period}) [{last['ma_slow']:.2f}]"
        # Death Cross (Sinyal Jual)
        elif prev["ma_fast"] >= prev["ma_slow"] and last["ma_fast"] < last["ma_slow"]:
            signal = "SELL"
            explanation = f"Death Cross: MA({fast_period}) [{last['ma_fast']:.2f}] memotong ke bawah MA({slow_period}) [{last['ma_slow']:.2f}]"

        return {
            "signal": signal, "price": price, "explanation": explanation,
            "ma_fast": last['ma_fast'], "ma_slow": last['ma_slow']
        }