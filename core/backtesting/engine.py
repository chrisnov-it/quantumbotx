# core/backtesting/engine.py

from core.strategies.strategy_map import STRATEGY_MAP

def run_backtest(strategy_id, params, historical_data_df):
    """
    Menjalankan simulasi backtesting untuk strategi tertentu pada data historis.
    """
    strategy_class = STRATEGY_MAP.get(strategy_id)
    if not strategy_class:
        return {"error": "Strategi tidak ditemukan"}

    # Inisialisasi state backtesting
    trades = []
    in_position = False
    initial_capital = 10000  # Modal awal virtual $10,000
    capital = initial_capital
    equity_curve = [initial_capital]
    peak_equity = initial_capital
    max_drawdown = 0.0

    position_type = None
    entry_price = 0.0
    sl_pips = params.get('sl_pips', 100)
    tp_pips = params.get('tp_pips', 200)
    
    # Asumsi pip value sederhana untuk backtesting, bisa disempurnakan nanti
    # Untuk pair JPY, point adalah 0.001, untuk yang lain 0.00001
    point = 0.001 if 'JPY' in historical_data_df.columns[0].upper() else 0.00001
    # Asumsi nilai per pip untuk 0.01 lot
    # Ini adalah penyederhanaan besar, tapi cukup untuk backtesting awal
    value_per_pip = 0.1 # $0.10 per pip

    pip_value = 10 * point

    # Mock bot object untuk strategi
    class MockBot:
        def __init__(self):
            self.market_for_mt5 = "BACKTEST"
            self.timeframe = "H1"
            self.tf_map = {}

    # Inisialisasi strategi dengan parameter yang diberikan
    strategy_instance = strategy_class(bot_instance=MockBot(), params=params)

    # Loop melalui setiap bar data historis
    for i in range(1, len(historical_data_df)):
        # Buat DataFrame "seolah-olah" ini adalah data real-time hingga bar saat ini
        # PERBAIKAN: Gunakan .copy() untuk membuat salinan eksplisit dari slice.
        # Ini akan menghilangkan SettingWithCopyWarning di semua strategi.
        current_market_data = historical_data_df.iloc[:i].copy()
                
        analysis = strategy_instance.analyze(current_market_data)
        signal = analysis.get("signal")
        current_price = historical_data_df.iloc[i]['close']

        # Cek SL/TP jika sedang dalam posisi
        if in_position:
            profit = 0
            if position_type == 'BUY':
                profit_pips = (current_price - entry_price) / point / 10
                if current_price <= entry_price - (sl_pips * pip_value):
                    trades.append({'entry': entry_price, 'exit': current_price, 'profit_pips': profit_pips, 'reason': 'SL'})
                    capital += profit_pips * value_per_pip
                    in_position = False
                elif current_price >= entry_price + (tp_pips * pip_value):
                    trades.append({'entry': entry_price, 'exit': current_price, 'profit_pips': profit_pips, 'reason': 'TP'})
                    capital += profit_pips * value_per_pip
                    in_position = False
            elif position_type == 'SELL':
                profit_pips = (entry_price - current_price) / point / 10
                if current_price >= entry_price + (sl_pips * pip_value):
                    trades.append({'entry': entry_price, 'exit': current_price, 'profit_pips': profit_pips, 'reason': 'SL'})
                    capital += profit_pips * value_per_pip
                    in_position = False
                elif current_price <= entry_price - (tp_pips * pip_value):
                    trades.append({'entry': entry_price, 'exit': current_price, 'profit_pips': profit_pips, 'reason': 'TP'})
                    capital += profit_pips * value_per_pip
                    in_position = False
            
            if not in_position: # Jika posisi baru saja ditutup
                equity_curve.append(capital)
                peak_equity = max(peak_equity, capital)
                drawdown = (peak_equity - capital) / peak_equity
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
            profit_pips = ((current_price - entry_price) if position_type == 'BUY' else (entry_price - current_price)) / point / 10
            trades.append({'entry': entry_price, 'exit': current_price, 'profit_pips': profit_pips, 'reason': 'Signal Flip'})
            capital += profit_pips * value_per_pip
            equity_curve.append(capital)
            peak_equity = max(peak_equity, capital)
            drawdown = (peak_equity - capital) / peak_equity
            max_drawdown = max(max_drawdown, drawdown)
            in_position = False

    # Hitung hasil akhir
    total_profit_pips = sum(trade['profit_pips'] for trade in trades)
    wins = len([trade for trade in trades if trade['profit_pips'] > 0])
    losses = len(trades) - wins
    win_rate = (wins / len(trades) * 100) if trades else 0

    return {
        "total_trades": len(trades),
        "total_profit_pips": total_profit_pips,
        "win_rate_percent": win_rate,
        "wins": wins,
        "losses": losses,
        "max_drawdown_percent": max_drawdown * 100,
        "equity_curve": equity_curve,
        "trades": trades[-20:] # Tampilkan 20 trade terakhir
    }