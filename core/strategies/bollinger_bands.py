# /core/strategies/bollinger_bands.py
from .base_strategy import BaseStrategy

class BollingerBandsStrategy(BaseStrategy):
    name = 'Bollinger Bands Reversion'
    description = 'Sinyal berdasarkan harga yang menyentuh atau melintasi batas atas atau bawah Bollinger Bands (Mean Reversion).'

    @classmethod
    def get_definable_params(cls):
        """Mengembalikan parameter yang bisa diatur untuk strategi ini."""
        return [
            {"name": "bb_length", "label": "Panjang BB", "type": "number", "default": 20},
            {"name": "bb_std", "label": "Standar Deviasi BB", "type": "number", "default": 2.0, "step": 0.1}
        ]

    def analyze(self, df):
        """
        Menganalisis pasar menggunakan strategi Bollinger Bands® Mean Reversion.
        Ideal untuk pasar ranging yang volatil seperti EURUSD.
        """
        if df is None or df.empty or len(df) < 21:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup untuk Bollinger Bands."}

        # --- Hitung Indikator ---
        bb_length = self.params.get('bb_length', 20)
        bb_std = self.params.get('bb_std', 2.0)

        # PERBAIKAN: Paksa format float dengan satu desimal pada nama kolom
        bbu_col = f'BBU_{bb_length}_{bb_std:.1f}'
        bbl_col = f'BBL_{bb_length}_{bb_std:.1f}'

        df.ta.bbands(length=bb_length, std=bb_std, append=True) # pandas-ta akan membuat kolom dengan format yang sama
        df.dropna(inplace=True)
        
        if len(df) < 1:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        price = last["close"]
        signal = "HOLD"
        explanation = f"Harga [{price:.4f}] di dalam Bands. Tidak ada sinyal."

        # --- Logika Sinyal ---
        # Sinyal Beli: Harga menyentuh atau menembus Band Bawah
        if last['low'] <= last[bbl_col]:
            signal = "BUY"
            explanation = f"Oversold: Harga [{last['low']:.4f}] menyentuh Band Bawah [{last[bbl_col]:.4f}]"
        # Sinyal Jual: Harga menyentuh atau menembus Band Atas
        elif last['high'] >= last[bbu_col]:
            signal = "SELL"
            explanation = f"Overbought: Harga [{last['high']:.4f}] menyentuh Band Atas [{last[bbu_col]:.4f}]"

        analysis_data = {
            "signal": signal,
            "price": price,
            "explanation": explanation,
            "BB_Upper": last.get(f'BBU_{bb_length}_{bb_std:.1f}'),
            "BB_Middle": last.get(f'BBM_{bb_length}_{bb_std:.1f}'),
            "BB_Lower": last.get(f'BBL_{bb_length}_{bb_std:.1f}'),
        }
        return analysis_data