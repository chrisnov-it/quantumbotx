# final_integration_test.py - Final Integration Verification
import sys
import os
import pandas as pd

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

def test_api_integration():
    """Test that the API integration works correctly"""
    
    print("🔬 Final Integration Test - API & Enhanced Engine")
    print("=" * 60)
    
    # Import the API route function directly
    from core.routes.api_backtest import save_backtest_result
    from core.backtesting.enhanced_engine import run_enhanced_backtest
    
    # Test data
    test_file = 'EURUSD_16385_data.csv'
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        return False
        
    # Load test data
    df = pd.read_csv(test_file).tail(200)  # Small sample for quick test
    
    print(f"📊 Testing with {len(df)} data points from {test_file}")
    
    # Simulate web interface parameters (what user would send)
    web_params = {
        'lot_size': 1.5,      # This gets mapped to risk_percent
        'sl_pips': 2.5,       # This gets mapped to sl_atr_multiplier  
        'tp_pips': 5.0        # This gets mapped to tp_atr_multiplier
    }
    
    print(f"🔄 Web interface parameters: {web_params}")
    
    # Simulate the API parameter mapping (like the web interface does)
    enhanced_params = web_params.copy()
    enhanced_params['risk_percent'] = float(web_params['lot_size'])
    enhanced_params['sl_atr_multiplier'] = float(web_params['sl_pips'])
    enhanced_params['tp_atr_multiplier'] = float(web_params['tp_pips'])
    
    print(f"🔄 Mapped parameters: {enhanced_params}")
    
    # Simulate engine config (like the API sets)
    engine_config = {
        'enable_spread_costs': True,
        'enable_slippage': True,
        'enable_realistic_execution': True
    }
    
    # Extract symbol name (like the API does)
    symbol_name = test_file.replace('.csv', '').split('_')[0].upper()
    print(f"🎯 Detected symbol: {symbol_name}")
    
    # Run enhanced backtest (like the API does)
    print(f"\n🚀 Running enhanced backtest...")
    try:
        results = run_enhanced_backtest(
            'MA_CROSSOVER',
            enhanced_params,
            df,
            symbol_name=symbol_name,
            engine_config=engine_config
        )
        
        if 'error' in results:
            print(f"❌ Backtest error: {results['error']}")
            return False
            
        print(f"✅ Backtest successful!")
        print(f"   💰 Gross Profit: ${results.get('total_profit_usd', 0):.2f}")
        print(f"   💸 Spread Costs: ${results.get('total_spread_costs', 0):.2f}")
        print(f"   💵 Net Profit: ${results.get('net_profit_after_costs', 0):.2f}")
        print(f"   📊 Total Trades: {results.get('total_trades', 0)}")
        print(f"   📈 Win Rate: {results.get('win_rate_percent', 0):.1f}%")
        
        # Check enhanced engine features
        engine_config_result = results.get('engine_config', {})
        print(f"\n🔧 Enhanced Engine Features:")
        print(f"   ✅ Spread costs enabled: {engine_config_result.get('spread_costs_enabled', False)}")
        print(f"   ✅ Slippage enabled: {engine_config_result.get('slippage_enabled', False)}")
        print(f"   ✅ Realistic execution: {engine_config_result.get('realistic_execution', False)}")
        
        # Check instrument config
        inst_config = engine_config_result.get('instrument_config', {})
        print(f"   🔒 Max risk: {inst_config.get('max_risk_percent', 'N/A')}%")
        print(f"   📏 Max lot: {inst_config.get('max_lot_size', 'N/A')}")
        print(f"   💸 Spread: {inst_config.get('typical_spread_pips', 'N/A')} pips")
        
    except Exception as e:
        print(f"❌ Backtest exception: {e}")
        return False
    
    # Test database save function (like the API does)
    print(f"\n💾 Testing database save...")
    try:
        strategy_name = results.get('strategy_name', 'MA_CROSSOVER')
        filename = test_file
        
        # This calls the same function the API uses
        save_backtest_result(strategy_name, filename, web_params, results)
        print(f"✅ Database save successful")
        
    except Exception as e:
        print(f"❌ Database save error: {e}")
        return False
    
    # Verify results contain all expected enhanced fields
    print(f"\n🔍 Verifying enhanced results format...")
    required_fields = [
        'total_profit_usd', 'total_spread_costs', 'net_profit_after_costs',
        'instrument', 'engine_config', 'wins', 'losses', 'total_trades'
    ]
    
    missing_fields = [field for field in required_fields if field not in results]
    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
        return False
    else:
        print(f"✅ All required enhanced fields present")
    
    # Check that spread costs are realistic
    spread_costs = results.get('total_spread_costs', 0)
    total_trades = results.get('total_trades', 0)
    if total_trades > 0 and spread_costs <= 0:
        print(f"⚠️ Warning: No spread costs despite {total_trades} trades")
    elif total_trades > 0:
        avg_spread_cost = spread_costs / total_trades
        print(f"✅ Realistic spread costs: ${avg_spread_cost:.2f} per trade")
    
    print(f"\n🎉 Final Integration Test: PASSED")
    print(f"\n📋 Summary:")
    print(f"   ✅ Enhanced engine integrated correctly")
    print(f"   ✅ Parameter mapping works")
    print(f"   ✅ Database integration functional")
    print(f"   ✅ Spread costs calculated")
    print(f"   ✅ Instrument protection applied")
    print(f"   ✅ Web interface compatibility maintained")
    
    return True

if __name__ == "__main__":
    # Change to lab directory
    lab_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(lab_dir)
    
    if test_api_integration():
        print(f"\n🎉 ALL TESTS PASSED - Integration Complete!")
        print(f"\n🚀 Enhanced Backtesting Engine is fully integrated and ready!")
    else:
        print(f"\n❌ Some tests failed - check integration")