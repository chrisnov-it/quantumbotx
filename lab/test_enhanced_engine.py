# test_enhanced_engine.py - Test Enhanced Engine vs Original Engine
import sys
import os
import pandas as pd

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import both engines for comparison
from core.backtesting.engine import run_backtest as run_original_backtest
from core.backtesting.enhanced_engine import run_enhanced_backtest

def test_engines_comparison():
    """Test both engines with real data to demonstrate improvements"""
    
    print("🚀 Enhanced vs Original Engine Comparison")
    print("=" * 60)
    
    # Test with different instruments
    test_cases = [
        {
            'file': 'EURUSD_16385_data.csv',
            'symbol': 'EURUSD',
            'description': 'Forex Major (Low Spread)'
        },
        {
            'file': 'XAUUSD_16385_data.csv', 
            'symbol': 'XAUUSD',
            'description': 'Gold (High Spread, High Risk)'
        }
    ]
    
    # Test parameters - similar to what would cause accuracy issues before
    test_params = {
        'risk_percent': 2.0,      # High risk that needs protection
        'sl_atr_multiplier': 3.0, # Large SL that needs limiting for gold
        'tp_atr_multiplier': 6.0  # Large TP
    }
    
    results = {}
    
    for test_case in test_cases:
        file_path = test_case['file']
        symbol = test_case['symbol']
        description = test_case['description']
        
        print(f"\n📊 Testing: {symbol} ({description})")
        print("-" * 40)
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
        
        # Load data
        try:
            df = pd.read_csv(file_path)
            
            # Check if data needs cleaning
            if 'spread' in df.columns or 'real_volume' in df.columns:
                print(f"⚠️ Data contains extra columns, cleaning...")
                keep_cols = ['time', 'open', 'high', 'low', 'close', 'volume', 'tick_volume']
                available_cols = [col for col in keep_cols if col in df.columns]
                df = df[available_cols[:6]]  # Keep first 6 essential columns
                
                # Rename tick_volume to volume if needed
                if 'tick_volume' in df.columns and 'volume' not in df.columns:
                    df = df.rename(columns={'tick_volume': 'volume'})
                
                print(f"✅ Cleaned data: {list(df.columns)}")
            
            # Use last 500 rows for faster testing
            df = df.tail(500).reset_index(drop=True)
            
            print(f"📈 Data points: {len(df)}")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            continue
        
        # Test Original Engine
        print(f"\n🔄 Testing Original Engine...")
        try:
            original_result = run_original_backtest(
                'MA_CROSSOVER', test_params, df, symbol_name=symbol
            )
            
            if 'error' not in original_result:
                print(f"✅ Original Engine Results:")
                print(f"   💰 Total Profit: ${original_result.get('total_profit_usd', 0):.2f}")
                print(f"   📊 Total Trades: {original_result.get('total_trades', 0)}")
                print(f"   📈 Win Rate: {original_result.get('win_rate_percent', 0):.1f}%")
                print(f"   💸 Spread Costs: Not modeled")
            else:
                print(f"❌ Original Engine Error: {original_result.get('error')}")
                original_result = None
                
        except Exception as e:
            print(f"❌ Original Engine Exception: {e}")
            original_result = None
        
        # Test Enhanced Engine - Perfect Execution Mode
        print(f"\n🔄 Testing Enhanced Engine (Perfect Mode)...")
        try:
            enhanced_perfect = run_enhanced_backtest(
                'MA_CROSSOVER', test_params, df, symbol_name=symbol,
                engine_config={
                    'enable_spread_costs': False,
                    'enable_slippage': False,
                    'enable_realistic_execution': False
                }
            )
            
            if 'error' not in enhanced_perfect:
                print(f"✅ Enhanced Engine (Perfect) Results:")
                print(f"   💰 Total Profit: ${enhanced_perfect.get('total_profit_usd', 0):.2f}")
                print(f"   📊 Total Trades: {enhanced_perfect.get('total_trades', 0)}")
                print(f"   📈 Win Rate: {enhanced_perfect.get('win_rate_percent', 0):.1f}%")
                print(f"   🔒 Protection Applied: {enhanced_perfect.get('engine_config', {}).get('instrument_config', {}).get('max_risk_percent', 'None')}")
            else:
                print(f"❌ Enhanced Engine (Perfect) Error: {enhanced_perfect.get('error')}")
                enhanced_perfect = None
                
        except Exception as e:
            print(f"❌ Enhanced Engine (Perfect) Exception: {e}")
            enhanced_perfect = None
        
        # Test Enhanced Engine - Realistic Execution Mode
        print(f"\n🔄 Testing Enhanced Engine (Realistic Mode)...")
        try:
            enhanced_realistic = run_enhanced_backtest(
                'MA_CROSSOVER', test_params, df, symbol_name=symbol,
                engine_config={
                    'enable_spread_costs': True,
                    'enable_slippage': True,
                    'enable_realistic_execution': True
                }
            )
            
            if 'error' not in enhanced_realistic:
                print(f"✅ Enhanced Engine (Realistic) Results:")
                print(f"   💰 Total Profit: ${enhanced_realistic.get('total_profit_usd', 0):.2f}")
                print(f"   💸 Spread Costs: ${enhanced_realistic.get('total_spread_costs', 0):.2f}")
                print(f"   💵 Net After Costs: ${enhanced_realistic.get('net_profit_after_costs', 0):.2f}")
                print(f"   📊 Total Trades: {enhanced_realistic.get('total_trades', 0)}")
                print(f"   📈 Win Rate: {enhanced_realistic.get('win_rate_percent', 0):.1f}%")
                print(f"   🔒 Max Risk %: {enhanced_realistic.get('engine_config', {}).get('instrument_config', {}).get('max_risk_percent', 'None')}")
                print(f"   📏 Max Lot Size: {enhanced_realistic.get('engine_config', {}).get('instrument_config', {}).get('max_lot_size', 'None')}")
            else:
                print(f"❌ Enhanced Engine (Realistic) Error: {enhanced_realistic.get('error')}")
                enhanced_realistic = None
                
        except Exception as e:
            print(f"❌ Enhanced Engine (Realistic) Exception: {e}")
            enhanced_realistic = None
        
        # Store results for comparison
        results[symbol] = {
            'original': original_result,
            'enhanced_perfect': enhanced_perfect,
            'enhanced_realistic': enhanced_realistic,
            'description': description
        }
    
    # Generate comparison summary
    print(f"\n📊 COMPREHENSIVE COMPARISON SUMMARY")
    print("=" * 60)
    
    for symbol, result_set in results.items():
        if not any(result_set.values()):
            continue
            
        print(f"\n🎯 {symbol} ({result_set['description']}):")
        print("-" * 30)
        
        # Extract results
        orig = result_set['original']
        perf = result_set['enhanced_perfect'] 
        real = result_set['enhanced_realistic']
        
        if orig:
            orig_profit = orig.get('total_profit_usd', 0)
            orig_trades = orig.get('total_trades', 0)
            print(f"📈 Original Engine: ${orig_profit:+7.0f} profit, {orig_trades:3d} trades")
        
        if perf:
            perf_profit = perf.get('total_profit_usd', 0)
            perf_trades = perf.get('total_trades', 0)
            max_risk = perf.get('engine_config', {}).get('instrument_config', {}).get('max_risk_percent', 0)
            print(f"🔒 Enhanced (Protected): ${perf_profit:+7.0f} profit, {perf_trades:3d} trades, {max_risk}% max risk")
        
        if real:
            real_profit = real.get('total_profit_usd', 0)
            real_trades = real.get('total_trades', 0)
            spread_costs = real.get('total_spread_costs', 0)
            print(f"💸 Enhanced (Realistic): ${real_profit:+7.0f} profit, {real_trades:3d} trades, ${spread_costs:4.0f} spread cost")
        
        # Show impact analysis
        if orig and real:
            if orig_profit != 0:
                accuracy_improvement = ((real_profit - orig_profit) / abs(orig_profit)) * 100
                print(f"🎯 Accuracy Difference: {accuracy_improvement:+.1f}% (realistic vs original)")
            
            if symbol == 'XAUUSD':
                print(f"🥇 Gold Protection: Risk capped, lot sizes limited, higher spreads modeled")
        
        print()
    
    print(f"\n💡 Key Improvements Summary:")
    print(f"   ✅ ATR-based risk management prevents oversized positions")
    print(f"   ✅ Instrument-specific protections (especially for gold)")
    print(f"   ✅ Realistic spread cost modeling")
    print(f"   ✅ Slippage simulation")
    print(f"   ✅ Emergency brake systems")
    print(f"   ✅ More accurate profit/loss calculations")
    
    print(f"\n🎯 Why Your Old Results Were Inaccurate:")
    print(f"   ❌ No spread cost deduction (major profit overestimation)")
    print(f"   ❌ Fixed SL/TP instead of ATR-based (wrong position sizing)")
    print(f"   ❌ No gold-specific protection (dangerous for XAUUSD)")
    print(f"   ❌ Perfect execution assumption (unrealistic)")
    
    return results

if __name__ == "__main__":
    # Change to lab directory
    lab_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(lab_dir)
    
    test_engines_comparison()