# core/strategies/pulse_sync.py
import pandas_ta as ta
import numpy as np
from .base_strategy import BaseStrategy

class PulseSyncStrategy(BaseStrategy):
    name = 'Pulse Sync (AI)'
    description = 'Menggunakan AI untuk menganalisis momentum harga berdasarkan Simple Moving Average (SMA).'

    def analyze(self, df):
        """Metode untuk LIVE TRADING."""
        if df is None or df.empty or len(df) < 30:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup"}

        df['SMA21'] = ta.sma(df['close'], length=21)
        df.dropna(inplace=True)

        if len(df) < 1:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        price = last["close"]

        signal = "HOLD"
        explanation = "AI functionality is currently disabled."

        return {"signal": signal, "price": price, "explanation": explanation}

    def analyze_df(self, df):
        """Metode untuk BACKTESTING. Dinonaktifkan untuk strategi ini."""
        df['signal'] = 'HOLD'
        return df