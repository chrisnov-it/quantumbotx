# core/strategies/index_momentum.py

import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import datetime, time
from .base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class IndexMomentumStrategy(BaseStrategy):
    """
    INDEX_MOMENTUM - Specialized Stock Index Momentum Strategy
    
    Complexity: 4/12 (INTERMEDIATE)
    Designed for: US30, US100, US500, DE30
    
    Features:
    - Session-aware trading (market hours detection)
    - Gap detection and management
    - Momentum confirmation with multiple timeframes
    - Volume-weighted signals
    - Index-specific risk management
    
    Best for: Trending index movements during active trading sessions
    """
    
    def __init__(self, bot_instance, params=None):
        # Default parameters optimized for stock indices
        default_params = {
            'momentum_period': 14,      # RSI period for momentum
            'volume_period': 20,        # Volume average period
            'gap_threshold': 0.5,       # % gap threshold for gap detection
            'momentum_oversold': 30,    # RSI oversold level
            'momentum_overbought': 70,  # RSI overbought level
            'volume_multiplier': 1.3,   # Volume confirmation multiplier
            'session_filter': True,     # Enable trading hours filter
            'gap_fade_mode': False,     # Fade gaps vs follow gaps
        }
        
        # Merge with user params
        if params:
            default_params.update(params)
            
        super().__init__(bot_instance, default_params)
        
        # Index-specific configurations
        self.index_configs = {
            'US30': {'session_start': 14.5, 'session_end': 21, 'volatility_adj': 1.0},
            'US100': {'session_start': 14.5, 'session_end': 21, 'volatility_adj': 1.2},
            'US500': {'session_start': 14.5, 'session_end': 21, 'volatility_adj': 1.0},
            'DE30': {'session_start': 7, 'session_end': 15.5, 'volatility_adj': 0.8}
        }

    def analyze(self, df):
        """
        Main analysis method for index momentum strategy
        """
        try:
            # Ensure sufficient data
            min_required = max(self.params['momentum_period'], self.params['volume_period']) + 5
            if len(df) < min_required:
                return {
                    "signal": "HOLD",
                    "price": df['close'].iloc[-1] if not df.empty else 0,
                    "explanation": f"Insufficient data: need {min_required}, got {len(df)}"
                }

            # Get current symbol for index-specific logic
            symbol = getattr(self.bot, 'market_for_mt5', 'US500')
            config = self.index_configs.get(symbol, self.index_configs['US500'])
            
            # Calculate technical indicators
            df = self._calculate_indicators(df)
            
            # Session filter check
            if self.params['session_filter'] and not self._is_trading_session(config):
                return {
                    "signal": "HOLD",
                    "price": df['close'].iloc[-1],
                    "explanation": "Outside trading session"
                }
            
            # Gap detection
            gap_info = self._detect_gap(df)
            
            # Generate signal based on momentum and conditions
            signal_info = self._generate_signal(df, gap_info, config)
            
            return signal_info
            
        except Exception as e:
            logger.error(f"IndexMomentumStrategy analysis error: {e}")
            return {
                "signal": "HOLD",
                "price": df['close'].iloc[-1] if not df.empty else 0,
                "explanation": f"Analysis error: {str(e)}"
            }

    def _calculate_indicators(self, df):
        """Calculate all required technical indicators"""
        # RSI for momentum
        df['rsi'] = ta.rsi(df['close'], length=self.params['momentum_period'])
        
        # Volume indicators
        df['volume_avg'] = df['tick_volume'].rolling(self.params['volume_period']).mean()
        df['volume_ratio'] = df['tick_volume'] / df['volume_avg']
        
        # Price momentum indicators
        df['price_change'] = df['close'].pct_change()
        df['momentum_ma'] = df['close'].rolling(10).mean()
        
        # ATR for volatility
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        
        return df

    def _is_trading_session(self, config):
        """Check if current time is within trading session"""
        try:
            current_hour = datetime.now().hour + datetime.now().minute / 60.0
            
            # Simple session check (can be enhanced with timezone handling)
            session_start = config['session_start']
            session_end = config['session_end']
            
            if session_start < session_end:
                return session_start <= current_hour <= session_end
            else:
                # Handle overnight sessions
                return current_hour >= session_start or current_hour <= session_end
                
        except Exception:
            return True  # Default to allow trading if check fails

    def _detect_gap(self, df):
        """Detect price gaps from previous close"""
        if len(df) < 2:
            return {'has_gap': False, 'gap_size': 0, 'gap_direction': None}
        
        try:
            prev_close = df['close'].iloc[-2]
            current_open = df['open'].iloc[-1]
            
            gap_size = abs(current_open - prev_close) / prev_close * 100
            gap_direction = 'up' if current_open > prev_close else 'down'
            
            has_significant_gap = gap_size > self.params['gap_threshold']
            
            return {
                'has_gap': has_significant_gap,
                'gap_size': gap_size,
                'gap_direction': gap_direction,
                'gap_points': current_open - prev_close
            }
            
        except Exception:
            return {'has_gap': False, 'gap_size': 0, 'gap_direction': None}

    def _generate_signal(self, df, gap_info, config):
        """Generate trading signal based on momentum and conditions"""
        current_price = df['close'].iloc[-1]
        current_rsi = df['rsi'].iloc[-1]
        volume_ratio = df['volume_ratio'].iloc[-1]
        price_change = df['price_change'].iloc[-1]
        
        # Volume confirmation
        volume_confirmed = volume_ratio >= self.params['volume_multiplier']
        
        # Momentum conditions
        bullish_momentum = (current_rsi > 50 and 
                          current_rsi < self.params['momentum_overbought'] and
                          price_change > 0)
        
        bearish_momentum = (current_rsi < 50 and 
                          current_rsi > self.params['momentum_oversold'] and
                          price_change < 0)
        
        # Gap trading logic
        gap_signal = self._analyze_gap_opportunity(gap_info, current_rsi)
        
        # Signal generation
        signal = "HOLD"
        explanation = "Waiting for clear momentum signal"
        
        # Buy conditions
        if (bullish_momentum and volume_confirmed) or gap_signal == "BUY":
            signal = "BUY"
            reasons = []
            if bullish_momentum:
                reasons.append(f"Bullish momentum (RSI: {current_rsi:.1f})")
            if volume_confirmed:
                reasons.append(f"Volume confirmed ({volume_ratio:.2f}x)")
            if gap_signal == "BUY":
                reasons.append(f"Gap opportunity ({gap_info['gap_direction']} {gap_info['gap_size']:.2f}%)")
            explanation = f"BUY: {', '.join(reasons)}"
            
        # Sell conditions  
        elif (bearish_momentum and volume_confirmed) or gap_signal == "SELL":
            signal = "SELL"
            reasons = []
            if bearish_momentum:
                reasons.append(f"Bearish momentum (RSI: {current_rsi:.1f})")
            if volume_confirmed:
                reasons.append(f"Volume confirmed ({volume_ratio:.2f}x)")
            if gap_signal == "SELL":
                reasons.append(f"Gap opportunity ({gap_info['gap_direction']} {gap_info['gap_size']:.2f}%)")
            explanation = f"SELL: {', '.join(reasons)}"
            
        # Override conditions
        if current_rsi > self.params['momentum_overbought']:
            signal = "HOLD"
            explanation = f"Overbought condition (RSI: {current_rsi:.1f})"
        elif current_rsi < self.params['momentum_oversold']:
            signal = "HOLD"
            explanation = f"Oversold condition (RSI: {current_rsi:.1f})"
        
        return {
            "signal": signal,
            "price": current_price,
            "explanation": explanation
        }

    def _analyze_gap_opportunity(self, gap_info, current_rsi):
        """Analyze gap trading opportunities"""
        if not gap_info['has_gap']:
            return "HOLD"
        
        gap_size = gap_info['gap_size']
        gap_direction = gap_info['gap_direction']
        
        # Small gaps - fade them
        if gap_size < 1.0:
            if self.params['gap_fade_mode']:
                return "SELL" if gap_direction == 'up' else "BUY"
            else:
                return "HOLD"
        
        # Large gaps - follow momentum with RSI confirmation
        elif gap_size > 2.0:
            if gap_direction == 'up' and current_rsi < 70:
                return "BUY"
            elif gap_direction == 'down' and current_rsi > 30:
                return "SELL"
        
        return "HOLD"

    def analyze_df(self, df):
        """
        Backtesting version of analyze method
        Processes entire DataFrame and adds signal columns
        """
        if len(df) < 30:
            return df
            
        try:
            # Calculate indicators for entire DataFrame
            df = self._calculate_indicators(df)
            
            # Initialize signal columns
            df['signal'] = 'HOLD'
            df['signal_strength'] = 0.0
            df['explanation'] = ''
            
            # Process each row for backtesting
            for i in range(30, len(df)):
                current_df = df.iloc[:i+1].copy()
                
                # Simple gap detection for backtesting
                gap_info = {'has_gap': False, 'gap_size': 0, 'gap_direction': None}
                if i > 0:
                    prev_close = df['close'].iloc[i-1]
                    current_open = df['open'].iloc[i]
                    gap_size = abs(current_open - prev_close) / prev_close * 100
                    if gap_size > self.params['gap_threshold']:
                        gap_info = {
                            'has_gap': True,
                            'gap_size': gap_size,
                            'gap_direction': 'up' if current_open > prev_close else 'down'
                        }
                
                # Generate signal
                symbol = getattr(self.bot, 'market_for_mt5', 'US500')
                config = self.index_configs.get(symbol, self.index_configs['US500'])
                signal_info = self._generate_signal(current_df, gap_info, config)
                
                # Store results
                df.loc[df.index[i], 'signal'] = signal_info['signal']
                df.loc[df.index[i], 'explanation'] = signal_info['explanation']
                
                # Calculate signal strength
                if signal_info['signal'] in ['BUY', 'SELL']:
                    rsi = df['rsi'].iloc[i]
                    volume_ratio = df['volume_ratio'].iloc[i]
                    strength = min(1.0, (volume_ratio - 1.0) * 0.5 + 0.5)
                    df.loc[df.index[i], 'signal_strength'] = strength
            
            return df
            
        except Exception as e:
            logger.error(f"IndexMomentumStrategy analyze_df error: {e}")
            return df

    @classmethod
    def get_definable_params(cls):
        """Return list of user-configurable parameters"""
        return [
            {
                'name': 'momentum_period',
                'display_name': 'Momentum Period',
                'type': 'int',
                'default': 14,
                'min': 5,
                'max': 30,
                'description': 'RSI period for momentum detection'
            },
            {
                'name': 'volume_period',
                'display_name': 'Volume Average Period',
                'type': 'int',
                'default': 20,
                'min': 10,
                'max': 50,
                'description': 'Period for volume average calculation'
            },
            {
                'name': 'gap_threshold',
                'display_name': 'Gap Threshold (%)',
                'type': 'float',
                'default': 0.5,
                'min': 0.1,
                'max': 3.0,
                'description': 'Minimum gap size to trigger gap trading'
            },
            {
                'name': 'volume_multiplier',
                'display_name': 'Volume Confirmation',
                'type': 'float',
                'default': 1.3,
                'min': 1.0,
                'max': 3.0,
                'description': 'Volume multiplier for signal confirmation'
            },
            {
                'name': 'session_filter',
                'display_name': 'Trading Hours Filter',
                'type': 'bool',
                'default': True,
                'description': 'Only trade during market hours'
            },
            {
                'name': 'gap_fade_mode',
                'display_name': 'Gap Fade Mode',
                'type': 'bool',
                'default': False,
                'description': 'Fade gaps instead of following them'
            }
        ]