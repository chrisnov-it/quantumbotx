# /core/data/fetch.py
import MetaTrader5 as mt5
import pandas as pd
import logging
from datetime import datetime, timedelta

# Gunakan logger yang konsisten dengan seluruh aplikasi
logger = logging.getLogger(__name__)

# =================================================
# FUNGSI-FUNGSI PENGAMBILAN DATA DARI METATRADER 5
# =================================================

def get_rates(symbol: str, timeframe: int, count: int = 100):
    """
    Mengambil data harga historis (rates) dari MT5 dalam bentuk DataFrame.
    Ini adalah fungsi utama untuk semua analisis strategi.
    """
    try:
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        
        # Periksa apakah data berhasil diambil
        if rates is None or len(rates) == 0:
            logger.warning(f"Gagal mengambil data harga untuk {symbol} (Timeframe: {timeframe}). MT5 mengembalikan None atau data kosong.")
            return None
        
        # Konversi ke DataFrame
        df = pd.DataFrame(rates)
        # Konversi kolom 'time' dari Unix timestamp menjadi objek datetime
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        return df
    except Exception as e:
        logger.error(f"Error tak terduga saat get_rates untuk {symbol}: {e}", exc_info=True)
        return None

def get_mt5_account_info():
    """Mengambil informasi akun (saldo, equity, profit) dari MT5."""
    try:
        info = mt5.account_info()
        # Periksa apakah info berhasil diambil sebelum mengubahnya menjadi dictionary
        if info:
            return info._asdict()
        else:
            logger.error(f"Gagal mengambil info akun. MT5 mengembalikan None. Error: {mt5.last_error()}")
            return None
    except Exception as e:
        logger.error(f"Error tak terduga saat get_mt5_account_info: {e}", exc_info=True)
        return None

def get_todays_profit():
    """Menghitung total profit dari histori trading hari ini."""
    try:
        from_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        to_date = datetime.now()
        
        deals = mt5.history_deals_get(from_date, to_date)
        
        if deals is None:
            return 0.0
            
        # Gunakan generator expression untuk efisiensi
        return sum(d.profit for d in deals if d.entry == 1)
    except Exception as e:
        logger.error(f"Error tak terduga saat get_todays_profit: {e}", exc_info=True)
        return 0.0

def get_trade_history_from_mt5(days_history: int = 30):
    """Mengambil riwayat transaksi yang sudah ditutup dari MT5."""
    try:
        from_date = datetime.now() - timedelta(days=days_history)
        to_date = datetime.now()
        
        deals = mt5.history_deals_get(from_date, to_date)

        if deals is None:
            logger.warning("Gagal mengambil histori deals dari MT5. MT5 mengembalikan None.")
            return []

        # Proses data hanya jika ada deals yang ditemukan
        if len(deals) > 0:
            df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
            df['time'] = pd.to_datetime(df['time'], unit='s')
            closed = df[df['entry'] == 1].sort_values(by='time', ascending=False)
            return closed.to_dict('records')
        
        return []

    except Exception as e:
        logger.error(f"Error tak terduga saat get_trade_history: {e}", exc_info=True)
        return []

def get_open_positions_from_mt5():
    """Mengambil semua posisi trading yang sedang terbuka dari akun MT5."""
    try:
        positions = mt5.positions_get()
        if positions is None:
            # Tidak perlu print error jika hanya tidak ada posisi
            return []

        # Ubah tuple of objects menjadi list of dictionaries
        return [
            {
                "ticket": pos.ticket, "symbol": pos.symbol, "type": pos.type,
                "volume": pos.volume, "price_open": pos.price_open,
                "price_current": pos.price_current, "profit": pos.profit,
                "magic": pos.magic,
                "time": datetime.fromtimestamp(pos.time).isoformat()
            }
            for pos in positions
        ]
    except Exception as e:
        logger.error(f"Error tak terduga saat get_open_positions: {e}", exc_info=True)
        return []