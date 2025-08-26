# core/strategies/bollinger_squeeze.py
import pandas_ta as ta

def analyze(df):
    """
    Bollinger Squeeze Strategy Analysis
    
    Squeeze occurs when:
    1. Bollinger Bands width is narrow (low volatility)
    2. Price is consolidating
    
    Breakout occurs when:
    1. Price breaks above/below Bollinger Bands
    2. After a squeeze period
    """
    
    if df is None or len(df) < 21:
        return 'HOLD'
    
    try:
        # Calculate Bollinger Bands
        bb = ta.bbands(df['close'], length=20, std=2)
        
        if bb is None or bb.empty:
            return 'HOLD'
            
        # Get latest values
        latest = df.iloc[-1]
        current_price = latest['close']
        
        # Bollinger Band values
        bb_upper = bb['BBU_20_2.0'].iloc[-1]
        bb_middle = bb['BBM_20_2.0'].iloc[-1]  # SMA
        bb_lower = bb['BBL_20_2.0'].iloc[-1]
        
        # Calculate bandwidth (volatility measure)
        bandwidth = (bb_upper - bb_lower) / bb_middle * 100
        
        # Get historical bandwidth for comparison
        bb_bandwidth = (bb['BBU_20_2.0'] - bb['BBL_20_2.0']) / bb['BBM_20_2.0'] * 100
        avg_bandwidth = bb_bandwidth.rolling(window=10).mean().iloc[-1]
        
        # Squeeze Detection
        # Squeeze occurs when current bandwidth is significantly lower than average
        squeeze_threshold = avg_bandwidth * 0.7  # 30% below average
        is_squeezing = bandwidth < squeeze_threshold
        
        # Price position relative to bands
        price_position = (current_price - bb_lower) / (bb_upper - bb_lower)
        
        # Momentum indicator (simple)
        rsi = ta.rsi(df['close'], length=14).iloc[-1]
        
        # Volume analysis (if available)
        volume_surge = False
        if 'volume' in df.columns:
            avg_volume = df['volume'].rolling(window=10).mean().iloc[-1]
            current_volume = df['volume'].iloc[-1]
            volume_surge = current_volume > avg_volume * 1.5
        
        # === SIGNAL LOGIC ===
        
        # 1. Breakout from Squeeze (HIGH PRIORITY)
        if is_squeezing:
            # During squeeze, wait for breakout
            if current_price > bb_upper and rsi < 70:
                return 'BUY'  # Bullish breakout
            elif current_price < bb_lower and rsi > 30:
                return 'SELL'  # Bearish breakout
            else:
                return 'HOLD'  # Still squeezing
        
        # 2. Post-Squeeze Momentum
        elif bandwidth > avg_bandwidth * 1.2:  # Bands expanding
            if price_position > 0.8 and volume_surge:  # Near upper band with volume
                return 'BUY'
            elif price_position < 0.2 and volume_surge:  # Near lower band with volume
                return 'SELL'
        
        # 3. Mean Reversion (when not squeezing)
        else:
            if current_price > bb_upper and rsi > 70:
                return 'SELL'  # Overbought
            elif current_price < bb_lower and rsi < 30:
                return 'BUY'   # Oversold
        
        return 'HOLD'
        
    except Exception as e:
        print(f"Bollinger Squeeze Analysis Error: {e}")
        return 'HOLD'

def get_analysis_data(df):
    """
    Return detailed analysis data for dashboard
    """
    if df is None or len(df) < 21:
        return {
            'signal': 'HOLD',
            'explanation': 'Insufficient data for Bollinger analysis',
            'indicators': {}
        }
    
    try:
        bb = ta.bbands(df['close'], length=20, std=2)
        
        if bb is None or bb.empty:
            return {
                'signal': 'HOLD',
                'explanation': 'Unable to calculate Bollinger Bands',
                'indicators': {}
            }
        
        # Get latest values
        latest = df.iloc[-1]
        current_price = latest['close']
        
        bb_upper = bb['BBU_20_2.0'].iloc[-1]
        bb_middle = bb['BBM_20_2.0'].iloc[-1]
        bb_lower = bb['BBL_20_2.0'].iloc[-1]
        
        bandwidth = (bb_upper - bb_lower) / bb_middle * 100
        bb_bandwidth = (bb['BBU_20_2.0'] - bb['BBL_20_2.0']) / bb['BBM_20_2.0'] * 100
        avg_bandwidth = bb_bandwidth.rolling(window=10).mean().iloc[-1]
        
        is_squeezing = bandwidth < avg_bandwidth * 0.7
        price_position = (current_price - bb_lower) / (bb_upper - bb_lower)
        
        signal = analyze(df)
        
        # Generate explanation
        explanation = ""
        if is_squeezing:
            explanation = f"🔄 SQUEEZE detected! Bandwidth: {bandwidth:.2f}% (Avg: {avg_bandwidth:.2f}%). "
            if signal == 'BUY':
                explanation += "Bullish breakout above upper band!"
            elif signal == 'SELL':
                explanation += "Bearish breakout below lower band!"
            else:
                explanation += "Waiting for breakout..."
        else:
            explanation = f"📊 Normal volatility. Bandwidth: {bandwidth:.2f}%. "
            if signal == 'BUY':
                explanation += "Bullish momentum or oversold bounce."
            elif signal == 'SELL':
                explanation += "Bearish momentum or overbought correction."
            else:
                explanation += "No clear signal."
        
        return {
            'signal': signal,
            'explanation': explanation,
            'indicators': {
                'bb_upper': round(bb_upper, 4),
                'bb_middle': round(bb_middle, 4),
                'bb_lower': round(bb_lower, 4),
                'bandwidth': round(bandwidth, 2),
                'avg_bandwidth': round(avg_bandwidth, 2),
                'is_squeezing': is_squeezing,
                'price_position': round(price_position * 100, 1)
            }
        }
        
    except Exception as e:
        return {
            'signal': 'HOLD',
            'explanation': f'Analysis error: {str(e)}',
            'indicators': {}
        }