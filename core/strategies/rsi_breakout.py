# /core/strategies/rsi_breakout.py
import pandas_ta as ta
from .base_strategy import BaseStrategy

class RSIBreakoutStrategy(BaseStrategy):
    name = 'RSI Breakout'
    description = 'Sinyal berdasarkan RSI yang keluar dari zona jenuh beli (overbought) atau jenuh jual (oversold).'

    @classmethod
    def get_definable_params(cls):
        """Mengembalikan parameter yang bisa diatur untuk strategi ini."""
        return [
            {"name": "rsi_period", "label": "Periode RSI", "type": "number", "default": 14},
            {"name": "overbought_level", "label": "Level Overbought", "type": "number", "default": 70},
            {"name": "oversold_level", "label": "Level Oversold", "type": "number", "default": 30}
        ]

    def analyze(self, df):
        rsi_period = self.params.get('rsi_period', 14)
        overbought_level = self.params.get('overbought_level', 70)
        oversold_level = self.params.get('oversold_level', 30)

        if df is None or df.empty or len(df) < rsi_period + 2:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup untuk RSI."}

        df['RSI'] = ta.rsi(df['close'], length=rsi_period)
        df.dropna(inplace=True)

        if len(df) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator RSI belum matang."}

        last = df.iloc[-1]
        prev = df.iloc[-2]
        price = last["close"]
        signal = "HOLD"
        explanation = f"RSI ({last['RSI']:.2f}) berada di zona netral."

        # Sinyal Beli: RSI melintasi ke atas dari level oversold
        if prev['RSI'] < oversold_level and last['RSI'] >= oversold_level:
            signal = "BUY"
            explanation = f"RSI Breakout NAIK! RSI ({last['RSI']:.2f}) melintasi ke atas level oversold ({oversold_level})."
        # Sinyal Jual: RSI melintasi ke bawah dari level overbought
        elif prev['RSI'] > overbought_level and last['RSI'] <= overbought_level:
            signal = "SELL"
            explanation = f"RSI Breakout TURUN! RSI ({last['RSI']:.2f}) melintasi ke bawah level overbought ({overbought_level})."

        return {
            "signal": signal, "price": price, "explanation": explanation,
            "RSI": last['RSI'], "Overbought_Level": overbought_level, "Oversold_Level": oversold_level
        }