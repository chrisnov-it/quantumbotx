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
        rsi_val = last['RSI']
        rsi_ma_val = last['RSI_MA']

        # Market context
        is_uptrend = last['close'] > last['SMA_Trend']
        is_downtrend = last['close'] < last['SMA_Trend']
        trend_text = "uptrend" if is_uptrend else ("downtrend" if is_downtrend else "sideways")

        # RSI zone context
        if rsi_val >= 70:
            zone = "overbought"
            zone_note = "berpotensi reversal turun"
        elif rsi_val <= 30:
            zone = "oversold"
            zone_note = "berpotensi reversal naik"
        elif rsi_val >= 55:
            zone = "bullish"
            zone_note = "momentum positif"
        elif rsi_val <= 45:
            zone = "bearish"
            zone_note = "momentum negatif"
        else:
            zone = "netral"
            zone_note = "tidak ada dominasi"

        # RSI vs RSI_MA gap
        rsi_gap = rsi_val - rsi_ma_val
        gap_direction = "di atas" if rsi_gap > 0 else "di bawah"

        signal = "HOLD"
        explanation = (
            f"RSI {rsi_val:.1f} ({zone}, {zone_note}) | "
            f"RSI MA {rsi_ma_val:.1f} (gap {gap_direction} sebesar {abs(rsi_gap):.1f}) | "
            f"Tren: {trend_text}. "
            f"Menunggu persilangan RSI-MA untuk konfirmasi sinyal."
        )

        # Kondisi Sinyal Crossover RSI
        rsi_bullish_cross = prev['RSI'] <= prev['RSI_MA'] and rsi_val > rsi_ma_val
        rsi_bearish_cross = prev['RSI'] >= prev['RSI_MA'] and rsi_val < rsi_ma_val

        if is_uptrend and rsi_bullish_cross:
            signal = "BUY"
            explanation = f"BUY signal: Uptrend terkonfirmasi + RSI Golden Cross ({rsi_val:.1f} naik di atas {rsi_ma_val:.1f}). {zone_note}."
        elif is_downtrend and rsi_bearish_cross:
            signal = "SELL"
            explanation = f"SELL signal: Downtrend terkonfirmasi + RSI Death Cross ({rsi_val:.1f} turun di bawah {rsi_ma_val:.1f}). {zone_note}."

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
