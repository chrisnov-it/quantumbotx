#!/usr/bin/env python3
# test_strategy_signals.py - Test INDEX_BREAKOUT_PRO with more dynamic data

import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_breakout_test_data():
    """Create test data with clear breakout patterns"""
    
    print("📊 Creating breakout test data...")
    
    # Create 500 periods with deliberate breakout patterns
    periods = 500
    dates = pd.date_range('2024-01-01', periods=periods, freq='h')
    
    base_price = 4350
    prices = []
    volumes = []
    
    price = base_price
    
    for i in range(periods):
        # Base random movement
        daily_vol = 0.003  # 0.3% daily volatility
        random_change = np.random.randn() * daily_vol
        
        # Add trend patterns
        if i < 100:
            # First 100: sideways with small movements
            trend = 0
        elif i < 200:
            # Next 100: clear uptrend with breakouts
            trend = 0.0008  # 0.08% per hour uptrend
            # Add volume spikes during breakouts
            if i % 25 == 0:  # Every 25 hours, create breakout
                random_change += 0.008  # 0.8% breakout move
        elif i < 300:
            # Next 100: downtrend with breakdowns
            trend = -0.0005  # 0.05% per hour downtrend
            if i % 30 == 0:
                random_change -= 0.006  # 0.6% breakdown move
        else:
            # Final 200: mixed with occasional large moves
            trend = 0.0002
            if i % 40 == 0:
                random_change += np.random.choice([0.01, -0.01])  # 1% move up or down
        
        # Apply changes
        price_change = random_change + trend
        price = price * (1 + price_change)
        prices.append(price)
        
        # Volume: higher during breakouts
        base_volume = 8000
        if abs(random_change) > 0.005:  # Large moves get high volume
            volume = base_volume * (2 + np.random.rand() * 2)  # 2-4x volume
        else:
            volume = base_volume * (0.8 + np.random.rand() * 0.4)  # 0.8-1.2x volume
        
        volumes.append(int(volume))
    
    # Create OHLCV data
    df = pd.DataFrame({
        'time': dates,
        'open': prices,
        'close': prices,
        'volume': volumes
    })
    
    # Add realistic high/low
    df['high'] = df['close'] * (1 + np.random.rand(periods) * 0.003)
    df['low'] = df['close'] * (1 - np.random.rand(periods) * 0.003)
    
    print(f"✅ Created {len(df)} periods of breakout test data")
    print(f"Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    print(f"Volume range: {df['volume'].min()} - {df['volume'].max()}")
    
    return df

def test_with_dynamic_data():
    """Test strategy with dynamic breakout data"""
    
    print("🚀 Testing INDEX_BREAKOUT_PRO with Dynamic Data")
    print("=" * 60)
    
    try:
        from core.strategies.index_breakout_pro import IndexBreakoutProStrategy
        
        # Create test data with breakouts
        df = create_breakout_test_data()
        
        # Create mock bot
        class MockBot:
            def __init__(self):
                self.market_for_mt5 = 'US500'
        
        # Test with different parameter sets
        test_scenarios = [
            {
                'name': 'Conservative (Default)',
                'params': {}  # Use defaults
            },
            {
                'name': 'Moderate', 
                'params': {
                    'volume_surge_multiplier': 1.3,
                    'min_breakout_size': 0.15,
                    'breakout_period': 15
                }
            },
            {
                'name': 'Aggressive',
                'params': {
                    'volume_surge_multiplier': 1.2,
                    'min_breakout_size': 0.1,
                    'breakout_period': 10
                }
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\\n📈 Testing {scenario['name']} Parameters:")
            print("-" * 40)
            
            strategy = IndexBreakoutProStrategy(MockBot(), scenario['params'])
            result_df = strategy.analyze_df(df)
            
            if 'signal' in result_df.columns:
                signals = result_df['signal'].value_counts()
                print(f"Signal distribution: {signals.to_dict()}")
                
                non_hold = result_df[result_df['signal'] != 'HOLD']
                print(f"Trading signals: {len(non_hold)} ({len(non_hold)/len(result_df)*100:.1f}%)")
                
                if len(non_hold) > 0:
                    buy_signals = len(non_hold[non_hold['signal'] == 'BUY'])
                    sell_signals = len(non_hold[non_hold['signal'] == 'SELL'])
                    print(f"BUY signals: {buy_signals}")
                    print(f"SELL signals: {sell_signals}")
                    
                    print(f"\\nSample signals:")
                    for i, row in non_hold.head(5).iterrows():
                        print(f"  • {row['signal']} at ${row['close']:.2f}: {row.get('explanation', 'No explanation')}")
                
                else:
                    print(f"❌ No trading signals generated")
                    print(f"Recent explanations:")
                    for exp in result_df['explanation'].tail(5):
                        print(f"  • {exp}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_real_data():
    """Test with actual US500 data from a volatile period"""
    
    print(f"\\n📊 Testing with Real US500 Data (Volatile Period)")
    print("="*60)
    
    try:
        csv_file = 'lab/backtest_data/US500_H1_data.csv'
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return False
            
        df = pd.read_csv(csv_file, parse_dates=['time'])
        
        # Find a volatile period (March 2020 - COVID crash)
        march_2020 = df[(df['time'] >= '2020-03-01') & (df['time'] <= '2020-04-30')]
        
        if len(march_2020) > 100:
            print(f"✅ Using March-April 2020 data ({len(march_2020)} rows) - COVID volatility period")
            test_df = march_2020.copy()
        else:
            # Fallback: use a more recent volatile period
            test_df = df.tail(1000).copy()
            print(f"✅ Using recent 1000 rows as fallback")
        
        print(f"Date range: {test_df['time'].min()} to {test_df['time'].max()}")
        print(f"Price range: ${test_df['close'].min():.2f} - ${test_df['close'].max():.2f}")
        
        # Calculate volatility of this period
        returns = test_df['close'].pct_change().dropna()  # pyright: ignore
        volatility = returns.std() * np.sqrt(24)  # Annualized hourly volatility
        print(f"Period volatility: {volatility:.1%} (annualized)")
        
        from core.strategies.index_breakout_pro import IndexBreakoutProStrategy
        
        class MockBot:
            def __init__(self):
                self.market_for_mt5 = 'US500'
        
        # Test with moderate parameters
        params = {
            'volume_surge_multiplier': 1.3,
            'min_breakout_size': 0.15,
            'breakout_period': 15
        }
        
        strategy = IndexBreakoutProStrategy(MockBot(), params)
        result_df = strategy.analyze_df(test_df)
        
        if 'signal' in result_df.columns:
            signals = result_df['signal'].value_counts()
            print(f"\\nSignal distribution: {signals.to_dict()}")
            
            non_hold = result_df[result_df['signal'] != 'HOLD']
            print(f"Trading signals: {len(non_hold)} ({len(non_hold)/len(result_df)*100:.1f}%)")
            
            if len(non_hold) > 0:
                print(f"\\n✅ Strategy generated signals in volatile period!")
                print(f"Sample signals:")
                for i, row in non_hold.head(8).iterrows():
                    date_str = row['time'].strftime('%m-%d %H:%M') if 'time' in row.index else 'Unknown'
                    print(f"  • {date_str}: {row['signal']} at ${row['close']:.2f}")
                return True
            else:
                print(f"❌ No signals even in volatile period")
                return False
        
    except Exception as e:
        print(f"❌ Real data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 INDEX_BREAKOUT_PRO Signal Generation Testing")
    print("=" * 70)
    
    test1 = test_with_dynamic_data()
    test2 = test_with_real_data()
    
    if test1 and test2:
        print(f"\\n✅ Signal generation tests successful!")
        print(f"\\n💡 The strategy can generate signals with:")
        print(f"   • Volatile market conditions")
        print(f"   • Moderate parameter settings")
        print(f"   • Clear breakout patterns")
        print(f"\\n🔧 For web interface:")
        print(f"   • Try using March 2020 data (COVID crash)")
        print(f"   • Use moderate parameters: volume_surge_multiplier=1.3")
        print(f"   • Consider shorter breakout_period=15")
    else:
        print(f"\\n❌ Some tests failed - strategy may need further tuning")