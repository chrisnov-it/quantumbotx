#!/usr/bin/env python3
# debug_index_strategy.py - Debug the INDEX_BREAKOUT_PRO strategy with US500 data

import sys
import os
import pandas as pd
import logging

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_index_breakout_strategy():
    """Test the INDEX_BREAKOUT_PRO strategy with US500 data"""
    
    print("🔍 Debugging INDEX_BREAKOUT_PRO Strategy with US500 Data")
    print("=" * 70)
    
    try:
        # Import required modules
        from core.backtesting.enhanced_engine import run_enhanced_backtest
        from core.strategies.strategy_map import STRATEGY_MAP
        
        # Check if strategy exists
        strategy_id = 'INDEX_BREAKOUT_PRO'
        if strategy_id not in STRATEGY_MAP:
            print(f"❌ Strategy {strategy_id} not found in STRATEGY_MAP")
            print(f"Available strategies: {list(STRATEGY_MAP.keys())}")
            return False
        
        strategy_class = STRATEGY_MAP[strategy_id]
        print(f"✅ Strategy found: {strategy_class}")
        print(f"Strategy name: {getattr(strategy_class, 'name', 'Unknown')}")
        print(f"Strategy description: {getattr(strategy_class, 'description', 'No description')}")
        
        # Load US500 data
        csv_file = 'lab/backtest_data/US500_H1_data.csv'
        if not os.path.exists(csv_file):
            print(f"❌ Data file not found: {csv_file}")
            return False
        
        print(f"\n📊 Loading data from: {csv_file}")
        df = pd.read_csv(csv_file, parse_dates=['time'])
        print(f"✅ Loaded {len(df)} rows of data")
        print(f"Date range: {df['time'].min()} to {df['time'].max()}")
        print(f"Columns: {list(df.columns)}")
        print("Sample data:")
        print(df.head())
        
        # Test strategy parameters
        print("\n⚙️ Testing strategy parameters...")
        if hasattr(strategy_class, 'get_definable_params'):
            params_def = strategy_class.get_definable_params()
            print(f"✅ Strategy has {len(params_def)} definable parameters:")
            for param in params_def:
                name = param.get('name', 'Unknown')
                display_name = param.get('display_name', param.get('label', 'Unknown'))
                default = param.get('default', 'No default')
                print(f"  - {name} ({display_name}): {default}")
        else:
            print("❌ Strategy has no get_definable_params method")
            return False
        
        # Test strategy instantiation
        print("\n🧪 Testing strategy instantiation...")
        try:
            # Create a mock bot instance
            class MockBot:
                def __init__(self):
                    self.market_for_mt5 = 'US500'
                    self.status = 'Testing'
            
            mock_bot = MockBot()
            strategy_instance = strategy_class(mock_bot, {})
            print("✅ Strategy instantiated successfully")
            
            # Test analyze_df method
            print("\n🔬 Testing analyze_df method...")
            
            # Use a smaller subset for testing
            test_df = df.tail(500).copy()  # Last 500 rows
            print(f"Testing with {len(test_df)} rows")
            
            result_df = strategy_instance.analyze_df(test_df)
            print("✅ analyze_df completed")
            print(f"Result columns: {list(result_df.columns)}")
            
            # Check for signals
            if 'signal' in result_df.columns:
                signals = result_df['signal'].value_counts()
                print(f"Signal distribution: {signals.to_dict()}")
                
                # Count non-HOLD signals
                non_hold_signals = result_df[result_df['signal'] != 'HOLD']
                print(f"Non-HOLD signals: {len(non_hold_signals)}")
                
                if len(non_hold_signals) > 0:
                    print("Sample signals:")
                    print(non_hold_signals[['time', 'signal', 'explanation']].head(10) if 'time' in result_df.columns else non_hold_signals[['signal', 'explanation']].head(10))
                else:
                    print("❌ No trading signals generated!")
                    print("Sample explanations:")
                    print(result_df['explanation'].tail(10).tolist())
            
        except Exception as e:
            print(f"❌ Strategy testing failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test full backtesting
        print("\n🚀 Testing full backtest...")
        
        # Simulate web interface parameters
        web_params = {
            'breakout_period': 20,
            'volume_surge_multiplier': 2.0,
            'confirmation_candles': 2,
            'atr_multiplier_sl': 2.0,
            'atr_multiplier_tp': 4.0
        }
        
        # Enhanced parameters (like API mapping)
        enhanced_params = web_params.copy()
        enhanced_params['risk_percent'] = 1.0  # Conservative for index
        enhanced_params['sl_atr_multiplier'] = web_params.get('atr_multiplier_sl', 2.0)
        enhanced_params['tp_atr_multiplier'] = web_params.get('atr_multiplier_tp', 4.0)
        
        print(f"Parameters: {enhanced_params}")
        
        # Engine configuration
        engine_config = {
            'enable_spread_costs': True,
            'enable_slippage': True,
            'enable_realistic_execution': True
        }
        
        # Extract symbol name (like API does)
        symbol_name = 'US500'
        print(f"Symbol: {symbol_name}")
        
        # Use smaller dataset for testing
        test_df = df.tail(1000).copy()  # Last 1000 rows for faster testing
        
        results = run_enhanced_backtest(
            strategy_id,
            enhanced_params,
            test_df,
            symbol_name=symbol_name,
            engine_config=engine_config
        )
        
        if 'error' in results:
            print(f"❌ Backtest error: {results['error']}")
            return False
        
        print("✅ Backtest completed successfully!")
        print("\n📈 Results Summary:")
        print(f"  Strategy: {results.get('strategy_name', 'Unknown')}")
        print(f"  Total Trades: {results.get('total_trades', 0)}")
        print(f"  Wins: {results.get('wins', 0)}")
        print(f"  Losses: {results.get('losses', 0)}")
        print(f"  Win Rate: {results.get('win_rate_percent', 0):.1f}%")
        print(f"  Total Profit USD: ${results.get('total_profit_usd', 0):.2f}")
        print(f"  Max Drawdown: {results.get('max_drawdown_percent', 0):.1f}%")
        print(f"  Final Capital: ${results.get('final_capital', 0):.2f}")
        
        if results.get('total_trades', 0) == 0:
            print("\n❌ PROBLEM: No trades generated!")
            print("This could be why the web interface shows empty results.")
            
            # Debug signal generation
            print("\n🔍 Debugging signal generation...")
            strategy_instance = strategy_class(MockBot(), enhanced_params)
            debug_df = test_df.tail(100).copy()
            debug_result = strategy_instance.analyze_df(debug_df)
            
            if 'signal' in debug_result.columns:
                signals = debug_result['signal'].value_counts()
                print(f"Signal counts in last 100 rows: {signals.to_dict()}")
                
                if 'BUY' in signals or 'SELL' in signals:
                    print("✅ Signals are being generated by strategy")
                    print("❓ Problem might be in the backtesting engine")
                else:
                    print("❌ Strategy is not generating BUY/SELL signals")
                    print("Sample explanations:")
                    sample_explanations = debug_result['explanation'].tail(10).tolist()
                    for i, exp in enumerate(sample_explanations):
                        print(f"  {i+1}: {exp}")
        else:
            print("✅ Trades were generated successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_index_breakout_strategy()
    if success:
        print("\n✅ Debug completed successfully")
    else:
        print("\n❌ Debug revealed issues that need fixing")