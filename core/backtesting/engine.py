# core/backtesting/engine.py

import math # Import modul math
import logging # Import modul logging
from core.strategies.strategy_map import STRATEGY_MAP

logger = logging.getLogger(__name__)
# Completely disable backtesting logs for silent operation
# Since we have backtesting history, terminal logs are not needed
logger.disabled = True
logger.propagate = False

def run_backtest(strategy_id, params, historical_data_df, symbol_name=None):
    """
    Menjalankan simulasi backtesting dengan position sizing dinamis.
    
    Args:
        strategy_id: ID strategi yang akan digunakan
        params: Parameter untuk backtesting
        historical_data_df: DataFrame dengan data historis
        symbol_name: Nama simbol (opsional, untuk deteksi XAUUSD yang akurat)
    """
    strategy_class = STRATEGY_MAP.get(strategy_id)
    if not strategy_class:
        return {"error": "Strategi tidak ditemukan"}

    # --- LANGKAH 1: Pra-perhitungan Indikator & ATR ---
    class MockBot:
        def __init__(self):
            # Improved symbol detection logic
            if symbol_name:
                self.market_for_mt5 = symbol_name
            elif historical_data_df.columns[0].count('_') > 0:
                self.market_for_mt5 = historical_data_df.columns[0].split('_')[0]
            else:
                # Default fallback for standardized column names
                self.market_for_mt5 = "UNKNOWN"
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
    
    # Enhanced XAUUSD/Gold detection with multiple methods
    is_gold_symbol = (
        'XAU' in str(historical_data_df.columns[0]).upper() or  # Column name check
        (symbol_name and 'XAU' in symbol_name.upper()) or      # Explicit symbol name
        'GOLD' in str(historical_data_df.columns[0]).upper() or # Alternative gold naming
        (hasattr(strategy_instance.bot, 'market_for_mt5') and 'XAU' in strategy_instance.bot.market_for_mt5.upper())
    )
    
    logger.debug(f"Gold symbol detection: {is_gold_symbol} (symbol: {symbol_name}, columns: {list(historical_data_df.columns)})")
    
    if is_gold_symbol:
        # ULTRA CONSERVATIVE defaults for gold - more aggressive than before
        if risk_percent > 1.0:  # Max 1% risk for gold (reduced from 2%)
            risk_percent = 1.0
            logger.debug(f"Risk CAPPED to {risk_percent}% for XAUUSD trading")
        
        # Much smaller ATR multipliers for gold due to extreme volatility
        if sl_atr_multiplier > 1.0:  # Reduced from 1.5 to 1.0
            sl_atr_multiplier = 1.0
            logger.debug(f"SL ATR multiplier CAPPED to {sl_atr_multiplier} for XAUUSD")
        if tp_atr_multiplier > 2.0:  # Reduced from 3.0 to 2.0
            tp_atr_multiplier = 2.0
            logger.debug(f"TP ATR multiplier CAPPED to {tp_atr_multiplier} for XAUUSD")

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
                # Tentukan ukuran kontrak berdasarkan simbol (100 untuk XAU, 100000 untuk Forex)
                contract_size = 100 if 'XAU' in strategy_instance.bot.market_for_mt5.upper() else 100000

                # Perhitungan profit yang disederhanakan
                profit_multiplier = lot_size * contract_size

                if position_type == 'BUY':
                    profit = (exit_price - entry_price) * profit_multiplier
                else: # SELL
                    profit = (entry_price - exit_price) * profit_multiplier
                
                # Pastikan profit adalah angka yang valid
                if not math.isfinite(profit):
                    profit = 0.0

                # Debug logging for individual trades (only show important ones)
                if abs(profit) > 50:  # Only log significant trades
                    logger.info(f"Significant trade: {position_type} | Entry: {entry_price} | Exit: {exit_price} | Profit: ${profit:.2f}")
                else:
                    logger.debug(f"Trade closed: {position_type} | Entry: {entry_price} | Exit: {exit_price} | Lot: {lot_size} | Profit: {profit}")
                
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
                entry_time = current_bar['time']
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

                # Kalkulasi Lot Size dengan proteksi khusus untuk XAUUSD
                amount_to_risk = capital * (risk_percent / 100.0)
                contract_size = 100 if 'XAU' in strategy_instance.bot.market_for_mt5.upper() else 100000
                
                # Enhanced gold detection for position sizing
                is_gold = (
                    'XAU' in strategy_instance.bot.market_for_mt5.upper() or
                    is_gold_symbol or  # Use the enhanced detection from above
                    (symbol_name and 'XAU' in symbol_name.upper())
                )
                
                if is_gold:
                    # EXTREME CONSERVATIVE approach for XAUUSD
                    # Fixed tiny lot sizes only - no dynamic calculation at all
                    # Gold volatility can destroy accounts in one trade
                    
                    # Base lot size selection (even smaller than before)
                    if risk_percent <= 0.25:
                        base_lot_size = 0.01  # Micro lot
                    elif risk_percent <= 0.5:
                        base_lot_size = 0.01  # Still micro lot
                    elif risk_percent <= 0.75:
                        base_lot_size = 0.02  # Very small
                    elif risk_percent <= 1.0:
                        base_lot_size = 0.02  # Still very small
                    else:
                        base_lot_size = 0.03  # MAXIMUM base for any XAUUSD trade
                    
                    # Additional ATR-based reduction for high volatility periods
                    # If ATR is very high, reduce lot size further
                    atr_threshold_high = 20.0  # High volatility threshold
                    atr_threshold_extreme = 30.0  # Extreme volatility threshold
                    
                    if atr_value > atr_threshold_extreme:
                        # Extreme volatility - use minimum lot size only
                        lot_size = 0.01
                        logger.warning(f"GOLD EXTREME VOLATILITY: ATR={atr_value:.1f}, lot=0.01")
                    elif atr_value > atr_threshold_high:
                        # High volatility - reduce lot size by 50%
                        lot_size = max(0.01, base_lot_size * 0.5)
                        logger.warning(f"GOLD HIGH VOLATILITY: ATR={atr_value:.1f}, lot={lot_size}")
                    else:
                        # Normal volatility - use base lot size
                        lot_size = base_lot_size
                        logger.debug(f"GOLD normal volatility: ATR={atr_value:.1f}, lot={lot_size}")
                    
                    # Final safety check - never allow lot size above 0.03 for gold
                    if lot_size > 0.03:
                        lot_size = 0.03
                        logger.warning("GOLD SAFETY: Lot capped at 0.03")
                    
                    # Round to valid lot size increments
                    lot_size = round(lot_size, 2)
                    
                    # Calculate estimated risk for logging
                    pip_size = 0.01
                    sl_distance_pips = sl_distance / pip_size
                    risk_in_currency_per_lot = sl_distance_pips * 1.0 * (lot_size / 0.01)  # $1 per pip per 0.01 lot
                    estimated_risk = abs(risk_in_currency_per_lot)
                    
                    logger.debug(f"XAUUSD PROTECTION: ATR={atr_value:.1f}, SL={sl_distance:.1f}, lot={lot_size}, risk=${estimated_risk:.0f}")
                    
                    # Emergency brake - if estimated risk is too high, skip trade
                    max_risk_dollar = capital * 0.05  # Never risk more than 5% of capital (increased from 2%)
                    if estimated_risk > max_risk_dollar:
                        logger.error(f"GOLD EMERGENCY BRAKE: Risk ${estimated_risk:.0f} > ${max_risk_dollar:.0f}, trade SKIPPED")
                        continue
                else:
                    # Standard forex calculation
                    risk_in_currency_per_lot = sl_distance * contract_size
                    
                    if risk_in_currency_per_lot <= 0:
                        logger.warning(f"Risk per lot is {risk_in_currency_per_lot}. Skipping trade.")
                        continue 
                    
                    calculated_lot_size = amount_to_risk / risk_in_currency_per_lot
                    
                    if calculated_lot_size < 0.00001:
                        logger.warning(f"Calculated lot size {calculated_lot_size} is too small. Skipping trade.")
                        continue 
                    if calculated_lot_size > 10.0:
                        logger.warning(f"Calculated lot size {calculated_lot_size} exceeds max limit. Skipping trade.")
                        continue 

                    if calculated_lot_size > 0 and calculated_lot_size < 0.01:
                        lot_size = 0.01
                    else:
                        lot_size = round(calculated_lot_size, 2)
                
                logger.debug("--- LOT SIZE CALCULATION ---")
                logger.debug(f"Symbol: {strategy_instance.bot.market_for_mt5}, Is Gold: {is_gold}")
                logger.debug(f"Signal: {signal} at price {entry_price}")
                logger.debug(f"ATR: {atr_value}, SL Multiplier: {sl_atr_multiplier}, SL Distance: {sl_distance}")
                logger.debug(f"Capital: {capital}, Risk Percent: {risk_percent}, Amount to Risk: {amount_to_risk}")
                logger.debug(f"Contract Size: {contract_size}, Risk per Lot: {risk_in_currency_per_lot}")
                logger.debug(f"Final Lot Size: {lot_size}")

                if not is_gold:
                    # Only do calculated lot size checks for non-gold instruments
                    calculated_lot_size = amount_to_risk / risk_in_currency_per_lot
                    logger.debug(f"Calculated Lot Size: {calculated_lot_size}")
                    
                    if calculated_lot_size < 0.00001:
                        logger.warning(f"Calculated lot size {calculated_lot_size} is too small. Skipping trade.")
                        continue 
                    if calculated_lot_size > 10.0:
                        logger.warning(f"Calculated lot size {calculated_lot_size} exceeds max limit. Skipping trade.")
                        continue 

                    if calculated_lot_size > 0 and calculated_lot_size < 0.01:
                        lot_size = 0.01
                    else:
                        lot_size = round(calculated_lot_size, 2)
                
                logger.debug(f"Final Lot Size: {lot_size}")
                
                if lot_size <= 0:
                    logger.warning("Final lot size is 0. Skipping trade.")
                    continue 

                in_position = True
                position_type = signal

    # --- LANGKAH 4: Hitung hasil akhir ---
    total_profit = capital - initial_capital
    wins = len([t for t in trades if t['profit'] > 0])
    losses = len(trades) - wins
    win_rate = (wins / len(trades) * 100) if trades else 0

    # Ensure no NaN/Inf values
    final_capital = round(capital, 2) if math.isfinite(capital) else 10000.0
    total_profit_clean = round(total_profit, 2) if math.isfinite(total_profit) else 0.0
    max_drawdown_clean = round(max_drawdown * 100, 2) if math.isfinite(max_drawdown) else 0.0
    win_rate_clean = round(win_rate, 2) if math.isfinite(win_rate) else 0.0

    # Summary logging (keep only essential results)
    logger.info(f"Backtest Complete: {len(trades)} trades, ${total_profit_clean:+.0f} profit, {win_rate_clean:.0f}% win rate")
    
    # Debug detailed results
    logger.debug("=== DETAILED BACKTEST RESULTS ===")
    logger.debug(f"Initial Capital: {initial_capital}")
    logger.debug(f"Final Capital: {capital}")
    logger.debug(f"Total Profit: {total_profit}")
    logger.debug(f"Total Trades: {len(trades)}")
    logger.debug(f"Wins: {wins}, Losses: {losses}")
    logger.debug(f"Win Rate: {win_rate}%")

    return {
        "strategy_name": strategy_class.name,
        "total_trades": len(trades),
        "final_capital": final_capital,
        "total_profit_usd": total_profit_clean,
        "win_rate_percent": win_rate_clean,
        "wins": wins,
        "losses": losses,
        "max_drawdown_percent": max_drawdown_clean,
        "equity_curve": equity_curve,
        "trades": trades[-20:]  # Last 20 trades
    }
