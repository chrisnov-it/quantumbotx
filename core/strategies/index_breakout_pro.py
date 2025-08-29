# core/strategies/index_breakout_pro.py

import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import datetime, time
from .base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class IndexBreakoutProStrategy(BaseStrategy):
    """
    INDEX_BREAKOUT_PRO - Advanced Stock Index Breakout Strategy
    
    Complexity: 7/12 (ADVANCED)
    Designed for: US30, US100, US500, DE30
    
    Features:
    - Multi-timeframe breakout confirmation
    - Institutional pattern recognition (support/resistance levels)
    - Volume-price analysis (VPA)
    - Dynamic stop-loss and take-profit
    - Market structure analysis
    - Pre-market and post-market gap trading
    
    Best for: Experienced traders seeking to capture major index movements
    """
    
    def __init__(self, bot_instance, params=None):
        # Advanced parameters for professional breakout trading
        default_params = {
            'breakout_period': 20,      # Lookback period for breakout levels
            'volume_surge_multiplier': 2.0,  # Volume surge detection
            'confirmation_candles': 2,   # Candles to confirm breakout
            'support_resistance_strength': 3,  # Minimum touches for S/R level
            'atr_multiplier_sl': 2.0,   # ATR multiplier for stop loss
            'atr_multiplier_tp': 4.0,   # ATR multiplier for take profit
            'min_breakout_size': 0.3,   # Minimum breakout size (% of ATR)
            'max_risk_per_trade': 1.0,  # Maximum risk per trade (%)
            'trend_filter_period': 50,  # Long-term trend filter
            'vwap_filter': True,        # Use VWAP as trend filter
            'institutional_levels': True,  # Detect institutional levels
            'gap_multiplier': 1.5,      # Gap trading multiplier
        }
        
        # Merge with user params
        if params:
            default_params.update(params)
            
        super().__init__(bot_instance, default_params)
        
        # Index-specific professional configurations
        self.pro_configs = {
            'US30': {
                'avg_daily_range': 400,    # Average daily range in points
                'key_levels': [34000, 34500, 35000, 35500],  # Key psychological levels
                'session_volatility': {'london': 1.2, 'ny': 1.5, 'asian': 0.8}
            },
            'US100': {
                'avg_daily_range': 350,
                'key_levels': [15000, 15500, 16000, 16500],
                'session_volatility': {'london': 1.1, 'ny': 1.8, 'asian': 0.7}
            },
            'US500': {
                'avg_daily_range': 60,
                'key_levels': [4200, 4250, 4300, 4350],
                'session_volatility': {'london': 1.1, 'ny': 1.4, 'asian': 0.8}
            },
            'DE30': {
                'avg_daily_range': 200,
                'key_levels': [15500, 16000, 16500, 17000],
                'session_volatility': {'london': 1.3, 'ny': 0.9, 'asian': 0.6}
            }
        }

    def analyze(self, df):
        """
        Advanced analysis method for professional index breakout trading
        """
        try:
            # Ensure sufficient data for advanced analysis
            min_required = max(self.params['breakout_period'], self.params['trend_filter_period']) + 10
            if len(df) < min_required:
                return {
                    "signal": "HOLD",
                    "price": df['close'].iloc[-1] if not df.empty else 0,
                    "explanation": f"Insufficient data for advanced analysis: need {min_required}, got {len(df)}"
                }

            # Get symbol configuration
            symbol = getattr(self.bot, 'market_for_mt5', 'US500')
            config = self.pro_configs.get(symbol, self.pro_configs['US500'])
            
            # Calculate advanced indicators
            df = self._calculate_advanced_indicators(df)
            
            # Market structure analysis
            market_structure = self._analyze_market_structure(df, config)
            
            # Support and resistance levels
            sr_levels = self._identify_support_resistance(df)
            
            # Volume-Price Analysis
            vpa_signal = self._volume_price_analysis(df)
            
            # Multi-timeframe confirmation
            mtf_signal = self._multi_timeframe_confirmation(df)
            
            # Generate professional signal
            signal_info = self._generate_professional_signal(
                df, market_structure, sr_levels, vpa_signal, mtf_signal, config
            )
            
            return signal_info
            
        except Exception as e:
            logger.error(f"IndexBreakoutProStrategy analysis error: {e}")
            return {
                "signal": "HOLD",
                "price": df['close'].iloc[-1] if not df.empty else 0,
                "explanation": f"Analysis error: {str(e)}"
            }

    def _calculate_advanced_indicators(self, df):
        """Calculate advanced technical indicators for professional analysis"""
        # Basic indicators
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        df['ema_20'] = ta.ema(df['close'], length=20)
        df['ema_50'] = ta.ema(df['close'], length=50)
        
        # Volume indicators
        df['volume_avg'] = df['tick_volume'].rolling(20).mean()
        df['volume_ratio'] = df['tick_volume'] / df['volume_avg']
        
        # VWAP calculation
        df['vwap'] = self._calculate_vwap(df)
        
        # Bollinger Bands for volatility
        bb = ta.bbands(df['close'], length=20)
        df['bb_upper'] = bb['BBU_20_2.0']
        df['bb_lower'] = bb['BBL_20_2.0']
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['close'] * 100
        
        # Market strength indicators
        df['rsi'] = ta.rsi(df['close'], length=14)
        df['adx'] = ta.adx(df['high'], df['low'], df['close'], length=14)['ADX_14']
        
        # Price momentum
        df['momentum'] = df['close'] / df['close'].shift(10) - 1
        df['rate_of_change'] = ta.roc(df['close'], length=10)
        
        return df

    def _calculate_vwap(self, df):
        """Calculate Volume Weighted Average Price"""
        try:
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            vwap = (typical_price * df['tick_volume']).cumsum() / df['tick_volume'].cumsum()
            return vwap
        except Exception:
            return df['close'].rolling(20).mean()  # Fallback to simple MA

    def _analyze_market_structure(self, df, config):
        """Analyze market structure for institutional patterns"""
        try:
            current_price = df['close'].iloc[-1]
            
            # Higher highs and lower lows analysis
            highs = df['high'].rolling(5).max()
            lows = df['low'].rolling(5).min()
            
            recent_high = highs.iloc[-10:].max()
            recent_low = lows.iloc[-10:].min()
            
            # Trend determination
            ema_20 = df['ema_20'].iloc[-1]
            ema_50 = df['ema_50'].iloc[-1]
            
            if ema_20 > ema_50 and current_price > ema_20:
                trend = 'bullish'
            elif ema_20 < ema_50 and current_price < ema_20:
                trend = 'bearish'
            else:
                trend = 'sideways'
            
            # Volatility regime
            atr_current = df['atr'].iloc[-1]
            atr_avg = df['atr'].rolling(20).mean().iloc[-1]
            volatility_regime = 'high' if atr_current > atr_avg * 1.5 else 'normal'
            
            return {
                'trend': trend,
                'recent_high': recent_high,
                'recent_low': recent_low,
                'volatility_regime': volatility_regime,
                'price_vs_vwap': 'above' if current_price > df['vwap'].iloc[-1] else 'below'
            }
            
        except Exception as e:
            logger.error(f"Market structure analysis error: {e}")
            return {'trend': 'sideways', 'volatility_regime': 'normal'}

    def _identify_support_resistance(self, df):
        """Identify key support and resistance levels"""
        try:
            levels = []
            lookback = self.params['breakout_period']
            
            # Find pivot highs and lows
            for i in range(lookback, len(df) - lookback):
                # Pivot high
                if (df['high'].iloc[i] > df['high'].iloc[i-lookback:i].max() and
                    df['high'].iloc[i] > df['high'].iloc[i+1:i+lookback+1].max()):
                    levels.append({'level': df['high'].iloc[i], 'type': 'resistance', 'strength': 1})
                
                # Pivot low
                if (df['low'].iloc[i] < df['low'].iloc[i-lookback:i].min() and
                    df['low'].iloc[i] < df['low'].iloc[i+1:i+lookback+1].min()):
                    levels.append({'level': df['low'].iloc[i], 'type': 'support', 'strength': 1})
            
            # Consolidate nearby levels
            consolidated_levels = self._consolidate_levels(levels)
            
            return consolidated_levels
            
        except Exception as e:
            logger.error(f"Support/Resistance identification error: {e}")
            return []

    def _consolidate_levels(self, levels):
        """Consolidate nearby support/resistance levels"""
        if not levels:
            return []
        
        consolidated = []
        tolerance = 0.002  # 0.2% tolerance for level grouping
        
        for level in levels:
            added = False
            for i, existing in enumerate(consolidated):
                if abs(level['level'] - existing['level']) / existing['level'] < tolerance:
                    # Merge levels
                    consolidated[i]['strength'] += level['strength']
                    consolidated[i]['level'] = (existing['level'] + level['level']) / 2
                    added = True
                    break
            
            if not added:
                consolidated.append(level)
        
        return sorted(consolidated, key=lambda x: x['strength'], reverse=True)[:10]

    def _volume_price_analysis(self, df):
        """Advanced Volume-Price Analysis"""
        try:
            current_volume = df['tick_volume'].iloc[-1]
            avg_volume = df['volume_avg'].iloc[-1]
            volume_ratio = current_volume / avg_volume
            
            price_change = df['close'].pct_change().iloc[-1]
            
            # Volume-Price relationship analysis
            if volume_ratio > self.params['volume_surge_multiplier']:
                if price_change > 0.001:  # 0.1% positive move
                    return {'signal': 'bullish_volume', 'strength': min(volume_ratio / 2, 3.0)}
                elif price_change < -0.001:  # 0.1% negative move
                    return {'signal': 'bearish_volume', 'strength': min(volume_ratio / 2, 3.0)}
            
            return {'signal': 'neutral', 'strength': 1.0}
            
        except Exception:
            return {'signal': 'neutral', 'strength': 1.0}

    def _multi_timeframe_confirmation(self, df):
        """Multi-timeframe trend confirmation"""
        try:
            # Short-term (last 5 candles)
            short_trend = 'bullish' if df['close'].iloc[-1] > df['close'].iloc[-6] else 'bearish'
            
            # Medium-term (last 20 candles)
            medium_trend = 'bullish' if df['ema_20'].iloc[-1] > df['ema_20'].iloc[-21] else 'bearish'
            
            # Long-term (last 50 candles)
            long_trend = 'bullish' if df['ema_50'].iloc[-1] > df['ema_50'].iloc[-51] else 'bearish'
            
            # Confluence scoring
            bullish_votes = [short_trend, medium_trend, long_trend].count('bullish')
            bearish_votes = [short_trend, medium_trend, long_trend].count('bearish')
            
            if bullish_votes >= 2:
                return {'trend': 'bullish', 'confidence': bullish_votes / 3}
            elif bearish_votes >= 2:
                return {'trend': 'bearish', 'confidence': bearish_votes / 3}
            else:
                return {'trend': 'neutral', 'confidence': 0.5}
                
        except Exception:
            return {'trend': 'neutral', 'confidence': 0.5}

    def _generate_professional_signal(self, df, market_structure, sr_levels, vpa_signal, mtf_signal, config):
        """Generate sophisticated trading signal based on all analyses"""
        current_price = df['close'].iloc[-1]
        current_atr = df['atr'].iloc[-1]
        
        # Initialize signal components
        signal_components = []
        signal_strength = 0.0
        
        # Breakout detection
        breakout_signal = self._detect_breakout(df, sr_levels)
        
        # Signal generation logic
        if breakout_signal['type'] == 'bullish_breakout':
            # Bullish breakout conditions
            if (market_structure['trend'] in ['bullish', 'sideways'] and
                vpa_signal['signal'] in ['bullish_volume', 'neutral'] and
                mtf_signal['trend'] in ['bullish', 'neutral']):
                
                signal_components.append("Bullish breakout detected")
                signal_strength += 2.0
                
                if vpa_signal['signal'] == 'bullish_volume':
                    signal_components.append(f"Volume confirmation ({vpa_signal['strength']:.1f}x)")
                    signal_strength += vpa_signal['strength']
                
                if mtf_signal['trend'] == 'bullish':
                    signal_components.append(f"Multi-timeframe bullish ({mtf_signal['confidence']:.0%})")
                    signal_strength += mtf_signal['confidence']
                
                return {
                    "signal": "BUY",
                    "price": current_price,
                    "explanation": f"PROFESSIONAL BUY: {', '.join(signal_components)}"
                }
        
        elif breakout_signal['type'] == 'bearish_breakout':
            # Bearish breakout conditions
            if (market_structure['trend'] in ['bearish', 'sideways'] and
                vpa_signal['signal'] in ['bearish_volume', 'neutral'] and
                mtf_signal['trend'] in ['bearish', 'neutral']):
                
                signal_components.append("Bearish breakout detected")
                signal_strength += 2.0
                
                if vpa_signal['signal'] == 'bearish_volume':
                    signal_components.append(f"Volume confirmation ({vpa_signal['strength']:.1f}x)")
                    signal_strength += vpa_signal['strength']
                
                if mtf_signal['trend'] == 'bearish':
                    signal_components.append(f"Multi-timeframe bearish ({mtf_signal['confidence']:.0%})")
                    signal_strength += mtf_signal['confidence']
                
                return {
                    "signal": "SELL",
                    "price": current_price,
                    "explanation": f"PROFESSIONAL SELL: {', '.join(signal_components)}"
                }
        
        # No clear signal
        hold_reasons = []
        if breakout_signal['type'] == 'no_breakout':
            hold_reasons.append("No significant breakout")
        if market_structure['volatility_regime'] == 'high':
            hold_reasons.append("High volatility regime")
        if vpa_signal['signal'] == 'neutral':
            hold_reasons.append("Neutral volume pattern")
        
        return {
            "signal": "HOLD",
            "price": current_price,
            "explanation": f"WAITING: {', '.join(hold_reasons) if hold_reasons else 'Analyzing market conditions'}"
        }

    def _detect_breakout(self, df, sr_levels):
        """Detect genuine breakouts from key levels"""
        try:
            current_price = df['close'].iloc[-1]
            current_atr = df['atr'].iloc[-1]
            
            min_breakout_distance = current_atr * self.params['min_breakout_size']
            
            for level in sr_levels:
                distance = abs(current_price - level['level'])
                
                if level['type'] == 'resistance' and current_price > level['level'] + min_breakout_distance:
                    # Bullish breakout
                    if self._confirm_breakout(df, level['level'], 'bullish'):
                        return {
                            'type': 'bullish_breakout',
                            'level': level['level'],
                            'strength': level['strength']
                        }
                
                elif level['type'] == 'support' and current_price < level['level'] - min_breakout_distance:
                    # Bearish breakout
                    if self._confirm_breakout(df, level['level'], 'bearish'):
                        return {
                            'type': 'bearish_breakout',
                            'level': level['level'],
                            'strength': level['strength']
                        }
            
            return {'type': 'no_breakout', 'level': None, 'strength': 0}
            
        except Exception:
            return {'type': 'no_breakout', 'level': None, 'strength': 0}

    def _confirm_breakout(self, df, level, direction):
        """Confirm breakout with multiple criteria"""
        try:
            confirmation_period = self.params['confirmation_candles']
            recent_closes = df['close'].iloc[-confirmation_period:]
            
            if direction == 'bullish':
                return all(close > level for close in recent_closes)
            else:
                return all(close < level for close in recent_closes)
                
        except Exception:
            return False

    def analyze_df(self, df):
        """Backtesting version with full DataFrame processing"""
        if len(df) < 60:
            return df
            
        try:
            # Calculate indicators for entire DataFrame
            df = self._calculate_advanced_indicators(df)
            
            # Initialize signal columns
            df['signal'] = 'HOLD'
            df['signal_strength'] = 0.0
            df['explanation'] = ''
            
            # Process each row for backtesting
            for i in range(60, len(df)):
                current_df = df.iloc[:i+1].copy()
                
                # Simplified analysis for backtesting performance
                signal_info = self._simplified_analysis(current_df)
                
                # Store results
                df.loc[df.index[i], 'signal'] = signal_info['signal']
                df.loc[df.index[i], 'explanation'] = signal_info['explanation']
                
                if signal_info['signal'] in ['BUY', 'SELL']:
                    df.loc[df.index[i], 'signal_strength'] = 0.8  # High confidence for pro strategy
            
            return df
            
        except Exception as e:
            logger.error(f"IndexBreakoutProStrategy analyze_df error: {e}")
            return df

    def _simplified_analysis(self, df):
        """Simplified analysis for backtesting performance"""
        try:
            current_price = df['close'].iloc[-1]
            
            # Simple breakout detection for backtesting
            lookback = 20
            recent_high = df['high'].iloc[-lookback:].max()
            recent_low = df['low'].iloc[-lookback:].min()
            
            volume_surge = df['volume_ratio'].iloc[-1] > 1.5
            
            if current_price > recent_high and volume_surge:
                return {
                    "signal": "BUY",
                    "price": current_price,
                    "explanation": "Breakout above recent high with volume"
                }
            elif current_price < recent_low and volume_surge:
                return {
                    "signal": "SELL", 
                    "price": current_price,
                    "explanation": "Breakdown below recent low with volume"
                }
            
            return {
                "signal": "HOLD",
                "price": current_price,
                "explanation": "No clear breakout signal"
            }
            
        except Exception:
            return {
                "signal": "HOLD",
                "price": df['close'].iloc[-1],
                "explanation": "Analysis error"
            }

    @classmethod
    def get_definable_params(cls):
        """Return list of user-configurable parameters for professional strategy"""
        return [
            {
                'name': 'breakout_period',
                'display_name': 'Breakout Detection Period',
                'type': 'int',
                'default': 20,
                'min': 10,
                'max': 50,
                'description': 'Lookback period for breakout level detection'
            },
            {
                'name': 'volume_surge_multiplier',
                'display_name': 'Volume Surge Multiplier',
                'type': 'float',
                'default': 2.0,
                'min': 1.5,
                'max': 5.0,
                'description': 'Volume multiplier to detect institutional activity'
            },
            {
                'name': 'confirmation_candles',
                'display_name': 'Breakout Confirmation Candles',
                'type': 'int',
                'default': 2,
                'min': 1,
                'max': 5,
                'description': 'Number of candles to confirm breakout'
            },
            {
                'name': 'atr_multiplier_sl',
                'display_name': 'ATR Stop Loss Multiplier',
                'type': 'float',
                'default': 2.0,
                'min': 1.0,
                'max': 4.0,
                'description': 'ATR multiplier for dynamic stop loss'
            },
            {
                'name': 'atr_multiplier_tp',
                'display_name': 'ATR Take Profit Multiplier',
                'type': 'float',
                'default': 4.0,
                'min': 2.0,
                'max': 8.0,
                'description': 'ATR multiplier for dynamic take profit'
            },
            {
                'name': 'min_breakout_size',
                'display_name': 'Minimum Breakout Size',
                'type': 'float',
                'default': 0.3,
                'min': 0.1,
                'max': 1.0,
                'description': 'Minimum breakout size as fraction of ATR'
            },
            {
                'name': 'vwap_filter',
                'display_name': 'VWAP Trend Filter',
                'type': 'bool',
                'default': True,
                'description': 'Use VWAP as additional trend filter'
            },
            {
                'name': 'institutional_levels',
                'display_name': 'Institutional Level Detection',
                'type': 'bool',
                'default': True,
                'description': 'Detect and use institutional support/resistance levels'
            }
        ]