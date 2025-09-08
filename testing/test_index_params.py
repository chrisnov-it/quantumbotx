#!/usr/bin/env python3
# test_index_params.py - Simple test for INDEX_BREAKOUT_PRO parameters and signals

import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_strategy_parameters():
    """Test INDEX_BREAKOUT_PRO parameter functionality"""
    
    print("🔧 Testing INDEX_BREAKOUT_PRO Parameters")
    print("=" * 50)
    
    try:
        from core.strategies.index_breakout_pro import IndexBreakoutProStrategy
        
        # Test 1: Check parameter definitions
        print("1️⃣ Testing parameter definitions...")
        params = IndexBreakoutProStrategy.get_definable_params()
        
        print(f"Found {len(params)} parameters:")
        for param in params:
            name = param.get('name', 'Unknown')
            display_name = param.get('display_name', 'No display name')
            label = param.get('label', 'No label')
            default = param.get('default', 'No default')
            param_type = param.get('type', 'Unknown type')
            
            print(f"  • {name}:")
            print(f"    - Display Name: {display_name}")
            print(f"    - Label: {label}")
            print(f"    - Default: {default}")
            print(f"    - Type: {param_type}")
        
        # Test 2: Parameter normalization (like the API does)
        print(f"\n2️⃣ Testing parameter normalization...")
        normalized_params = []
        for param in params:
            normalized_param = param.copy()
            if 'display_name' in param and 'label' not in param:
                normalized_param['label'] = param['display_name']
            elif 'label' not in param and 'display_name' not in param:
                normalized_param['label'] = param['name'].replace('_', ' ').title()
            normalized_params.append(normalized_param)
        
        print(f"Normalized parameters for frontend:")
        for param in normalized_params:
            print(f"  • {param['name']}: '{param.get('label', 'NO LABEL')}'")
        
        # Test 3: Strategy instantiation and signal generation
        print(f"\n3️⃣ Testing signal generation...")
        
        # Create simple test data
        dates = pd.date_range('2024-01-01', periods=100, freq='h')
        
        # Generate price data with some volatility
        base_price = 4350  # US500 base price
        price_changes = np.random.randn(100) * 0.005  # 0.5% random changes
        
        # Add some trend and breakout patterns
        trend = np.linspace(0, 0.02, 100)  # 2% uptrend
        breakout_pattern = np.zeros(100)
        breakout_pattern[70:75] = 0.01  # 1% breakout at position 70-75
        
        cumulative_changes = np.cumsum(price_changes + trend + breakout_pattern)
        prices = base_price * (1 + cumulative_changes)
        
        # Create OHLCV data
        df = pd.DataFrame({
            'time': dates,
            'open': prices,
            'high': prices * (1 + np.random.rand(100) * 0.002),  # Small random high
            'low': prices * (1 - np.random.rand(100) * 0.002),   # Small random low
            'close': prices,
            'volume': np.random.randint(5000, 15000, 100)  # Random volume
        })
        
        # Create mock bot
        class MockBot:
            def __init__(self):
                self.market_for_mt5 = 'US500'
        
        # Test with default parameters
        print(f"Creating strategy instance with default parameters...")
        strategy = IndexBreakoutProStrategy(MockBot(), {})
        
        # Test analyze_df
        print(f"Running analyze_df on test data...")
        result_df = strategy.analyze_df(df)
        
        # Check signals
        if 'signal' in result_df.columns:
            signals = result_df['signal'].value_counts()
            print(f"Signal distribution: {signals.to_dict()}")
            
            non_hold_signals = result_df[result_df['signal'] != 'HOLD']
            print(f"Non-HOLD signals: {len(non_hold_signals)}")
            
            if len(non_hold_signals) > 0:
                print(f"Sample trading signals:")
                for i, row in non_hold_signals.head(5).iterrows():
                    print(f"  • {row['signal']} at ${row['close']:.2f}: {row.get('explanation', 'No explanation')}")
            else:
                print(f"⚠️ No trading signals generated")
                print(f"Sample explanations from recent data:")
                recent_explanations = result_df['explanation'].tail(10)
                for i, exp in enumerate(recent_explanations):
                    print(f"  {i+1}: {exp}")
        
        # Test 4: Test with custom parameters
        print(f"\n4️⃣ Testing with custom parameters...")
        custom_params = {
            'breakout_period': 10,  # Shorter period for more signals
            'volume_surge_multiplier': 1.5,  # Lower threshold
            'min_breakout_size': 0.1  # Smaller breakout size
        }
        
        strategy_custom = IndexBreakoutProStrategy(MockBot(), custom_params)
        result_df_custom = strategy_custom.analyze_df(df)
        
        if 'signal' in result_df_custom.columns:
            signals_custom = result_df_custom['signal'].value_counts()
            print(f"Custom parameter signals: {signals_custom.to_dict()}")
            
            non_hold_custom = result_df_custom[result_df_custom['signal'] != 'HOLD']
            print(f"Custom non-HOLD signals: {len(non_hold_custom)}")
        
        print(f"\n✅ Parameter testing completed!")
        return True
        
    except Exception as e:
        print(f"❌ Parameter testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_data_compatibility():
    """Test the actual US500 CSV data"""
    
    print(f"\n📊 Testing US500 CSV Data Compatibility")
    print("=" * 50)
    
    try:
        csv_file = 'lab/backtest_data/US500_H1_data.csv'
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return False
        
        # Load actual data
        df = pd.read_csv(csv_file, parse_dates=['time'])
        print(f"✅ Loaded {len(df)} rows from {csv_file}")
        print(f"Date range: {df['time'].min()} to {df['time'].max()}")
        print(f"Columns: {list(df.columns)}")
        
        # Check for missing data
        missing_data = df.isnull().sum()
        print(f"Missing data per column: {missing_data.to_dict()}")
        
        # Take a recent subset for testing
        recent_df = df.tail(200).copy()  # Last 200 rows
        print(f"\nTesting with recent {len(recent_df)} rows...")
        
        # Test strategy with this data
        from core.strategies.index_breakout_pro import IndexBreakoutProStrategy
        
        class MockBot:
            def __init__(self):
                self.market_for_mt5 = 'US500'
        
        strategy = IndexBreakoutProStrategy(MockBot(), {})
        result_df = strategy.analyze_df(recent_df)
        
        if 'signal' in result_df.columns:
            signals = result_df['signal'].value_counts()
            print(f"✅ Signal generation successful: {signals.to_dict()}")
            
            non_hold = result_df[result_df['signal'] != 'HOLD']
            if len(non_hold) > 0:
                print(f"✅ Generated {len(non_hold)} trading signals")
                print(f"Recent signals:")
                for i, row in non_hold.tail(3).iterrows():
                    print(f"  • {row['signal']} at ${row['close']:.2f}")
            else:
                print(f"⚠️ No trading signals in recent data")
        
        return True
        
    except Exception as e:
        print(f"❌ CSV data testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 INDEX_BREAKOUT_PRO Parameter & Signal Testing")
    print("=" * 70)
    
    test1_success = test_strategy_parameters()
    test2_success = test_csv_data_compatibility()
    
    if test1_success and test2_success:
        print(f"\n✅ All tests passed!")
        print(f"\n💡 If web interface still shows 'undefined' parameters:")
        print(f"   1. Check browser console for JavaScript errors")
        print(f"   2. Verify the parameter API endpoint is working")
        print(f"   3. Check frontend parameter display code")
        print(f"\n💡 If backtest still returns empty results:")
        print(f"   1. Strategy may be too conservative (not generating signals)")
        print(f"   2. Check engine configuration")
        print(f"   3. Try with more volatile data or different parameters")
    else:
        print(f"\n❌ Some tests failed - check output above")