# core/utils/mt5.py
import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# --- PERBAIKAN: Definisikan TIMEFRAME_MAP di sini ---
TIMEFRAME_MAP = {
    "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15, "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4, "D1": mt5.TIMEFRAME_D1,
    "W1": mt5.TIMEFRAME_W1, "MN1": mt5.TIMEFRAME_MN1
}

def initialize_mt5(account, password, server):
    """Login ke MetaTrader 5."""
    if not mt5.initialize(login=account, password=password, server=server):
        logger.error(f"Inisialisasi atau Login MT5 gagal: {mt5.last_error()}")
        return False
    
    logger.info(f"Berhasil login ke MT5 ({account}) di server {server}")
    return True

def get_mt5_account_info():
    """Mengambil info akun dari MetaTrader 5."""
    try:
        info = mt5.account_info()
        if info is not None:
            return info._asdict()
        else:
            logger.error(f"Gagal mengambil account_info(): {mt5.last_error()}")
            return None
    except Exception as e:
        logger.error(f"Error saat mengambil info akun MT5: {e}", exc_info=True)
        return None

def get_todays_profit():
    """Menghitung total profit dari histori trading hari ini."""
    try:
        # Tentukan rentang waktu dari jam 00:00 hari ini sampai sekarang
        from_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        to_date = datetime.now()
        
        # Ambil histori order yang sudah selesai
        history_deals = mt5.history_deals_get(from_date, to_date)
        
        if history_deals is None:
            return 0.0

        total_profit = 0.0
        for deal in history_deals:
            # Hanya hitung deal yang merupakan 'penutupan' posisi
            if deal.entry == 1: # 0 = in, 1 = out, 2 = in/out
                total_profit += deal.profit
        return total_profit
    except Exception as e:
        logger.error(f"Gagal menghitung profit hari ini: {e}", exc_info=True)
        return 0.0

def get_rates_from_mt5(symbol, timeframe, count):
    """Fungsi utama untuk mengambil data harga historis langsung dari MT5."""
    try:
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None or len(rates) == 0:
            logger.warning(f"Tidak ada data yang diterima dari MT5 untuk {symbol}")
            return pd.DataFrame() # Kembalikan DataFrame kosong agar tidak error
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df

    except Exception as e:
        logger.error(f"Error saat mengambil data dari MT5 untuk {symbol}: {e}", exc_info=True)
        return pd.DataFrame()
