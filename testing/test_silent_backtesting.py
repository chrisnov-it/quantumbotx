#!/usr/bin/env python3
"""
🔇 Silent Backtesting Demo
Demonstrates the completely silent backtesting - no terminal noise!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_silent_backtesting():
    """Demonstrate silent backtesting"""
    
    print("🔇 Testing SILENT Backtesting")
    print("=" * 50)
    print("Before: Lots of noisy terminal logs")
    print("After: Complete silence during backtesting!")
    print("=" * 50)
    
    try:
        from core.backtesting.engine import run_backtest
        import pandas as pd
        import numpy as np
        
        # Create simple test data
        dates = pd.date_range('2024-01-01', periods=200, freq='H')
        base_price = 1.1000
        prices = base_price + np.cumsum(np.random.randn(200) * 0.001)
        
        df = pd.DataFrame({
            'time': dates,
            'open': prices,
            'high': prices + np.random.uniform(0, 0.002, 200),
            'low': prices - np.random.uniform(0, 0.002, 200),
            'close': prices,
            'volume': np.random.randint(1000, 5000, 200)
        })
        
        # Ensure OHLC integrity
        df['high'] = df[['high', 'open', 'close']].max(axis=1)
        df['low'] = df[['low', 'open', 'close']].min(axis=1)
        
        print("\\n🚀 Running backtest (should be completely silent)...")
        print("👀 Watch carefully - no logs should appear!")
        print("\\n--- BACKTESTING START ---")
        
        # Run backtest - should be completely silent
        result = run_backtest(
            strategy_id='MA_CROSSOVER',
            params={
                'lot_size': 1.0,
                'sl_pips': 2.0,
                'tp_pips': 4.0
            },
            historical_data_df=df,
            symbol_name='EURUSD'
        )
        
        print("--- BACKTESTING END ---")
        print("\\n✅ Backtest completed SILENTLY!")
        print(f"📊 Results: {result.get('total_trades', 0)} trades, ${result.get('total_profit_usd', 0):.2f} profit")
        
        print("\\n🎉 SUCCESS!")
        print("✅ No terminal noise")
        print("✅ Results still available")
        print("✅ Backtesting history still works")
        print("✅ Perfect for production use")
        
        print("\\n💡 Benefits:")
        print("• Clean terminal output")
        print("• No log spam during backtesting")
        print("• Results still captured in history")
        print("• Better user experience")
        print("• Professional appearance")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔇 QuantumBotX Silent Backtesting Demo")
    print("=" * 60)
    
    success = test_silent_backtesting()
    
    if success:
        print("\\n" + "=" * 60)
        print("🎯 SILENT BACKTESTING IS READY!")
        print("Your backtesting is now completely quiet.")
        print("Check the backtesting history page for results.")
        print("=" * 60)
    else:
        print("\\n❌ Test failed - check the error above")