# backtester_turtle.py
import pandas as pd
import matplotlib.pyplot as plt

def get_profit_multiplier(symbol, lot_size=0.01):
    if "USD" in symbol and "XAU" not in symbol: return 100000 * lot_size
    elif "XAU" in symbol: return 100 * lot_size
    else: return 1

def run_turtle_backtest(data_path, symbol, initial_balance=10000):
    print(f"Memulai backtest TURTLE BREAKOUT untuk simbol: {symbol}")
    multiplier = get_profit_multiplier(symbol)
    df = pd.read_csv(data_path, parse_dates=['time'])

    # --- Hitung Channel untuk Entry dan Exit ---
    # Channel untuk sinyal masuk (periode 20)
    # .shift(1) SANGAT PENTING untuk mencegah "melihat ke masa depan"
    df['entry_upper'] = df['high'].rolling(window=20).max().shift(1)
    df['entry_lower'] = df['low'].rolling(window=20).min().shift(1)
    
    # Channel untuk sinyal keluar (periode 10)
    df['exit_upper'] = df['high'].rolling(window=10).max().shift(1)
    df['exit_lower'] = df['low'].rolling(window=10).min().shift(1)
    
    df.dropna(inplace=True)
    df = df.reset_index(drop=True) # Reset index setelah dropna

    # --- Siapkan Variabel Simulasi ---
    balance, position, trades, equity_curve = initial_balance, None, [], []

    print("Memulai Loop Backtest...")
    for i in range(len(df)):
        current = df.iloc[i]
        
        # --- Logika Exit ---
        if position:
            if position['type'] == 'BUY' and current['close'] < current['exit_lower']:
                profit = (current['close'] - position['entry_price']) * multiplier
                balance += profit; trades.append({'profit': profit}); position = None
            elif position['type'] == 'SELL' and current['close'] > current['exit_upper']:
                profit = (position['entry_price'] - current['close']) * multiplier
                balance += profit; trades.append({'profit': profit}); position = None

        # --- Logika Entry (Hanya jika tidak ada posisi) ---
        if not position:
            # Sinyal BELI: Harga menembus ke atas channel 20 periode
            if current['close'] > current['entry_upper']:
                position = {'type': 'BUY', 'entry_price': current['close']}
            # Sinyal JUAL: Harga menembus ke bawah channel 20 periode
            elif current['close'] < current['entry_lower']:
                position = {'type': 'SELL', 'entry_price': current['close']}
        
        equity_curve.append(balance)

    # --- Analisis Hasil ---
    print("\n--- Backtest Selesai ---")
    print(f"Balance Awal: ${initial_balance:.2f}")
    print(f"Balance Akhir: ${balance:.2f}")
    print(f"Total Profit/Loss: ${balance - initial_balance:.2f} ({(balance - initial_balance)/initial_balance*100:.2f}%)")
    print(f"Total Trades: {len(trades)}")
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['time'], equity_curve)
    plt.title(f'Equity Curve - Strategi TURTLE BREAKOUT on {symbol}')
    plt.xlabel('Tanggal')
    plt.ylabel('Balance ($)')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    # UJI COBA #1: Di pasar tren (XAUUSD)
    symbol_to_test = "XAUUSD"
    file_name = "XAUUSD_16385_data.csv"
    
    # UJI COBA #2: Di pasar sideways (EURUSD)
    #symbol_to_test = "EURUSD"
    #file_name = "EURUSD_16385_data.csv"
    
    run_turtle_backtest(file_name, symbol=symbol_to_test)