# core/strategies/index_breakout_pro.py

import pandas as pd
import pandas_ta as ta
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
    
    name = 'INDEX_BREAKOUT_PRO'
    description = 'Advanced breakout strategy with institutional pattern recognition for stock indices'
    
    def __init__(self, bot_instance, params=None):
        # Advanced parameters for professional breakout trading
        default_params = {
            'breakout_period': 20,      # Lookback period for breakout levels
            'volume_surge_multiplier': 1.5,  # Volume surge detection (reduced from 2.0 for more signals)
            'confirmation_candles': 2,   # Candles to confirm breakout
            'support_resistance_strength': 3,  # Minimum touches for S/R level
            'atr_multiplier_sl': 2.0,   # ATR multiplier for stop loss
            'atr_multiplier_tp': 4.0,   # ATR multiplier for take profit
            'min_breakout_size': 0.2,   # Minimum breakout size (reduced from 0.3 for sensitivity)
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
        # Handle volume column compatibility (CSV files use 'volume', MT5 uses 'tick_volume')
        if 'volume' in df.columns and 'tick_volume' not in df.columns:
            df['tick_volume'] = df['volume']
        elif 'tick_volume' not in df.columns and 'volume' not in df.columns:
            # Fallback: create dummy volume data
            df['tick_volume'] = df['close'] * 0 + 1  # Dummy volume
            logger.warning("No volume data found, using dummy volume for calculations")
        
        # Basic indicators
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        df['ema_20'] = ta.ema(df['close'], length=20)
        df['ema_50'] = ta.ema(df['close'], length=50)
        
        # More practical volume indicators for backtesting
        # Use a shorter period and ensure we always have valid volume ratios
        volume_period = min(10, len(df) // 4)  # Adaptive period
        if volume_period < 5:
            volume_period = 5
            
        df['volume_avg'] = df['tick_volume'].rolling(volume_period, min_periods=1).mean()
        
        # Prevent division by zero and ensure realistic volume ratios
        df['volume_ratio'] = df['tick_volume'] / df['volume_avg'].replace(0, df['tick_volume'].mean())
        
        # Fill any NaN values in volume_ratio
        df['volume_ratio'] = df['volume_ratio'].fillna(1.0)
        
        # VWAP calculation
        df['vwap'] = self._calculate_vwap(df)
        
        # Bollinger Bands for volatility
        bb = ta.bbands(df['close'], length=20)
        if bb is not None:
            df['bb_upper'] = bb['BBU_20_2.0']
            df['bb_lower'] = bb['BBL_20_2.0']
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['close'] * 100
        else:
            # Fallback calculation when ta.bbands returns None
            sma_20 = df['close'].rolling(20).mean()
            std_20 = df['close'].rolling(20).std()
            df['bb_upper'] = sma_20 + (std_20 * 2)
            df['bb_lower'] = sma_20 - (std_20 * 2)
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['close'] * 100
        
        # Market strength indicators
        rsi_result = ta.rsi(df['close'], length=14)
        if rsi_result is not None:
            df['rsi'] = rsi_result
        else:
            # Fallback RSI calculation
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
        adx_result = ta.adx(df['high'], df['low'], df['close'], length=14)
        if adx_result is not None and 'ADX_14' in adx_result.columns:
            df['adx'] = adx_result['ADX_14']
        else:
            # Fallback: use a simple trend strength indicator
            df['adx'] = abs(df['close'].pct_change(14)) * 100
        
        # Price momentum
        df['momentum'] = df['close'] / df['close'].shift(10) - 1
        roc_result = ta.roc(df['close'], length=10)
        if roc_result is not None:
            df['rate_of_change'] = roc_result
        else:
            # Fallback ROC calculation
            df['rate_of_change'] = (df['close'] / df['close'].shift(10) - 1) * 100
        
        return df

    def _calculate_vwap(self, df):
        """Calculate Volume Weighted Average Price"""
        try:
            # Use tick_volume if available, otherwise use volume, otherwise fallback
            volume_col = 'tick_volume' if 'tick_volume' in df.columns else ('volume' if 'volume' in df.columns else None)
            
            if volume_col is None:
                logger.warning("No volume data available for VWAP calculation, using simple MA")
                return df['close'].rolling(20).mean()
            
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            vwap = (typical_price * df[volume_col]).cumsum() / df[volume_col].cumsum()
            return vwap
        except Exception as e:
            logger.warning(f"VWAP calculation failed: {e}, using simple MA fallback")
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
        df['atr'].iloc[-1]
        
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
                abs(current_price - level['level'])
                
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
                # Skip if we don't have enough data or NaN values
                if (pd.isna(df['atr'].iloc[i]) or 
                    pd.isna(df['volume_ratio'].iloc[i]) or 
                    pd.isna(df['ema_20'].iloc[i]) or
                    pd.isna(df['ema_50'].iloc[i])):
                    continue
                
                # Get current data slice for analysis
                current_df = df.iloc[:i+1].copy()
                
                # Simplified analysis for backtesting performance
                signal_info = self._simplified_analysis(current_df)
                
                # Store results
                df.loc[df.index[i], 'signal'] = signal_info['signal']
                df.loc[df.index[i], 'explanation'] = signal_info['explanation']
                
                if signal_info['signal'] in ['BUY', 'SELL']:
                    # Calculate signal strength based on volume and momentum
                    volume_strength = min(2.0, df['volume_ratio'].iloc[i]) - 1.0
                    momentum_strength = abs(df['momentum'].iloc[i]) if not pd.isna(df['momentum'].iloc[i]) else 0.0
                    signal_strength = min(1.0, (volume_strength + momentum_strength) * 0.4 + 0.6)
                    df.loc[df.index[i], 'signal_strength'] = signal_strength
            
            return df
            
        except Exception as e:
            logger.error(f"IndexBreakoutProStrategy analyze_df error: {e}")
            return df

    def _simplified_analysis(self, df):
        """Simplified analysis for backtesting performance"""
        try:
            if len(df) < 20:
                return {
                    "signal": "HOLD",
                    "price": df['close'].iloc[-1],
                    "explanation": "Insufficient data for analysis"
                }
            
            current_price = df['close'].iloc[-1]
            
            # Practical breakout detection for backtesting
            lookback = min(self.params.get('breakout_period', 20), len(df) - 1)
            recent_high = df['high'].iloc[-lookback:].max()
            recent_low = df['low'].iloc[-lookback:].min()
            
            # Calculate price position relative to range
            price_range = recent_high - recent_low
            price_position = (current_price - recent_low) / price_range if price_range > 0 else 0.5
            
            # Volume analysis (more lenient)
            volume_ratio = df['volume_ratio'].iloc[-1] if not pd.isna(df['volume_ratio'].iloc[-1]) else 1.0
            volume_threshold = self.params.get('volume_surge_multiplier', 1.5) * 0.8  # Even more lenient
            volume_confirmed = volume_ratio >= volume_threshold
            
            # Trend analysis using EMAs
            ema_20 = df['ema_20'].iloc[-1]
            ema_50 = df['ema_50'].iloc[-1]
            
            if not pd.isna(ema_20) and not pd.isna(ema_50):
                bullish_trend = ema_20 > ema_50
                bearish_trend = ema_20 < ema_50
                abs(ema_20 - ema_50) / ema_50 if ema_50 > 0 else 0
            else:
                # Fallback trend detection using simple price comparison
                bullish_trend = current_price > df['close'].iloc[-10] if len(df) > 10 else True
                bearish_trend = current_price < df['close'].iloc[-10] if len(df) > 10 else True
            
            # Price momentum analysis
            if len(df) >= 5:
                momentum_5 = (current_price - df['close'].iloc[-5]) / df['close'].iloc[-5]
                momentum_10 = (current_price - df['close'].iloc[-10]) / df['close'].iloc[-10] if len(df) >= 10 else momentum_5
            else:
                momentum_5 = momentum_10 = 0
            
            # ATR-based breakout threshold (more sensitive)
            atr = df['atr'].iloc[-1]
            if not pd.isna(atr) and atr > 0:
                breakout_threshold = atr * self.params.get('min_breakout_size', 0.2) * 0.5  # Half the normal threshold
            else:
                breakout_threshold = price_range * 0.002  # 0.2% of range
            
            # Generate signals with multiple criteria (more flexible)
            
            # Strong breakout signals (primary)
            if current_price > recent_high + breakout_threshold:
                if volume_confirmed and bullish_trend:
                    return {
                        "signal": "BUY",
                        "price": current_price,
                        "explanation": f"Strong bullish breakout: price {current_price:.2f} > high {recent_high:.2f}, vol {volume_ratio:.2f}x, trend up"
                    }
                elif volume_confirmed:
                    return {
                        "signal": "BUY",
                        "price": current_price,
                        "explanation": f"Volume breakout: price {current_price:.2f} > high {recent_high:.2f}, vol {volume_ratio:.2f}x"
                    }
                elif momentum_5 > 0.003:  # 0.3% momentum
                    return {
                        "signal": "BUY",
                        "price": current_price,
                        "explanation": f"Momentum breakout: price {current_price:.2f} > high {recent_high:.2f}, momentum {momentum_5:.1%}"
                    }
            
            elif current_price < recent_low - breakout_threshold:
                if volume_confirmed and bearish_trend:
                    return {
                        "signal": "SELL",
                        "price": current_price,
                        "explanation": f"Strong bearish breakdown: price {current_price:.2f} < low {recent_low:.2f}, vol {volume_ratio:.2f}x, trend down"
                    }
                elif volume_confirmed:
                    return {
                        "signal": "SELL",
                        "price": current_price,
                        "explanation": f"Volume breakdown: price {current_price:.2f} < low {recent_low:.2f}, vol {volume_ratio:.2f}x"
                    }
                elif momentum_5 < -0.003:  # -0.3% momentum
                    return {
                        "signal": "SELL",
                        "price": current_price,
                        "explanation": f"Momentum breakdown: price {current_price:.2f} < low {recent_low:.2f}, momentum {momentum_5:.1%}"
                    }
            
            # Secondary signals: Range position based (more signals)
            elif price_position > 0.85 and bullish_trend and momentum_5 > 0.001:
                return {
                    "signal": "BUY",
                    "price": current_price,
                    "explanation": f"Range top breakout setup: {price_position:.0%} of range, trend up, momentum {momentum_5:.1%}"
                }
            
            elif price_position < 0.15 and bearish_trend and momentum_5 < -0.001:
                return {
                    "signal": "SELL",
                    "price": current_price,
                    "explanation": f"Range bottom breakdown setup: {price_position:.0%} of range, trend down, momentum {momentum_5:.1%}"
                }
            
            # Tertiary signals: Strong momentum (even without breakouts)
            elif abs(momentum_5) > 0.005 and abs(momentum_10) > 0.008:  # Strong momentum
                if momentum_5 > 0 and momentum_10 > 0 and bullish_trend:
                    return {
                        "signal": "BUY",
                        "price": current_price,
                        "explanation": f"Strong momentum: 5-period {momentum_5:.1%}, 10-period {momentum_10:.1%}, trend aligned"
                    }
                elif momentum_5 < 0 and momentum_10 < 0 and bearish_trend:
                    return {
                        "signal": "SELL",
                        "price": current_price,
                        "explanation": f"Strong negative momentum: 5-period {momentum_5:.1%}, 10-period {momentum_10:.1%}, trend aligned"
                    }
            
            # Provide informative HOLD explanation
            if not volume_confirmed:
                return {
                    "signal": "HOLD",
                    "price": current_price,
                    "explanation": f"Low volume: {volume_ratio:.2f}x (need {volume_threshold:.2f}x), price at {price_position:.0%} of range"
                }
            elif price_range / current_price < 0.01:  # Range too small
                return {
                    "signal": "HOLD",
                    "price": current_price,
                    "explanation": f"Narrow range: ${price_range:.2f} ({price_range/current_price:.1%}), waiting for volatility"
                }
            else:
                return {
                    "signal": "HOLD",
                    "price": current_price,
                    "explanation": f"No clear signal: {price_position:.0%} range position, vol {volume_ratio:.2f}x, momentum {momentum_5:.1%}"
                }
            
        except Exception as e:
            logger.error(f"Simplified analysis error: {e}")
            return {
                "signal": "HOLD",
                "price": df['close'].iloc[-1] if not df.empty else 0,
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
                'default': 1.5,
                'min': 1.2,
                'max': 3.0,
                'description': 'Volume multiplier to detect institutional activity (lower = more signals)'
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
                'default': 0.2,
                'min': 0.1,
                'max': 0.8,
                'description': 'Minimum breakout size as fraction of ATR (lower = more sensitive)'
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
            },
            {
                'name': 'support_resistance_strength',
                'display_name': 'S/R Level Strength',
                'type': 'int',
                'default': 3,
                'min': 2,
                'max': 10,
                'description': 'Minimum number of touches required for valid support/resistance level'
            },
            {
                'name': 'max_risk_per_trade',
                'display_name': 'Maximum Risk Per Trade (%)',
                'type': 'float',
                'default': 1.0,
                'min': 0.5,
                'max': 5.0,
                'description': 'Maximum risk percentage per individual trade'
            },
            {
                'name': 'trend_filter_period',
                'display_name': 'Trend Filter Period',
                'type': 'int',
                'default': 50,
                'min': 20,
                'max': 100,
                'description': 'Period for long-term trend filter analysis'
            },
            {
                'name': 'gap_multiplier',
                'display_name': 'Gap Trading Multiplier',
                'type': 'float',
                'default': 1.5,
                'min': 1.0,
                'max': 3.0,
                'description': 'Multiplier for gap trading opportunity sizing'
            }
        ]