# backtester_ichimoku.py
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

def get_profit_multiplier(symbol, lot_size=0.01):
    if "USD" in symbol and "XAU" not in symbol: return 100000 * lot_size
    elif "XAU" in symbol: return 100 * lot_size
    else: return 1

def run_ichimoku_backtest(data_path, symbol, initial_balance=10000):
    print(f"Memulai backtest ICHIMOKU CLOUD untuk simbol: {symbol}")
    multiplier = get_profit_multiplier(symbol)
    df = pd.read_csv(data_path, parse_dates=['time'])

    # --- Hitung Indikator Ichimoku ---
    # Pengaturan standar 9, 26, 52
    df.ta.ichimoku(append=True)
    df.dropna(inplace=True)
    df = df.reset_index(drop=True) # Reset index setelah dropna

    # Nama kolom dari pandas_ta:
    tenkan_col = 'ITS_9'   # Conversion Line
    kijun_col = 'IKS_26'   # Base Line
    span_a_col = 'ISA_9'   # Leading Span A (membentuk Awan)
    span_b_col = 'ISB_26'  # Leading Span B (membentuk Awan)

    # --- Siapkan Variabel Simulasi ---
    balance, position, trades, equity_curve = initial_balance, None, [], []

    print("Memulai Loop Backtest...")
    for i in range(1, len(df)):
        current = df.iloc[i]
        prev = df.iloc[i-1]
        
        # --- Kondisi Awan (Filter Utama) ---
        is_above_cloud = current['close'] > current[span_a_col] and current['close'] > current[span_b_col]
        is_below_cloud = current['close'] < current[span_a_col] and current['close'] < current[span_b_col]
        
        # --- Kondisi Persilangan Tenkan/Kijun (Pemicu) ---
        tk_cross_up = prev[tenkan_col] <= prev[kijun_col] and current[tenkan_col] > current[kijun_col]
        tk_cross_down = prev[tenkan_col] >= prev[kijun_col] and current[tenkan_col] < current[kijun_col]
        
        # --- Logika Exit (Keluar jika ada sinyal berlawanan) ---
        if position:
            if position['type'] == 'BUY' and tk_cross_down:
                profit = (current['close'] - position['entry_price']) * multiplier
                balance += profit; trades.append({'profit': profit}); position = None
            elif position['type'] == 'SELL' and tk_cross_up:
                profit = (position['entry_price'] - current['close']) * multiplier
                balance += profit; trades.append({'profit': profit}); position = None

        # --- Logika Entry (Hanya jika tidak ada posisi) ---
        if not position:
            # Sinyal BELI: Harga di atas Awan DAN terjadi Golden Cross Tenkan/Kijun
            if is_above_cloud and tk_cross_up:
                position = {'type': 'BUY', 'entry_price': current['close']}
            # Sinyal JUAL: Harga di bawah Awan DAN terjadi Death Cross Tenkan/Kijun
            elif is_below_cloud and tk_cross_down:
                position = {'type': 'SELL', 'entry_price': current['close']}
        
        equity_curve.append(balance)

    # --- Analisis Hasil ---
    print("\n--- Backtest Selesai ---")
    print(f"Balance Awal: ${initial_balance:.2f}")
    print(f"Balance Akhir: ${balance:.2f}")
    print(f"Total Profit/Loss: ${balance - initial_balance:.2f} ({(balance - initial_balance)/initial_balance*100:.2f}%)")
    print(f"Total Trades: {len(trades)}")
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['time'].iloc[1:], equity_curve) # Mulai dari 1 karena kita butuh `prev`
    plt.title(f'Equity Curve - Strategi ICHIMOKU CLOUD on {symbol}')
    plt.xlabel('Tanggal')
    plt.ylabel('Balance ($)')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    # UJI COBA #1: Di pasar tren (XAUUSD)
    # symbol_to_test = "XAUUSD"
    # file_name = "XAUUSD_16385_data.csv"
    
    # UJI COBA #2: Di pasar sideways (EURUSD)
    symbol_to_test = "EURUSD"
    file_name = "EURUSD_16385_data.csv"
    
    run_ichimoku_backtest(file_name, symbol=symbol_to_test)