# core/strategies/strategy_switcher.py
"""
🔄 Automatic Strategy Switching Logic

This module implements the core logic for automatically switching between
strategy/instrument combinations based on performance scores and market conditions.

Features:
- Automatic strategy switching based on performance rankings
- Market condition-aware switching
- Performance threshold monitoring
- Switching cooldown periods
- Historical performance tracking
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
import json
import os

from .market_condition_detector import get_market_condition
from .performance_scorer import calculate_strategy_score, rank_strategies
from ..backtesting.enhanced_engine import run_enhanced_backtest
from .strategy_map import STRATEGY_MAP

logger = logging.getLogger(__name__)

class StrategySwitcher:
    """
    Automatic strategy switching system
    """
    
    def __init__(self, config_file: str = 'strategy_switcher_config.json'):
        self.config_file = config_file
        self.config = self._load_config()
        self.performance_history = []
        self.last_switch_time = None
        self.current_strategy = None
        self.current_symbol = None
        self.switch_log = []
        
        # Default instruments to monitor
        self.monitored_instruments = self.config.get('monitored_instruments', [
            'US500', 'EURUSD', 'GBPUSD', 'XAUUSD', 'BTCUSD'
        ])
        
        # Default strategies to test
        self.test_strategies = self.config.get('test_strategies', [
            'INDEX_BREAKOUT_PRO', 'MA_CROSSOVER', 'RSI_CROSSOVER', 
            'TURTLE_BREAKOUT', 'QUANTUMBOTX_HYBRID'
        ])
    
    def _load_config(self) -> dict:
        """Load configuration from file or use defaults"""
        default_config = {
            'switching_cooldown_hours': 24,
            'performance_evaluation_period': 500,  # bars
            'min_performance_score': 0.6,
            'switch_threshold': 0.1,  # Minimum score improvement to trigger switch
            'data_directory': 'lab/backtest_data',
            'monitored_instruments': ['US500', 'EURUSD', 'GBPUSD', 'XAUUSD', 'BTCUSD'],
            'test_strategies': [
                'INDEX_BREAKOUT_PRO', 'MA_CROSSOVER', 'RSI_CROSSOVER', 
                'TURTLE_BREAKOUT', 'QUANTUMBOTX_HYBRID'
            ]
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                default_config.update(config)
        except Exception as e:
            logger.warning(f"Could not load config file {self.config_file}: {e}")
        
        return default_config
    
    def evaluate_and_switch(self, current_data: Dict[str, pd.DataFrame]) -> Optional[Dict[str, Any]]:
        """
        Evaluate all strategy/instrument combinations and switch if needed
        
        Args:
            current_data: Dictionary of symbol -> DataFrame with current market data
            
        Returns:
            dict: Switching decision or None if no switch needed
        """
        try:
            # Check if we're in cooldown period
            if self._in_cooldown():
                logger.info("Strategy switcher in cooldown period")
                return None
            
            # Evaluate all combinations
            performance_scores = self._evaluate_all_combinations(current_data)
            
            if not performance_scores:
                logger.warning("No performance scores calculated")
                return None
            
            # Rank combinations
            ranked_combinations = rank_strategies(performance_scores)
            
            # Determine if switch is needed
            switch_decision = self._determine_switch(ranked_combinations)
            
            if switch_decision:
                # Log the switch
                self._log_switch(switch_decision)
                
                # Update current strategy
                self.current_strategy = switch_decision['new_strategy']
                self.current_symbol = switch_decision['new_symbol']
                self.last_switch_time = datetime.now()
                
                return switch_decision
            else:
                logger.info("No strategy switch needed at this time")
                return None
                
        except Exception as e:
            logger.error(f"Strategy switching evaluation error: {e}")
            return None
    
    def _evaluate_all_combinations(self, current_data: Dict[str, pd.DataFrame]) -> List[dict]:
        """Evaluate all strategy/instrument combinations"""
        performance_scores = []
        
        for symbol in self.monitored_instruments:
            if symbol not in current_data:
                logger.warning(f"No data available for {symbol}")
                continue
            
            df = current_data[symbol]
            if df.empty:
                logger.warning(f"Empty data for {symbol}")
                continue
            
            # Get market condition for this symbol
            market_condition = get_market_condition(df, symbol)
            
            # Test each strategy on this symbol
            for strategy_id in self.test_strategies:
                if strategy_id not in STRATEGY_MAP:
                    logger.warning(f"Strategy {strategy_id} not found in STRATEGY_MAP")
                    continue
                
                try:
                    # Run backtest with recent data
                    test_df = df.tail(self.config['performance_evaluation_period']).copy()
                    
                    # Get strategy-specific parameters
                    strategy_params = self._get_strategy_parameters(strategy_id, symbol)
                    
                    # Run backtest
                    backtest_results = run_enhanced_backtest(
                        strategy_id,
                        strategy_params,
                        test_df,
                        symbol_name=symbol
                    )
                    
                    if 'error' in backtest_results:
                        logger.warning(f"Backtest error for {strategy_id}/{symbol}: {backtest_results['error']}")
                        continue
                    
                    # Calculate performance score
                    score = calculate_strategy_score(
                        backtest_results, market_condition, strategy_id, symbol
                    )
                    
                    performance_scores.append(score)
                    
                except Exception as e:
                    logger.error(f"Error evaluating {strategy_id}/{symbol}: {e}")
                    continue
        
        return performance_scores
    
    def _get_strategy_parameters(self, strategy_id: str, symbol: str) -> dict:
        """Get appropriate parameters for strategy and symbol combination"""
        # Base parameters for different strategy types
        base_params = {
            'INDEX_BREAKOUT_PRO': {
                'breakout_period': 25,
                'volume_surge_multiplier': 1.8,
                'confirmation_candles': 3,
                'atr_multiplier_sl': 2.5,
                'atr_multiplier_tp': 3.5,
                'min_breakout_size': 0.25,
                'risk_percent': 0.5
            },
            'MA_CROSSOVER': {
                'fast_period': 12,
                'slow_period': 26,
                'risk_percent': 0.8,
                'sl_atr_multiplier': 1.8,
                'tp_atr_multiplier': 3.6
            },
            'RSI_CROSSOVER': {
                'rsi_period': 14,
                'rsi_ma_period': 7,
                'trend_filter_period': 30,
                'risk_percent': 1.0,
                'sl_atr_multiplier': 2.0,
                'tp_atr_multiplier': 4.0
            },
            'TURTLE_BREAKOUT': {
                'entry_period': 20,
                'exit_period': 10,
                'risk_percent': 1.0,
                'sl_atr_multiplier': 2.0,
                'tp_atr_multiplier': 4.0
            },
            'QUANTUMBOTX_HYBRID': {
                'adx_period': 14,
                'adx_threshold': 25,
                'ma_fast_period': 12,
                'ma_slow_period': 26,
                'bb_length': 20,
                'bb_std': 2.0,
                'trend_filter_period': 50,
                'risk_percent': 1.0,
                'sl_atr_multiplier': 2.0,
                'tp_atr_multiplier': 4.0
            }
        }
        
        # Get base parameters
        params = base_params.get(strategy_id, {}).copy()
        
        # Adjust for symbol type
        symbol_upper = symbol.upper()
        if any(index in symbol_upper for index in ['US30', 'US100', 'US500', 'DE30']):
            # Index-specific adjustments
            params['risk_percent'] = min(params.get('risk_percent', 1.0), 0.5)
            if 'sl_atr_multiplier' in params:
                params['sl_atr_multiplier'] = min(params['sl_atr_multiplier'], 2.0)
        
        elif 'XAU' in symbol_upper:
            # Gold-specific adjustments
            params['risk_percent'] = min(params.get('risk_percent', 1.0), 0.3)
        
        elif any(crypto in symbol_upper for crypto in ['BTC', 'ETH']):
            # Crypto-specific adjustments
            params['risk_percent'] = min(params.get('risk_percent', 1.0), 0.5)
        
        return params
    
    def _determine_switch(self, ranked_combinations: List[dict]) -> Optional[dict]:
        """Determine if a strategy switch is needed"""
        if not ranked_combinations:
            return None
        
        # Get top-ranked combination
        top_combination = ranked_combinations[0]
        top_score = top_combination['composite_score']
        
        # Check if score meets minimum threshold
        if top_score < self.config['min_performance_score']:
            logger.info(f"Top score {top_score:.3f} below minimum threshold {self.config['min_performance_score']}")
            return None
        
        # If this is the first evaluation, switch to top performer
        if self.current_strategy is None or self.current_symbol is None:
            return {
                'action': 'INITIAL_SWITCH',
                'new_strategy': top_combination['strategy_id'],
                'new_symbol': top_combination['symbol'],
                'reason': f'Initial setup - top performer: {top_score:.3f}',
                'confidence': top_score,
                'performance_metrics': top_combination['metrics']
            }
        
        # Check if we're already using the top combination
        if (top_combination['strategy_id'] == self.current_strategy and 
            top_combination['symbol'] == self.current_symbol):
            logger.info(f"Already using top performer {self.current_strategy}/{self.current_symbol}")
            return None
        
        # Get current combination score
        current_score = self._get_current_combination_score(ranked_combinations)
        
        if current_score is None:
            # Current combination not in evaluation - switch to top
            improvement = top_score  # Full score as improvement
        else:
            improvement = top_score - current_score
        
        # Check if improvement meets threshold
        if improvement >= self.config['switch_threshold']:
            return {
                'action': 'STRATEGY_SWITCH',
                'new_strategy': top_combination['strategy_id'],
                'new_symbol': top_combination['symbol'],
                'old_strategy': self.current_strategy,
                'old_symbol': self.current_symbol,
                'reason': f'Score improvement: {improvement:.3f} (from {current_score:.3f} to {top_score:.3f})',
                'confidence': top_score,
                'improvement': improvement,
                'performance_metrics': top_combination['metrics']
            }
        else:
            logger.info(f"Score improvement {improvement:.3f} below threshold {self.config['switch_threshold']}")
            return None
    
    def _get_current_combination_score(self, ranked_combinations: List[dict]) -> Optional[float]:
        """Get performance score for current strategy/symbol combination"""
        if self.current_strategy is None or self.current_symbol is None:
            return None
        
        for combination in ranked_combinations:
            if (combination['strategy_id'] == self.current_strategy and 
                combination['symbol'] == self.current_symbol):
                return combination['composite_score']
        
        return None
    
    def _in_cooldown(self) -> bool:
        """Check if switching is in cooldown period"""
        if self.last_switch_time is None:
            return False
        
        cooldown_hours = self.config.get('switching_cooldown_hours', 24)
        cooldown_end = self.last_switch_time + timedelta(hours=cooldown_hours)
        
        return datetime.now() < cooldown_end
    
    def _log_switch(self, switch_decision: dict):
        """Log strategy switch decision"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'decision': switch_decision
        }
        
        self.switch_log.append(log_entry)
        
        # Keep only recent logs
        if len(self.switch_log) > 100:
            self.switch_log = self.switch_log[-50:]
        
        logger.info(f"Strategy switch logged: {switch_decision}")
        
        # Create notification for the switch
        self._create_switch_notification(switch_decision)
    
    def _create_switch_notification(self, switch_decision: dict):
        """Create a notification for strategy switch events"""
        try:
            # Import here to avoid circular imports
            from core.db.queries import add_history_log
            
            if switch_decision['action'] == 'INITIAL_SWITCH':
                action = "STRATEGY_SWITCHER_INITIALIZED"
                details = f"Strategy switcher initialized with {switch_decision['new_strategy']}/{switch_decision['new_symbol']} (Score: {switch_decision['confidence']:.3f})"
            else:  # STRATEGY_SWITCH
                action = "STRATEGY_SWITCHED"
                details = f"Switched from {switch_decision['old_strategy']}/{switch_decision['old_symbol']} to {switch_decision['new_strategy']}/{switch_decision['new_symbol']} (Improvement: +{switch_decision['improvement']:.3f})"
            
            # Create the notification in the trade_history table
            # Using bot_id=0 as this is a system-level notification not tied to a specific bot
            add_history_log(
                bot_id=0,
                action=action,
                details=details,
                is_notification=True
            )
        except Exception as e:
            logger.error(f"Failed to create switch notification: {e}")
    
    def get_status(self) -> dict:
        """Get current strategy switcher status"""
        return {
            'current_strategy': self.current_strategy,
            'current_symbol': self.current_symbol,
            'last_switch_time': self.last_switch_time.isoformat() if self.last_switch_time else None,
            'in_cooldown': self._in_cooldown(),
            'monitored_instruments': self.monitored_instruments,
            'test_strategies': self.test_strategies,
            'performance_history_count': len(self.performance_history),
            'switch_log_count': len(self.switch_log)
        }
    
    def get_recent_switches(self, count: int = 5) -> List[dict]:
        """Get recent switch history"""
        return self.switch_log[-count:] if self.switch_log else []

# Global instance
strategy_switcher = StrategySwitcher()

def evaluate_strategy_switch(current_data: Dict[str, pd.DataFrame]) -> Optional[Dict[str, Any]]:
    """
    Convenience function to evaluate and potentially switch strategies
    
    Args:
        current_data: Dictionary of symbol -> DataFrame with market data
        
    Returns:
        dict: Switch decision or None
    """
    return strategy_switcher.evaluate_and_switch(current_data)

def get_switcher_status() -> dict:
    """
    Get strategy switcher status
    
    Returns:
        dict: Current status information
    """
    return strategy_switcher.get_status()

def get_recent_switches(count: int = 5) -> List[dict]:
    """
    Get recent strategy switches
    
    Args:
        count: Number of recent switches to return
        
    Returns:
        List[dict]: Recent switch history
    """
    return strategy_switcher.get_recent_switches(count)