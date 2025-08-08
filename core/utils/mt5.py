# core/utils/mt5.py (VERSI FINAL LENGKAP)

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Definisikan konstanta di satu tempat
TIMEFRAME_MAP = {
    "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15, 
    "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4, "D1": mt5.TIMEFRAME_D1,
    "W1": mt5.TIMEFRAME_W1, "MN1": mt5.TIMEFRAME_MN1
}

def initialize_mt5(account, password, server):
    """Login ke MetaTrader 5."""
    if not mt5.initialize(login=account, password=password, server=server):
        logger.error(f"Inisialisasi atau Login MT5 gagal: {mt5.last_error()}")
        return False
    logger.info(f"Berhasil login ke MT5 ({account}) di server {server}")
    return True

def get_account_info_mt5():
    """Mengambil informasi akun (saldo, equity, profit) dari MT5."""
    try:
        info = mt5.account_info()
        if info:
            return info._asdict()
        else:
            logger.warning(f"Gagal mengambil info akun. Error: {mt5.last_error()}")
            return None
    except Exception as e:
        logger.error(f"Error saat get_account_info_mt5: {e}", exc_info=True)
        return None

def get_rates_mt5(symbol: str, timeframe: int, count: int = 100):
    """Mengambil data harga historis (rates) dari MT5 dalam bentuk DataFrame."""
    try:
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None or len(rates) == 0:
            logger.warning(f"Gagal mengambil data harga untuk {symbol} (Timeframe: {timeframe}).")
            return pd.DataFrame()
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        df.set_index('time', inplace=True) # Jadikan kolom 'time' sebagai index DataFrame
        
        return df
    except Exception as e:
        logger.error(f"Error saat get_rates_mt5 untuk {symbol}: {e}", exc_info=True)
        return pd.DataFrame()

def get_open_positions_mt5():
    """Mengambil semua posisi trading yang sedang terbuka dari akun MT5."""
    try:
        positions = mt5.positions_get()
        if positions is None:
            return []
        # Mengubah tuple objek menjadi list dictionary
        return [pos._asdict() for pos in positions]
    except Exception as e:
        logger.error(f"Error saat get_open_positions_mt5: {e}", exc_info=True)
        return []

def get_trade_history_mt5(days: int = 30):
    """Mengambil riwayat transaksi yang sudah ditutup dari MT5."""
    try:
        from_date = datetime.now() - timedelta(days=days)
        deals = mt5.history_deals_get(from_date, datetime.now())
        if deals is None:
            logger.warning("Gagal mengambil histori deals dari MT5.")
            return []
        # Filter hanya deal penutupan (entry == 1) dan konversi ke dict
        closed_deals = [d._asdict() for d in deals if d.entry == 1]
        return closed_deals
    except Exception as e:
        logger.error(f"Error saat get_trade_history_mt5: {e}", exc_info=True)
        return []

def get_todays_profit_mt5():
    """Menghitung total profit dari histori trading hari ini."""
    try:
        from_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        to_date = datetime.now()
        
        deals = mt5.history_deals_get(from_date, to_date)
        
        if deals is None:
            logger.warning("Gagal mengambil histori deals untuk profit hari ini.")
            return 0.0
            
        # Gunakan generator expression untuk efisiensi dan filter deal penutupan
        return sum(d.profit for d in deals if d.entry == 1)
    except Exception as e:
        logger.error(f"Error saat get_todays_profit_mt5: {e}", exc_info=True)
        return 0.0

def find_mt5_symbol(base_symbol: str) -> str | None:
    """
    Mencari nama simbol yang benar di MT5 berdasarkan nama dasar.
    Fungsi ini mencoba mencocokkan variasi umum (suffix, prefix, nama alternatif)
    dan memastikan simbol tersebut terlihat di Market Watch.

    Args:
        base_symbol (str): Nama simbol dasar (misal, "XAUUSD", "EURUSD").

    Returns:
        str | None: Nama simbol yang valid dan terlihat di MT5, atau None jika tidak ditemukan.
    """
    import re
    base_symbol_cleaned = re.sub(r'[^A-Z0-9]', '', base_symbol.upper())
    
    try:
        all_symbols = mt5.symbols_get()
        if all_symbols is None:
            logger.error("Gagal mengambil daftar simbol dari MT5.")
            return None
    except Exception as e:
        logger.error(f"Error saat mengambil daftar simbol dari MT5: {e}")
        return None

    visible_symbols = {s.name for s in all_symbols if s.visible}

    # 1. Cek kecocokan langsung (paling umum)
    if base_symbol_cleaned in visible_symbols:
        logger.info(f"Simbol '{base_symbol_cleaned}' ditemukan secara langsung.")
        return base_symbol_cleaned

    # 2. Buat pola regex untuk mencari variasi
    pattern = re.compile(f"^[a-zA-Z]*{base_symbol_cleaned}[a-zA-Z0-9._-]*$", re.IGNORECASE)
    
    # Cari di antara simbol yang terlihat
    for symbol_name in visible_symbols:
        if pattern.match(symbol_name):
            logger.info(f"Variasi simbol '{symbol_name}' ditemukan untuk basis '{base_symbol_cleaned}'.")
            if mt5.symbol_select(symbol_name, True):
                return symbol_name
            else:
                logger.warning(f"Simbol '{symbol_name}' ditemukan tapi gagal diaktifkan.")

    logger.warning(f"Tidak ada variasi simbol yang valid dan terlihat untuk '{base_symbol}' ditemukan di Market Watch.")
    return None