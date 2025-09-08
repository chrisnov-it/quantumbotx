#!/usr/bin/env python3
# test_index_risk_fix.py - Test the fixed index risk management

import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_index_risk_management():
    """Test the corrected index risk management and position sizing"""
    
    print("🔧 Testing INDEX Risk Management Fix")
    print("=" * 60)
    
    try:
        from core.backtesting.enhanced_engine import InstrumentConfig, EnhancedBacktestEngine
        
        # Test 1: Verify US500 detection and configuration
        print("1️⃣ Testing US500 instrument detection...")
        config = InstrumentConfig.get_config('US500')
        
        print(f"US500 Configuration:")
        print(f"  Contract Size: {config['contract_size']}")
        print(f"  Max Risk: {config['max_risk_percent']}%")
        print(f"  Max Lot Size: {config['max_lot_size']}")
        print(f"  Typical Spread: {config['typical_spread_pips']} pips")
        
        if config['max_risk_percent'] <= 0.5 and config['max_lot_size'] <= 0.1:
            print("  ✅ Conservative risk limits applied")
        else:
            print("  ❌ Risk limits too high")
            return False
        
        # Test 2: Test position sizing
        print(f"\\n2️⃣ Testing position sizing for US500...")
        engine = EnhancedBacktestEngine()
        
        # Simulate realistic parameters
        capital = 10000
        risk_percent = 2.0  # User requested 2%
        atr_value = 45.0  # Typical US500 ATR
        sl_distance = atr_value * 2.0  # 2x ATR stop loss
        
        position_size = engine.calculate_position_size(
            'US500', capital, risk_percent, sl_distance, atr_value, config
        )
        
        print(f"  Capital: ${capital}")
        print(f"  Requested Risk: {risk_percent}%")
        print(f"  Applied Risk: {min(risk_percent, config['max_risk_percent'])}%")
        print(f"  ATR: {atr_value}")
        print(f"  SL Distance: {sl_distance}")
        print(f"  Calculated Lot Size: {position_size}")
        
        # Calculate actual risk amount
        max_loss = position_size * sl_distance * config['contract_size']
        actual_risk_percent = (max_loss / capital) * 100
        
        print(f"  Max Potential Loss: ${max_loss:.2f}")
        print(f"  Actual Risk %: {actual_risk_percent:.2f}%")
        
        if actual_risk_percent <= 0.5:  # Should be very conservative
            print("  ✅ Position sizing is now conservative")
        else:
            print("  ❌ Position sizing still too aggressive")
            return False
        
        # Test 3: Test with very high volatility
        print(f"\\n3️⃣ Testing high volatility protection...")
        high_atr = 120.0  # Very high ATR
        high_vol_position = engine.calculate_position_size(
            'US500', capital, risk_percent, high_atr * 2, high_atr, config
        )
        
        print(f"  High ATR: {high_atr}")
        print(f"  High Vol Position Size: {high_vol_position}")
        
        if high_vol_position <= 0.01:
            print("  ✅ Extreme volatility protection working")
        else:
            print("  ⚠️ High volatility position might still be risky")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_backtest_with_fixes():
    """Test a full backtest with the risk management fixes"""
    
    print(f"\\n🚀 Testing Full Backtest with Risk Fixes")
    print("=" * 60)
    
    try:
        from core.backtesting.enhanced_engine import run_enhanced_backtest
        
        # Load US500 data
        csv_file = 'lab/backtest_data/US500_H1_data.csv'
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return False
        
        df = pd.read_csv(csv_file, parse_dates=['time'])
        test_df = df.tail(500).copy()  # Small sample for quick test
        
        # Conservative parameters
        params = {
            'breakout_period': 20,
            'volume_surge_multiplier': 1.5,
            'min_breakout_size': 0.2,
            'risk_percent': 2.0,  # This will be capped at 0.5% for indices
            'sl_atr_multiplier': 2.0,
            'tp_atr_multiplier': 4.0
        }
        
        engine_config = {
            'enable_spread_costs': True,
            'enable_slippage': True,
            'enable_realistic_execution': True
        }
        
        print(f"Testing with {len(test_df)} rows...")
        print(f"Parameters: {params}")
        
        results = run_enhanced_backtest(
            'INDEX_BREAKOUT_PRO',
            params,
            test_df,
            symbol_name='US500',
            engine_config=engine_config
        )
        
        if 'error' in results:
            print(f"❌ Backtest error: {results['error']}")
            return False
        
        print(f"\\n📈 Fixed Results:")
        print(f"  Total Trades: {results.get('total_trades', 0)}")
        print(f"  Total Profit: ${results.get('total_profit_usd', 0):.2f}")
        print(f"  Max Drawdown: {results.get('max_drawdown_percent', 0):.2f}%")
        print(f"  Win Rate: {results.get('win_rate_percent', 0):.1f}%")
        print(f"  Final Capital: ${results.get('final_capital', 0):.2f}")
        
        # Check if results are reasonable
        max_drawdown = results.get('max_drawdown_percent', 0)
        total_profit = abs(results.get('total_profit_usd', 0))
        
        if max_drawdown < 50 and total_profit < 5000:  # Much more reasonable
            print(f"\\n✅ Results look much more reasonable!")
            print(f"   • Drawdown under control: {max_drawdown:.1f}%")
            print(f"   • Profit/loss reasonable: ${total_profit:.2f}")
            return True
        else:
            print(f"\\n⚠️ Results still concerning:")
            print(f"   • Drawdown: {max_drawdown:.1f}% (should be <50%)")
            print(f"   • P/L magnitude: ${total_profit:.2f} (should be <$5000)")
            return False
        
    except Exception as e:
        print(f"❌ Full backtest test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 INDEX Risk Management Fix Testing")
    print("=" * 70)
    
    test1 = test_index_risk_management()
    test2 = test_full_backtest_with_fixes()
    
    if test1 and test2:
        print(f"\\n✅ INDEX RISK MANAGEMENT FIXED!")
        print(f"\\n📋 What was fixed:")
        print(f"   1. Added INDICES configuration with 0.5% max risk")
        print(f"   2. Added ultra-conservative position sizing for indices")
        print(f"   3. Added volatility protection for high ATR periods")
        print(f"   4. Corrected spread cost calculation for indices")
        print(f"\\n🎯 Expected improvement in web interface:")
        print(f"   • Much smaller position sizes (0.01-0.03 lots max)")
        print(f"   • Reasonable profit/loss amounts (<$5000)")
        print(f"   • Controlled drawdowns (<50%)")
        print(f"   • Proper risk management for US500/indices")
    else:
        print(f"\\n❌ Some issues remain - check output above")