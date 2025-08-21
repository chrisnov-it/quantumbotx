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
        """
        Metode untuk LIVE TRADING.
        Menganalisis state saat ini dan menghasilkan sinyal masuk atau keluar.
        """
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

        # Dapatkan status posisi saat ini dari instance bot
        in_position = getattr(self.bot, 'in_position', False)
        position_type = getattr(self.bot, 'position_type', None) # 'BUY' or 'SELL'

        # --- Logika Exit ---
        if in_position:
            if position_type == 'BUY' and price < last['exit_lower']:
                signal = "SELL" # Sinyal untuk menutup posisi BUY
                explanation = f"Keluar dari BUY: Harga di bawah {exit_period}-periode terendah."
            elif position_type == 'SELL' and price > last['exit_upper']:
                signal = "BUY" # Sinyal untuk menutup posisi SELL
                explanation = f"Keluar dari SELL: Harga di atas {exit_period}-periode tertinggi."
            
            # Jika ada sinyal keluar, kembalikan. Jangan periksa sinyal masuk.
            if signal != 'HOLD':
                 return {"signal": signal, "price": price, "explanation": explanation}

        # --- Logika Entry (Hanya jika tidak ada posisi) ---
        if not in_position:
            if price > last['entry_upper']:
                signal = "BUY"
                explanation = f"Masuk BUY: Harga menembus {entry_period}-periode tertinggi."
            elif price < last['entry_lower']:
                signal = "SELL"
                explanation = f"Masuk SELL: Harga menembus {entry_period}-periode terendah."

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
        
        df.dropna(inplace=True)
        df = df.reset_index(drop=True)

        signals = ['HOLD'] * len(df)
        in_position = False
        position_type = None # 'BUY' or 'SELL'

        for i in range(len(df)):
            current_bar = df.iloc[i]
            signals[i] = 'HOLD' # Default signal for the bar

            if pd.isna(current_bar['entry_upper']) or pd.isna(current_bar['exit_lower']):
                continue

            # --- Logika Exit ---
            if in_position:
                if position_type == 'BUY' and current_bar['close'] < current_bar['exit_lower']:
                    signals[i] = 'SELL' # Sinyal untuk menutup posisi BUY
                    in_position = False
                    position_type = None
                elif position_type == 'SELL' and current_bar['close'] > current_bar['exit_upper']:
                    signals[i] = 'BUY' # Sinyal untuk menutup posisi SELL
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