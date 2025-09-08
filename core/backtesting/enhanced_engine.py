# core/backtesting/enhanced_engine.py
# Enhanced Backtesting Engine with ATR-based Risk Management and Spread Modeling

import math
import logging
import os
from core.strategies.strategy_map import STRATEGY_MAP

logger = logging.getLogger(__name__)
# Set appropriate logging level
backtest_log_level = os.getenv('BACKTEST_LOG_LEVEL', 'INFO')
if backtest_log_level == 'DEBUG':
    logger.setLevel(logging.DEBUG)
else:
    logger.disabled = True
    logger.propagate = False

class InstrumentConfig:
    """Configuration for different trading instruments"""
    
    FOREX_MAJOR = {
        'contract_size': 100000,
        'pip_size': 0.0001,
        'typical_spread_pips': 1.0,  # Reduced from 2.0 for more realistic backtesting
        'max_risk_percent': 2.0,
        'max_lot_size': 10.0,
        'slippage_pips': 0.2  # Reduced from 0.5 for backtesting
    }
    
    FOREX_JPY = {
        'contract_size': 100000,
        'pip_size': 0.01,
        'typical_spread_pips': 1.5,  # Reduced from 2.0
        'max_risk_percent': 2.0,
        'max_lot_size': 10.0,
        'slippage_pips': 0.3  # Reduced from 0.5
    }
    
    GOLD = {
        'contract_size': 100,
        'pip_size': 0.01,
        'typical_spread_pips': 8.0,  # Reduced from 15.0 but still higher than forex
        'max_risk_percent': 1.0,      # Conservative for gold
        'max_lot_size': 0.10,         # Much smaller max lot
        'slippage_pips': 1.0,         # Reduced from 2.0
        'atr_volatility_threshold_high': 20.0,
        'atr_volatility_threshold_extreme': 30.0,
        'emergency_brake_percent': 0.05  # 5% emergency brake
    }
    
    CRYPTO = {
        'contract_size': 1,
        'pip_size': 0.01,
        'typical_spread_pips': 2.0,  # Reduced from 5.0
        'max_risk_percent': 1.5,
        'max_lot_size': 1.0,
        'slippage_pips': 0.5  # Reduced from 1.0
    }
    
    INDICES = {
        'contract_size': 1,  # 1 point = $1 for index CFDs
        'pip_size': 0.01,  # 0.01 point = 1 pip
        'typical_spread_pips': 3.0,  # Index spreads are typically higher
        'max_risk_percent': 0.5,  # Very conservative for indices
        'max_lot_size': 0.1,  # Small lot sizes for indices
        'slippage_pips': 0.5,
        'atr_volatility_threshold_high': 50.0,  # Index-specific thresholds
        'atr_volatility_threshold_extreme': 100.0,
        'emergency_brake_percent': 0.1  # 10% emergency brake
    }
    
    @classmethod
    def get_config(cls, symbol_name):
        """Get configuration for a specific instrument"""
        symbol_upper = symbol_name.upper()
        
        # Index detection (US30, US100, US500, DE30, etc.)
        if any(index in symbol_upper for index in ['US30', 'US100', 'US500', 'DE30', 'UK100', 'JP225', 'NAS100', 'SPX500']):
            return cls.INDICES
        elif 'XAU' in symbol_upper or 'GOLD' in symbol_upper:
            return cls.GOLD
        elif any(jpy in symbol_upper for jpy in ['JPY', 'USDJPY', 'EURJPY', 'GBPJPY']):
            return cls.FOREX_JPY
        elif any(crypto in symbol_upper for crypto in ['BTC', 'ETH', 'CRYPTO']):
            return cls.CRYPTO
        else:
            return cls.FOREX_MAJOR

class EnhancedBacktestEngine:
    """Enhanced backtesting engine with realistic cost modeling"""
    
    def __init__(self, enable_spread_costs=True, enable_slippage=True, enable_realistic_execution=True):
        self.enable_spread_costs = enable_spread_costs
        self.enable_slippage = enable_slippage
        self.enable_realistic_execution = enable_realistic_execution
        
    def calculate_realistic_entry_price(self, signal, close_price, spread_pips, pip_size, slippage_pips=0):
        """Calculate realistic entry price with spread and slippage"""
        spread_cost = spread_pips * pip_size
        slippage_cost = slippage_pips * pip_size if self.enable_slippage else 0
        
        if signal == 'BUY':
            # Buy at ask price + slippage
            return close_price + (spread_cost / 2) + slippage_cost
        else:  # SELL
            # Sell at bid price - slippage
            return close_price - (spread_cost / 2) - slippage_cost
    
    def calculate_realistic_exit_price(self, position_type, target_price, spread_pips, pip_size, slippage_pips=0):
        """Calculate realistic exit price with spread and slippage"""
        spread_cost = spread_pips * pip_size
        slippage_cost = slippage_pips * pip_size if self.enable_slippage else 0
        
        if position_type == 'BUY':
            # Close BUY at bid price - slippage
            return target_price - (spread_cost / 2) - slippage_cost
        else:  # SELL
            # Close SELL at ask price + slippage
            return target_price + (spread_cost / 2) + slippage_cost
    
    def calculate_position_size(self, symbol_name, capital, risk_percent, sl_distance, atr_value, config):
        """Enhanced position sizing with instrument-specific rules"""
        
        # Apply instrument-specific risk limits
        risk_percent = min(risk_percent, config['max_risk_percent'])
        
        amount_to_risk = capital * (risk_percent / 100.0)
        
        # Special handling for high-risk instruments
        if config == InstrumentConfig.GOLD:
            return self._calculate_gold_position_size(risk_percent, atr_value, amount_to_risk, sl_distance, config)
        elif config == InstrumentConfig.INDICES:
            return self._calculate_index_position_size(risk_percent, atr_value, amount_to_risk, sl_distance, config)
        else:
            return self._calculate_standard_position_size(amount_to_risk, sl_distance, config)
    
    def _calculate_gold_position_size(self, risk_percent, atr_value, amount_to_risk, sl_distance, config):
        """Ultra-conservative position sizing for gold"""
        
        # Base lot size based on risk percentage (ultra-conservative)
        if risk_percent <= 0.25:
            base_lot_size = 0.01
        elif risk_percent <= 0.5:
            base_lot_size = 0.01
        elif risk_percent <= 0.75:
            base_lot_size = 0.02
        elif risk_percent <= 1.0:
            base_lot_size = 0.02
        else:
            base_lot_size = 0.03  # Maximum for any gold trade
        
        # ATR-based volatility adjustments
        atr_threshold_high = config.get('atr_volatility_threshold_high', 20.0)
        atr_threshold_extreme = config.get('atr_volatility_threshold_extreme', 30.0)
        
        if atr_value > atr_threshold_extreme:
            lot_size = 0.01  # Extreme volatility
            logger.warning(f"GOLD EXTREME VOLATILITY: ATR={atr_value:.1f}, lot=0.01")
        elif atr_value > atr_threshold_high:
            lot_size = max(0.01, base_lot_size * 0.5)  # High volatility
            logger.warning(f"GOLD HIGH VOLATILITY: ATR={atr_value:.1f}, lot={lot_size}")
        else:
            lot_size = base_lot_size  # Normal volatility
        
        # Final safety cap
        lot_size = min(lot_size, config['max_lot_size'])
        
        return round(lot_size, 2)
    
    def _calculate_index_position_size(self, risk_percent, atr_value, amount_to_risk, sl_distance, config):
        """Ultra-conservative position sizing for stock indices (US500, US30, etc.)"""
        
        # Base lot size for indices (extremely conservative)
        if risk_percent <= 0.25:
            base_lot_size = 0.01
        elif risk_percent <= 0.5:
            base_lot_size = 0.01
        elif risk_percent <= 0.75:
            base_lot_size = 0.02
        elif risk_percent <= 1.0:
            base_lot_size = 0.02
        else:
            base_lot_size = 0.03  # Maximum for any index trade
        
        # ATR-based volatility adjustments for indices
        atr_threshold_high = config.get('atr_volatility_threshold_high', 50.0)
        atr_threshold_extreme = config.get('atr_volatility_threshold_extreme', 100.0)
        
        if atr_value > atr_threshold_extreme:
            lot_size = 0.01  # Extreme volatility - minimum size
            logger.warning(f"INDEX EXTREME VOLATILITY: ATR={atr_value:.1f}, lot=0.01")
        elif atr_value > atr_threshold_high:
            lot_size = max(0.01, base_lot_size * 0.5)  # High volatility - reduce size
            logger.warning(f"INDEX HIGH VOLATILITY: ATR={atr_value:.1f}, lot={lot_size}")
        else:
            lot_size = base_lot_size  # Normal volatility
        
        # Final safety cap
        lot_size = min(lot_size, config['max_lot_size'])
        
        logger.debug(f"INDEX POSITION: Risk={risk_percent}%, ATR={atr_value:.1f}, Lot={lot_size}")
        
        return round(lot_size, 2)
    
    def _calculate_standard_position_size(self, amount_to_risk, sl_distance, config):
        """Standard position sizing for forex and other instruments"""
        
        risk_in_currency_per_lot = sl_distance * config['contract_size']
        
        if risk_in_currency_per_lot <= 0:
            return 0
        
        calculated_lot_size = amount_to_risk / risk_in_currency_per_lot
        
        # Apply limits
        if calculated_lot_size < 0.01:
            return 0.01
        elif calculated_lot_size > config['max_lot_size']:
            return config['max_lot_size']
        
        return round(calculated_lot_size, 2)
    
    def calculate_spread_cost(self, lot_size, spread_pips, config):
        """Calculate the cost of spread for a round-trip trade"""
        if not self.enable_spread_costs:
            return 0
        
        # Calculate pip value per lot based on instrument type
        if config == InstrumentConfig.GOLD:
            # For gold: $1 per 0.01 pip per 1 oz
            pip_value_per_lot = 1.0
        elif config == InstrumentConfig.INDICES:
            # For indices: $1 per point per lot (very conservative for backtesting)
            pip_value_per_lot = 0.1  # Much more conservative for indices
        elif config['contract_size'] == 100:  # Other instruments with 100 contract size
            pip_value_per_lot = 1.0
        else:  # Forex
            # For major pairs: Use conservative pip value for backtesting
            pip_value_per_lot = 1.0
        
        spread_cost = spread_pips * pip_value_per_lot * lot_size
        
        return spread_cost

def run_enhanced_backtest(strategy_id, params, historical_data_df, symbol_name=None, engine_config=None):
    """
    Run enhanced backtesting with realistic cost modeling
    
    Args:
        strategy_id: Strategy to test
        params: Strategy parameters
        historical_data_df: Historical OHLC data
        symbol_name: Symbol name for instrument detection
        engine_config: Engine configuration options
    """
    
    # Initialize engine
    engine_config = engine_config or {}
    engine = EnhancedBacktestEngine(
        enable_spread_costs=engine_config.get('enable_spread_costs', True),
        enable_slippage=engine_config.get('enable_slippage', True),
        enable_realistic_execution=engine_config.get('enable_realistic_execution', True)
    )
    
    # Get strategy
    strategy_class = STRATEGY_MAP.get(strategy_id)
    if not strategy_class:
        return {"error": "Strategy not found"}
    
    # Detect instrument and get configuration
    if symbol_name:
        instrument_symbol = symbol_name
    elif historical_data_df.columns[0].count('_') > 0:
        instrument_symbol = historical_data_df.columns[0].split('_')[0]
    else:
        instrument_symbol = "UNKNOWN"
    
    config = InstrumentConfig.get_config(instrument_symbol)
    
    # Initialize strategy
    class MockBot:
        def __init__(self):
            self.market_for_mt5 = instrument_symbol
            self.timeframe = "H1"
            self.tf_map = {}
    
    strategy_instance = strategy_class(bot_instance=MockBot(), params=params)
    df = historical_data_df.copy()
    df_with_signals = strategy_instance.analyze_df(df)
    df_with_signals.ta.atr(length=14, append=True)
    df_with_signals.dropna(inplace=True)
    df_with_signals.reset_index(inplace=True)
    
    if df_with_signals.empty:
        return {"error": "Insufficient data for analysis"}
    
    # Initialize state
    trades = []
    in_position = False
    initial_capital = 10000.0
    capital = initial_capital
    equity_curve = [initial_capital]
    peak_equity = initial_capital
    max_drawdown = 0.0
    total_spread_costs = 0.0
    
    position_type = None
    entry_price = 0.0
    sl_price = 0.0
    tp_price = 0.0
    lot_size = 0.0
    entry_time = None
    
    # Enhanced parameter handling
    risk_percent = float(params.get('risk_percent', params.get('lot_size', 1.0)))
    sl_atr_multiplier = float(params.get('sl_atr_multiplier', params.get('sl_pips', 2.0)))
    tp_atr_multiplier = float(params.get('tp_atr_multiplier', params.get('tp_pips', 4.0)))
    
    # Apply instrument-specific parameter limits
    if config == InstrumentConfig.GOLD:
        risk_percent = min(risk_percent, 1.0)
        sl_atr_multiplier = min(sl_atr_multiplier, 1.0)
        tp_atr_multiplier = min(tp_atr_multiplier, 2.0)
        logger.debug(f"GOLD PROTECTION: Risk={risk_percent}%, SL={sl_atr_multiplier}x ATR, TP={tp_atr_multiplier}x ATR")
    
    # Main backtesting loop
    for i in range(1, len(df_with_signals)):
        current_bar = df_with_signals.iloc[i]
        
        if capital <= 0:
            break
        
        if in_position:
            # Check for exit conditions with realistic execution
            exit_price = None
            exit_reason = None
            
            if position_type == 'BUY':
                if current_bar['low'] <= sl_price:
                    exit_price = engine.calculate_realistic_exit_price(
                        'BUY', sl_price, config['typical_spread_pips'], 
                        config['pip_size'], config.get('slippage_pips', 0)
                    )
                    exit_reason = 'Stop Loss'
                elif current_bar['high'] >= tp_price:
                    exit_price = engine.calculate_realistic_exit_price(
                        'BUY', tp_price, config['typical_spread_pips'], 
                        config['pip_size'], config.get('slippage_pips', 0)
                    )
                    exit_reason = 'Take Profit'
            else:  # SELL
                if current_bar['high'] >= sl_price:
                    exit_price = engine.calculate_realistic_exit_price(
                        'SELL', sl_price, config['typical_spread_pips'], 
                        config['pip_size'], config.get('slippage_pips', 0)
                    )
                    exit_reason = 'Stop Loss'
                elif current_bar['low'] <= tp_price:
                    exit_price = engine.calculate_realistic_exit_price(
                        'SELL', tp_price, config['typical_spread_pips'], 
                        config['pip_size'], config.get('slippage_pips', 0)
                    )
                    exit_reason = 'Take Profit'
            
            if exit_price is not None:
                # Calculate profit with realistic execution
                profit_multiplier = lot_size * config['contract_size']
                
                if position_type == 'BUY':
                    profit = (exit_price - entry_price) * profit_multiplier
                else:
                    profit = (entry_price - exit_price) * profit_multiplier
                
                # Deduct spread costs
                spread_cost = engine.calculate_spread_cost(lot_size, config['typical_spread_pips'], config)
                profit -= spread_cost
                total_spread_costs += spread_cost
                
                if not math.isfinite(profit):
                    profit = 0.0
                
                capital += profit
                trades.append({
                    'entry_time': str(entry_time),
                    'exit_time': str(current_bar['time']),
                    'entry': entry_price,
                    'exit': exit_price,
                    'profit': profit,
                    'spread_cost': spread_cost,
                    'reason': exit_reason,
                    'position_type': position_type,
                    'lot_size': lot_size
                })
                
                equity_curve.append(capital)
                peak_equity = max(peak_equity, capital)
                drawdown = (peak_equity - capital) / peak_equity if peak_equity > 0 else 0
                max_drawdown = max(max_drawdown, drawdown)
                in_position = False
                
                logger.debug(f"Trade closed: {position_type} | Entry: {entry_price:.4f} | Exit: {exit_price:.4f} | Profit: ${profit:.2f} | Spread Cost: ${spread_cost:.2f}")
        
        if not in_position:
            signal = current_bar.get("signal", "HOLD")
            if signal in ['BUY', 'SELL']:
                atr_value = current_bar['ATRr_14']
                if atr_value <= 0:
                    continue
                
                # Calculate SL/TP distances
                sl_distance = atr_value * sl_atr_multiplier
                tp_distance = atr_value * tp_atr_multiplier
                
                # Calculate position size
                lot_size = engine.calculate_position_size(
                    instrument_symbol, capital, risk_percent, sl_distance, atr_value, config
                )
                
                if lot_size <= 0:
                    continue
                
                # Emergency brake for high-risk trades (especially gold)
                if config == InstrumentConfig.GOLD:
                    estimated_risk = sl_distance * lot_size * config['contract_size']
                    max_risk_dollar = capital * config.get('emergency_brake_percent', 0.05)
                    if estimated_risk > max_risk_dollar:
                        logger.warning(f"EMERGENCY BRAKE: Risk ${estimated_risk:.0f} > ${max_risk_dollar:.0f}, trade SKIPPED")
                        continue
                
                # Calculate realistic entry price
                entry_price = engine.calculate_realistic_entry_price(
                    signal, current_bar['close'], config['typical_spread_pips'], 
                    config['pip_size'], config.get('slippage_pips', 0)
                )
                entry_time = current_bar['time']
                
                # Set SL/TP levels
                if signal == 'BUY':
                    sl_price = entry_price - sl_distance
                    tp_price = entry_price + tp_distance
                else:
                    sl_price = entry_price + sl_distance
                    tp_price = entry_price - tp_distance
                
                in_position = True
                position_type = signal
                
                logger.debug(f"New {signal} position: Entry={entry_price:.4f}, SL={sl_price:.4f}, TP={tp_price:.4f}, Lot={lot_size}")
    
    # Calculate final results
    total_profit = capital - initial_capital
    wins = len([t for t in trades if t['profit'] > 0])
    losses = len(trades) - wins
    win_rate = (wins / len(trades) * 100) if trades else 0
    
    # Clean up results
    final_capital = round(capital, 2) if math.isfinite(capital) else 10000.0
    total_profit_clean = round(total_profit, 2) if math.isfinite(total_profit) else 0.0
    max_drawdown_clean = round(max_drawdown * 100, 2) if math.isfinite(max_drawdown) else 0.0
    win_rate_clean = round(win_rate, 2) if math.isfinite(win_rate) else 0.0
    
    logger.info(f"Enhanced Backtest Complete: {len(trades)} trades, ${total_profit_clean:+.0f} profit, {win_rate_clean:.0f}% win rate, ${total_spread_costs:.0f} spread costs")
    
    return {
        "strategy_name": strategy_class.name,
        "instrument": instrument_symbol,
        "total_trades": len(trades),
        "final_capital": final_capital,
        "total_profit_usd": total_profit_clean,
        "total_spread_costs": round(total_spread_costs, 2),
        "net_profit_after_costs": round(total_profit_clean, 2),
        "win_rate_percent": win_rate_clean,
        "wins": wins,
        "losses": losses,
        "max_drawdown_percent": max_drawdown_clean,
        "equity_curve": equity_curve,
        "trades": trades[-20:],  # Last 20 trades
        "engine_config": {
            "spread_costs_enabled": engine.enable_spread_costs,
            "slippage_enabled": engine.enable_slippage,
            "realistic_execution": engine.enable_realistic_execution,
            "instrument_config": config
        }
    }

# Wrapper function for backward compatibility
def run_backtest(strategy_id, params, historical_data_df, symbol_name=None):
    """Backward compatible wrapper for enhanced backtesting"""
    return run_enhanced_backtest(strategy_id, params, historical_data_df, symbol_name)