# backtester_trend_dip.py
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

def run_trend_dip_backtest(data_path, symbol, initial_balance=10000):
    """
    Menjalankan backtest untuk strategi "Trend & Dip", yang dirancang khusus
    untuk pasar saham/indeks dengan bias bullish jangka panjang.
    """
    print(f"Memulai backtest TREND & DIP untuk simbol: {symbol}")
    # Kode baru yang disarankan
    LOT_SIZE = 0.01 # Definisikan ukuran lot di satu tempat
    multiplier = get_profit_multiplier(symbol, LOT_SIZE)
    df = pd.read_csv(data_path, parse_dates=['time'])

    # --- Hitung Indikator ---
    # 1. "Wasit" Tren Jangka Panjang: SMA 200
    df['SMA_200'] = ta.sma(df['close'], length=200)
    
    # 2. "Pemicu" Entry/Exit Jangka Pendek: RSI 14
    df['RSI_14'] = ta.rsi(df['close'], length=14)

    df.dropna(inplace=True)
    df = df.reset_index(drop=True)

    # --- Siapkan Variabel Simulasi ---
    balance, position, trades, equity_curve = initial_balance, None, [], []

    print("Memulai Loop Backtest...")
    for i in range(1, len(df)): # Mulai dari 1 agar bisa akses `prev`
        current = df.iloc[i]
        prev = df.iloc[i-1]
        
        # --- Logika Exit (Keluar jika pasar sudah "panas" kembali) ---
        if position:
            # Keluar dari posisi Beli jika RSI cross ke atas 70
            if position['type'] == 'BUY' and prev['RSI_14'] <= 70 and current['RSI_14'] > 70:
                profit = (current['close'] - position['entry_price']) * multiplier
                balance += profit
                trades.append({'profit': profit})
                position = None
        
        # --- Logika Entry (SANGAT SELEKTIF) ---
        if not position:
            # Kondisi 1: Apakah kita di "Musim Bullish"? (Harga di atas SMA 200)
            is_bull_market = current['close'] > current['SMA_200']
            
            # Kondisi 2: Apakah ada "Diskon"? (RSI baru saja turun di bawah 40)
            is_dip_signal = prev['RSI_14'] >= 40 and current['RSI_14'] < 40
            
            # Hanya buka posisi Beli jika KEDUA kondisi terpenuhi
            if is_bull_market and is_dip_signal:
                position = {'type': 'BUY', 'entry_price': current['close']}
        
        # Strategi ini TIDAK membuka posisi JUAL (short).
        # Ini adalah fitur desain untuk menghormati bias bullish pasar saham.
        
        equity_curve.append(balance)

    # --- Analisis Hasil ---
    print("\n--- Backtest Selesai ---")
    print(f"Balance Awal: ${initial_balance:.2f}")
    print(f"Balance Akhir: ${balance:.2f}")
    print(f"Total Profit/Loss: ${balance - initial_balance:.2f} ({(balance - initial_balance)/initial_balance*100:.2f}%)")
    print(f"Total Trades: {len(trades)}")
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['time'].iloc[1:], equity_curve)
    plt.title(f'Equity Curve - Strategi TREND & DIP on {symbol}')
    plt.xlabel('Tanggal')
    plt.ylabel('Balance ($)')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    # Ganti ini untuk menguji Indeks yang berbeda
    symbol_to_test = "US500" # atau "SP500m", "ND100m", dll.
    file_name = "lab/US500_16385_data.csv" # Pastikan nama file cocok
    
    run_trend_dip_backtest(file_name, symbol=symbol_to_test)