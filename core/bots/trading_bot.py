# core/bots/trading_bot.py - VERSI GABUNGAN FINAL

import threading
import time
import logging
import MetaTrader5 as mt5
from core.strategies.strategy_map import STRATEGY_MAP
from core.mt5.trade import place_trade, close_trade
from core.utils.mt5 import TIMEFRAME_MAP  # <-- Impor dari lokasi terpusat
# AI Mentor Integration
from core.db.models import log_trade_for_ai_analysis

logger = logging.getLogger(__name__)


class TradingBot(threading.Thread):
    def __init__(self, id, name, market, risk_percent, sl_pips, tp_pips, timeframe, check_interval, strategy, strategy_params={}, status='Dijeda', enable_strategy_switching=False):
        super().__init__()
        self.id = id
        self.name = name
        self.market = market
        self.risk_percent = risk_percent
        self.sl_pips = sl_pips
        self.tp_pips = tp_pips
        self.timeframe = timeframe
        self.check_interval = check_interval
        self.strategy_name = strategy
        self.strategy_params = strategy_params
        self.enable_strategy_switching = enable_strategy_switching
        self.market_for_mt5 = None # Akan diisi setelah verifikasi simbol
        self.status = status

        self.last_analysis = {"signal": "MEMUAT", "explanation": "Bot sedang memulai, menunggu analisis pertama..."}
        self._stop_event = threading.Event()
        self.strategy_instance = None
        # Gunakan map yang diimpor untuk menjaga konsistensi
        self.tf_map = TIMEFRAME_MAP

    def run(self):
        """Metode utama yang dijalankan oleh thread, kini dengan eksekusi trade."""
        self.status = 'Aktif'
        self.log_activity('START', f"Bot '{self.name}' dimulai.", is_notification=True)

        # --- PERBAIKAN: Verifikasi Simbol Cerdas ---
        from core.utils.mt5 import find_mt5_symbol
        self.market_for_mt5 = find_mt5_symbol(self.market)

        if not self.market_for_mt5:
            msg = f"Simbol '{self.market}' atau variasinya tidak dapat ditemukan/diaktifkan di Market Watch MT5."
            self.log_activity('ERROR', msg, is_notification=True)
            self.status = 'Error'
            self.last_analysis = {"signal": "ERROR", "explanation": msg}
            return # Hentikan eksekusi jika simbol tidak valid

        try:
            strategy_class = STRATEGY_MAP.get(self.strategy_name)
            if not strategy_class:
                raise ValueError(f"Strategi '{self.strategy_name}' tidak ditemukan.")

            # Inisialisasi kelas strategi dengan benar
            self.strategy_instance = strategy_class(bot_instance=self, params=self.strategy_params)

        except Exception as e:
            self.log_activity('ERROR', f"Inisialisasi Gagal: {e}", is_notification=True)
            self.status = 'Error'
            return

        while not self._stop_event.is_set():
            try:
                # Simbol sudah diverifikasi, jadi pemeriksaan ini menjadi redundan
                # if not mt5.symbol_select(self.market_for_mt5, True): ...

                symbol_info = mt5.symbol_info(self.market_for_mt5)  # type: ignore
                if not symbol_info:
                    msg = f"Tidak dapat mengambil info untuk simbol {self.market_for_mt5}."
                    self.log_activity('WARNING', msg)
                    self.last_analysis = {"signal": "ERROR", "price": None, "explanation": msg}
                    time.sleep(self.check_interval)
                    continue

                # Bot sekarang yang mengambil data
                from core.utils.mt5 import get_rates_mt5
                tf_const = self.tf_map.get(self.timeframe, mt5.TIMEFRAME_H1)
                df = get_rates_mt5(self.market_for_mt5, tf_const, 250)

                if df.empty:
                    msg = f"Gagal mengambil data harga untuk {self.market_for_mt5}. Periksa koneksi atau ketersediaan data historis."
                    self.log_activity('WARNING', msg)
                    self.last_analysis = {"signal": "ERROR", "explanation": msg}
                    time.sleep(self.check_interval)
                    continue

                self.last_analysis = self.strategy_instance.analyze(df)
                logger.info(f"Bot {self.id} [{self.strategy_name}] - Last Analysis: {self.last_analysis}")
                signal = self.last_analysis.get("signal", "HOLD")

                current_position = self._get_open_position()

                self._handle_trade_signal(signal, current_position)

                time.sleep(self.check_interval)
            except Exception as e:
                error_message = f"Error pada loop utama: {e}"
                self.log_activity('ERROR', error_message, exc_info=True, is_notification=True)
                # PERBAIKAN: Perbarui status analisis agar error terlihat di UI
                self.last_analysis = {"signal": "ERROR", "explanation": str(e)}
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
            positions = mt5.positions_get(symbol=self.market_for_mt5)  # type: ignore
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
                
                # Log untuk AI mentor analysis
                profit_loss = position.profit if hasattr(position, 'profit') else 0
                self._log_trade_for_ai_mentor(position, profit_loss, 'CLOSE_SELL')
                
                close_trade(position)
                position = None  # Reset posisi setelah ditutup

            # Jika tidak ada posisi, buka posisi BUY baru
            if not position:
                self.log_activity('OPEN BUY', "Membuka posisi BELI berdasarkan sinyal.", is_notification=True)
                place_trade(self.market_for_mt5, mt5.ORDER_TYPE_BUY, self.risk_percent, self.sl_pips, self.tp_pips, self.id, self.timeframe)

        # Logika untuk sinyal SELL
        elif signal == 'SELL':
            # Jika ada posisi BUY, tutup dulu
            if position and position.type == mt5.ORDER_TYPE_BUY:
                self.log_activity('CLOSE BUY', "Menutup posisi BELI untuk membuka posisi JUAL.", is_notification=True)
                
                # Log untuk AI mentor analysis
                profit_loss = position.profit if hasattr(position, 'profit') else 0
                self._log_trade_for_ai_mentor(position, profit_loss, 'CLOSE_BUY')
                
                close_trade(position)
                position = None  # Reset posisi setelah ditutup

            # Jika tidak ada posisi, buka posisi SELL baru
            if not position:
                self.log_activity('OPEN SELL', "Membuka posisi JUAL berdasarkan sinyal.", is_notification=True)
                place_trade(self.market_for_mt5, mt5.ORDER_TYPE_SELL, self.risk_percent, self.sl_pips, self.tp_pips, self.id, self.timeframe)
    
    def _log_trade_for_ai_mentor(self, position, profit_loss, action_type):
        """Log trade data untuk analisis AI mentor"""
        try:
            # Hitung apakah stop loss dan take profit digunakan
            stop_loss_used = hasattr(position, 'sl') and position.sl > 0
            take_profit_used = hasattr(position, 'tp') and position.tp > 0
            
            # Log ke database untuk AI analysis
            log_trade_for_ai_analysis(
                bot_id=self.id,
                symbol=self.market_for_mt5 or self.market,
                profit_loss=profit_loss,
                lot_size=position.volume if hasattr(position, 'volume') else self.risk_percent,
                stop_loss_used=stop_loss_used,
                take_profit_used=take_profit_used,
                risk_percent=self.risk_percent,
                strategy_used=self.strategy_name
            )
            
            logger.info(f"[AI MENTOR] Trade logged for bot {self.id}: {action_type} {self.market_for_mt5} P/L: ${profit_loss:.2f}")
            
        except Exception as e:
            logger.error(f"[AI MENTOR] Failed to log trade for AI analysis: {e}")
