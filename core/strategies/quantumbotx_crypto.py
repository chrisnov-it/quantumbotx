# /core/strategies/quantumbotx_crypto.py
import pandas as pd
import pandas_ta as ta
import numpy as np
from .base_strategy import BaseStrategy

class QuantumBotXCryptoStrategy(BaseStrategy):
    name = 'QuantumBotX Crypto'
    description = 'Bitcoin and crypto optimized strategy with enhanced volatility management and 24/7 market awareness.'

    @classmethod
    def get_definable_params(cls):
        return [
            # Faster periods for crypto volatility
            {"name": "adx_period", "label": "ADX Period", "type": "number", "default": 10},
            {"name": "adx_threshold", "label": "ADX Threshold", "type": "number", "default": 20},
            {"name": "ma_fast_period", "label": "Fast MA Period", "type": "number", "default": 12},
            {"name": "ma_slow_period", "label": "Slow MA Period", "type": "number", "default": 26},
            {"name": "bb_length", "label": "BB Length", "type": "number", "default": 20},
            {"name": "bb_std", "label": "BB Std Dev", "type": "number", "default": 2.2, "step": 0.1},
            {"name": "trend_filter_period", "label": "Trend Filter (SMA)", "type": "number", "default": 100},
            # Crypto-specific parameters
            {"name": "rsi_period", "label": "RSI Period", "type": "number", "default": 14},
            {"name": "rsi_overbought", "label": "RSI Overbought", "type": "number", "default": 75},
            {"name": "rsi_oversold", "label": "RSI Oversold", "type": "number", "default": 25},
            {"name": "volatility_filter", "label": "Volatility Filter", "type": "number", "default": 2.0, "step": 0.1},
            {"name": "weekend_mode", "label": "Weekend Mode", "type": "boolean", "default": True}
        ]

    def analyze(self, df):
        """Method for LIVE TRADING - Bitcoin optimized."""
        trend_filter_period = self.params.get('trend_filter_period', 100)
        if df is None or df.empty or len(df) < trend_filter_period:
            return {"signal": "HOLD", "price": None, "explanation": "Insufficient data for crypto analysis."}

        # Get parameters
        adx_period = self.params.get('adx_period', 10)
        adx_threshold = self.params.get('adx_threshold', 20)
        ma_fast_period = self.params.get('ma_fast_period', 12)
        ma_slow_period = self.params.get('ma_slow_period', 26)
        bb_length = self.params.get('bb_length', 20)
        bb_std = self.params.get('bb_std', 2.2)
        rsi_period = self.params.get('rsi_period', 14)
        rsi_overbought = self.params.get('rsi_overbought', 75)
        rsi_oversold = self.params.get('rsi_oversold', 25)
        volatility_filter = self.params.get('volatility_filter', 2.0)
        weekend_mode = self.params.get('weekend_mode', True)

        # Calculate indicators
        bbu_col = f'BBU_{bb_length}_{bb_std:.1f}'
        bbl_col = f'BBL_{bb_length}_{bb_std:.1f}'
        trend_filter_col = f'SMA_{trend_filter_period}'

        df.ta.adx(length=adx_period, append=True)
        df[f'SMA_{ma_fast_period}'] = ta.sma(df['close'], length=ma_fast_period)
        df[f'SMA_{ma_slow_period}'] = ta.sma(df['close'], length=ma_slow_period)
        df.ta.bbands(length=bb_length, std=bb_std, append=True)
        df[trend_filter_col] = ta.sma(df['close'], length=trend_filter_period)
        df.ta.rsi(length=rsi_period, append=True)
        
        # Crypto volatility indicator
        df['volatility'] = df['close'].rolling(24).std() / df['close'].rolling(24).mean()
        
        df.dropna(inplace=True)
        
        if len(df) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Indicators not ready."}

        last = df.iloc[-1]
        prev = df.iloc[-2]
        price = last["close"]
        signal = "HOLD"
        explanation = "Crypto market conditions not met."

        # Market state analysis
        is_uptrend = price > last[trend_filter_col]
        is_downtrend = price < last[trend_filter_col]
        adx_value = last[f'ADX_{adx_period}']
        rsi_value = last[f'RSI_{rsi_period}']
        current_volatility = last['volatility']
        
        # Weekend detection (crypto never sleeps!)
        is_weekend = last.name.weekday() in [5, 6] if hasattr(last.name, 'weekday') else False
        
        # Volatility filter - avoid trading in extreme volatility
        if current_volatility > volatility_filter:
            return {"signal": "HOLD", "price": price, "explanation": f"High volatility ({current_volatility:.3f}) - waiting for stability."}

        # Bitcoin-specific logic
        if adx_value > adx_threshold:  # Trending mode
            # Golden Cross with RSI confirmation
            if (is_uptrend and 
                prev[f'SMA_{ma_fast_period}'] <= prev[f'SMA_{ma_slow_period}'] and 
                last[f'SMA_{ma_fast_period}'] > last[f'SMA_{ma_slow_period}'] and
                rsi_value < rsi_overbought):
                signal = "BUY"
                explanation = f"Bitcoin Uptrend & Trending: Golden Cross, RSI={rsi_value:.1f}"
            
            # Death Cross with RSI confirmation  
            elif (is_downtrend and 
                  prev[f'SMA_{ma_fast_period}'] >= prev[f'SMA_{ma_slow_period}'] and 
                  last[f'SMA_{ma_fast_period}'] < last[f'SMA_{ma_slow_period}'] and
                  rsi_value > rsi_oversold):
                signal = "SELL"
                explanation = f"Bitcoin Downtrend & Trending: Death Cross, RSI={rsi_value:.1f}"
                
        else:  # Ranging mode (common in crypto weekends)
            # Bollinger Bands with RSI oversold
            if (is_uptrend and 
                last['low'] <= last[bbl_col] and 
                rsi_value < rsi_oversold):
                signal = "BUY"
                explanation = f"Bitcoin Uptrend & Ranging: Oversold BB + RSI={rsi_value:.1f}"
            
            # Bollinger Bands with RSI overbought
            elif (is_downtrend and 
                  last['high'] >= last[bbu_col] and 
                  rsi_value > rsi_overbought):
                signal = "SELL"
                explanation = f"Bitcoin Downtrend & Ranging: Overbought BB + RSI={rsi_value:.1f}"
        
        # Weekend mode adjustments
        if weekend_mode and is_weekend:
            explanation += " [Weekend Mode]"
            # More conservative on weekends
            if signal in ["BUY", "SELL"]:
                # Add extra confirmation for weekend trades
                if abs(rsi_value - 50) < 15:  # RSI too neutral for weekend
                    signal = "HOLD"
                    explanation = "Weekend: RSI too neutral, waiting for clearer signal."

        return {"signal": signal, "price": price, "explanation": explanation}

    def analyze_df(self, df):
        """Method for BACKTESTING - Bitcoin optimized."""
        # Get parameters
        adx_period = self.params.get('adx_period', 10)
        adx_threshold = self.params.get('adx_threshold', 20)
        ma_fast_period = self.params.get('ma_fast_period', 12)
        ma_slow_period = self.params.get('ma_slow_period', 26)
        bb_length = self.params.get('bb_length', 20)
        bb_std = self.params.get('bb_std', 2.2)
        trend_filter_period = self.params.get('trend_filter_period', 100)
        rsi_period = self.params.get('rsi_period', 14)
        rsi_overbought = self.params.get('rsi_overbought', 75)
        rsi_oversold = self.params.get('rsi_oversold', 25)
        volatility_filter = self.params.get('volatility_filter', 2.0)
        weekend_mode = self.params.get('weekend_mode', True)

        # Calculate all indicators
        bbu_col = f'BBU_{bb_length}_{bb_std:.1f}'
        bbl_col = f'BBL_{bb_length}_{bb_std:.1f}'
        trend_filter_col = f'SMA_{trend_filter_period}'

        df.ta.adx(length=adx_period, append=True)
        df[f'SMA_{ma_fast_period}'] = ta.sma(df['close'], length=ma_fast_period)
        df[f'SMA_{ma_slow_period}'] = ta.sma(df['close'], length=ma_slow_period)
        df.ta.bbands(length=bb_length, std=bb_std, append=True)
        df[trend_filter_col] = ta.sma(df['close'], length=trend_filter_period)
        df.ta.rsi(length=rsi_period, append=True)
        
        # Crypto-specific indicators
        df['volatility'] = df['close'].rolling(24).std() / df['close'].rolling(24).mean()
        
        # Safe weekend detection with multiple fallback methods
        try:
            # Method 1: If index is datetime
            if hasattr(df.index, 'dayofweek'):
                df['is_weekend'] = df.index.dayofweek.isin([5, 6])
            # Method 2: If there's a time column
            elif 'time' in df.columns:
                # Ensure time column is datetime
                if not pd.api.types.is_datetime64_any_dtype(df['time']):
                    df['time'] = pd.to_datetime(df['time'])
                df['is_weekend'] = df['time'].dt.dayofweek.isin([5, 6])
            else:
                # Method 3: Fallback - no weekend detection for crypto (24/7 market)
                df['is_weekend'] = False
        except (AttributeError, TypeError) as e:
            # Safe fallback - crypto markets are 24/7 anyway
            df['is_weekend'] = False

        # Market conditions
        is_trending = df[f'ADX_{adx_period}'] > adx_threshold
        is_ranging = ~is_trending
        is_uptrend = df['close'] > df[trend_filter_col]
        is_downtrend = df['close'] < df[trend_filter_col]
        
        # Volatility filter
        low_volatility = df['volatility'] <= volatility_filter

        # Signal conditions
        golden_cross = (df[f'SMA_{ma_fast_period}'].shift(1) <= df[f'SMA_{ma_slow_period}'].shift(1)) & (df[f'SMA_{ma_fast_period}'] > df[f'SMA_{ma_slow_period}'])
        death_cross = (df[f'SMA_{ma_fast_period}'].shift(1) >= df[f'SMA_{ma_slow_period}'].shift(1)) & (df[f'SMA_{ma_fast_period}'] < df[f'SMA_{ma_slow_period}'])
        
        # RSI conditions
        rsi_not_overbought = df[f'RSI_{rsi_period}'] < rsi_overbought
        rsi_not_oversold = df[f'RSI_{rsi_period}'] > rsi_oversold
        rsi_oversold_cond = df[f'RSI_{rsi_period}'] < rsi_oversold
        rsi_overbought_cond = df[f'RSI_{rsi_period}'] > rsi_overbought

        # Trending signals
        trending_buy = (is_uptrend & is_trending & golden_cross & 
                       rsi_not_overbought & low_volatility)
        trending_sell = (is_downtrend & is_trending & death_cross & 
                        rsi_not_oversold & low_volatility)

        # Ranging signals  
        ranging_buy = (is_uptrend & is_ranging & (df['low'] <= df[bbl_col]) & 
                      rsi_oversold_cond & low_volatility)
        ranging_sell = (is_downtrend & is_ranging & (df['high'] >= df[bbu_col]) & 
                       rsi_overbought_cond & low_volatility)

        # Weekend mode adjustments
        if weekend_mode:
            # More conservative weekend trading
            weekend_filter = ~df['is_weekend'] | (abs(df[f'RSI_{rsi_period}'] - 50) >= 15)
            trending_buy = trending_buy & weekend_filter
            trending_sell = trending_sell & weekend_filter
            ranging_buy = ranging_buy & weekend_filter  
            ranging_sell = ranging_sell & weekend_filter

        # Final signals
        df['signal'] = np.where(
            trending_buy | ranging_buy, 'BUY', 
            np.where(trending_sell | ranging_sell, 'SELL', 'HOLD')
        )

        return df

    def get_position_size(self, account_balance, current_price, symbol="BTCUSD"):
        """Bitcoin-specific position sizing with enhanced risk management."""
        # Conservative sizing for crypto volatility
        base_risk_percent = 0.5  # 0.5% risk per trade (half of forex)
        
        # Detect if it's Bitcoin
        if 'BTC' in symbol.upper():
            # Even more conservative for Bitcoin
            base_risk_percent = 0.3  # 0.3% for Bitcoin
            
        # Calculate position size
        risk_amount = account_balance * (base_risk_percent / 100)
        
        # Assume 2% stop loss for crypto (tighter than forex)
        stop_loss_percent = 2.0
        stop_loss_amount = current_price * (stop_loss_percent / 100)
        
        # Position size calculation
        position_size = risk_amount / stop_loss_amount
        
        # Bitcoin lot constraints (based on XM specifications)
        min_lot = 0.01
        max_lot = 10.0  # Conservative max for demo
        lot_step = 0.01
        
        # Round to valid lot size
        position_size = max(min_lot, min(max_lot, 
                           round(position_size / lot_step) * lot_step))
        
        return position_size

    def get_stop_loss_take_profit(self, entry_price, signal, symbol="BTCUSD"):
        """Bitcoin-specific SL/TP levels."""
        if 'BTC' in symbol.upper():
            # Tighter stops for Bitcoin volatility
            sl_percent = 2.0  # 2% stop loss
            tp_percent = 4.0  # 2:1 risk-reward
        else:
            # Other crypto pairs
            sl_percent = 1.5
            tp_percent = 3.0
        
        if signal == "BUY":
            stop_loss = entry_price * (1 - sl_percent / 100)
            take_profit = entry_price * (1 + tp_percent / 100)
        elif signal == "SELL":
            stop_loss = entry_price * (1 + sl_percent / 100)
            take_profit = entry_price * (1 - tp_percent / 100)
        else:
            return None, None
        
        return stop_loss, take_profit