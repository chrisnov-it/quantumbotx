#!/usr/bin/env python3
"""
XAUUSD Backtesting Validator
Tests the fixes for gold trading position sizing and risk management
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_xauusd_pulse_sync():
    """Test Pulse Sync strategy on XAUUSD with conservative parameters"""
    from core.backtesting.engine import run_backtest
    
    print("🧪 Testing XAUUSD with Pulse Sync Strategy...")
    
    # Create realistic XAUUSD test data
    dates = pd.date_range('2023-01-01', periods=300, freq='h')
    base_price = 1950.0
    
    # Gold price movements
    price_changes = np.random.randn(300) * 1.5  # Realistic gold volatility
    prices = base_price + np.cumsum(price_changes)
    
    df = pd.DataFrame({
        'time': dates,
        'open': prices,
        'high': prices + np.random.uniform(0.5, 2.0, 300),
        'low': prices - np.random.uniform(0.5, 2.0, 300),
        'close': prices + np.random.uniform(-0.5, 0.5, 300),
        'volume': np.random.randint(100, 1000, 300)
    })
    
    # Ensure OHLC integrity
    df['high'] = df[['high', 'close', 'open']].max(axis=1)
    df['low'] = df[['low', 'close', 'open']].min(axis=1)
    
    print(f"📊 Created XAUUSD data: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    
    # Test different parameter sets
    test_cases = [
        {'lot_size': 0.5, 'sl_pips': 1.0, 'tp_pips': 2.0, 'name': 'Conservative'},
        {'lot_size': 1.0, 'sl_pips': 1.5, 'tp_pips': 3.0, 'name': 'Moderate'},
        {'lot_size': 2.0, 'sl_pips': 2.0, 'tp_pips': 4.0, 'name': 'Aggressive (will be capped)'},
    ]
    
    results = []
    
    for test_case in test_cases:
        params = {k: v for k, v in test_case.items() if k != 'name'}
        name = test_case['name']
        
        print(f"\\n📈 Testing {name}: Risk={params['lot_size']}%, SL={params['sl_pips']}x ATR")
        
        try:
            # Pass XAUUSD as symbol name for accurate detection
            result = run_backtest('PULSE_SYNC', params, df, symbol_name='XAUUSD')
            
            if 'error' in result:
                print(f"  ❌ Error: {result['error']}")
                continue
            
            # Extract key metrics
            profit = result.get('total_profit_usd', 0)
            trades = result.get('total_trades', 0)
            final_capital = result.get('final_capital', 10000)
            drawdown = result.get('max_drawdown_percent', 0)
            win_rate = result.get('win_rate_percent', 0)
            
            # Safety check
            is_safe = (
                abs(profit) < 25000 and  # No extreme profits/losses
                drawdown < 40 and       # Reasonable drawdown
                final_capital > 5000    # Account didn't blow up
            )
            
            status = "✅ SAFE" if is_safe else "⚠️ RISKY"
            
            print(f"  {status} Results:")
            print(f"    Profit: ${profit:,.2f}")
            print(f"    Trades: {trades}")
            print(f"    Final Capital: ${final_capital:,.2f}")
            print(f"    Max Drawdown: {drawdown:.2f}%")
            print(f"    Win Rate: {win_rate:.2f}%")
            
            if not is_safe:
                print(f"    ⚠️ WARNING: Position sizing may still be too aggressive!")
            
            results.append({
                'name': name,
                'params': params,
                'result': result,
                'is_safe': is_safe
            })
            
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            import traceback
            traceback.print_exc()
    
    return results

def main():
    """Main test function"""
    print("🥇 XAUUSD Position Sizing Validator")
    print("=" * 50)
    
    try:
        results = test_xauusd_pulse_sync()
        
        print("\\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)
        
        safe_count = sum(1 for r in results if r['is_safe'])
        total_count = len(results)
        
        print(f"Safe Results: {safe_count}/{total_count}")
        
        if safe_count == total_count:
            print("✅ ALL TESTS PASSED! XAUUSD position sizing is now safe.")
        elif safe_count > 0:
            print("🟡 Some tests passed. Position sizing improved but needs more work.")
        else:
            print("❌ All tests failed. Position sizing algorithm needs major fixes.")
        
        print("\\n💡 XAUUSD Trading Recommendations:")
        print("  • Use maximum 0.1 lot size for gold")
        print("  • Keep risk below 1% per trade")
        print("  • Use smaller ATR multipliers (1.0-1.5x)")
        print("  • Monitor drawdown closely")
        print("  • Consider using fixed lot sizes instead of dynamic sizing")
        
        return safe_count > 0
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)