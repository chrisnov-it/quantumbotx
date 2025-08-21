# core/strategies/london_breakout.py
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from .base_strategy import BaseStrategy

class LondonBreakoutStrategy(BaseStrategy):
    name = "London Breakout"
    description = "Strategi yang dirancang untuk menangkap volatilitas pada pembukaan sesi London dengan menembus rentang sesi Asia."

    def __init__(self, bot_instance, params=None):
        # Assuming BaseStrategy __init__ takes only params
        super().__init__(bot_instance=bot_instance, params=params) 
        self.bot_instance = bot_instance
        self.symbol = "DUMMY_SYMBOL" # Explicitly initialize symbol
        self._point = None
        self.state = {
            "today": None,
            "box_high": None,
            "box_low": None,
            "trade_taken": False
        }

    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "box_start_hour", "label": "Jam Mulai Box Sesi Asia (Waktu London)", "type": "number", "default": 0},
            {"name": "box_end_hour", "label": "Jam Selesai Box Sesi Asia (Waktu London)", "type": "number", "default": 8},
            {"name": "breakout_start_hour", "label": "Jam Mulai Periode Breakout (Waktu London)", "type": "number", "default": 8},
            {"name": "trade_end_hour", "label": "Jam Selesai Periode Trade (Waktu London)", "type": "number", "default": 16},
            {"name": "offset_pips", "label": "Offset Pips untuk Entry", "type": "number", "default": 2},
            {"name": "tp_pips", "label": "Take Profit (pips)", "type": "number", "default": 100},
            {"name": "sl_pips", "label": "Stop Loss (pips)", "type": "number", "default": 30},
        ]

    def _get_point(self):
        """Mengambil ukuran point untuk simbol saat ini dan menyimpannya."""
        if self._point is None:
            if self.symbol == "DUMMY_SYMBOL":
                # This should ideally not happen if symbol is set correctly before _get_point is called
                print("Warning: _get_point called with DUMMY_SYMBOL. Symbol not yet set.")
                return 0.0001 # Fallback

            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info is None:
                print(f"Gagal mendapatkan info untuk simbol: {self.symbol}")
                # Fallback ke nilai umum jika gagal, meskipun tidak ideal
                self._point = 0.0001 if "JPY" not in self.symbol else 0.001
            else:
                self._point = symbol_info.point
        return self._point

    def _convert_pips_to_price(self, pips):
        """Konversi pips ke nilai harga absolut menggunakan point dinamis."""
        # Perbaiki agar selalu pips * _get_point()
        return pips * self._get_point() * 10 

    def analyze(self, df):
        """Metode untuk LIVE TRADING (Stateful)."""
        if df.empty:
            return {"signal": "HOLD"}

        # Ensure self.symbol is set for live trading context
        if self.symbol == "DUMMY_SYMBOL" and hasattr(self.bot_instance, 'symbol'):
            self.symbol = self.bot_instance.symbol
        elif self.symbol == "DUMMY_SYMBOL":
            print("Error: Symbol not set for live trading.")
            return {"signal": "HOLD"}

        # --- Setup ---
        current_time = df.index[-1].tz_convert('Europe/London')
        current_price = df.iloc[-1]['close']
        today = current_time.date()

        # --- Reset Harian ---
        if self.state["today"] != today:
            self.state["today"] = today
            self.state["box_high"] = None
            self.state["box_low"] = None
            self.state["trade_taken"] = False

        # --- 1. Identifikasi Box Sesi Asia ---
        if self.state["box_high"] is None and current_time.hour >= self.params["box_end_hour"]:
            start_time = current_time.replace(hour=self.params['box_start_hour'], minute=0, second=0, microsecond=0)
            end_time = current_time.replace(hour=self.params['box_end_hour'] - 1, minute=59, second=59, microsecond=999999)
            
            # Ambil data historis yang cukup untuk box
            # This assumes self.bot_instance has a method to get historical data
            if hasattr(self.bot_instance, 'get_historical_data'):
                box_df = self.bot_instance.get_historical_data(self.symbol, mt5.TIMEFRAME_M1, start_time, end_time) # Assuming M1 for box
                if not box_df.empty:
                    self.state["box_high"] = box_df['high'].max()
                    # PERBAIKAN: Tanda kutip tunggal yang konsisten
                    self.state["box_low"] = box_df['low'].min()
                    print(f"[{today}] Box Asia teridentifikasi: High={self.state['box_high']}, Low={self.state['box_low']}")
            else:
                print("Warning: bot_instance does not have get_historical_data method for live trading box calculation.")

        # --- 2. Cek Sinyal Breakout ---
        if self.state["box_high"] is not None and not self.state["trade_taken"]:
            is_breakout_session = self.params['breakout_start_hour'] <= current_time.hour < self.params['trade_end_hour']
            
            if is_breakout_session:
                offset_val = self._convert_pips_to_price(self.params["offset_pips"])
                entry_buy = self.state["box_high"] + offset_val
                entry_sell = self.state["box_low"] - offset_val

                signal = "HOLD"
                if current_price > entry_buy:
                    signal = "BUY"
                elif current_price < entry_sell:
                    signal = "SELL"

                if signal != "HOLD":
                    self.state["trade_taken"] = True
                    sl = self._convert_pips_to_price(self.params['sl_pips'])
                    tp = self._convert_pips_to_price(self.params['tp_pips'])
                    
                    sl_price = entry_buy - sl if signal == "BUY" else entry_sell + sl
                    tp_price = entry_buy + tp if signal == "BUY" else entry_sell - tp

                    return {
                        "signal": signal,
                        "price": current_price,
                        "sl": sl_price,
                        "tp": tp_price,
                        "explanation": f"Breakout {signal} dari box {self.state['box_low']:.5f}-{self.state['box_high']:.5f}"
                    }
        
        return {"signal": "HOLD"}

    def analyze_df(self, df):
        """Metode untuk BACKTESTING (Vectorized)."""
        if df is None or df.empty:
            return df

        df = df.copy() # Bekerja pada salinan agar tidak memodifikasi DF asli

        # Set self.symbol from the DataFrame for backtesting context
        if self.symbol == "DUMMY_SYMBOL":
            # Perbaiki agar lebih kuat
            if not df.empty and isinstance(df.columns, pd.MultiIndex):
                self.symbol = df.columns.levels[0][0].upper()
            elif not df.empty:
                self.symbol = df.columns[0].upper()
            else:
                print("Warning: DataFrame is empty, cannot set symbol for backtesting.")

        # --- 0. Setup & Konversi Timezone ---
        df_original_index = df.index
        try:
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index, utc=True)
            if df.index.tz is None:
                df.index = df.index.tz_localize('UTC')
            df.index = df.index.tz_convert('Europe/London')
        except Exception as e:
            print(f"Error saat konversi timezone ke Europe/London: {e}")
            return pd.DataFrame(index=df_original_index) # Return empty DF with original index to avoid errors

        # --- 1. Hitung Box Harian (Vectorized) ---
        box_start_h = self.params.get('box_start_hour', 0)
        box_end_h = self.params.get('box_end_hour', 8)
        
        box_time_mask = (df.index.hour >= box_start_h) & (df.index.hour < box_end_h)
        df_box = df[box_time_mask].copy()
        
        daily_boxes = df_box.groupby(df_box.index.date).agg(
            box_high=('high', 'max'),
            box_low=('low', 'min')
        )
        
        df['box_high'] = df.index.to_series().dt.date.map(daily_boxes['box_high']).ffill()
        df['box_low'] = df.index.to_series().dt.date.map(daily_boxes['box_low']).ffill()

        # --- 2. Hasilkan Sinyal (Vectorized) ---
        offset_val = self._convert_pips_to_price(self.params.get('offset_pips', 2))
        breakout_start_h = self.params.get('breakout_start_hour', 8)
        trade_end_h = self.params.get('trade_end_hour', 16)

        breakout_time_mask = (df.index.hour >= breakout_start_h) & (df.index.hour < trade_end_h)
        
        entry_buy_price = df['box_high'] + offset_val
        entry_sell_price = df['box_low'] - offset_val

        potential_buy = (df['high'] > entry_buy_price) & breakout_time_mask & df['box_high'].notna()
        potential_sell = (df['low'] < entry_sell_price) & breakout_time_mask & df['box_low'].notna()

        df['signal'] = np.select(
            [potential_buy, potential_sell],
            ['BUY', 'SELL'],
            default='HOLD'
        )

        # --- 3. Pastikan Hanya Satu Sinyal per Hari ---
        df['trade_today'] = (df['signal'] != 'HOLD').groupby(df.index.date).cumsum()
        df['is_first_trade'] = (df['trade_today'] == 1) & (df['signal'] != 'HOLD')
        
        # Hanya pertahankan sinyal pertama setiap hari
        df.loc[~df['is_first_trade'], 'signal'] = 'HOLD'

        # --- 4. Cleanup ---
        df.drop(columns=['box_high', 'box_low', 'trade_today', 'is_first_trade'], inplace=True, errors='ignore')
        df.index = df_original_index # Kembalikan index asli
        
        return df