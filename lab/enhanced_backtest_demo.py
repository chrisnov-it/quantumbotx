# enhanced_backtest_demo.py - Demo of Enhanced Backtesting Features
import os
import sys
import pandas as pd
import numpy as np

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from core.backtesting.enhanced_engine import run_enhanced_backtest, InstrumentConfig

def demo_enhanced_features():
    """Demonstrate enhanced backtesting features"""
    
    print("🚀 Enhanced Backtesting Engine Demo")
    print("=" * 50)
    
    # Check for real data files
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and 'data' in f and not f.endswith('.bak')]
    
    if csv_files:
        print("📁 Using real market data")
        # Use EURUSD if available
        eurusd_files = [f for f in csv_files if 'EURUSD' in f.upper()]
        if eurusd_files:
            filename = eurusd_files[0]
            df = pd.read_csv(filename)
            
            # Check format
            if 'close' not in df.columns:
                print("⚠️ Data needs cleaning, using synthetic data instead")
                df = create_synthetic_data()
                symbol = "EURUSD_DEMO"
            else:
                df = df.tail(500)  # Use last 500 bars for demo
                symbol = "EURUSD"
        else:
            df = create_synthetic_data()
            symbol = "EURUSD_DEMO"
    else:
        print("📊 Using synthetic market data")
        df = create_synthetic_data()
        symbol = "EURUSD_DEMO"
    
    print(f"📈 Data points: {len(df)}")
    print(f"🎯 Testing instrument: {symbol}")
    
    # Test different configurations
    configurations = [
        {
            'name': 'Perfect Execution (Old Style)',
            'config': {
                'enable_spread_costs': False,
                'enable_slippage': False,
                'enable_realistic_execution': False
            },
            'params': {'risk_percent': 1.0, 'sl_atr_multiplier': 2.0, 'tp_atr_multiplier': 4.0}
        },
        {
            'name': 'Spread Costs Only',
            'config': {
                'enable_spread_costs': True,
                'enable_slippage': False,
                'enable_realistic_execution': True
            },
            'params': {'risk_percent': 1.0, 'sl_atr_multiplier': 2.0, 'tp_atr_multiplier': 4.0}
        },
        {
            'name': 'Full Realistic Execution',
            'config': {
                'enable_spread_costs': True,
                'enable_slippage': True,
                'enable_realistic_execution': True
            },
            'params': {'risk_percent': 1.0, 'sl_atr_multiplier': 2.0, 'tp_atr_multiplier': 4.0}
        }
    ]
    
    results = []
    
    for test_config in configurations:
        print(f"\n🔄 Testing: {test_config['name']}")
        print("-" * 30)
        
        try:
            result = run_enhanced_backtest(
                'MA_CROSSOVER',
                test_config['params'], 
                df,
                symbol,
                test_config['config']
            )
            
            if 'error' not in result:
                profit = result.get('total_profit_usd', 0)
                spread_costs = result.get('total_spread_costs', 0)
                trades = result.get('total_trades', 0)
                win_rate = result.get('win_rate_percent', 0)
                
                print(f"   💰 Total Profit: ${profit:.2f}")
                print(f"   💸 Spread Costs: ${spread_costs:.2f}")
                print(f"   📊 Total Trades: {trades}")
                print(f"   📈 Win Rate: {win_rate:.1f}%")
                
                results.append({
                    'name': test_config['name'],
                    'profit': profit,
                    'spread_costs': spread_costs,
                    'trades': trades,
                    'win_rate': win_rate
                })
                
                print(f"   ✅ Test completed successfully")
            else:
                print(f"   ❌ Test failed: {result['error']}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Show comparison
    if len(results) >= 2:
        print(f"\n📊 COMPARISON RESULTS")
        print("=" * 40)
        
        perfect = results[0]
        realistic = results[-1]
        
        profit_diff = realistic['profit'] - perfect['profit']
        spread_impact = realistic['spread_costs']
        
        print(f"💰 Perfect Execution Profit: ${perfect['profit']:.2f}")
        print(f"💰 Realistic Execution Profit: ${realistic['profit']:.2f}")
        print(f"💸 Spread Costs Deducted: ${spread_impact:.2f}")
        print(f"📉 Net Difference: ${profit_diff:.2f}")
        
        if perfect['profit'] != 0:
            impact_percent = (spread_impact / abs(perfect['profit'])) * 100
            print(f"📈 Spread Impact: {impact_percent:.1f}% of profits")
        
        print(f"\n💡 Key Insights:")
        if spread_impact > abs(perfect['profit']) * 0.2:
            print(f"   🔴 HIGH IMPACT: Spread costs significantly affect results")
        elif spread_impact > abs(perfect['profit']) * 0.1:
            print(f"   🟡 MEDIUM IMPACT: Spread costs moderately affect results")
        else:
            print(f"   🟢 LOW IMPACT: Spread costs minimally affect results")
    
    # Test Gold protection
    demo_gold_protection()

def create_synthetic_data():
    """Create synthetic market data for demo"""
    
    np.random.seed(42)  # For reproducible results
    
    # Generate 1000 hourly bars
    dates = pd.date_range('2023-01-01', periods=1000, freq='H')
    
    # Random walk price with trend
    price_start = 1.1000
    returns = np.random.normal(0.0001, 0.0010, 1000)  # Small trend + volatility
    prices = price_start + np.cumsum(returns)
    
    # Create OHLC from the price series
    data = []
    for i, price in enumerate(prices):
        volatility = np.random.uniform(0.0005, 0.0020)
        
        open_price = price if i == 0 else data[i-1]['close']
        high_price = open_price + np.random.uniform(0, volatility)
        low_price = open_price - np.random.uniform(0, volatility)
        close_price = open_price + np.random.uniform(-volatility/2, volatility/2)
        
        # Ensure high >= open,close and low <= open,close
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        data.append({
            'time': dates[i],
            'open': round(open_price, 5),
            'high': round(high_price, 5),
            'low': round(low_price, 5),
            'close': round(close_price, 5),
            'volume': np.random.randint(100, 1000)
        })
    
    return pd.DataFrame(data)

def demo_gold_protection():
    """Demonstrate gold-specific protection features"""
    
    print(f"\n🥇 Gold (XAUUSD) Protection Demo")
    print("=" * 40)
    
    # Create volatile gold-like data
    np.random.seed(123)
    dates = pd.date_range('2023-01-01', periods=500, freq='H')
    
    # Higher volatility for gold
    price_start = 2000.0
    returns = np.random.normal(0.001, 0.015, 500)  # High volatility
    prices = price_start + np.cumsum(returns)
    
    # Create OHLC
    data = []
    for i, price in enumerate(prices):
        volatility = np.random.uniform(2.0, 10.0)  # Much higher volatility
        
        open_price = price if i == 0 else data[i-1]['close']
        high_price = open_price + np.random.uniform(0, volatility)
        low_price = open_price - np.random.uniform(0, volatility)
        close_price = open_price + np.random.uniform(-volatility/2, volatility/2)
        
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        data.append({
            'time': dates[i],
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': np.random.randint(100, 1000)
        })
    
    df_gold = pd.DataFrame(data)
    
    # Test different risk levels for gold
    risk_levels = [0.5, 1.0, 2.0, 5.0]
    
    print("🔒 Testing Gold Protection at Different Risk Levels:")
    
    for risk in risk_levels:
        try:
            result = run_enhanced_backtest(
                'MA_CROSSOVER',
                {'risk_percent': risk, 'sl_atr_multiplier': 2.0, 'tp_atr_multiplier': 4.0},
                df_gold,
                'XAUUSD',
                {'enable_spread_costs': True, 'enable_slippage': True}
            )
            
            if 'error' not in result:
                config = result.get('engine_config', {}).get('instrument_config', {})
                max_lot = config.get('max_lot_size', 'Unknown')
                
                profit = result.get('total_profit_usd', 0)
                trades = result.get('total_trades', 0)
                spread_costs = result.get('total_spread_costs', 0)
                
                print(f"   Risk {risk:3.1f}%: Profit=${profit:7.0f}, Trades={trades:3d}, "
                      f"Spread=${spread_costs:5.0f}, MaxLot={max_lot}")
            
        except Exception as e:
            print(f"   Risk {risk:3.1f}%: Error - {e}")
    
    print(f"\n💡 Gold Protection Features:")
    print(f"   🔒 Maximum lot size capped at 0.10")
    print(f"   ⚡ ATR-based volatility reduction")
    print(f"   🚨 Emergency brake at 5% capital risk")
    print(f"   💸 Higher spread costs (15 pips vs 2 pips)")
    print(f"   📉 Conservative risk limits (1% max)")

if __name__ == "__main__":
    # Change to lab directory
    lab_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(lab_dir)
    
    demo_enhanced_features()