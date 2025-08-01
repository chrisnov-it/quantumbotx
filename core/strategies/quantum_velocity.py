# d:\dev\quantumbotx\core\strategies\quantum_velocity.py

import pandas_ta as ta
import numpy as np
import MetaTrader5 as mt5
from .base_strategy import BaseStrategy
from core.data.fetch import get_rates

class QuantumVelocityStrategy(BaseStrategy):
    name = 'Quantum Velocity'
    description = 'Menggabungkan filter tren jangka panjang (EMA 200) dengan pemicu volatilitas (Bollinger Squeeze Breakout).'

    @classmethod
    def get_definable_params(cls):
        """Mengembalikan parameter yang bisa diatur untuk strategi ini."""
        return [
            {"name": "ema_period", "label": "Periode EMA Tren", "type": "number", "default": 200},
            {"name": "bb_length", "label": "Panjang BB", "type": "number", "default": 20},
            {"name": "bb_std", "label": "Std Dev BB", "type": "number", "default": 2.0, "step": 0.1},
            {"name": "squeeze_window", "label": "Window Squeeze", "type": "number", "default": 10},
            {"name": "squeeze_factor", "label": "Faktor Squeeze", "type": "number", "default": 0.7, "step": 0.1},
        ]

    def analyze(self):
        """
        Menganalisis pasar dengan filter tren jangka panjang dan pemicu breakout.
        """
        tf_const = self.bot.tf_map.get(self.bot.timeframe, mt5.TIMEFRAME_H1)
        
        # Butuh data yang cukup untuk EMA 200
        df = get_rates(self.bot.market_for_mt5, tf_const, 250)

        if df is None or df.empty or len(df) < 201:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup untuk Quantum Velocity."}

        # --- Ambil Parameter ---
        ema_period = self.params.get('ema_period', 200)
        bb_length = self.params.get('bb_length', 20)
        bb_std = self.params.get('bb_std', 2.0)
        squeeze_window = self.params.get('squeeze_window', 10)
        squeeze_factor = self.params.get('squeeze_factor', 0.7)

        # --- Hitung Indikator ---
        df[f'EMA_{ema_period}'] = ta.ema(df['close'], length=ema_period)
        
        bbu_col = f'BBU_{bb_length}_{bb_std:.1f}'
        bbm_col = f'BBM_{bb_length}_{bb_std:.1f}'
        bbl_col = f'BBL_{bb_length}_{bb_std:.1f}'

        df.ta.bbands(length=bb_length, std=bb_std, append=True)
        df['BB_BANDWIDTH'] = np.where(df[bbm_col] != 0, (df[bbu_col] - df[bbl_col]) / df[bbm_col] * 100, 0)
        df['AVG_BANDWIDTH'] = df['BB_BANDWIDTH'].rolling(window=squeeze_window).mean()
        df['SQUEEZE_LEVEL'] = df['AVG_BANDWIDTH'] * squeeze_factor
        df['SQUEEZE'] = df['BB_BANDWIDTH'] < df['SQUEEZE_LEVEL']

        df.dropna(inplace=True)
        
        if len(df) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        prev = df.iloc[-2]
        price = last["close"]
        signal = "HOLD"
        explanation = "Tidak ada kondisi yang terpenuhi."
        trend_regime = "N/A"

        # --- FILTER 1: Tentukan Rezim Tren (EMA 200) ---
        if price > last[f'EMA_{ema_period}']:
            trend_regime = "Bullish"
        elif price < last[f'EMA_{ema_period}']:
            trend_regime = "Bearish"
        else:
            trend_regime = "Choppy"

        # --- FILTER 2: Cari Sinyal Pemicu (Squeeze Breakout) ---
        is_in_squeeze = prev['SQUEEZE']
        
        if is_in_squeeze:
            explanation = f"Rezim: {trend_regime}. Squeeze terdeteksi, menunggu breakout."
            
            # Hanya cari sinyal BUY jika dalam Rezim Bullish
            if trend_regime == "Bullish" and last['close'] > prev[bbu_col]:
                signal = "BUY"
                explanation = f"Rezim: {trend_regime}. Sinyal: Squeeze & Breakout NAIK!"
            
            # Hanya cari sinyal SELL jika dalam Rezim Bearish
            elif trend_regime == "Bearish" and last['close'] < prev[bbl_col]:
                signal = "SELL"
                explanation = f"Rezim: {trend_regime}. Sinyal: Squeeze & Breakout TURUN!"

        analysis_data = {
            "signal": signal,
            "price": price,
            "explanation": explanation,
            "Trend_Regime": trend_regime,
            f"EMA_{ema_period}": last.get(f'EMA_{ema_period}'),
            "Is_Squeeze": bool(last.get('SQUEEZE', False)),
        }
        return analysis_data
