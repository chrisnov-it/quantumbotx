# backtester_full_mercy.py
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

def run_full_mercy_backtest(h1_data_path, symbol, initial_balance=10000):
    """
    Fungsi utama untuk menjalankan simulasi backtesting
    untuk strategi multi-timeframe "Full Mercy".
    """
    print(f"Memulai backtest FULL MERCY untuk simbol: {symbol}")
    # Kode baru yang disarankan
    LOT_SIZE = 0.01 # Definisikan ukuran lot di satu tempat
    multiplier = get_profit_multiplier(symbol, LOT_SIZE)
    print(f"Multiplier profit yang digunakan: {multiplier}")
    
    # ... (kode dari Tahap 1 sampai 4 tetap sama persis) ...
    print("1. Memuat data H1...")
    df_h1 = pd.read_csv(h1_data_path, parse_dates=['time'])
    if df_h1.empty:
        print("Gagal memuat data H1. Keluar.")
        return

    print("2. Membuat data D1 dari data H1 (Resampling)...")
    df_d1 = df_h1.resample('D', on='time').agg({
        'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'
    }).dropna().reset_index()

    print("3. Menghitung indikator MACD di D1 dan H1...")
    df_d1.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)
    df_h1.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)
    df_h1.ta.stoch(high='high', low='low', close='close', k=14, d=3, smooth_k=3, append=True)

    print("4. Menggabungkan data D1 dan H1...")
    df_d1_indicator = df_d1[['time', 'MACDh_12_26_9']].rename(columns={'MACDh_12_26_9': 'D1_MACDh'})
    df_d1_indicator['date_key'] = df_d1_indicator['time'].dt.date
    df_h1['date_key'] = df_h1['time'].dt.date
    df_merged = pd.merge(df_h1, df_d1_indicator[['date_key', 'D1_MACDh']], on='date_key', how='left')
    df_merged['D1_MACDh'] = df_merged['D1_MACDh'].ffill()
    df_merged.dropna(inplace=True)

    balance, position, trades, equity_curve = initial_balance, None, [], []

    print("5. Memulai loop backtest...")
    for i in range(1, len(df_merged)):
        current, prev = df_merged.iloc[i], df_merged.iloc[i - 1]
        
        if position:
            is_buy_pos = position['type'] == 'BUY'
            
            if is_buy_pos and prev['STOCHk_14_3_3'] > prev['STOCHd_14_3_3'] and current['STOCHk_14_3_3'] < current['STOCHd_14_3_3']:
                # --- PERBAIKAN DI SINI ---
                profit = (current['close'] - position['entry_price']) * multiplier
                balance += profit
                trades.append({'profit': profit})
                position = None
            elif not is_buy_pos and prev['STOCHk_14_3_3'] < prev['STOCHd_14_3_3'] and current['STOCHk_14_3_3'] > current['STOCHd_14_3_3']:
                # --- PERBAIKAN DI SINI ---
                profit = (position['entry_price'] - current['close']) * multiplier
                balance += profit
                trades.append({'profit': profit})
                position = None

        if not position:
            is_buy_signal = (current['D1_MACDh'] > 0 and current['MACDh_12_26_9'] > 0 and current['STOCHk_14_3_3'] > current['STOCHd_14_3_3'] and prev['STOCHk_14_3_3'] <= prev['STOCHd_14_3_3'])
            is_sell_signal = (current['D1_MACDh'] < 0 and current['MACDh_12_26_9'] < 0 and current['STOCHk_14_3_3'] < current['STOCHd_14_3_3'] and prev['STOCHk_14_3_3'] >= prev['STOCHd_14_3_3'])
            if is_buy_signal:
                position = {'type': 'BUY', 'entry_price': current['close']}
            elif is_sell_signal:
                position = {'type': 'SELL', 'entry_price': current['close']}
        
        equity_curve.append(balance)

    print("\n--- Backtest Selesai ---")
    print(f"Balance Awal: ${initial_balance:.2f}")
    print(f"Balance Akhir: ${balance:.2f}")
    total_profit = balance - initial_balance
    print(f"Total Profit/Loss: ${total_profit:.2f} ({total_profit/initial_balance*100:.2f}%)")
    print(f"Total Trades: {len(trades)}")
    
    plt.figure(figsize=(12, 6))
    plt.plot(df_merged['time'].iloc[1:], equity_curve)
    plt.title(f'Equity Curve - Strategi "Full Mercy" on {symbol}')
    plt.xlabel('Tanggal')
    plt.ylabel('Balance ($)')
    plt.grid(True)
    plt.show()

# --- Jalankan Backtest ---
if __name__ == '__main__':
    # Sekarang kita perlu memberi tahu backtester simbol apa yang sedang diuji
    symbol_to_test = "US500" # Ubah ini ke "EURUSD" jika ingin menguji EURUSD
    file_name = "lab/US500_16385_data.csv" # Pastikan nama file cocok
    
    run_full_mercy_backtest(file_name, symbol=symbol_to_test)