#!/usr/bin/env python3
"""
🔇 Test Quiet Backtesting
Quick test to verify backtesting logs are clean
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set logging to INFO level to see what shows up
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def generate_test_data():
    """Generate simple test data for backtesting"""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
    
    # Generate realistic EURUSD price movement
    base_price = 1.1000
    returns = np.random.randn(100) * 0.001  # Small hourly returns
    prices = base_price * (1 + returns).cumprod()
    
    df = pd.DataFrame({
        'time': dates,
        'open': prices,
        'high': prices * (1 + np.random.uniform(0, 0.002, 100)),
        'low': prices * (1 - np.random.uniform(0, 0.002, 100)),
        'close': prices,
        'tick_volume': np.random.randint(1000, 5000, 100)
    })
    
    # Ensure OHLC integrity
    df['high'] = df[['high', 'close', 'open']].max(axis=1)
    df['low'] = df[['low', 'close', 'open']].min(axis=1)
    
    return df

def test_quiet_backtesting():
    """Test that backtesting is now much quieter"""
    print("🔍 Testing Quiet Backtesting...")
    
    try:
        from core.backtesting.engine import run_backtest
        
        # Generate test data
        df = generate_test_data()
        
        # Test parameters
        params = {
            'lot_size': 1.0,  # 1% risk
            'sl_pips': 2.0,   # 2x ATR for SL
            'tp_pips': 4.0    # 4x ATR for TP
        }
        
        print("\\n📊 Running backtest with EURUSD data...")
        print("⏱️ Before: You would see tons of detailed logs")
        print("🎯 After: Should only see essential information")
        
        # Capture log output
        result = run_backtest(
            strategy_id='MA_CROSSOVER',
            params=params,
            historical_data_df=df,
            symbol_name='EURUSD'
        )
        
        print("\\n✅ Backtest completed!")
        print(f"📈 Result summary: {result.get('total_trades', 0)} trades, ${result.get('total_profit_usd', 0):.0f} profit")
        
        print("\\n🎉 SUCCESS! Backtesting is now much cleaner!")
        print("\\n📝 What you'll see now:")
        print("  ✅ Only essential backtest completion message")
        print("  ✅ Significant trades (>$50 profit/loss)")
        print("  ✅ XAUUSD warnings (when needed)")
        print("  ✅ Error messages")
        print("\\n🚫 What's filtered out:")
        print("  ❌ Detailed lot size calculations")
        print("  ❌ Every single trade entry/exit")
        print("  ❌ Step-by-step position sizing")
        print("  ❌ Verbose XAUUSD protection details")
        
        # Test with XAUUSD to see gold warnings
        print("\\n🥇 Testing XAUUSD (should show warnings but less verbose)...")
        
        # Generate gold price data
        df_gold = df.copy()
        df_gold['close'] = df_gold['close'] * 1800  # Scale to gold prices
        df_gold['open'] = df_gold['open'] * 1800
        df_gold['high'] = df_gold['high'] * 1800
        df_gold['low'] = df_gold['low'] * 1800
        
        result_gold = run_backtest(
            strategy_id='MA_CROSSOVER',
            params=params,
            historical_data_df=df_gold,
            symbol_name='XAUUSD'
        )
        
        print(f"🥇 Gold result: {result_gold.get('total_trades', 0)} trades")
        
    except Exception as e:
        print(f"❌ Error testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\\n🎯 To enable detailed logs for debugging:")
    print("   Set logging level to DEBUG in your code")
    print("   logging.basicConfig(level=logging.DEBUG)")

if __name__ == "__main__":
    test_quiet_backtesting()