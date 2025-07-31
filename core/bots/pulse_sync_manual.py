# core/bots/pulse_sync.py
import pandas_ta as ta
from core.bots.base_bot import BaseStrategy
import MetaTrader5 as mt5

class PulseSyncStrategy(BaseStrategy):
    def analyze(self):
        self.bot.market.replace('/', '')
        df_d1 = self.bot.fetch_data(mt5.TIMEFRAME_D1, 200)
        df_h1 = self.bot.fetch_data(mt5.TIMEFRAME_H1, 100)

        if df_d1 is None or df_h1 is None or len(df_d1) < 50 or len(df_h1) < 30:
            return

        macd_d1 = ta.macd(df_d1['close']).rename(columns={'MACDh_12_26_9': 'hist_d1'})
        macd_h1 = ta.macd(df_h1['close']).rename(columns={'MACDh_12_26_9': 'hist_h1'})
        stoch = ta.stoch(df_h1['high'], df_h1['low'], df_h1['close'])

        df_d1 = df_d1.join(macd_d1)
        df_h1 = df_h1.join(macd_h1)
        df_h1['stoch_k'] = stoch.iloc[:, 0]
        df_h1['stoch_d'] = stoch.iloc[:, 1]

        last_d1 = df_d1.iloc[-1]
        last_h1 = df_h1.iloc[-1]
        prev_h1 = df_h1.iloc[-2]

        if (
            last_d1['hist_d1'] > 0 and last_h1['hist_h1'] > 0 and
            last_h1['stoch_k'] > last_h1['stoch_d'] and
            prev_h1['stoch_k'] <= prev_h1['stoch_d']
        ):
            self.bot.send_signal('BUY', reason="All bullish filters met (MACD D1 + H1 + STOCH)")
        elif (
            last_d1['hist_d1'] < 0 and last_h1['hist_h1'] < 0 and
            last_h1['stoch_k'] < last_h1['stoch_d'] and
            prev_h1['stoch_k'] >= prev_h1['stoch_d']
        ):
            self.bot.send_signal('SELL', reason="All bearish filters met (MACD D1 + H1 + STOCH)")
