# core/backtesting/engine.py

from core.strategies.strategy_map import STRATEGY_MAP

def run_backtest(strategy_id, params, historical_data_df):
    """
    Menjalankan simulasi backtesting untuk strategi tertentu pada data historis.
    VERSI OPTIMIZED: Indikator dihitung sekali di awal.
    """
    strategy_class = STRATEGY_MAP.get(strategy_id)
    if not strategy_class:
        return {"error": "Strategi tidak ditemukan"}

    # --- LANGKAH 1: Hitung semua indikator SEKALI di awal ---
    class MockBot:
        def __init__(self):
            self.market_for_mt5 = "BACKTEST"
            self.timeframe = "H1"
            self.tf_map = {}

    strategy_instance = strategy_class(bot_instance=MockBot(), params=params)

    # Panggil metode baru 'analyze_df' untuk pra-perhitungan indikator
    df_with_indicators = strategy_instance.analyze_df(historical_data_df.copy())

    if df_with_indicators.empty:
        return {"error": "Gagal menghasilkan data indikator. Periksa panjang data input."}

    strategy_name = strategy_instance.name

    # --- LANGKAH 2: Inisialisasi state backtesting ---
    trades = []
    in_position = False
    initial_capital = 10000
    capital = initial_capital
    equity_curve = [initial_capital]
    peak_equity = initial_capital
    max_drawdown = 0.0
    position_type = None
    entry_price = 0.0
    sl_pips = params.get('sl_pips', 100)
    tp_pips = params.get('tp_pips', 200)

    symbol_name = historical_data_df.columns[0].upper()
    pip_size = 0.0001 # Default untuk Forex standar
    if 'JPY' in symbol_name:
        pip_size = 0.01
    elif 'XAU' in symbol_name or 'XAG' in symbol_name: # Emas atau Perak
        pip_size = 0.01

    # Tentukan nilai per pip berdasarkan simbol (untuk lot 0.01)
    if 'XAU' in symbol_name or 'XAG' in symbol_name: # Emas atau Perak
        # Untuk 0.01 lot (1 oz), pergerakan harga $0.01 = profit/loss $0.01
        value_per_pip = 0.01
    else:
        # Untuk Forex (misal EURUSD), 0.01 lot, pergerakan 1 pip = profit/loss $0.1
        # Ini adalah asumsi umum, untuk JPY pairs nilainya bisa sedikit berbeda
        value_per_pip = 0.1

    # --- LANGKAH 3: Loop melalui data yang sudah ada indikatornya ---
    for i in range(1, len(df_with_indicators)):
        current_bar = df_with_indicators.iloc[i]
        signal = current_bar.get("signal", "HOLD")
        current_price = current_bar['close']

        # Cek SL/TP jika sedang dalam posisi
        if in_position:
            profit = 0
            if position_type == 'BUY':
                profit_pips = (current_price - entry_price) / pip_size
                if current_price <= entry_price - (sl_pips * pip_size):
                    trades.append({'entry': entry_price, 'exit': current_price, 'profit_pips': -sl_pips, 'reason': 'SL'})
                    capital -= sl_pips * value_per_pip
                    in_position = False
                elif current_price >= entry_price + (tp_pips * pip_size):
                    trades.append({'entry': entry_price, 'exit': current_price, 'profit_pips': tp_pips, 'reason': 'TP'})
                    capital += tp_pips * value_per_pip
                    in_position = False
            elif position_type == 'SELL':
                profit_pips = (entry_price - current_price) / pip_size
                if current_price >= entry_price + (sl_pips * pip_size):
                    trades.append({'entry': entry_price, 'exit': current_price, 'profit_pips': -sl_pips, 'reason': 'SL'})
                    capital -= sl_pips * value_per_pip
                    in_position = False
                elif current_price <= entry_price - (tp_pips * pip_size):
                    trades.append({'entry': entry_price, 'exit': current_price, 'profit_pips': tp_pips, 'reason': 'TP'})
                    capital += tp_pips * value_per_pip
                    in_position = False

            if not in_position: # Jika posisi baru saja ditutup
                equity_curve.append(capital)
                peak_equity = max(peak_equity, capital)
                drawdown = (peak_equity - capital) / peak_equity if peak_equity > 0 else 0
                max_drawdown = max(max_drawdown, drawdown)

        # Cek sinyal baru
        if signal == 'BUY' and not in_position:
            in_position = True
            position_type = 'BUY'
            entry_price = current_price
        elif signal == 'SELL' and not in_position:
            in_position = True
            position_type = 'SELL'
            entry_price = current_price
        elif (signal == 'SELL' and in_position and position_type == 'BUY') or \
             (signal == 'BUY' and in_position and position_type == 'SELL'):
            # Sinyal berlawanan, tutup posisi lama
            profit_pips = ((current_price - entry_price) if position_type == 'BUY' else (entry_price - current_price)) / pip_size # Calculate pips
            trades.append({'entry': entry_price, 'exit': current_price, 'profit_pips': profit_pips, 'reason': 'Signal Flip'}) # Log trade
            capital += profit_pips * value_per_pip
            equity_curve.append(capital)
            peak_equity = max(peak_equity, capital)
            drawdown = (peak_equity - capital) / peak_equity if peak_equity > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
            in_position = False

    # Hitung hasil akhir
    total_profit_pips = sum(trade['profit_pips'] for trade in trades)
    wins = len([trade for trade in trades if trade['profit_pips'] > 0])
    losses = len(trades) - wins
    win_rate = (wins / len(trades) * 100) if trades else 0

    return {
        "strategy_name": strategy_name,
        "total_trades": len(trades),
        "total_profit_pips": total_profit_pips,
        "win_rate_percent": win_rate,
        "wins": wins,
        "losses": losses,
        "max_drawdown_percent": max_drawdown * 100,
        "equity_curve": equity_curve,
        "trades": trades[-20:]
    }