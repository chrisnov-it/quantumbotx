import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

def get_profit_multiplier(symbol, lot_size=0.01):
    if "500" in symbol or "100" in symbol or "30" in symbol:
        return 1 * lot_size
    elif "XAU" in symbol:
        return 100 * lot_size
    elif "JPY" in symbol:
        return 1000 * lot_size
    else:
        return 100000 * lot_size

def run_bb_rsi_backtest(data_path, symbol, initial_balance=10000):
    print(f"Memulai backtest BBANDS + RSI untuk simbol: {symbol}")
    LOT_SIZE = 0.01
    multiplier = get_profit_multiplier(symbol, LOT_SIZE)
    print(f"Multiplier profit yang digunakan: {multiplier}")

    df = pd.read_csv(data_path, parse_dates=['time'])
    df.ta.bbands(length=20, std=2.0, append=True)
    df["rsi"] = ta.rsi(df["close"], length=14)
    df.dropna(inplace=True)

    balance, position, trades, equity_curve = initial_balance, None, [], []
    cooldown = 0

    print("Memulai Loop Backtest...")
    for i in range(1, len(df)):
        current = df.iloc[i]
        if cooldown > 0:
            cooldown -= 1
            equity_curve.append(balance)
            continue

        # Exit logic
        if position:
            if position['type'] == 'BUY' and current['close'] >= current['BBM_20_2.0']:
                profit = (current['close'] - position['entry_price']) * multiplier
                balance += profit
                trades.append({'type': 'BUY', 'profit': profit})
                position = None
                cooldown = 3
            elif position['type'] == 'SELL' and current['close'] <= current['BBM_20_2.0']:
                profit = (position['entry_price'] - current['close']) * multiplier
                balance += profit
                trades.append({'type': 'SELL', 'profit': profit})
                position = None
                cooldown = 3

        # Entry logic
        if not position:
            if current['low'] <= current['BBL_20_2.0'] and current['rsi'] < 30:
                position = {'type': 'BUY', 'entry_price': current['close']}
            elif current['high'] >= current['BBU_20_2.0'] and current['rsi'] > 70:
                position = {'type': 'SELL', 'entry_price': current['close']}

        equity_curve.append(balance)

    # Output Summary
    print("\n--- Backtest Selesai ---")
    print(f"Balance Awal     : ${initial_balance:.2f}")
    print(f"Balance Akhir    : ${balance:.2f}")
    total_profit = balance - initial_balance
    print(f"Total Profit/Loss: ${total_profit:.2f} ({total_profit/initial_balance*100:.2f}%)")
    print(f"Total Trades     : {len(trades)}")

    wins = [t['profit'] for t in trades if t['profit'] > 0]
    losses = [t['profit'] for t in trades if t['profit'] <= 0]
    winrate = len(wins) / len(trades) * 100 if trades else 0
    profit_factor = sum(wins) / abs(sum(losses)) if losses else float('inf')
    avg_win = pd.Series(wins).mean() if wins else 0
    avg_loss = pd.Series(losses).mean() if losses else 0

    print(f"Win Rate         : {winrate:.2f}%")
    print(f"Profit Factor    : {profit_factor:.2f}")
    print(f"Avg Win / Loss   : ${avg_win:.2f} / ${avg_loss:.2f}")

    # Equity Curve
    plt.figure(figsize=(12, 6))
    plt.plot(df['time'].iloc[-len(equity_curve):], equity_curve, label='Equity Curve')
    plt.title(f'Equity Curve - BBANDS + RSI on {symbol}')
    plt.xlabel('Tanggal')
    plt.ylabel('Balance ($)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    symbol_to_test = "USDJPY"  # Ganti dengan EURUSD, USDJPY, dll
    file_name = "lab/USDJPY_16385_data.csv"
    run_bb_rsi_backtest(file_name, symbol=symbol_to_test)
