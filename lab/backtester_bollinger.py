# backtester_bollinger.py
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

def run_bollinger_backtest(data_path, symbol, initial_balance=10000):
    print(f"Memulai backtest BOLLINGER BANDS untuk simbol: {symbol}")
    # Kode baru yang disarankan
    LOT_SIZE = 0.01 # Definisikan ukuran lot di satu tempat
    multiplier = get_profit_multiplier(symbol, LOT_SIZE)
    df = pd.read_csv(data_path, parse_dates=['time'])

    # --- Hitung Indikator ---
    df.ta.bbands(length=20, std=2.0, append=True)
    df.dropna(inplace=True)

    # --- Siapkan Variabel Simulasi ---
    balance, position, trades, equity_curve = initial_balance, None, [], []

    print("Memulai Loop Backtest...")
    for i in range(1, len(df)):
        current = df.iloc[i]
        
        # --- Logika Exit (Keluar jika menyentuh MA tengah) ---
        if position:
            if position['type'] == 'BUY' and current['close'] >= current['BBM_20_2.0']:
                profit = (current['close'] - position['entry_price']) * multiplier
                balance += profit; trades.append({'profit': profit}); position = None
            elif position['type'] == 'SELL' and current['close'] <= current['BBM_20_2.0']:
                profit = (position['entry_price'] - current['close']) * multiplier
                balance += profit; trades.append({'profit': profit}); position = None

        # --- Logika Entry (Hanya jika tidak ada posisi) ---
        if not position:
            # Sinyal BELI: Harga menyentuh atau menembus band bawah
            if current['low'] <= current['BBL_20_2.0']:
                position = {'type': 'BUY', 'entry_price': current['close']}
            # Sinyal JUAL: Harga menyentuh atau menembus band atas
            elif current['high'] >= current['BBU_20_2.0']:
                position = {'type': 'SELL', 'entry_price': current['close']}
        
        equity_curve.append(balance)

    # --- Analisis Hasil ---
    print("\n--- Backtest Selesai ---")
    print(f"Balance Awal: ${initial_balance:.2f}")
    print(f"Balance Akhir: ${balance:.2f}")
    print(f"Total Profit/Loss: ${balance - initial_balance:.2f} ({(balance - initial_balance)/initial_balance*100:.2f}%)")
    print(f"Total Trades: {len(trades)}")
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['time'].iloc[1:], equity_curve)
    plt.title(f'Equity Curve - Strategi BOLLINGER BANDS on {symbol}')
    plt.xlabel('Tanggal')
    plt.ylabel('Balance ($)')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    symbol_to_test = "XAUUSD"  # Ganti dengan simbol yang ingin diuji
    file_name = "lab/XAUUSD_16385_data.csv"
    run_bollinger_backtest(file_name, symbol=symbol_to_test)