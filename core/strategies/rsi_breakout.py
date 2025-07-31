# core/strategies/rsi_breakout.py
import pandas_ta as ta
import MetaTrader5 as mt5
from .base_strategy import BaseStrategy
from core.utils.mt5 import get_rates_from_mt5

class RSIBreakoutStrategy(BaseStrategy):
    name = 'RSI Breakout'
    description = 'Sinyal berdasarkan level jenuh beli (overbought) dan jenuh jual (oversold) dari Relative Strength Index (RSI).'

    def analyze(self):
        tf_const = self.bot.tf_map.get(self.bot.timeframe, mt5.TIMEFRAME_H1)
        df = get_rates_from_mt5(self.bot.market_for_mt5, tf_const, 100)

        if df is None or df.empty or len(df) < 20:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup"}

        df["RSI"] = ta.rsi(df["close"], length=14)
        df.dropna(inplace=True)

        if len(df) < 1:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        price = last["close"]
        rsi = last["RSI"]

        signal = "HOLD"
        explanation = f"RSI saat ini {rsi:.2f}, dalam zona netral"

        if rsi > 70:
            signal = "SELL"
            explanation = f"RSI {rsi:.2f} > 70 (overbought)"
        elif rsi < 30:
            signal = "BUY"
            explanation = f"RSI {rsi:.2f} < 30 (oversold)"

        return {
            "signal": signal, "price": price, "explanation": explanation,
            "rsi": rsi
        }
