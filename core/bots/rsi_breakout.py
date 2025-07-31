import pandas_ta as ta
from core.bots.base_bot import BaseStrategy

class RSIBreakoutStrategy(BaseStrategy):
    def analyze(self):
        df = self.bot.fetch_data()
        if df is None or len(df) < 20:
            return

        df['RSI'] = ta.rsi(df['close'], length=14)
        last, prev = df.iloc[-1], df.iloc[-2]

        if prev['RSI'] < 30 and last['RSI'] > 30:
            self.bot.send_signal('BUY', reason=f"RSI breakout up: {last['RSI']:.2f}")
        elif prev['RSI'] > 70 and last['RSI'] < 70:
            self.bot.send_signal('SELL', reason=f"RSI breakout down: {last['RSI']:.2f}")
