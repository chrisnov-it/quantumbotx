# backtester_hybrid.py
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

def get_profit_multiplier(symbol, lot_size=0.01):
    if "USD" in symbol and "XAU" not in symbol: return 100000 * lot_size
    elif "XAU" in symbol: return 100 * lot_size
    else: return 1

def run_hybrid_backtest(data_path, symbol, initial_balance=10000):
    print(f"Memulai backtest QUANTUMBOTX HYBRID untuk simbol: {symbol}")
    multiplier = get_profit_multiplier(symbol)
    df = pd.read_csv(data_path, parse_dates=['time'])

    # --- Hitung SEMUA Indikator yang Dibutuhkan ---
    # Indikator untuk "Wasit Pasar"
    df.ta.adx(length=14, append=True)
    
    # Indikator untuk Pemain #1: MA Crossover
    df['SMA_20'] = ta.sma(df['close'], length=20)
    df['SMA_50'] = ta.sma(df['close'], length=50)
    
    # Indikator untuk Pemain #2: Bollinger Bands
    df.ta.bbands(length=20, std=2.0, append=True)
    
    df.dropna(inplace=True)
    df = df.reset_index(drop=True)

    # --- Siapkan Variabel Simulasi ---
    balance, position, trades, equity_curve = initial_balance, None, [], []

    print("Memulai Loop Backtest...")
    for i in range(1, len(df)):
        current = df.iloc[i]
        prev = df.iloc[i-1]
        
        # --- Tahap 1: "Wasit" Menganalisis Pasar ---
        adx_value = current['ADX_14']

        # --- Tahap 2: Pilih Pemain Berdasarkan Kondisi Pasar ---
        
        # KONDISI 1: PASAR SEDANG TRENDING (ADX > 25)
        if adx_value > 25:
            # Gunakan Logika MA_CROSSOVER
            if position: # Logika Exit
                if position['type'] == 'BUY' and prev['SMA_20'] > prev['SMA_50'] and current['SMA_20'] < current['SMA_50']:
                    profit = (current['close'] - position['entry_price']) * multiplier
                    balance += profit; trades.append({'profit': profit}); position = None
                elif position['type'] == 'SELL' and prev['SMA_20'] < prev['SMA_50'] and current['SMA_20'] > current['SMA_50']:
                    profit = (position['entry_price'] - current['close']) * multiplier
                    balance += profit; trades.append({'profit': profit}); position = None
            if not position: # Logika Entry
                if prev['SMA_20'] <= prev['SMA_50'] and current['SMA_20'] > current['SMA_50']:
                    position = {'type': 'BUY', 'entry_price': current['close']}
                elif prev['SMA_20'] >= prev['SMA_50'] and current['SMA_20'] < current['SMA_50']:
                    position = {'type': 'SELL', 'entry_price': current['close']}

        # KONDISI 2: PASAR SEDANG SIDEWAYS (ADX < 25)
        elif adx_value < 25:
            # Gunakan Logika BOLLINGER BANDS
            if position: # Logika Exit
                if position['type'] == 'BUY' and current['close'] >= current['BBM_20_2.0']:
                    profit = (current['close'] - position['entry_price']) * multiplier
                    balance += profit; trades.append({'profit': profit}); position = None
                elif position['type'] == 'SELL' and current['close'] <= current['BBM_20_2.0']:
                    profit = (position['entry_price'] - current['close']) * multiplier
                    balance += profit; trades.append({'profit': profit}); position = None
            if not position: # Logika Entry
                if current['low'] <= current['BBL_20_2.0']:
                    position = {'type': 'BUY', 'entry_price': current['close']}
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
    plt.title(f'Equity Curve - Strategi QUANTUMBOTX HYBRID on {symbol}')
    plt.xlabel('Tanggal')
    plt.ylabel('Balance ($)')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    symbol_to_test = "EURUSD"
    file_name = "EURUSD_16385_data.csv"
    run_hybrid_backtest(file_name, symbol=symbol_to_test)