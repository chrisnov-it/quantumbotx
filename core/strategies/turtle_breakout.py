# core/strategies/turtle_breakout.py
import pandas as pd
from .base_strategy import BaseStrategy

class TurtleBreakoutStrategy(BaseStrategy):
    name = 'Turtle Breakout'
    description = 'Strategi trend-following klasik berdasarkan penembusan harga tertinggi/terendah N periode.'

    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "entry_period", "label": "Periode Channel Masuk", "type": "number", "default": 20},
            {"name": "exit_period", "label": "Periode Channel Keluar", "type": "number", "default": 10},
        ]

    def analyze(self, df):
        """Metode untuk LIVE TRADING."""
        entry_period = self.params.get('entry_period', 20)
        exit_period = self.params.get('exit_period', 10)

        if df is None or df.empty or len(df) < entry_period + 1:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup."}

        # Hitung Channel (menggunakan shift(1) untuk menghindari look-ahead)
        df['entry_upper'] = df['high'].rolling(window=entry_period).max().shift(1)
        df['entry_lower'] = df['low'].rolling(window=entry_period).min().shift(1)
        df['exit_upper'] = df['high'].rolling(window=exit_period).max().shift(1)
        df['exit_lower'] = df['low'].rolling(window=exit_period).min().shift(1)
        
        df.dropna(inplace=True)
        
        if df.empty:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        price = last["close"]
        signal = "HOLD"
        explanation = "Tidak ada sinyal."

        # Logika Entry (hanya jika tidak ada posisi)
        # Dalam live trading, bot.in_position akan mengelola state
        # Kita hanya memberikan sinyal BUY/SELL jika kondisi terpenuhi
        if price > last['entry_upper']:
            signal = "BUY"
            explanation = f"Harga menembus {entry_period}-periode tertinggi."
        elif price < last['entry_lower']:
            signal = "SELL"
            explanation = f"Harga menembus {entry_period}-periode terendah."

        return {"signal": signal, "price": price, "explanation": explanation}

    def analyze_df(self, df):
        """Metode untuk BACKTESTING (stateful)."""
        entry_period = self.params.get('entry_period', 20)
        exit_period = self.params.get('exit_period', 10)

        # Hitung Channel (menggunakan shift(1) untuk menghindari look-ahead)
        df['entry_upper'] = df['high'].rolling(window=entry_period).max().shift(1)
        df['entry_lower'] = df['low'].rolling(window=entry_period).min().shift(1)
        df['exit_upper'] = df['high'].rolling(window=exit_period).max().shift(1)
        df['exit_lower'] = df['low'].rolling(window=exit_period).min().shift(1)
        
        # Dropna untuk memastikan semua indikator terhitung
        df.dropna(inplace=True)
        df = df.reset_index(drop=True) # Reset index setelah dropna

        signals = ['HOLD'] * len(df)
        in_position = False
        position_type = None # 'BUY' or 'SELL'

        # Loop melalui data untuk mensimulasikan stateful trading
        for i in range(len(df)):
            current_bar = df.iloc[i]
            
            # Pastikan channel values tersedia untuk bar saat ini
            if pd.isna(current_bar['entry_upper']) or pd.isna(current_bar['exit_lower']):
                continue # Lewati jika data indikator belum lengkap

            # --- Logika Exit ---
            if in_position:
                if position_type == 'BUY' and current_bar['close'] < current_bar['exit_lower']:
                    signals[i] = 'HOLD' # Sinyal untuk menutup posisi
                    in_position = False
                    position_type = None
                elif position_type == 'SELL' and current_bar['close'] > current_bar['exit_upper']:
                    signals[i] = 'HOLD' # Sinyal untuk menutup posisi
                    in_position = False
                    position_type = None

            # --- Logika Entry (Hanya jika tidak ada posisi) ---
            if not in_position:
                if current_bar['close'] > current_bar['entry_upper']:
                    signals[i] = 'BUY'
                    in_position = True
                    position_type = 'BUY'
                elif current_bar['close'] < current_bar['entry_lower']:
                    signals[i] = 'SELL'
                    in_position = True
                    position_type = 'SELL'
        
        df['signal'] = signals
        return df