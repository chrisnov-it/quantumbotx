# core/strategies/mercy_edge.py
import MetaTrader5 as mt5
import pandas_ta as ta
from .base_strategy import BaseStrategy
from core.utils.mt5 import get_rates_from_mt5

class MercyEdgeStrategy(BaseStrategy):
    name = 'Mercy Edge (AI)'
    description = 'Strategi hybrid yang menggabungkan MACD, Stochastic, dan validasi AI untuk sinyal presisi tinggi.'

    def analyze(self):
        df_d1 = get_rates_from_mt5(self.bot.market_for_mt5, mt5.TIMEFRAME_D1, 200)
        df_h1 = get_rates_from_mt5(self.bot.market_for_mt5, mt5.TIMEFRAME_H1, 100)

        if df_d1 is None or df_h1 is None or len(df_d1) < 50 or len(df_h1) < 30:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup"}

        macd_d1 = ta.macd(df_d1['close']).rename(columns={'MACDh_12_26_9': 'hist_d1'})
        macd_h1 = ta.macd(df_h1['close']).rename(columns={'MACDh_12_26_9': 'hist_h1'})
        stoch = ta.stoch(df_h1['high'], df_h1['low'], df_h1['close'])

        df_d1 = df_d1.join(macd_d1).dropna()
        df_h1 = df_h1.join(macd_h1)
        df_h1['stoch_k'] = stoch.iloc[:, 0]
        df_h1['stoch_d'] = stoch.iloc[:, 1]
        df_h1 = df_h1.dropna()

        if len(df_d1) < 1 or len(df_h1) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Data indikator belum matang."}

        last_d1 = df_d1.iloc[-1]
        last_h1 = df_h1.iloc[-1]
        prev_h1 = df_h1.iloc[-2]

        ta_suggestion = "HOLD"
        if (
            last_d1['hist_d1'] > 0 and last_h1['hist_h1'] > 0 and
            last_h1['stoch_k'] > last_h1['stoch_d'] and
            prev_h1['stoch_k'] <= prev_h1['stoch_d']
        ):
            ta_suggestion = "BUY"
        elif (
            last_d1['hist_d1'] < 0 and last_h1['hist_h1'] < 0 and
            last_h1['stoch_k'] < last_h1['stoch_d'] and
            prev_h1['stoch_k'] >= prev_h1['stoch_d']
        ):
            ta_suggestion = "SELL"

        # AI functionality is temporarily disabled.
        final_signal = ta_suggestion

        return {
            "signal": final_signal, "price": last_h1["close"],
            "explanation": f"TA: {ta_suggestion} (AI disabled)",
            "D1_MACDh": last_d1['hist_d1'], "H1_MACDh": last_h1['hist_h1'],
            "H1_STOCHk": last_h1['stoch_k'], "H1_STOCHd": last_h1['stoch_d']
        }
