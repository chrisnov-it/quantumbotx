# backtester_mercy_trend.py
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

def get_profit_multiplier(symbol, lot_size=0.01):
    if "USD" in symbol and "XAU" not in symbol: return 100000 * lot_size
    elif "XAU" in symbol: return 100 * lot_size
    else: return 1

def run_mercy_trend_backtest(h1_data_path, symbol, initial_balance=10000):
    print(f"Memulai backtest MERCY_TREND (Technical Base) untuk simbol: {symbol}")
    multiplier = get_profit_multiplier(symbol)

    # Tahap 1 & 2: Load dan siapkan data (sama seperti Full Mercy)
    df_h1 = pd.read_csv(h1_data_path, parse_dates=['time'])
    df_d1 = df_h1.resample('D', on='time').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}).dropna().reset_index()
    df_d1.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)
    df_h1.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)
    df_h1.ta.stoch(high='high', low='low', close='close', k=14, d=3, smooth_k=3, append=True)

    # Tahap 3: Gabungkan data
    df_d1_indicator = df_d1[['time', 'MACDh_12_26_9']].rename(columns={'MACDh_12_26_9': 'D1_MACDh'})
    df_d1_indicator['date_key'] = df_d1_indicator['time'].dt.date
    df_h1['date_key'] = df_h1['time'].dt.date
    df_merged = pd.merge(df_h1, df_d1_indicator[['date_key', 'D1_MACDh']], on='date_key', how='left')
    df_merged['D1_MACDh'] = df_merged['D1_MACDh'].ffill()
    df_merged.dropna(inplace=True)

    # Tahap 4: Simulasi
    balance, position, trades, equity_curve = initial_balance, None, [], []

    print("Memulai Loop Backtest...")
    for i in range(1, len(df_merged)):
        current, prev = df_merged.iloc[i], df_merged.iloc[i - 1]
        
        # Logika Exit
        if position:
            is_buy_pos = position['type'] == 'BUY'
            if is_buy_pos and prev['STOCHk_14_3_3'] > prev['STOCHd_14_3_3'] and current['STOCHk_14_3_3'] < current['STOCHd_14_3_3']:
                profit = (current['close'] - position['entry_price']) * multiplier
                balance += profit; trades.append({'profit': profit}); position = None
            elif not is_buy_pos and prev['STOCHk_14_3_3'] < prev['STOCHd_14_3_3'] and current['STOCHk_14_3_3'] > current['STOCHd_14_3_3']:
                profit = (position['entry_price'] - current['close']) * multiplier
                balance += profit; trades.append({'profit': profit}); position = None
        
        # Logika Entry (Sesuai sinyal TA dari Mercy Edge)
        if not position:
            is_buy_signal = (current['D1_MACDh'] > 0 and current['MACDh_12_26_9'] > 0 and current['STOCHk_14_3_3'] > current['STOCHd_14_3_3'] and prev['STOCHk_14_3_3'] <= prev['STOCHd_14_3_3'])
            is_sell_signal = (current['D1_MACDh'] < 0 and current['MACDh_12_26_9'] < 0 and current['STOCHk_14_3_3'] < current['STOCHd_14_3_3'] and prev['STOCHk_14_3_3'] >= prev['STOCHd_14_3_3'])
            if is_buy_signal:
                position = {'type': 'BUY', 'entry_price': current['close']}
            elif is_sell_signal:
                position = {'type': 'SELL', 'entry_price': current['close']}
        
        equity_curve.append(balance)

    # Tahap 5: Analisis
    print("\n--- Backtest Selesai ---")
    print(f"Balance Awal: ${initial_balance:.2f}")
    print(f"Balance Akhir: ${balance:.2f}")
    print(f"Total Profit/Loss: ${balance - initial_balance:.2f} ({(balance - initial_balance)/initial_balance*100:.2f}%)")
    print(f"Total Trades: {len(trades)}")
    
    plt.figure(figsize=(12, 6))
    plt.plot(df_merged['time'].iloc[1:], equity_curve)
    plt.title(f'Equity Curve - Strategi MERCY_TREND (TA Base) on {symbol}')
    plt.xlabel('Tanggal')
    plt.ylabel('Balance ($)')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    symbol_to_test = "EURUSD"
    file_name = "lab/EURUSD_16385_data.csv"
    run_mercy_trend_backtest(file_name, symbol=symbol_to_test)