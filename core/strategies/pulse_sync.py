# core/strategies/pulse_sync.py
import pandas_ta as ta
from .base_strategy import BaseStrategy

class PulseSyncStrategy(BaseStrategy):
    name = 'Pulse Sync (AI)'
    description = 'Menggunakan AI untuk menganalisis momentum harga berdasarkan Simple Moving Average (SMA).'

    def analyze(self, df):
        if df is None or df.empty or len(df) < 30:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup"}

        df['SMA21'] = ta.sma(df['close'], length=21)
        df.dropna(inplace=True)

        if len(df) < 1:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        price = last["close"]

        # AI functionality is temporarily disabled.
        signal = "HOLD"
        explanation = "AI functionality is currently disabled for performance reasons."

        analysis_data = {
            "signal": signal,
            "price": price,
            "explanation": explanation,
            "SMA_21": last.get('SMA21'),
        }
        return analysis_data
