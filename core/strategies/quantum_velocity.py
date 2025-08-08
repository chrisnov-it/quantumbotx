# d:\dev\quantumbotx\core\strategies\quantum_velocity.py

import pandas_ta as ta
import numpy as np
from .base_strategy import BaseStrategy

class QuantumVelocityStrategy(BaseStrategy):
    name = 'Quantum Velocity'
    description = 'Menggabungkan filter tren jangka panjang (EMA 200) dengan pemicu volatilitas (Bollinger Squeeze Breakout).'

    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "ema_period", "label": "Periode EMA Tren", "type": "number", "default": 200},
            {"name": "bb_length", "label": "Panjang BB", "type": "number", "default": 20},
            {"name": "bb_std", "label": "Std Dev BB", "type": "number", "default": 2.0, "step": 0.1},
            {"name": "squeeze_window", "label": "Window Squeeze", "type": "number", "default": 10},
            {"name": "squeeze_factor", "label": "Faktor Squeeze", "type": "number", "default": 0.7, "step": 0.1},
        ]

    def analyze(self, df):
        """Metode untuk LIVE TRADING."""
        if df is None or df.empty or len(df) < self.params.get('ema_period', 200) + 1:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup."}

        ema_period = self.params.get('ema_period', 200)
        bb_length = self.params.get('bb_length', 20)
        bb_std = self.params.get('bb_std', 2.0)
        squeeze_window = self.params.get('squeeze_window', 10)
        squeeze_factor = self.params.get('squeeze_factor', 0.7)

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

        if price > last[f'EMA_{ema_period}']:
            if prev['SQUEEZE'] and last['close'] > prev[bbu_col]:
                signal = "BUY"
                explanation = "Squeeze & Breakout NAIK!"
        elif price < last[f'EMA_{ema_period}']:
            if prev['SQUEEZE'] and last['close'] < prev[bbl_col]:
                signal = "SELL"
                explanation = "Squeeze & Breakout TURUN!"

        return {"signal": signal, "price": price, "explanation": explanation}

    def analyze_df(self, df):
        """Metode untuk BACKTESTING."""
        ema_period = self.params.get('ema_period', 200)
        bb_length = self.params.get('bb_length', 20)
        bb_std = self.params.get('bb_std', 2.0)
        squeeze_window = self.params.get('squeeze_window', 10)
        squeeze_factor = self.params.get('squeeze_factor', 0.7)

        df[f'EMA_{ema_period}'] = ta.ema(df['close'], length=ema_period)
        
        bbu_col = f'BBU_{bb_length}_{bb_std:.1f}'
        bbm_col = f'BBM_{bb_length}_{bb_std:.1f}'
        bbl_col = f'BBL_{bb_length}_{bb_std:.1f}'

        df.ta.bbands(length=bb_length, std=bb_std, append=True)
        df['BB_BANDWIDTH'] = np.where(df[bbm_col] != 0, (df[bbu_col] - df[bbl_col]) / df[bbm_col] * 100, 0)
        df['AVG_BANDWIDTH'] = df['BB_BANDWIDTH'].rolling(window=squeeze_window).mean()
        df['SQUEEZE_LEVEL'] = df['AVG_BANDWIDTH'] * squeeze_factor
        df['SQUEEZE'] = df['BB_BANDWIDTH'] < df['SQUEEZE_LEVEL']

        trend_regime_bullish = df['close'] > df[f'EMA_{ema_period}']
        trend_regime_bearish = df['close'] < df[f'EMA_{ema_period}']
        is_in_squeeze = df['SQUEEZE'].shift(1)

        buy_signal = trend_regime_bullish & is_in_squeeze & (df['close'] > df[bbu_col].shift(1))
        sell_signal = trend_regime_bearish & is_in_squeeze & (df['close'] < df[bbl_col].shift(1))

        df['signal'] = np.where(buy_signal, 'BUY', np.where(sell_signal, 'SELL', 'HOLD'))

        return df
