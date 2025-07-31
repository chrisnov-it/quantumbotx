# backtester.py (VERSI DIPERBAIKI)
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

def get_profit_multiplier(symbol, lot_size=0.01):
    """
    Mengembalikan multiplier yang benar untuk perhitungan profit berdasarkan
    simbol, kelas aset, dan ukuran lot.
    """
    # 1. Untuk Indeks Saham (seperti US500, NAS100, SPX500m, dll.)
    # Pergerakan 1 poin = profit $0.01 untuk 0.01 lot.
    if "500" in symbol or "100" in symbol or "30" in symbol:
        return 1 * lot_size

    # 2. Untuk Emas (XAUUSD)
    # Pergerakan $1 = profit $1 untuk 0.01 lot.
    elif "XAU" in symbol:
        return 100 * lot_size
        
    # 3. Untuk Pasangan Mata Uang Forex (seperti EURUSD, USDJPY)
    # Pergerakan 1 pip = profit ~$0.10 untuk 0.01 lot.
    # Nilai 100000 adalah standar industri untuk 1 lot.
    else:
        # Periksa apakah ini pasangan JPY, karena nilainya berbeda
        if "JPY" in symbol:
            return 1000 * lot_size # Untuk pasangan JPY, 1 pip adalah 0.01
        else:
            return 100000 * lot_size # Untuk pasangan non-JPY, 1 pip adalah 0.0001

def run_backtest(data_path, symbol, initial_balance=10000):
    """Fungsi utama untuk menjalankan simulasi backtesting."""
    
    print(f"Memulai backtest MA_CROSSOVER untuk simbol: {symbol}")
    # Kode baru yang disarankan
    LOT_SIZE = 0.01 # Definisikan ukuran lot di satu tempat
    multiplier = get_profit_multiplier(symbol, LOT_SIZE)
    print(f"Multiplier profit yang digunakan: {multiplier}")

    # 1. Muat dan siapkan data historis
    df = pd.read_csv(data_path, parse_dates=['time'])
    
    # --- Parameter Strategi ---
    FAST_MA = 20
    SLOW_MA = 50
    
    # Hitung indikator
    df.ta.sma(length=FAST_MA, append=True)
    df.ta.sma(length=SLOW_MA, append=True)
    
    fast_ma_col = f'SMA_{FAST_MA}'
    slow_ma_col = f'SMA_{SLOW_MA}'
    
    # 2. Siapkan variabel untuk simulasi
    balance = initial_balance
    position = None
    trades = []
    equity_curve = []

    print("Memulai Loop Backtest...")
    # 3. Loop utama
    for i in range(1, len(df)):
        current_row = df.iloc[i]
        prev_row = df.iloc[i - 1]
        
        # --- Simulasi Logika Exit ---
        if position:
            # Sinyal keluar untuk BUY adalah Death Cross
            if position['type'] == 'BUY' and prev_row[fast_ma_col] > prev_row[slow_ma_col] and current_row[fast_ma_col] < current_row[slow_ma_col]:
                # --- PERBAIKAN DI SINI ---
                profit = (current_row['close'] - position['entry_price']) * multiplier
                balance += profit
                trades.append({'profit': profit})
                position = None

            # Sinyal keluar untuk SELL adalah Golden Cross
            elif position['type'] == 'SELL' and prev_row[fast_ma_col] < prev_row[slow_ma_col] and current_row[fast_ma_col] > current_row[slow_ma_col]:
                # --- PERBAIKAN DI SINI ---
                profit = (position['entry_price'] - current_row['close']) * multiplier
                balance += profit
                trades.append({'profit': profit})
                position = None

        # --- Simulasi Logika Entry ---
        if not position:
            # Golden Cross (Sinyal BELI)
            if prev_row[fast_ma_col] <= prev_row[slow_ma_col] and current_row[fast_ma_col] > current_row[slow_ma_col]:
                position = {'type': 'BUY', 'entry_price': current_row['close']}
            # Death Cross (Sinyal JUAL)
            elif prev_row[fast_ma_col] >= prev_row[slow_ma_col] and current_row[fast_ma_col] < current_row[slow_ma_col]:
                position = {'type': 'SELL', 'entry_price': current_row['close']}
        
        equity_curve.append(balance)

    # 4. Analisis Hasil
    print("\n--- Backtest Selesai ---")
    print(f"Balance Awal: ${initial_balance:.2f}")
    print(f"Balance Akhir: ${balance:.2f}")
    total_profit = balance - initial_balance
    print(f"Total Profit/Loss: ${total_profit:.2f} ({total_profit/initial_balance*100:.2f}%)")
    print(f"Total Trades: {len(trades)}")
    
    # Tampilkan Grafik Equity
    plt.figure(figsize=(12, 6))
    plt.plot(df['time'].iloc[1:], equity_curve)
    plt.title(f'Equity Curve - Strategi MA_CROSSOVER on {symbol}')
    plt.xlabel('Tanggal')
    plt.ylabel('Balance ($)')
    plt.grid(True)
    plt.show()

# --- Jalankan Backtest ---
if __name__ == '__main__':
    # --- KONFIGURASI PENGUJIAN ---
    symbol_to_test = "XAUUSD" # Ubah ini ke "EURUSD" jika ingin menguji EURUSD
    # Gunakan nama file yang sesuai dengan data yang Anda download
    file_name = "lab/XAUUSD_16385_data.csv" 
    
    run_backtest(file_name, symbol=symbol_to_test)