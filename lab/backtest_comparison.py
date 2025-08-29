# backtest_comparison.py - Compare Original vs Enhanced Backtesting Engine
import os
import sys
import pandas as pd
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import both engines
from core.backtesting.engine import run_backtest as run_original_backtest
from core.backtesting.enhanced_engine import run_enhanced_backtest

def compare_backtesting_engines():
    """Compare original vs enhanced backtesting engines"""
    
    print("🔬 Backtesting Engine Comparison")
    print("=" * 60)
    
    # Find available data files
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and 'data' in f and not f.endswith('.bak')]
    
    if not csv_files:
        print("❌ No cleaned CSV data files found.")
        print("💡 Please run 'python clean_data.py' first to prepare data files.")
        return
    
    # Test instruments
    test_instruments = [
        ('EURUSD', 'MA_CROSSOVER'),
        ('XAUUSD', 'BOLLINGER_REVERSION'),
        ('GBPUSD', 'RSI_CROSSOVER')
    ]
    
    # Test parameters
    test_params = {
        'risk_percent': 1.0,
        'sl_atr_multiplier': 2.0,
        'tp_atr_multiplier': 4.0,
        # Backward compatibility
        'lot_size': 1.0,
        'sl_pips': 2.0,
        'tp_pips': 4.0
    }
    
    results = []
    
    for instrument, strategy in test_instruments:
        # Find matching file
        matching_files = [f for f in csv_files if instrument in f.upper()]
        if not matching_files:
            print(f"⚠️ No data file found for {instrument}")
            continue
            
        filename = matching_files[0]
        
        try:
            print(f"\n📊 Testing {instrument} with {strategy}")
            print(f"📁 Data file: {filename}")
            print("-" * 40)
            
            # Load data
            df = pd.read_csv(filename)
            
            # Check if data is in correct format
            expected_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in expected_columns):
                print(f"   ⚠️ Skipping - data needs cleaning")
                continue
            
            # Sample data for faster testing (last 1000 rows)
            df_sample = df.tail(1000).copy()
            
            print(f"   📈 Data points: {len(df_sample)}")
            
            # Run original backtesting
            print("   🔄 Running original engine...")
            try:
                original_result = run_original_backtest(strategy, test_params, df_sample, instrument)
                original_success = 'error' not in original_result
            except Exception as e:
                print(f"   ❌ Original engine error: {e}")
                original_success = False
                original_result = {'error': str(e)}
            
            # Run enhanced backtesting
            print("   🔄 Running enhanced engine...")
            try:
                enhanced_result = run_enhanced_backtest(strategy, test_params, df_sample, instrument)
                enhanced_success = 'error' not in enhanced_result
            except Exception as e:
                print(f"   ❌ Enhanced engine error: {e}")
                enhanced_success = False
                enhanced_result = {'error': str(e)}
            
            # Compare results
            if original_success and enhanced_success:
                print("   ✅ Both engines completed successfully")
                
                orig_profit = original_result.get('total_profit_usd', 0)
                enh_profit = enhanced_result.get('total_profit_usd', 0)
                spread_costs = enhanced_result.get('total_spread_costs', 0)
                
                print(f"   💰 Original Profit: ${orig_profit:.2f}")
                print(f"   💰 Enhanced Profit: ${enh_profit:.2f}")
                print(f"   💸 Spread Costs: ${spread_costs:.2f}")
                print(f"   📉 Difference: ${enh_profit - orig_profit:.2f}")
                
                orig_trades = original_result.get('total_trades', 0)
                enh_trades = enhanced_result.get('total_trades', 0)
                
                print(f"   📊 Original Trades: {orig_trades}")
                print(f"   📊 Enhanced Trades: {enh_trades}")
                
                if orig_profit != 0:
                    impact_percent = ((orig_profit - enh_profit) / abs(orig_profit)) * 100
                    print(f"   📈 Spread Impact: {impact_percent:.1f}%")
                
                results.append({
                    'instrument': instrument,
                    'strategy': strategy,
                    'original_profit': orig_profit,
                    'enhanced_profit': enh_profit,
                    'spread_costs': spread_costs,
                    'impact_percent': impact_percent if orig_profit != 0 else 0,
                    'original_trades': orig_trades,
                    'enhanced_trades': enh_trades
                })
                
            elif original_success:
                print("   ⚠️ Only original engine succeeded")
            elif enhanced_success:
                print("   ⚠️ Only enhanced engine succeeded")
            else:
                print("   ❌ Both engines failed")
                
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    # Summary
    if results:
        print(f"\n📊 COMPARISON SUMMARY")
        print("=" * 60)
        
        total_original_profit = sum(r['original_profit'] for r in results)
        total_enhanced_profit = sum(r['enhanced_profit'] for r in results)
        total_spread_costs = sum(r['spread_costs'] for r in results)
        
        print(f"💰 Total Original Profit: ${total_original_profit:.2f}")
        print(f"💰 Total Enhanced Profit: ${total_enhanced_profit:.2f}")
        print(f"💸 Total Spread Costs: ${total_spread_costs:.2f}")
        print(f"📉 Total Difference: ${total_enhanced_profit - total_original_profit:.2f}")
        
        if total_original_profit != 0:
            total_impact = ((total_original_profit - total_enhanced_profit) / abs(total_original_profit)) * 100
            print(f"📈 Overall Spread Impact: {total_impact:.1f}%")
        
        print(f"\n📋 Individual Results:")
        for r in results:
            print(f"  {r['instrument']:>7} | {r['strategy']:>15} | "
                  f"Original: ${r['original_profit']:>7.0f} | "
                  f"Enhanced: ${r['enhanced_profit']:>7.0f} | "
                  f"Impact: {r['impact_percent']:>5.1f}%")
        
        print(f"\n💡 Key Insights:")
        
        # Find highest impact instrument
        highest_impact = max(results, key=lambda x: abs(x['impact_percent']))
        print(f"   🔴 Highest spread impact: {highest_impact['instrument']} ({highest_impact['impact_percent']:.1f}%)")
        
        # Average impact
        avg_impact = sum(r['impact_percent'] for r in results) / len(results)
        print(f"   📊 Average spread impact: {avg_impact:.1f}%")
        
        if avg_impact > 15:
            print(f"   ⚠️  HIGH IMPACT: Consider using enhanced engine for realistic results")
        elif avg_impact > 5:
            print(f"   ⚠️  MODERATE IMPACT: Enhanced engine recommended for accuracy")
        else:
            print(f"   ✅ LOW IMPACT: Both engines give similar results")
    
    print(f"\n🔧 Enhanced Engine Features:")
    print(f"   ✅ ATR-based position sizing")
    print(f"   ✅ Realistic spread cost modeling")
    print(f"   ✅ Instrument-specific configurations")
    print(f"   ✅ Slippage simulation")
    print(f"   ✅ Enhanced XAUUSD protection")
    print(f"   ✅ Emergency brake system")

def test_enhanced_features():
    """Test enhanced features separately"""
    
    print(f"\n🧪 Enhanced Features Test")
    print("=" * 40)
    
    # Test with different configurations
    test_configs = [
        {'enable_spread_costs': False, 'enable_slippage': False, 'name': 'Perfect Execution'},
        {'enable_spread_costs': True, 'enable_slippage': False, 'name': 'Spread Only'},
        {'enable_spread_costs': True, 'enable_slippage': True, 'name': 'Realistic Execution'}
    ]
    
    print("🎯 Testing different execution models...")
    print("   (This would run with actual data in a full test)")

if __name__ == "__main__":
    # Change to lab directory
    lab_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(lab_dir)
    
    compare_backtesting_engines()
    test_enhanced_features()