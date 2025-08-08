# core/strategies/mercy_edge.py
import MetaTrader5 as mt5
import pandas_ta as ta
import numpy as np
from .base_strategy import BaseStrategy
from core.utils.mt5 import get_rates_mt5

class MercyEdgeStrategy(BaseStrategy):
    name = 'Mercy Edge (AI)'
    description = 'Strategi hybrid yang menggabungkan MACD, Stochastic, dan validasi AI untuk sinyal presisi tinggi.'

    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "macd_fast", "label": "MACD Fast", "type": "number", "default": 12},
            {"name": "macd_slow", "label": "MACD Slow", "type": "number", "default": 26},
            {"name": "macd_signal", "label": "MACD Signal", "type": "number", "default": 9},
            {"name": "stoch_k", "label": "Stoch %K", "type": "number", "default": 14},
            {"name": "stoch_d", "label": "Stoch %D", "type": "number", "default": 3},
            {"name": "stoch_smooth", "label": "Stoch Smooth", "type": "number", "default": 3},
        ]

    def analyze(self, df_h1):
        """Metode untuk LIVE TRADING."""
        # ... (logika live trading yang ada tetap di sini)
        macd_fast = self.params.get('macd_fast', 12)
        macd_slow = self.params.get('macd_slow', 26)
        macd_signal_p = self.params.get('macd_signal', 9)
        stoch_k = self.params.get('stoch_k', 14)
        stoch_d = self.params.get('stoch_d', 3)
        stoch_smooth = self.params.get('stoch_smooth', 3)

        df_d1 = get_rates_mt5(self.bot.market_for_mt5, mt5.TIMEFRAME_D1, 200)

        if df_d1 is None or df_h1 is None or len(df_d1) < 50 or len(df_h1) < 30:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup"}

        macd_hist_col = f'MACDh_{macd_fast}_{macd_slow}_{macd_signal_p}'
        stoch_k_col = f'STOCHk_{stoch_k}_{stoch_d}_{stoch_smooth}'
        stoch_d_col = f'STOCHd_{stoch_k}_{stoch_d}_{stoch_smooth}'

        df_d1.ta.macd(fast=macd_fast, slow=macd_slow, signal=macd_signal_p, append=True)
        df_h1.ta.macd(fast=macd_fast, slow=macd_slow, signal=macd_signal_p, append=True)
        df_h1.ta.stoch(k=stoch_k, d=stoch_d, smooth_k=stoch_smooth, append=True)

        df_d1.dropna(inplace=True)
        df_h1.dropna(inplace=True)

        if len(df_d1) < 1 or len(df_h1) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Data indikator belum matang."}

        last_d1 = df_d1.iloc[-1]
        last_h1 = df_h1.iloc[-1]
        prev_h1 = df_h1.iloc[-2]

        ta_suggestion = "HOLD"
        if (last_d1[macd_hist_col] > 0 and last_h1[macd_hist_col] > 0 and
            last_h1[stoch_k_col] > last_h1[stoch_d_col] and prev_h1[stoch_k_col] <= prev_h1[stoch_d_col]):
            ta_suggestion = "BUY"
        elif (last_d1[macd_hist_col] < 0 and last_h1[macd_hist_col] < 0 and
              last_h1[stoch_k_col] < last_h1[stoch_d_col] and prev_h1[stoch_k_col] >= prev_h1[stoch_d_col]):
            ta_suggestion = "SELL"

        final_signal = ta_suggestion

        return {"signal": final_signal, "price": last_h1["close"], "explanation": f"TA: {ta_suggestion}"}

    def analyze_df(self, df):
        """Metode untuk BACKTESTING. Dinonaktifkan untuk strategi ini."""
        df['signal'] = 'HOLD'
        return df