#!/usr/bin/env python3
"""
Test the FIXED enhanced backtesting engine
Verify that the spread cost fixes resolved the 100% drawdown issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_sample_data_with_trends():
    """Create sample data with clear trends for better strategy testing"""
    np.random.seed(42)
    
    # Create trending market data
    base_price = 1.1000
    bars = 500
    
    # Generate trending price movement
    trend_strength = 0.0001  # Gentle uptrend
    noise_level = 0.0002     # Market noise
    
    prices = [base_price]
    for i in range(bars):
        # Add trend + noise
        trend_component = trend_strength * (1 + 0.5 * np.sin(i / 50))  # Wavy trend
        noise_component = np.random.normal(0, noise_level)
        
        new_price = prices[-1] + trend_component + noise_component
        new_price = max(0.9000, min(1.3000, new_price))
        prices.append(new_price)
    
    prices = np.array(prices[1:])
    
    # Create OHLC data
    data = []
    for i, close in enumerate(prices):
        high = close + np.random.uniform(0, 0.0003)
        low = close - np.random.uniform(0, 0.0003)
        open_price = low + (high - low) * np.random.random()
        
        time = datetime(2024, 1, 1) + timedelta(hours=i)
        
        data.append({
            'time': time,
            'open': round(open_price, 5),
            'high': round(high, 5),
            'low': round(low, 5),
            'close': round(close, 5),
            'volume': np.random.randint(1000, 10000)
        })
    
    df = pd.DataFrame(data)
    return df

def test_fixed_enhanced_engine():
    """Test the fixed enhanced engine with realistic scenarios"""
    print("Testing FIXED Enhanced Backtesting Engine")
    print("=" * 70)
    
    try:
        from core.backtesting.enhanced_engine import run_enhanced_backtest
        from core.backtesting.engine import run_backtest as run_original_backtest
        
        # Create test data
        df = create_sample_data_with_trends()
        print(f"Created {len(df)} bars of test data")
        print(f"Price range: {df['close'].min():.5f} to {df['close'].max():.5f}")
        
        # Test parameters (conservative for safety)
        params = {
            'bb_length': 20,
            'bb_std': 2.0,
            'squeeze_window': 10,
            'squeeze_factor': 0.7,
            'rsi_period': 14,
            'risk_percent': 1.0,
            'sl_atr_multiplier': 2.0,
            'tp_atr_multiplier': 4.0
        }
        
        print(f"Test parameters: {params}")
        
        # Test with EURUSD (should have reasonable costs now)
        print(f"Testing EURUSD with Bollinger Squeeze Strategy...")
        
        # Enhanced engine test
        enhanced_result = run_enhanced_backtest('bollinger_squeeze', params, df, 'EURUSD')
        
        print(f"Enhanced Engine Results:")
        print(f"  Total trades: {enhanced_result.get('total_trades', 0)}")
        print(f"  Gross profit: ${enhanced_result.get('total_profit_usd', 0):.2f}")
        print(f"  Spread costs: ${enhanced_result.get('total_spread_costs', 0):.2f}")
        print(f"  Net profit: ${enhanced_result.get('net_profit_after_costs', 0):.2f}")
        print(f"  Win rate: {enhanced_result.get('win_rate_percent', 0):.1f}%")
        print(f"  Max drawdown: {enhanced_result.get('max_drawdown_percent', 0):.1f}%")
        print(f"  Final capital: ${enhanced_result.get('final_capital', 0):.2f}")
        
        # Original engine test for comparison
        original_result = run_original_backtest('bollinger_squeeze', params, df, 'EURUSD')
        
        print(f"Original Engine Results:")
        print(f"  Total trades: {original_result.get('total_trades', 0)}")
        print(f"  Total profit: ${original_result.get('total_profit_usd', 0):.2f}")
        print(f"  Win rate: {original_result.get('win_rate_percent', 0):.1f}%")
        print(f"  Max drawdown: {original_result.get('max_drawdown_percent', 0):.1f}%")
        print(f"  Final capital: ${original_result.get('final_capital', 0):.2f}")
        
        # Analysis
        enhanced_dd = enhanced_result.get('max_drawdown_percent', 0)
        original_dd = original_result.get('max_drawdown_percent', 0)
        enhanced_profit = enhanced_result.get('net_profit_after_costs', 0)
        original_profit = original_result.get('total_profit_usd', 0)
        
        print(f"ANALYSIS:")
        print(f"  Enhanced DD: {enhanced_dd:.1f}% vs Original DD: {original_dd:.1f}%")
        print(f"  Enhanced Profit: ${enhanced_profit:.2f} vs Original Profit: ${original_profit:.2f}")
        
        # Success criteria
        success = True
        issues = []
        
        if enhanced_dd > 80:  # Still too high
            success = False
            issues.append(f"Enhanced engine still has extreme drawdown: {enhanced_dd:.1f}%")
        
        if enhanced_result.get('total_trades', 0) == 0:
            success = False
            issues.append("No trades executed in enhanced engine")
        
        # Check spread costs ratio
        if enhanced_result.get('total_trades', 0) > 0:
            gross_profit = enhanced_result.get('total_profit_usd', 0)
            spread_costs = enhanced_result.get('total_spread_costs', 0)
            if abs(gross_profit) > 0:
                spread_ratio = abs(spread_costs / gross_profit) if gross_profit != 0 else 0
                print(f"  Spread cost ratio: {spread_ratio*100:.1f}% of gross profit")
                if spread_ratio > 1.0:  # Spread costs > 100% of gross profit
                    success = False
                    issues.append(f"Spread costs still too high: {spread_ratio*100:.1f}% of gross profit")
        
        if success:
            print(f"SUCCESS: Enhanced engine is now working properly!")
            print(f"  - Drawdown is reasonable (<80%)")
            print(f"  - Trades are being executed")
            print(f"  - Spread costs are not excessive")
        else:
            print(f"ISSUES REMAIN:")
            for issue in issues:
                print(f"  - {issue}")
        
        return success, enhanced_result, original_result
        
    except Exception as e:
        print(f"Error testing engines: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

def main():
    print("COMPREHENSIVE TEST OF FIXED BACKTESTING ENGINE")
    print("=" * 80)
    
    # Test main engine fix validation
    success, enhanced_result, original_result = test_fixed_enhanced_engine()
    
    print("=" * 80)
    print("FINAL ASSESSMENT")
    print("=" * 80)
    
    if success:
        print("SUCCESS: Backtesting engine has been FIXED!")
        print("  - Spread costs are now reasonable")
        print("  - Extreme drawdowns resolved")
        print("RECOMMENDATION:")
        print("  - Deploy the fixed enhanced engine")
        print("  - Test with your actual EURUSD data")
        print("  - Monitor spread cost ratios in production")
    else:
        print("CRITICAL ISSUES REMAIN")
        print("  - Enhanced engine still has problems")
        print("  - May need deeper investigation")
    
    print("NEXT STEPS:")
    print("1. Test the fixed engine with your actual EURUSD data")
    print("2. Compare results with the original problematic backtests")
    print("3. If results are now reasonable, the issue is resolved")
    print("4. Monitor performance with different strategies and timeframes")

if __name__ == '__main__':
    main()