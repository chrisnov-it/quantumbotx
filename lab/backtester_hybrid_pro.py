# lab/backtester_hybrid_pro.py
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from pathlib import Path

def get_profit_multiplier(symbol, lot_size=0.01):
    if "500" in symbol or "100" in symbol or "30" in symbol: return 1 * lot_size
    elif "XAU" in symbol: return 100 * lot_size
    elif "JPY" in symbol: return 1000 * lot_size
    else: return 100000 * lot_size

def run_hybrid_pro_backtest(data_path, symbol, strategy_params, initial_balance=10000):
    """
    Menjalankan backtest untuk strategi QuantumBotX Hybrid versi Pro
    dengan parameter yang dapat dikonfigurasi.
    """
    print(f"Memulai backtest HYBRID PRO untuk simbol: {symbol}")
    print(f"Parameter yang digunakan: {strategy_params}")
    
    LOT_SIZE = 0.01
    multiplier = get_profit_multiplier(symbol, LOT_SIZE)
    df = pd.read_csv(data_path, parse_dates=['time'])

    # --- Ambil Parameter Dinamis dari Argumen Fungsi ---
    adx_period = strategy_params.get('adx_period', 14)
    adx_threshold = strategy_params.get('adx_threshold', 25)
    ma_fast_period = strategy_params.get('ma_fast_period', 20)
    ma_slow_period = strategy_params.get('ma_slow_period', 50)
    bb_length = strategy_params.get('bb_length', 20)
    bb_std = strategy_params.get('bb_std', 2.0)

    # --- Hitung Indikator ---
    df.ta.adx(length=adx_period, append=True)
    df[f'SMA_{ma_fast_period}'] = ta.sma(df['close'], length=ma_fast_period)
    df[f'SMA_{ma_slow_period}'] = ta.sma(df['close'], length=ma_slow_period)
    df.ta.bbands(length=bb_length, std=bb_std, append=True)
    
    df.dropna(inplace=True)
    df = df.reset_index(drop=True)

    # --- Siapkan Nama Kolom Dinamis ---
    adx_col = f'ADX_{adx_period}'
    ma_fast_col = f'SMA_{ma_fast_period}'
    ma_slow_col = f'SMA_{ma_slow_period}'
    bbu_col = f'BBU_{bb_length}_{bb_std:.1f}'
    bbl_col = f'BBL_{bb_length}_{bb_std:.1f}'

    # --- Siapkan Variabel Simulasi ---
    balance, position, trades, equity_curve = initial_balance, None, [], []

    print("Memulai Loop Backtest...")
    for i in range(1, len(df)):
        current, prev = df.iloc[i], df.iloc[i-1]
        
        adx_value = current[adx_col]

        # --- Logika Adaptif ---
        if adx_value > adx_threshold: # Mode Trending
            if position and position['strategy'] == 'Bollinger': # Keluar dari posisi Bollinger jika tren dimulai
                 profit = (current['close'] - position['entry_price']) * multiplier if position['type'] == 'BUY' else (position['entry_price'] - current['close']) * multiplier
                 balance += profit; trades.append({'profit': profit}); position = None
            
            if not position: # Entry MA Crossover
                if prev[ma_fast_col] <= prev[ma_slow_col] and current[ma_fast_col] > current[ma_slow_col]:
                    position = {'type': 'BUY', 'entry_price': current['close'], 'strategy': 'MA_Crossover'}
                elif prev[ma_fast_col] >= prev[ma_slow_col] and current[ma_fast_col] < current[ma_slow_col]:
                    position = {'type': 'SELL', 'entry_price': current['close'], 'strategy': 'MA_Crossover'}

        elif adx_value < adx_threshold: # Mode Ranging
            if position and position['strategy'] == 'MA_Crossover': # Keluar dari posisi MA jika pasar sideways
                profit = (current['close'] - position['entry_price']) * multiplier if position['type'] == 'BUY' else (position['entry_price'] - current['close']) * multiplier
                balance += profit; trades.append({'profit': profit}); position = None

            if not position: # Entry Bollinger Bands
                if current['low'] <= current[bbl_col]:
                    position = {'type': 'BUY', 'entry_price': current['close'], 'strategy': 'Bollinger'}
                elif current['high'] >= current[bbu_col]:
                    position = {'type': 'SELL', 'entry_price': current['close'], 'strategy': 'Bollinger'}
        
        equity_curve.append(balance)

    # --- Analisis Hasil ---
    print("\n--- Backtest Selesai ---")
    print(f"Balance Awal: ${initial_balance:.2f}")
    print(f"Balance Akhir: ${balance:.2f}")
    print(f"Total Profit/Loss: ${balance - initial_balance:.2f} ({(balance - initial_balance)/initial_balance*100:.2f}%)")
    print(f"Total Trades: {len(trades)}")
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['time'].iloc[1:], equity_curve)
    plt.title(f'Equity Curve - HYBRID PRO on {symbol}')
    plt.xlabel('Tanggal')
    plt.ylabel('Balance ($)')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    # --- PUSAT KONTROL EKSPERIMEN ---
    
    # Definisikan parameter yang ingin diuji.
    # Ini sama seperti `get_definable_params` di strategi Anda.
    params_to_test = {
        "adx_period": 14,
        "adx_threshold": 25,
        "ma_fast_period": 20,
        "ma_slow_period": 50,
        "bb_length": 20,
        "bb_std": 2.0
    }

    # Pilih pasar yang ingin diuji
    symbol_to_test = "EURUSD" 
    data_folder = Path(__file__).parent.resolve() # Otomatis mencari di folder 'lab/'
    file_name = data_folder / f"{symbol_to_test}_16385_data.csv"

    # Jalankan backtest dengan parameter dan pasar yang dipilih
    run_hybrid_pro_backtest(str(file_name), symbol=symbol_to_test, strategy_params=params_to_test)