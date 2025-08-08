# /core/strategies/rsi_crossover.py
import pandas_ta as ta
import numpy as np
from .base_strategy import BaseStrategy

class RSICrossoverStrategy(BaseStrategy):
    name = 'RSI Crossover' # Nama diubah untuk mencerminkan logika baru
    description = 'Mencari sinyal momentum dari persilangan RSI dengan MA-nya, yang divalidasi oleh filter tren jangka panjang.'

    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "rsi_period", "label": "Periode RSI", "type": "number", "default": 14},
            {"name": "rsi_ma_period", "label": "Periode MA dari RSI", "type": "number", "default": 10},
            {"name": "trend_filter_period", "label": "Periode SMA Filter Tren", "type": "number", "default": 50}
        ]

    def analyze(self, df):
        """Metode untuk LIVE TRADING."""
        rsi_period = self.params.get('rsi_period', 14)
        rsi_ma_period = self.params.get('rsi_ma_period', 10)
        trend_filter_period = self.params.get('trend_filter_period', 50)

        if df is None or df.empty or len(df) < trend_filter_period + 2:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup."}

        # Hitung Indikator
        df['RSI'] = ta.rsi(df['close'], length=rsi_period)
        df['RSI_MA'] = ta.sma(df['RSI'], length=rsi_ma_period) # MA dari RSI
        df['SMA_Trend'] = ta.sma(df['close'], length=trend_filter_period)
        df.dropna(inplace=True)

        if len(df) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        prev = df.iloc[-2]
        price = last["close"]
        signal = "HOLD"
        explanation = f"RSI ({last['RSI']:.2f}) / RSI MA ({last['RSI_MA']:.2f}) - No Cross."

        # Kondisi Filter Tren
        is_uptrend = last['close'] > last['SMA_Trend']
        is_downtrend = last['close'] < last['SMA_Trend']

        # Kondisi Sinyal Crossover RSI
        rsi_bullish_cross = prev['RSI'] <= prev['RSI_MA'] and last['RSI'] > last['RSI_MA']
        rsi_bearish_cross = prev['RSI'] >= prev['RSI_MA'] and last['RSI'] < last['RSI_MA']

        if is_uptrend and rsi_bullish_cross:
            signal = "BUY"
            explanation = f"Uptrend & RSI Bullish Crossover."
        elif is_downtrend and rsi_bearish_cross:
            signal = "SELL"
            explanation = f"Downtrend & RSI Bearish Crossover."

        return {"signal": signal, "price": price, "explanation": explanation}

    def analyze_df(self, df):
        """Metode untuk BACKTESTING."""
        rsi_period = self.params.get('rsi_period', 14)
        rsi_ma_period = self.params.get('rsi_ma_period', 10)
        trend_filter_period = self.params.get('trend_filter_period', 50)

        # Hitung Indikator
        df['RSI'] = ta.rsi(df['close'], length=rsi_period)
        df['RSI_MA'] = ta.sma(df['RSI'], length=rsi_ma_period) # MA dari RSI
        df['SMA_Trend'] = ta.sma(df['close'], length=trend_filter_period)

        # Kondisi Filter Tren
        is_uptrend = df['close'] > df['SMA_Trend']
        is_downtrend = df['close'] < df['SMA_Trend']

        # Kondisi Sinyal Crossover RSI
        rsi_bullish_cross = (df['RSI'].shift(1) <= df['RSI_MA'].shift(1)) & (df['RSI'] > df['RSI_MA'])
        rsi_bearish_cross = (df['RSI'].shift(1) >= df['RSI_MA'].shift(1)) & (df['RSI'] < df['RSI_MA'])

        # Gabungkan sinyal dengan filter tren
        buy_signal = is_uptrend & rsi_bullish_cross
        sell_signal = is_downtrend & rsi_bearish_cross

        df['signal'] = np.where(buy_signal, 'BUY', np.where(sell_signal, 'SELL', 'HOLD'))

        return df
