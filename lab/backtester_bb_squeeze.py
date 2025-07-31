# backtester_bb_squeeze.py
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

def get_profit_multiplier(symbol, lot_size=0.01):
    if "USD" in symbol and "XAU" not in symbol: return 100000 * lot_size
    elif "XAU" in symbol: return 100 * lot_size
    else: return 1

def run_bb_squeeze_backtest(data_path, symbol, initial_balance=10000):
    print(f"Memulai backtest BOLLINGER BAND SQUEEZE untuk simbol: {symbol}")
    multiplier = get_profit_multiplier(symbol)
    df = pd.read_csv(data_path, parse_dates=['time'])

    # --- Hitung Indikator ---
    # Gunakan parameter standar Bollinger Bands
    df.ta.bbands(length=20, std=2.0, append=True)
    
    # Hitung Lebar Bollinger Band (Band Atas - Band Bawah)
    df['BB_WIDTH'] = df['BBU_20_2.0'] - df['BBL_20_2.0']
    
    # Cari titik terendah dari Lebar Band dalam 120 candle terakhir (sekitar 5 hari di H1)
    df['SQUEEZE_LEVEL'] = df['BB_WIDTH'].rolling(window=120).min()

    df.dropna(inplace=True)
    df = df.reset_index(drop=True)

    # --- Siapkan Variabel Simulasi ---
    balance, position, trades, equity_curve = initial_balance, None, [], []

    print("Memulai Loop Backtest...")
    for i in range(1, len(df)): # Mulai dari 1 agar bisa akses `prev`
        current = df.iloc[i]
        prev = df.iloc[i-1]
        
        # --- Logika Exit (Keluar jika harga kembali cross ke MA tengah) ---
        if position:
            if position['type'] == 'BUY' and current['close'] < current['BBM_20_2.0']:
                profit = (current['close'] - position['entry_price']) * multiplier
                balance += profit; trades.append({'profit': profit}); position = None
            elif position['type'] == 'SELL' and current['close'] > current['BBM_20_2.0']:
                profit = (position['entry_price'] - current['close']) * multiplier
                balance += profit; trades.append({'profit': profit}); position = None

        # --- Logika Entry (Hanya jika tidak ada posisi) ---
        if not position:
            # Kondisi 1: Apakah pasar sedang dalam kondisi "Squeeze"?
            # Kita lihat di candle SEBELUMNYA untuk menghindari melihat masa depan.
            is_in_squeeze = prev['BB_WIDTH'] <= prev['SQUEEZE_LEVEL']
            
            if is_in_squeeze:
                # Kondisi 2: Jika ya, apakah harga SEKARANG breakout?
                # Breakout ke atas (sinyal Beli)
                if current['close'] > prev['BBU_20_2.0']:
                    position = {'type': 'BUY', 'entry_price': current['close']}
                # Breakout ke bawah (sinyal Jual)
                elif current['close'] < prev['BBL_20_2.0']:
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
    plt.title(f'Equity Curve - Strategi BOLLINGER SQUEEZE on {symbol}')
    plt.xlabel('Tanggal')
    plt.ylabel('Balance ($)')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    symbol_to_test = "US500"  # Ganti dengan simbol yang ingin diuji
    file_name = "lab/US500_16385_data.csv"
    run_bb_squeeze_backtest(file_name, symbol=symbol_to_test)