# backtester.py

import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import os

def get_profit_multiplier(symbol, lot_size=0.01):
    """
    Mengembalikan multiplier yang benar untuk perhitungan profit berdasarkan
    simbol, kelas aset, dan ukuran lot.
    """
    if "500" in symbol or "100" in symbol or "30" in symbol:
        return 1 * lot_size
    elif "XAU" in symbol:
        return 100 * lot_size
    else:
        if "JPY" in symbol:
            return 1000 * lot_size
        else:
            return 100000 * lot_size

def run_backtest(data_path, symbol, initial_balance=10000, lot_size=0.01):
    df = pd.read_csv(data_path, parse_dates=['time'])

    # Tambahkan indikator teknikal (contoh: SMA 20 & SMA 50)
    df['sma_20'] = ta.sma(df['close'], length=20)
    df['sma_50'] = ta.sma(df['close'], length=50)

    # Logika strategi sederhana (golden cross)
    df['signal'] = 0
    df.loc[df['sma_20'] > df['sma_50'], 'signal'] = 1
    df.loc[df['sma_20'] < df['sma_50'], 'signal'] = -1

    # Hitung perubahan harga dan profit
    df['price_change'] = df['close'].diff()
    multiplier = get_profit_multiplier(symbol, lot_size)
    df['profit'] = df['price_change'] * df['signal'].shift(1) * multiplier
    df['balance'] = initial_balance + df['profit'].cumsum()

    # Plot hasil backtest
    plt.figure(figsize=(14, 6))
    plt.plot(df['time'], df['balance'], label='Equity Curve')
    plt.title(f'Backtest Result - {symbol}')
    plt.xlabel('Time')
    plt.ylabel('Balance ($)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Ganti nama file sesuai file CSV yang kamu download
    file_name = "XAUUSD_16385_data.csv"
    symbol = "XAUUSD"  # Ganti dengan simbol yang sesuai
    
    # Pastikan path benar
    data_path = os.path.join(os.path.dirname(__file__), file_name)
    
    if os.path.exists(data_path):
        run_backtest(data_path, symbol)
    else:
        print(f"File {file_name} tidak ditemukan!")
