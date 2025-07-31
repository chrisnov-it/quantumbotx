# /core/strategies/bollinger_bands.py
import MetaTrader5 as mt5
from .base_strategy import BaseStrategy
from core.data.fetch import get_rates

class BollingerBandsStrategy(BaseStrategy):
    name = 'Bollinger Bands Reversion'
    description = 'Sinyal berdasarkan harga yang menyentuh atau melintasi batas atas atau bawah Bollinger Bands (Mean Reversion).'

    def analyze(self):
        """
        Menganalisis pasar menggunakan strategi Bollinger Bands® Mean Reversion.
        Ideal untuk pasar ranging yang volatil seperti EURUSD.
        """
        tf_const = self.bot.tf_map.get(self.bot.timeframe, mt5.TIMEFRAME_H1)
        
        # Butuh data yang cukup untuk BBands(20)
        df = get_rates(self.bot.market_for_mt5, tf_const, 21)

        if df is None or df.empty or len(df) < 21:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup untuk Bollinger Bands."}

        # --- Hitung Indikator ---
        df.ta.bbands(length=20, std=2.0, append=True)
        df.dropna(inplace=True)
        
        if len(df) < 1:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        price = last["close"]
        signal = "HOLD"
        explanation = f"Harga [{price:.4f}] di dalam Bands. Tidak ada sinyal."

        # --- Logika Sinyal ---
        # Sinyal Beli: Harga menyentuh atau menembus Band Bawah
        if last['low'] <= last['BBL_20_2.0']:
            signal = "BUY"
            explanation = f"Oversold: Harga [{last['low']:.4f}] menyentuh Band Bawah [{last['BBL_20_2.0']:.4f}]"
        # Sinyal Jual: Harga menyentuh atau menembus Band Atas
        elif last['high'] >= last['BBU_20_2.0']:
            signal = "SELL"
            explanation = f"Overbought: Harga [{last['high']:.4f}] menyentuh Band Atas [{last['BBU_20_2.0']:.4f}]"

        analysis_data = {
            "signal": signal,
            "price": price,
            "explanation": explanation,
            "BB_Upper": last.get('BBU_20_2.0'),
            "BB_Middle": last.get('BBM_20_2.0'),
            "BB_Lower": last.get('BBL_20_2.0'),
        }
        return analysis_data