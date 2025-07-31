import pandas_ta as ta
from core.bots.base_bot import BaseStrategy

class MACrossoverStrategy(BaseStrategy):
    def analyze(self):
        df = self.bot.fetch_data()
        if df is None or len(df) < 50:
            return

        df['SMA_fast'] = ta.sma(df['close'], length=20)
        df['SMA_slow'] = ta.sma(df['close'], length=50)
        last, prev = df.iloc[-1], df.iloc[-2]

        if prev['SMA_fast'] <= prev['SMA_slow'] and last['SMA_fast'] > last['SMA_slow']:
            self.bot.send_signal('BUY', reason="Golden Cross MA detected.")
        elif prev['SMA_fast'] >= prev['SMA_slow'] and last['SMA_fast'] < last['SMA_slow']:
            self.bot.send_signal('SELL', reason="Death Cross MA detected.")
