# download_data.py
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

# --- Kredensial Anda ---
ACCOUNT = 94464091
PASSWORD = "3rX@GcMm"
SERVER = "MetaQuotes-Demo"

# --- Inisialisasi MT5 ---
if not mt5.initialize(login=ACCOUNT, password=PASSWORD, server=SERVER):
    print("Gagal menginisialisasi MT5!", mt5.last_error())
    mt5.shutdown()
else:
    print("Berhasil terhubung ke MT5")

    # --- Parameter Download ---
    symbol = "GBPCHF"  # Ganti dengan simbol yang Anda inginkan
    timeframe = mt5.TIMEFRAME_H1 # Timeframe 1 Jam
    start_date = datetime(2020, 1, 1) # Mulai dari 1 Januari 2020
    end_date = datetime.now() # Sampai sekarang

    # --- Ambil Data ---
    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)
    mt5.shutdown()

    # --- Simpan ke File CSV ---
    if rates is not None and len(rates) > 0:
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Simpan ke file agar tidak perlu download lagi
        file_path = f'{symbol}_{timeframe}_data.csv'
        df.to_csv(file_path, index=False)
        print(f"Data berhasil disimpan ke {file_path}. Total {len(df)} baris.")
    else:
        print("Tidak ada data yang diunduh.")