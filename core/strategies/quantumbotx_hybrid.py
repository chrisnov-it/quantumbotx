# /core/strategies/quantumbotx_hybrid.py
import pandas_ta as ta
import numpy as np
from .base_strategy import BaseStrategy

class QuantumBotXHybridStrategy(BaseStrategy):
    name = 'QuantumBotX Hybrid'
    description = 'Strategi eksklusif yang menggabungkan beberapa indikator untuk performa optimal, kini dengan filter tren jangka panjang.'

    @classmethod
    def get_definable_params(cls):
        return [
            {"name": "adx_period", "label": "Periode ADX", "type": "number", "default": 14},
            {"name": "adx_threshold", "label": "Ambang ADX", "type": "number", "default": 25},
            {"name": "ma_fast_period", "label": "Periode MA Cepat", "type": "number", "default": 20},
            {"name": "ma_slow_period", "label": "Periode MA Lambat", "type": "number", "default": 50},
            {"name": "bb_length", "label": "Panjang BB", "type": "number", "default": 20},
            {"name": "bb_std", "label": "Std Dev BB", "type": "number", "default": 2.0, "step": 0.1},
            {"name": "trend_filter_period", "label": "Periode Filter Tren (SMA)", "type": "number", "default": 200}
        ]

    def get_crypto_optimized_params(self, symbol_name):
        """Get crypto-optimized parameters based on symbol detection."""
        symbol_upper = symbol_name.upper() if symbol_name else ""
        
        # Detect if this is a crypto symbol
        crypto_indicators = ['BTC', 'ETH', 'ADA', 'SOL', 'DOGE', 'USDT', 'USDC']
        is_crypto = any(indicator in symbol_upper for indicator in crypto_indicators)
        
        if is_crypto:
            # Crypto-optimized parameters
            return {
                'adx_period': 10,        # Faster ADX for crypto volatility
                'adx_threshold': 20,     # Lower threshold for more signals
                'ma_fast_period': 12,    # Faster MAs for crypto
                'ma_slow_period': 26,    # EMA-style periods
                'bb_length': 18,         # Shorter BB period
                'bb_std': 2.2,          # Wider BB for crypto volatility
                'trend_filter_period': 100,  # Shorter trend filter
                'risk_multiplier': 0.5,  # Half risk for crypto volatility
                'volatility_filter': True  # Enable volatility filtering
            }
        else:
            # Standard forex parameters
            return {
                'adx_period': self.params.get('adx_period', 14),
                'adx_threshold': self.params.get('adx_threshold', 25),
                'ma_fast_period': self.params.get('ma_fast_period', 20),
                'ma_slow_period': self.params.get('ma_slow_period', 50),
                'bb_length': self.params.get('bb_length', 20),
                'bb_std': self.params.get('bb_std', 2.0),
                'trend_filter_period': self.params.get('trend_filter_period', 200),
                'risk_multiplier': 1.0,
                'volatility_filter': False
            }

    def analyze(self, df):
        """Metode untuk LIVE TRADING."""
        # Get symbol name from bot context
        symbol_name = getattr(self.bot, 'market_for_mt5', None) if hasattr(self, 'bot') else None
        
        # Get optimized parameters for this market type
        params = self.get_crypto_optimized_params(symbol_name)
        
        trend_filter_period = params['trend_filter_period']
        if df is None or df.empty or len(df) < trend_filter_period:
            return {"signal": "HOLD", "price": None, "explanation": "Data tidak cukup untuk filter tren."}

        adx_period = params['adx_period']
        adx_threshold = params['adx_threshold']
        ma_fast_period = params['ma_fast_period']
        ma_slow_period = params['ma_slow_period']
        bb_length = params['bb_length']
        bb_std = params['bb_std']

        bbu_col = f'BBU_{bb_length}_{bb_std:.1f}'
        bbl_col = f'BBL_{bb_length}_{bb_std:.1f}'
        trend_filter_col = f'SMA_{trend_filter_period}'

        df.ta.adx(length=adx_period, append=True)
        df[f'SMA_{ma_fast_period}'] = ta.sma(df['close'], length=ma_fast_period)
        df[f'SMA_{ma_slow_period}'] = ta.sma(df['close'], length=ma_slow_period)
        df.ta.bbands(length=bb_length, std=bb_std, append=True)
        df[trend_filter_col] = ta.sma(df['close'], length=trend_filter_period)
        
        df.dropna(inplace=True)
        
        if len(df) < 2:
            return {"signal": "HOLD", "price": None, "explanation": "Indikator belum matang."}

        last = df.iloc[-1]
        prev = df.iloc[-2]
        price = last["close"]
        signal = "HOLD"
        explanation = "Kondisi pasar tidak memenuhi syarat."

        is_uptrend = price > last[trend_filter_col]
        is_downtrend = price < last[trend_filter_col]
        adx_value = last[f'ADX_{adx_period}']

        if adx_value > adx_threshold: # Mode Trending
            if is_uptrend and prev[f'SMA_{ma_fast_period}'] <= prev[f'SMA_{ma_slow_period}'] and last[f'SMA_{ma_fast_period}'] > last[f'SMA_{ma_slow_period}']:
                signal = "BUY"
                explanation = "Uptrend & Trending: Golden Cross."
            elif is_downtrend and prev[f'SMA_{ma_fast_period}'] >= prev[f'SMA_{ma_slow_period}'] and last[f'SMA_{ma_fast_period}'] < last[f'SMA_{ma_slow_period}']:
                signal = "SELL"
                explanation = "Downtrend & Trending: Death Cross."
        else: # Mode Ranging
            if is_uptrend and last['low'] <= last[bbl_col]:
                signal = "BUY"
                explanation = "Uptrend & Ranging: Oversold."
            elif is_downtrend and last['high'] >= last[bbu_col]:
                signal = "SELL"
                explanation = "Downtrend & Ranging: Overbought."

        return {"signal": signal, "price": price, "explanation": explanation}

    def analyze_df(self, df):
        """Metode untuk BACKTESTING dengan deteksi crypto."""
        # Try to detect crypto symbol from various sources
        symbol_name = None
        
        # Check if there's a symbol_name parameter passed to the strategy
        if hasattr(self, 'symbol_name'):
            symbol_name = self.symbol_name
        elif hasattr(self, 'bot') and hasattr(self.bot, 'market_for_mt5'):
            symbol_name = self.bot.market_for_mt5
        
        # Get optimized parameters based on market type
        if symbol_name:
            params = self.get_crypto_optimized_params(symbol_name)
        else:
            # Fallback to original params if no symbol detection
            params = {
                'adx_period': self.params.get('adx_period', 14),
                'adx_threshold': self.params.get('adx_threshold', 25),
                'ma_fast_period': self.params.get('ma_fast_period', 20),
                'ma_slow_period': self.params.get('ma_slow_period', 50),
                'bb_length': self.params.get('bb_length', 20),
                'bb_std': self.params.get('bb_std', 2.0),
                'trend_filter_period': self.params.get('trend_filter_period', 200),
                'risk_multiplier': 1.0,
                'volatility_filter': False
            }
        
        adx_period = params['adx_period']
        adx_threshold = params['adx_threshold']
        ma_fast_period = params['ma_fast_period']
        ma_slow_period = params['ma_slow_period']
        bb_length = params['bb_length']
        bb_std = params['bb_std']
        trend_filter_period = params['trend_filter_period']
        volatility_filter = params.get('volatility_filter', False)

        bbu_col = f'BBU_{bb_length}_{bb_std:.1f}'
        bbl_col = f'BBL_{bb_length}_{bb_std:.1f}'
        trend_filter_col = f'SMA_{trend_filter_period}'

        df.ta.adx(length=adx_period, append=True)
        df[f'SMA_{ma_fast_period}'] = ta.sma(df['close'], length=ma_fast_period)
        df[f'SMA_{ma_slow_period}'] = ta.sma(df['close'], length=ma_slow_period)
        df.ta.bbands(length=bb_length, std=bb_std, append=True)
        df[trend_filter_col] = ta.sma(df['close'], length=trend_filter_period)
        
        # Add volatility filter for crypto markets
        if volatility_filter:
            df['volatility'] = df['close'].rolling(24).std() / df['close'].rolling(24).mean()
            # Define reasonable volatility threshold for crypto (higher than forex)
            max_volatility = 0.05  # 5% maximum volatility for signal generation
            low_vol_condition = df['volatility'] <= max_volatility
        else:
            low_vol_condition = True  # No volatility filter for forex

        is_trending = df[f'ADX_{adx_period}'] > adx_threshold
        is_ranging = ~is_trending
        is_uptrend = df['close'] > df[trend_filter_col]
        is_downtrend = df['close'] < df[trend_filter_col]

        golden_cross = (df[f'SMA_{ma_fast_period}'].shift(1) <= df[f'SMA_{ma_slow_period}'].shift(1)) & (df[f'SMA_{ma_fast_period}'] > df[f'SMA_{ma_slow_period}'])
        death_cross = (df[f'SMA_{ma_fast_period}'].shift(1) >= df[f'SMA_{ma_slow_period}'].shift(1)) & (df[f'SMA_{ma_fast_period}'] < df[f'SMA_{ma_slow_period}'])
        
        # Apply volatility filter to all signals
        trending_buy = is_uptrend & is_trending & golden_cross & low_vol_condition
        trending_sell = is_downtrend & is_trending & death_cross & low_vol_condition

        ranging_buy = is_uptrend & is_ranging & (df['low'] <= df[bbl_col]) & low_vol_condition
        ranging_sell = is_downtrend & is_ranging & (df['high'] >= df[bbu_col]) & low_vol_condition

        df['signal'] = np.where(trending_buy | ranging_buy, 'BUY', np.where(trending_sell | ranging_sell, 'SELL', 'HOLD'))

        return df
