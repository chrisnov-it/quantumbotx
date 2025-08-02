# core/bots/trading_bot.py - VERSI GABUNGAN FINAL

import threading
import time
import logging
import MetaTrader5 as mt5
from core.strategies.strategy_map import STRATEGY_MAP
from core.mt5.trade import place_trade, close_trade
from core.utils.mt5 import TIMEFRAME_MAP  # <-- Impor dari lokasi terpusat

logger = logging.getLogger(__name__)


class TradingBot(threading.Thread):
    def __init__(self, id, name, market, lot_size, sl_pips, tp_pips, timeframe, check_interval, strategy, strategy_params={}, status='Dijeda'):
        super().__init__()
        self.id = id
        self.name = name
        self.market = market
        self.lot_size = lot_size
        self.sl_pips = sl_pips
        self.tp_pips = tp_pips
        self.timeframe = timeframe
        self.check_interval = check_interval
        self.strategy_name = strategy
        self.strategy_params = strategy_params
        self.market_for_mt5 = self.market.replace('/', '') # Versi simbol yang bersih untuk MT5
        self.status = status

        self.last_analysis = {}
        self._stop_event = threading.Event()
        self.strategy_instance = None
        # Gunakan map yang diimpor untuk menjaga konsistensi
        self.tf_map = TIMEFRAME_MAP

    def run(self):
        """Metode utama yang dijalankan oleh thread, kini dengan eksekusi trade."""
        self.status = 'Aktif'
        self.log_activity('START', f"Bot '{self.name}' dimulai.", is_notification=True)

        try:
            strategy_class = STRATEGY_MAP.get(self.strategy_name)
            if not strategy_class:
                raise ValueError(f"Strategi '{self.strategy_name}' tidak ditemukan.")

            # --- PERBAIKAN: Inisialisasi kelas strategi dengan benar ---
            self.strategy_instance = strategy_class(bot_instance=self, params=self.strategy_params)

        except Exception as e:
            self.log_activity('ERROR', f"Inisialisasi Gagal: {e}", is_notification=True)
            self.status = 'Error'
            return

        while not self._stop_event.is_set():
            try:
                if not mt5.symbol_select(self.market_for_mt5, True):
                    msg = f"Gagal mengaktifkan simbol {self.market} (di MT5: {self.market_for_mt5}). Pastikan simbol ada di Market Watch."
                    self.log_activity('WARNING', msg)
                    self.last_analysis = {"signal": "ERROR", "price": None, "explanation": msg}
                    time.sleep(self.check_interval)
                    continue

                symbol_info = mt5.symbol_info(self.market_for_mt5)
                if not symbol_info:
                    msg = f"Tidak dapat mengambil info untuk simbol {self.market} (di MT5: {self.market_for_mt5})."
                    self.log_activity('WARNING', msg)
                    self.last_analysis = {"signal": "ERROR", "price": None, "explanation": msg}
                    time.sleep(self.check_interval)
                    continue

                # --- PERBAIKAN: Bot sekarang yang mengambil data ---
                from core.data.fetch import get_rates
                tf_const = self.tf_map.get(self.timeframe, mt5.TIMEFRAME_H1)
                # Ambil data yang cukup untuk strategi terkompleks (misal, 250 bar untuk EMA 200)
                df = get_rates(self.market_for_mt5, tf_const, 250)

                self.last_analysis = self.strategy_instance.analyze(df)
                logger.info(f"Bot {self.id} [{self.strategy_name}] - Last Analysis: {self.last_analysis}")
                signal = self.last_analysis.get("signal", "HOLD")

                current_position = self._get_open_position()

                self._handle_trade_signal(signal, current_position)

                time.sleep(self.check_interval)
            except Exception as e:
                self.log_activity('ERROR', f"Error pada loop utama: {e}", exc_info=True, is_notification=True)
                time.sleep(self.check_interval * 2)

        self.status = 'Dijeda'
        self.log_activity('STOP', f"Bot '{self.name}' dihentikan.", is_notification=True)

    def stop(self):
        """Mengirim sinyal berhenti ke thread."""
        self._stop_event.set()

    def is_stopped(self):
        """Memeriksa apakah thread sudah diberi sinyal berhenti."""
        return self._stop_event.is_set()

    def log_activity(self, action, details, exc_info=False, is_notification=False):
        """Mencatat aktivitas bot ke database dan file log."""
        try:
            from core.db.queries import add_history_log
            add_history_log(self.id, action, details, is_notification)
            log_message = f"Bot {self.id} [{action}]: {details}"
            if exc_info:
                logger.error(log_message, exc_info=True)
            else:
                logger.info(log_message)
        except Exception as e:
            logger.error(f"Gagal mencatat riwayat untuk bot {self.id}: {e}")

    def _get_open_position(self):
        """Mendapatkan posisi terbuka untuk bot ini berdasarkan magic number (ID bot)."""
        try:
            positions = mt5.positions_get(symbol=self.market_for_mt5)
            if positions:
                for pos in positions:
                    if pos.magic == self.id:
                        return pos
            return None
        except Exception as e:
            self.log_activity('ERROR', f"Gagal mendapatkan posisi terbuka: {e}", exc_info=True, is_notification=True)
            return None

    def _handle_trade_signal(self, signal, position):
        """Menangani sinyal trading: membuka, menutup, atau tidak melakukan apa-apa."""
        # Logika untuk sinyal BUY
        if signal == 'BUY':
            # Jika ada posisi SELL, tutup dulu
            if position and position.type == mt5.ORDER_TYPE_SELL:
                self.log_activity('CLOSE SELL', "Menutup posisi JUAL untuk membuka posisi BELI.", is_notification=True)
                close_trade(position)
                position = None  # Reset posisi setelah ditutup

            # Jika tidak ada posisi, buka posisi BUY baru
            if not position:
                self.log_activity('OPEN BUY', "Membuka posisi BELI berdasarkan sinyal.", is_notification=True)
                place_trade(self.market_for_mt5, mt5.ORDER_TYPE_BUY, self.lot_size, self.sl_pips, self.tp_pips, self.id)

        # Logika untuk sinyal SELL
        elif signal == 'SELL':
            # Jika ada posisi BUY, tutup dulu
            if position and position.type == mt5.ORDER_TYPE_BUY:
                self.log_activity('CLOSE BUY', "Menutup posisi BELI untuk membuka posisi JUAL.", is_notification=True)
                close_trade(position)
                position = None  # Reset posisi setelah ditutup

            # Jika tidak ada posisi, buka posisi SELL baru
            if not position:
                self.log_activity('OPEN SELL', "Membuka posisi JUAL berdasarkan sinyal.", is_notification=True)
                place_trade(self.market_for_mt5, mt5.ORDER_TYPE_SELL, self.lot_size, self.sl_pips, self.tp_pips, self.id)
