# core/strategies/market_condition_detector.py
"""
📊 Market Condition Detector for Automatic Strategy Switching

This module detects market conditions (trending vs ranging) for different instruments
and provides market state information for strategy selection.

Features:
- Trending vs ranging detection using multiple methods
- Volatility regime analysis
- Session-aware trading conditions
- Instrument-specific market characteristics
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MarketConditionDetector:
    """
    Detects market conditions for automatic strategy switching
    """
    
    def __init__(self):
        # Market characteristics for different instrument types
        self.instrument_configs = {
            'INDICES': {
                'trend_sensitivity': 0.7,
                'volatility_threshold': 1.5,
                'session_hours': {'ny': (13, 22), 'london': (8, 16)},
                'typical_volatility': 0.8
            },
            'FOREX': {
                'trend_sensitivity': 0.6,
                'volatility_threshold': 1.2,
                'session_hours': {'ny': (13, 22), 'london': (8, 16), 'asian': (0, 8)},
                'typical_volatility': 0.5
            },
            'GOLD': {
                'trend_sensitivity': 0.8,
                'volatility_threshold': 2.0,
                'session_hours': {'ny': (13, 22), 'london': (8, 16)},
                'typical_volatility': 1.2
            },
            'CRYPTO': {
                'trend_sensitivity': 0.5,
                'volatility_threshold': 3.0,
                'session_hours': {},  # 24/7 market
                'typical_volatility': 2.5
            }
        }
    
    def detect_market_condition(self, df: pd.DataFrame, symbol: str = 'EURUSD') -> dict:
        """
        Detect current market condition for a given instrument
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol (e.g., 'EURUSD', 'US500')
            
        Returns:
            dict: Market condition analysis
        """
        try:
            if df.empty or len(df) < 50:
                return self._default_condition()
            
            # Determine instrument type
            instrument_type = self._classify_instrument(symbol)
            config = self.instrument_configs.get(instrument_type, self.instrument_configs['FOREX'])
            
            # Calculate indicators
            df_analysis = self._calculate_indicators(df)
            
            # Detect trend vs range
            trend_score = self._calculate_trend_score(df_analysis, config)
            volatility_regime = self._analyze_volatility_regime(df_analysis, config)
            session_status = self._check_trading_session(config)
            
            # Determine market condition
            if trend_score > config['trend_sensitivity']:
                market_condition = 'trending'
                confidence = min(1.0, trend_score)
            else:
                market_condition = 'ranging'
                confidence = min(1.0, 1 - trend_score)
            
            # Price action characteristics
            price_action = self._analyze_price_action(df_analysis)
            
            return {
                'instrument_type': instrument_type,
                'market_condition': market_condition,
                'confidence': confidence,
                'volatility_regime': volatility_regime,
                'session_status': session_status,
                'price_action': price_action,
                'trend_score': trend_score,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Market condition detection error: {e}")
            return self._default_condition()
    
    def _classify_instrument(self, symbol: str) -> str:
        """Classify instrument type based on symbol"""
        symbol_upper = symbol.upper()
        
        # Indices
        if any(index in symbol_upper for index in ['US30', 'US100', 'US500', 'DE30', 'UK100', 'JP225', 'NAS100', 'SPX500']):
            return 'INDICES'
        
        # Gold/Metals
        if any(gold in symbol_upper for gold in ['XAU', 'XAG', 'GOLD']):
            return 'GOLD'
        
        # Crypto
        if any(crypto in symbol_upper for crypto in ['BTC', 'ETH', 'LTC', 'ADA', 'DOT', 'SOL']):
            return 'CRYPTO'
        
        # Default to Forex
        return 'FOREX'
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for market condition analysis"""
        df_calc = df.copy()
        
        # Price changes
        df_calc['returns'] = df_calc['close'].pct_change()
        df_calc['price_change'] = df_calc['close'] - df_calc['open']
        
        # Moving averages
        df_calc['sma_20'] = df_calc['close'].rolling(20).mean()
        df_calc['sma_50'] = df_calc['close'].rolling(50).mean()
        
        # ATR for volatility
        df_calc['tr'] = np.maximum(
            np.maximum(
                df_calc['high'] - df_calc['low'],
                abs(df_calc['high'] - df_calc['close'].shift(1))
            ),
            abs(df_calc['low'] - df_calc['close'].shift(1))
        )
        df_calc['atr'] = df_calc['tr'].rolling(14).mean()
        
        # ADX for trend strength
        df_calc = self._calculate_adx(df_calc)
        
        return df_calc
    
    def _calculate_adx(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate ADX (Average Directional Index)"""
        # This is a simplified ADX calculation
        df_calc = df.copy()
        
        # +DI and -DI calculation (simplified)
        up_move = df_calc['high'] - df_calc['high'].shift(1)
        down_move = df_calc['low'].shift(1) - df_calc['low']
        
        # +DM and -DM
        df_calc['+dm'] = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        df_calc['-dm'] = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        # ATR (already calculated)
        atr = df_calc['atr']
        
        # +DI and -DI
        df_calc['+di'] = 100 * (df_calc['+dm'].rolling(14).mean() / atr)
        df_calc['-di'] = 100 * (df_calc['-dm'].rolling(14).mean() / atr)
        
        # ADX
        dx = 100 * (abs(df_calc['+di'] - df_calc['-di']) / (df_calc['+di'] + df_calc['-di']))
        df_calc['adx'] = dx.rolling(14).mean()
        
        return df_calc
    
    def _calculate_trend_score(self, df: pd.DataFrame, config: dict) -> float:
        """Calculate trend score based on multiple factors"""
        if len(df) < 50:
            return 0.5
        
        # ADX trend strength (0-100, higher = stronger trend)
        adx_values = df['adx'].tail(20).dropna()
        if len(adx_values) > 0:
            adx_trend = np.mean(adx_values) / 100  # Normalize to 0-1
        else:
            adx_trend = 0.5
        
        # Moving average alignment
        recent_data = df.tail(20)
        if len(recent_data) > 0:
            ma_aligned = (recent_data['sma_20'] > recent_data['sma_50']).mean()
            ma_trend = abs(ma_aligned - 0.5) * 2  # Convert to 0-1 scale
        else:
            ma_trend = 0.5
        
        # Price trend consistency
        returns = df['returns'].tail(20).dropna()
        if len(returns) > 0:
            trend_consistency = abs(returns.mean() / (returns.std() + 1e-10))  # Sharpe-like ratio
            trend_consistency = min(1.0, trend_consistency)  # Cap at 1.0
        else:
            trend_consistency = 0.5
        
        # Weighted average of trend factors
        trend_score = (adx_trend * 0.4 + ma_trend * 0.3 + trend_consistency * 0.3)
        
        return min(1.0, max(0.0, trend_score))
    
    def _analyze_volatility_regime(self, df: pd.DataFrame, config: dict) -> str:
        """Analyze current volatility regime"""
        if len(df) < 20:
            return 'normal'
        
        # Current ATR vs historical ATR
        current_atr = df['atr'].iloc[-1]
        avg_atr = df['atr'].tail(50).mean()
        
        if pd.isna(current_atr) or pd.isna(avg_atr) or avg_atr == 0:
            return 'normal'
        
        volatility_ratio = current_atr / avg_atr
        
        if volatility_ratio > config['volatility_threshold']:
            return 'high'
        elif volatility_ratio < (1 / config['volatility_threshold']):
            return 'low'
        else:
            return 'normal'
    
    def _check_trading_session(self, config: dict) -> str:
        """Check current trading session status"""
        try:
            current_time = datetime.now()
            current_hour = current_time.hour
            
            # Check active sessions
            active_sessions = []
            for session_name, (start_hour, end_hour) in config['session_hours'].items():
                if start_hour <= current_hour <= end_hour:
                    active_sessions.append(session_name)
            
            if active_sessions:
                return f"active_{'_'.join(active_sessions)}"
            else:
                return "quiet"
                
        except Exception:
            return "unknown"
    
    def _analyze_price_action(self, df: pd.DataFrame) -> dict:
        """Analyze recent price action characteristics"""
        if len(df) < 20:
            return {'pattern': 'neutral', 'strength': 0.5}
        
        recent_data = df.tail(20)
        
        # Calculate price action metrics
        body_size = abs(recent_data['close'] - recent_data['open'])
        wick_size = (recent_data['high'] - recent_data['low']) - body_size
        body_wick_ratio = body_size / (wick_size + 1e-10)
        
        # Trend direction
        price_change = recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]
        trend_direction = 'bullish' if price_change > 0 else 'bearish' if price_change < 0 else 'neutral'
        
        # Volatility
        volatility = recent_data['returns'].std() * 100
        
        return {
            'pattern': trend_direction,
            'strength': min(1.0, volatility / 2),  # Normalize volatility
            'body_wick_ratio': body_wick_ratio.mean() if len(body_wick_ratio) > 0 else 1.0
        }
    
    def _default_condition(self) -> dict:
        """Return default market condition when detection fails"""
        return {
            'instrument_type': 'FOREX',
            'market_condition': 'ranging',
            'confidence': 0.5,
            'volatility_regime': 'normal',
            'session_status': 'unknown',
            'price_action': {'pattern': 'neutral', 'strength': 0.5},
            'trend_score': 0.5,
            'timestamp': datetime.now().isoformat()
        }

# Global instance
market_condition_detector = MarketConditionDetector()

def get_market_condition(df: pd.DataFrame, symbol: str = 'EURUSD') -> dict:
    """
    Convenience function to get market condition
    
    Args:
        df: DataFrame with OHLCV data
        symbol: Trading symbol
        
    Returns:
        dict: Market condition analysis
    """
    return market_condition_detector.detect_market_condition(df, symbol)