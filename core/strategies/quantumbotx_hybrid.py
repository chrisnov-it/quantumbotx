# /core/strategies/quantumbotx_hybrid.py
import pandas_ta as ta
import MetaTrader5 as mt5
from .base_strategy import BaseStrategy
from core.data.fetch import get_rates

class QuantumBotXHybridStrategy(BaseStrategy):
    name = 'QuantumBotX Hybrid'
    description = 'Strategi eksklusif yang menggabungkan beberapa indikator untuk performa optimal di berbagai kondisi pasar.'

    @classmethod
    def get_definable_params(cls):
        """Mengembalikan parameter yang bisa diatur untuk strategi ini."""
        return [
            {"name": "adx_period", "label": "Periode ADX", "type": "number", "default": 14},
            {"name": "adx_threshold", "label": "Ambang ADX", "type": "number", "default": 25},
            {"name": "ma_fast_period", "label": "Periode MA Cepat", "type": "number", "default": 20},
            {"name": "ma_slow_period", "label": "Periode MA Lambat", "type": "number", "default": 50},
            {"name": "bb_length", "label": "Panjang BB", "type": "number", "default": 20},
            {"name": "bb_std", "label": "Std Dev BB", "type": "number", "default": 2.0, "step": 0.1}
        ]

    def analyze(self):
        """
        Menganalisis pasar menggunakan strategi Hybrid yang adaptif.
        Menggunakan MA Crossover saat trending (ADX > 25) dan
        Bollinger Bands saat ranging (ADX < 25).
        """
        tf_const = self.bot.tf_map.get(self.bot.timeframe, mt5.TIMEFRAME_H1)
        
        # PERBAIKAN: Minta lebih banyak data. Indikator kompleks seperti ADX
        # butuh "pemanasan" lebih lama. 100 bar adalah angka yang lebih aman.
        data_points_to_fetch = 100
        required_data_points = 51 # Tetap butuh minimal 51 untuk SMA(50)
        df = get_rates(self.bot.market_for_mt5, tf_const, data_points_to_fetch)

        if df is None or df.empty or len(df) < required_data_points:
            return {"signal": "HOLD", "price": None, "explanation": f"Data tidak cukup ({len(df) if df is not None else 0}/{required_data_points} bar)."}

        # --- Ambil Parameter Dinamis ---
        adx_period = self.params.get('adx_period', 14)
        adx_threshold = self.params.get('adx_threshold', 25)
        ma_fast_period = self.params.get('ma_fast_period', 20)
        ma_slow_period = self.params.get('ma_slow_period', 50)
        bb_length = self.params.get('bb_length', 20)
        bb_std = self.params.get('bb_std', 2.0)

        # PERBAIKAN: Paksa format float dengan satu desimal pada nama kolom
        # untuk mencegah KeyError (misal: 'BBL_20_2' vs 'BBL_20_2.0')
        bbu_col = f'BBU_{bb_length}_{bb_std:.1f}'
        bbl_col = f'BBL_{bb_length}_{bb_std:.1f}'

        # --- Hitung SEMUA Indikator yang Dibutuhkan ---
        df.ta.adx(length=adx_period, append=True)
        df[f'SMA_{ma_fast_period}'] = ta.sma(df['close'], length=ma_fast_period)
        df[f'SMA_{ma_slow_period}'] = ta.sma(df['close'], length=ma_slow_period)
        df.ta.bbands(length=bb_length, std=bb_std, append=True)
        
        # Simpan panjang sebelum dropna untuk debugging
        len_before_drop = len(df)
        df.dropna(inplace=True)
        
        if len(df) < 2:
            return {"signal": "HOLD", "price": None, "explanation": f"Indikator belum matang setelah dropna (dari {len_before_drop} menjadi {len(df)} bar)."}

        last = df.iloc[-1]
        prev = df.iloc[-2]
        price = last["close"]
        signal = "HOLD"
        explanation = "Kondisi pasar tidak memenuhi syarat."
        market_mode = "N/A"

        # --- Logika "Wasit Pasar" (ADX) ---
        adx_value = last[f'ADX_{adx_period}']

        # KONDISI 1: PASAR TRENDING
        if adx_value > adx_threshold:
            market_mode = "Trending"
            explanation = f"Mode: {market_mode} (ADX {adx_value:.1f}). Menunggu Crossover."
            if prev[f'SMA_{ma_fast_period}'] <= prev[f'SMA_{ma_slow_period}'] and last[f'SMA_{ma_fast_period}'] > last[f'SMA_{ma_slow_period}']:
                signal = "BUY"
                explanation = f"Mode: {market_mode} (ADX {adx_value:.1f}). Sinyal: Golden Cross."
            elif prev[f'SMA_{ma_fast_period}'] >= prev[f'SMA_{ma_slow_period}'] and last[f'SMA_{ma_fast_period}'] < last[f'SMA_{ma_slow_period}']:
                signal = "SELL"
                explanation = f"Mode: {market_mode} (ADX {adx_value:.1f}). Sinyal: Death Cross."
                
        # KONDISI 2: PASAR SIDEWAYS
        elif adx_value < adx_threshold:
            market_mode = "Ranging"
            explanation = f"Mode: {market_mode} (ADX {adx_value:.1f}). Menunggu pantulan Bands."
            if last['low'] <= last[bbl_col]:
                signal = "BUY"
                explanation = f"Mode: {market_mode} (ADX {adx_value:.1f}). Sinyal: Oversold di Band Bawah."
            elif last['high'] >= last[bbu_col]:
                signal = "SELL"
                explanation = f"Mode: {market_mode} (ADX {adx_value:.1f}). Sinyal: Overbought di Band Atas."

        analysis_data = {
            "signal": signal,
            "price": price,
            "explanation": explanation,
            "Market_Mode": market_mode,
            f"ADX_{adx_period}": adx_value,
            f"SMA_{ma_fast_period}": last.get(f'SMA_{ma_fast_period}'),
            f"SMA_{ma_slow_period}": last.get(f'SMA_{ma_slow_period}'),
        }
        return analysis_data