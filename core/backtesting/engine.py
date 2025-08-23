# core/backtesting/engine.py

import math # Import modul math
import logging # Import modul logging
from core.strategies.strategy_map import STRATEGY_MAP

logger = logging.getLogger(__name__)

def run_backtest(strategy_id, params, historical_data_df):
    """
    Menjalankan simulasi backtesting dengan position sizing dinamis.
    """
    strategy_class = STRATEGY_MAP.get(strategy_id)
    if not strategy_class:
        return {"error": "Strategi tidak ditemukan"}

    # --- LANGKAH 1: Pra-perhitungan Indikator & ATR ---
    class MockBot:
        def __init__(self):
            # Dapatkan nama simbol dari data historis
            self.market_for_mt5 = historical_data_df.columns[0].split('_')[0]
            self.timeframe = "H1"
            self.tf_map = {}

    strategy_instance = strategy_class(bot_instance=MockBot(), params=params)
    df = historical_data_df.copy()
    df_with_signals = strategy_instance.analyze_df(df)
    df_with_signals.ta.atr(length=14, append=True)
    df_with_signals.dropna(inplace=True)
    df_with_signals.reset_index(inplace=True)

    if df_with_signals.empty:
        return {"error": "Data tidak cukup untuk analisa."}

    # --- LANGKAH 2: Inisialisasi state & parameter ---
    trades = []
    in_position = False
    initial_capital = 10000.0
    capital = initial_capital
    equity_curve = [initial_capital]
    peak_equity = initial_capital
    max_drawdown = 0.0
    
    position_type = None
    entry_price = 0.0
    sl_price = 0.0
    tp_price = 0.0
    lot_size = 0.0
    entry_time = None # Inisialisasi entry_time

    risk_percent = float(params.get('lot_size', 1.0))
    sl_atr_multiplier = float(params.get('sl_pips', 2.0))
    tp_atr_multiplier = float(params.get('tp_pips', 4.0))

    # --- LANGKAH 3: Loop melalui data ---
    for i in range(1, len(df_with_signals)):
        current_bar = df_with_signals.iloc[i]

        # Hentikan backtest jika modal habis
        if capital <= 0:
            break

        if in_position:
            exit_price = None
            if position_type == 'BUY' and current_bar['low'] <= sl_price: exit_price = sl_price
            elif position_type == 'BUY' and current_bar['high'] >= tp_price: exit_price = tp_price
            elif position_type == 'SELL' and current_bar['high'] >= sl_price: exit_price = sl_price
            elif position_type == 'SELL' and current_bar['low'] <= tp_price: exit_price = tp_price

            if exit_price is not None:
                # Tentukan ukuran kontrak berdasarkan simbol
                contract_size = 100 if 'XAU' in strategy_instance.bot.market_for_mt5.upper() else 100000

                # Profit calculation needs to account for scaled prices in commodities
                symbol = strategy_instance.bot.market_for_mt5.upper()
                if 'XAU' in symbol or 'XAG' in symbol:
                    point_value = 0.01
                    profit_multiplier = lot_size * contract_size * point_value
                else:
                    profit_multiplier = lot_size * contract_size

                if position_type == 'BUY':
                    profit = (exit_price - entry_price) * profit_multiplier
                else: # SELL
                    profit = (entry_price - exit_price) * profit_multiplier
                
                # Pastikan profit adalah angka yang valid
                if not math.isfinite(profit):
                    profit = 0.0

                capital += profit
                trades.append({
                    'entry_time': str(entry_time),
                    'exit_time': str(current_bar['time']),
                    'entry': entry_price,
                    'exit': exit_price,
                    'profit': profit,
                    'reason': 'SL/TP', # Default reason
                    'position_type': position_type
                })
                equity_curve.append(capital)
                peak_equity = max(peak_equity, capital)
                drawdown = (peak_equity - capital) / peak_equity if peak_equity > 0 else 0
                max_drawdown = max(max_drawdown, drawdown)
                in_position = False

        if not in_position:
            signal = current_bar.get("signal", "HOLD")
            if signal in ['BUY', 'SELL']:
                entry_price = current_bar['close']
                entry_time = current_bar['time'] # Tambahkan baris ini
                atr_value = current_bar['ATRr_14']
                if atr_value <= 0: 
                    continue

                sl_distance = atr_value * sl_atr_multiplier
                tp_distance = atr_value * tp_atr_multiplier
                
                if signal == 'BUY':
                    sl_price = entry_price - sl_distance
                    tp_price = entry_price + tp_distance
                else:
                    sl_price = entry_price + sl_distance
                    tp_price = entry_price - tp_distance

                # Kalkulasi Lot Size
                amount_to_risk = capital * (risk_percent / 100.0)
                contract_size = 100 if 'XAU' in strategy_instance.bot.market_for_mt5.upper() else 100000
                symbol = strategy_instance.bot.market_for_mt5.upper()

                # Risk calculation needs to account for scaled prices in commodities
                if 'XAU' in symbol or 'XAG' in symbol:
                    point_value = 0.01
                    risk_in_currency_per_lot = sl_distance * contract_size * point_value
                else:
                    risk_in_currency_per_lot = sl_distance * contract_size
                if risk_in_currency_per_lot <= 0: 
                    continue 
                
                calculated_lot_size = amount_to_risk / risk_in_currency_per_lot
                
                # Terapkan batasan lot size minimum dan maksimum
                if calculated_lot_size < 0.00001: 
                    continue 
                if calculated_lot_size > 10.0: 
                    continue 

                                # Round lot size to a reasonable precision (e.g., 2 decimal places for most brokers)
                # Jika calculated_lot_size sangat kecil tapi positif, gunakan lot minimum broker
                if calculated_lot_size > 0 and calculated_lot_size < 0.01:
                    lot_size = 0.01 # Gunakan lot minimum broker
                else:
                    lot_size = round(calculated_lot_size, 2) 
                
                # Pastikan lot_size tidak nol setelah pembulatan
                if lot_size <= 0: 
                    continue 

                in_position = True
                position_type = signal

    # --- LANGKAH 4: Hitung hasil akhir ---
    total_profit = capital - initial_capital
    wins = len([t for t in trades if t['profit'] > 0])
    losses = len(trades) - wins
    win_rate = (wins / len(trades) * 100) if trades else 0

    return {
        "strategy_name": strategy_class.name,
        "total_trades": len(trades),
        "final_capital": round(capital, 2),
        "total_profit_usd": round(total_profit, 2),
        "win_rate_percent": round(win_rate, 2),
        "wins": wins,
        "losses": losses,
        "max_drawdown_percent": round(max_drawdown * 100, 2),
        "equity_curve": equity_curve,
        "trades": trades[-20:]
    }
