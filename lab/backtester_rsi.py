# backtester_rsi_breakout.py
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

# Kita pinjam fungsi helper dari backtester sebelumnya
def get_profit_multiplier(symbol, lot_size=0.01):
    if "USD" in symbol and "XAU" not in symbol: return 100000 * lot_size
    elif "XAU" in symbol: return 100 * lot_size
    else: return 1

def run_rsi_backtest(data_path, symbol, initial_balance=10000):
    print(f"Memulai backtest RSI_BREAKOUT untuk simbol: {symbol}")
    multiplier = get_profit_multiplier(symbol)
    df = pd.read_csv(data_path, parse_dates=['time'])

    # --- Hitung Indikator ---
    df.ta.rsi(length=14, append=True)
    df.dropna(inplace=True)

    # --- Siapkan Variabel Simulasi ---
    balance, position, trades, equity_curve = initial_balance, None, [], []

    print("Memulai Loop Backtest...")
    for i in range(1, len(df)):
        current = df.iloc[i]
        prev = df.iloc[i-1] # Kita butuh baris sebelumnya untuk deteksi cross
        
        # --- Logika Exit (Sangat Penting untuk RSI) ---
        # Keluar posisi jika RSI kembali ke zona netral (misal: cross 50)
        if position:
            if position['type'] == 'BUY' and prev['RSI_14'] < 50 and current['RSI_14'] >= 50:
                profit = (current['close'] - position['entry_price']) * multiplier
                balance += profit
                trades.append({'profit': profit})
                position = None
            elif position['type'] == 'SELL' and prev['RSI_14'] > 50 and current['RSI_14'] <= 50:
                profit = (position['entry_price'] - current['close']) * multiplier
                balance += profit
                trades.append({'profit': profit})
                position = None

        # --- Logika Entry (Hanya jika tidak ada posisi) ---
        if not position:
            # Sinyal BELI: RSI cross ke bawah 30
            if prev['RSI_14'] >= 30 and current['RSI_14'] < 30:
                position = {'type': 'BUY', 'entry_price': current['close']}
            # Sinyal JUAL: RSI cross ke atas 70
            elif prev['RSI_14'] <= 70 and current['RSI_14'] > 70:
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
    plt.title(f'Equity Curve - Strategi RSI_BREAKOUT on {symbol}')
    plt.xlabel('Tanggal')
    plt.ylabel('Balance ($)')
    plt.grid(True)
    plt.show()

# --- Jalankan Backtest ---
if __name__ == '__main__':
    symbol_to_test = "EURUSD"
    file_name = "lab/EURUSD_16385_data.csv"
    run_rsi_backtest(file_name, symbol=symbol_to_test)