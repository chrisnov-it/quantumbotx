# /core/strategies/quantumbotx_hybrid.py
import pandas_ta as ta
import MetaTrader5 as mt5
from .base_strategy import BaseStrategy
from core.data.fetch import get_rates

class QuantumBotXHybridStrategy(BaseStrategy):
    name = 'QuantumBotX Hybrid'
    description = 'Strategi eksklusif yang menggabungkan beberapa indikator untuk performa optimal di berbagai kondisi pasar.'

    def analyze(self):
        """
        Menganalisis pasar menggunakan strategi Hybrid yang adaptif.
        Menggunakan MA Crossover saat trending (ADX > 25) dan
        Bollinger Bands saat ranging (ADX < 25).
        """
        tf_const = self.bot.tf_map.get(self.bot.timeframe, mt5.TIMEFRAME_H1)
        
        # Butuh data yang cukup untuk indikator terpanjang (SMA 50)
        df = get_rates(self.bot.market_for_mt5, tf_const, 52)

        if df is None or df.empty or len(df) < 51:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup untuk Hybrid."}

        # --- Hitung SEMUA Indikator yang Dibutuhkan ---
        df.ta.adx(length=14, append=True)
        df['SMA_20'] = ta.sma(df['close'], length=20)
        df['SMA_50'] = ta.sma(df['close'], length=50)
        df.ta.bbands(length=20, std=2.0, append=True)
        df.dropna(inplace=True)
        
        if len(df) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        prev = df.iloc[-2]
        price = last["close"]
        signal = "HOLD"
        explanation = "Kondisi pasar tidak memenuhi syarat."
        market_mode = "N/A"

        # --- Logika "Wasit Pasar" (ADX) ---
        adx_value = last['ADX_14']

        # KONDISI 1: PASAR TRENDING
        if adx_value > 25:
            market_mode = "Trending"
            explanation = f"Mode: {market_mode} (ADX {adx_value:.1f}). Menunggu Crossover."
            if prev['SMA_20'] <= prev['SMA_50'] and last['SMA_20'] > last['SMA_50']:
                signal = "BUY"
                explanation = f"Mode: {market_mode} (ADX {adx_value:.1f}). Sinyal: Golden Cross."
            elif prev['SMA_20'] >= prev['SMA_50'] and last['SMA_20'] < last['SMA_50']:
                signal = "SELL"
                explanation = f"Mode: {market_mode} (ADX {adx_value:.1f}). Sinyal: Death Cross."
                
        # KONDISI 2: PASAR SIDEWAYS
        elif adx_value < 25:
            market_mode = "Ranging"
            explanation = f"Mode: {market_mode} (ADX {adx_value:.1f}). Menunggu pantulan Bands."
            if last['low'] <= last['BBL_20_2.0']:
                signal = "BUY"
                explanation = f"Mode: {market_mode} (ADX {adx_value:.1f}). Sinyal: Oversold di Band Bawah."
            elif last['high'] >= last['BBU_20_2.0']:
                signal = "SELL"
                explanation = f"Mode: {market_mode} (ADX {adx_value:.1f}). Sinyal: Overbought di Band Atas."

        analysis_data = {
            "signal": signal,
            "price": price,
            "explanation": explanation,
            "Market_Mode": market_mode,
            "ADX_14": adx_value,
            "SMA_20": last.get('SMA_20'),
            "SMA_50": last.get('SMA_50'),
        }
        return analysis_data