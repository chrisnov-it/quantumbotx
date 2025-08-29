#!/usr/bin/env python3
"""
Diagnostic script to identify the root cause of backtesting issues
Focuses on the specific problem: 100% max drawdown and terrible performance across all strategies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import yfinance as yf
from core.backtesting.engine import run_backtest as run_original_backtest
from core.backtesting.enhanced_engine import run_enhanced_backtest
from core.strategies.bollinger_squeeze import BollingerSqueezeStrategy
from datetime import datetime, timedelta

def download_test_data():
    """Download recent EURUSD data for testing"""
    try:
        # Download EURUSD data for the last 6 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        # Download EURUSD data
        ticker = yf.Ticker("EURUSD=X")
        df = ticker.history(start=start_date, end=end_date, interval="1h")
        
        if df.empty:
            print("❌ Failed to download EURUSD data")
            return None
            
        # Standardize column names
        df.columns = df.columns.str.lower()
        df.reset_index(inplace=True)
        
        print(f"✅ Downloaded {len(df)} EURUSD bars from {df['datetime'].min()} to {df['datetime'].max()}")
        return df
        
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        return None

def test_strategy_signals(df, strategy_class, params):
    """Test if strategy is generating reasonable signals"""
    print(f"\n🔍 Testing {strategy_class.name} signal generation...")
    
    # Create mock bot
    class MockBot:
        def __init__(self):
            self.market_for_mt5 = "EURUSD"
            self.timeframe = "H1"
            self.tf_map = {}
    
    try:
        # Initialize strategy
        strategy_instance = strategy_class(bot_instance=MockBot(), params=params)
        
        # Analyze data
        df_with_signals = strategy_instance.analyze_df(df.copy())
        
        # Count signals
        signal_counts = df_with_signals['signal'].value_counts()
        print(f"Signal distribution: {dict(signal_counts)}")
        
        # Check if we have reasonable signals
        buy_signals = len(df_with_signals[df_with_signals['signal'] == 'BUY'])
        sell_signals = len(df_with_signals[df_with_signals['signal'] == 'SELL'])
        hold_signals = len(df_with_signals[df_with_signals['signal'] == 'HOLD'])
        
        total_bars = len(df_with_signals)
        
        print(f"BUY signals: {buy_signals} ({buy_signals/total_bars*100:.1f}%)")
        print(f"SELL signals: {sell_signals} ({sell_signals/total_bars*100:.1f}%)")
        print(f"HOLD signals: {hold_signals} ({hold_signals/total_bars*100:.1f}%)")
        
        # Check for indicators
        print(f"Available columns: {list(df_with_signals.columns)}")
        
        # Check ATR
        if 'ATRr_14' in df_with_signals.columns:
            atr_stats = df_with_signals['ATRr_14'].describe()
            print(f"ATR stats: min={atr_stats['min']:.6f}, max={atr_stats['max']:.6f}, mean={atr_stats['mean']:.6f}")
        else:
            print("❌ ATR indicator missing!")
        
        return df_with_signals
        
    except Exception as e:
        print(f"❌ Error in strategy analysis: {e}")
        return None

def test_backtest_calculations(df_with_signals, params):
    """Test the actual backtest calculations step by step"""
    print(f"\n🧮 Testing backtest calculations...")
    
    # Parameters for testing
    risk_percent = float(params.get('lot_size', 1.0))
    sl_atr_multiplier = float(params.get('sl_pips', 2.0))
    tp_atr_multiplier = float(params.get('tp_pips', 4.0))
    
    print(f"Risk: {risk_percent}%, SL: {sl_atr_multiplier}x ATR, TP: {tp_atr_multiplier}x ATR")
    
    # Simulate a few trades manually
    trades_found = 0
    capital = 10000.0
    initial_capital = capital
    
    for i in range(1, min(len(df_with_signals), 100)):  # Check first 100 bars
        current_bar = df_with_signals.iloc[i]
        signal = current_bar.get("signal", "HOLD")
        
        if signal in ['BUY', 'SELL']:
            trades_found += 1
            entry_price = current_bar['close']
            atr_value = current_bar.get('ATRr_14', 0)
            
            print(f"\nTrade #{trades_found} at bar {i}:")
            print(f"  Signal: {signal}")
            print(f"  Entry price: {entry_price}")
            print(f"  ATR: {atr_value}")
            print(f"  Capital: ${capital:.2f}")
            
            if atr_value > 0:
                # Calculate position size
                sl_distance = atr_value * sl_atr_multiplier
                tp_distance = atr_value * tp_atr_multiplier
                
                # For EURUSD (forex major)
                contract_size = 100000
                amount_to_risk = capital * (risk_percent / 100.0)
                risk_in_currency_per_lot = sl_distance * contract_size
                
                if risk_in_currency_per_lot > 0:
                    calculated_lot_size = amount_to_risk / risk_in_currency_per_lot
                    lot_size = max(0.01, min(calculated_lot_size, 10.0))
                else:
                    lot_size = 0.01
                
                print(f"  SL distance: {sl_distance:.5f}")
                print(f"  TP distance: {tp_distance:.5f}")
                print(f"  Amount to risk: ${amount_to_risk:.2f}")
                print(f"  Risk per lot: ${risk_in_currency_per_lot:.2f}")
                print(f"  Calculated lot size: {calculated_lot_size:.4f}")
                print(f"  Final lot size: {lot_size:.2f}")
                
                # Set SL/TP levels
                if signal == 'BUY':
                    sl_price = entry_price - sl_distance
                    tp_price = entry_price + tp_distance
                else:
                    sl_price = entry_price + sl_distance
                    tp_price = entry_price - tp_distance
                
                print(f"  SL price: {sl_price:.5f}")
                print(f"  TP price: {tp_price:.5f}")
                
                # Check if prices are reasonable
                if sl_price <= 0 or tp_price <= 0:
                    print("  ❌ Invalid SL/TP prices!")
                elif abs((sl_price - entry_price) / entry_price) > 0.1:
                    print("  ❌ SL distance too large (>10%)!")
                elif abs((tp_price - entry_price) / entry_price) > 0.2:
                    print("  ❌ TP distance too large (>20%)!")
                else:
                    print("  ✅ Trade setup looks reasonable")
            else:
                print("  ❌ Invalid ATR value!")
            
            if trades_found >= 5:  # Limit to first 5 trades
                break
    
    print(f"\nFound {trades_found} trades in first 100 bars")
    return trades_found > 0

def run_diagnostic():
    """Main diagnostic function"""
    print("🚀 Starting Backtesting Diagnostic...")
    print("=" * 60)
    
    # 1. Download test data
    df = download_test_data()
    if df is None:
        return
    
    # 2. Test strategy parameters
    params = {
        'bb_length': 20,
        'bb_std': 2.0,
        'squeeze_window': 10,
        'squeeze_factor': 0.7,
        'rsi_period': 14,
        'lot_size': 1.0,  # 1% risk
        'sl_pips': 2.0,   # 2x ATR
        'tp_pips': 4.0    # 4x ATR
    }
    
    print(f"Test parameters: {params}")
    
    # 3. Test Bollinger Squeeze strategy signals
    df_with_signals = test_strategy_signals(df, BollingerSqueezeStrategy, params)
    if df_with_signals is None:
        return
    
    # 4. Test manual calculations
    if not test_backtest_calculations(df_with_signals, params):
        print("❌ No valid trades found for manual testing")
        return
    
    # 5. Run original backtest
    print(f"\n🔄 Running original backtest...")
    try:
        original_result = run_original_backtest('bollinger_squeeze', params, df, 'EURUSD')
        print(f"Original engine result:")
        print(f"  Total trades: {original_result.get('total_trades', 0)}")
        print(f"  Total profit: ${original_result.get('total_profit_usd', 0):.2f}")
        print(f"  Win rate: {original_result.get('win_rate_percent', 0):.1f}%")
        print(f"  Max drawdown: {original_result.get('max_drawdown_percent', 0):.1f}%")
    except Exception as e:
        print(f"❌ Original backtest failed: {e}")
        original_result = None
    
    # 6. Run enhanced backtest
    print(f"\n🚀 Running enhanced backtest...")
    try:
        enhanced_result = run_enhanced_backtest('bollinger_squeeze', params, df, 'EURUSD')
        print(f"Enhanced engine result:")
        print(f"  Total trades: {enhanced_result.get('total_trades', 0)}")
        print(f"  Gross profit: ${enhanced_result.get('total_profit_usd', 0):.2f}")
        print(f"  Spread costs: ${enhanced_result.get('total_spread_costs', 0):.2f}")
        print(f"  Net profit: ${enhanced_result.get('net_profit_after_costs', 0):.2f}")
        print(f"  Win rate: {enhanced_result.get('win_rate_percent', 0):.1f}%")
        print(f"  Max drawdown: {enhanced_result.get('max_drawdown_percent', 0):.1f}%")
        
        # Check individual trades
        if enhanced_result.get('trades'):
            print(f"\nLast few trades:")
            for i, trade in enumerate(enhanced_result['trades'][-3:]):
                print(f"  Trade {i+1}: {trade['position_type']} | Entry: {trade['entry']:.5f} | Exit: {trade['exit']:.5f} | Profit: ${trade['profit']:.2f}")
                
    except Exception as e:
        print(f"❌ Enhanced backtest failed: {e}")
        enhanced_result = None
    
    # 7. Analysis and recommendations
    print(f"\n📊 DIAGNOSIS SUMMARY:")
    print("=" * 60)
    
    if original_result and enhanced_result:
        if enhanced_result.get('max_drawdown_percent', 0) > 90:
            print("❌ CRITICAL ISSUE: Enhanced engine shows extreme drawdown!")
            print("   Possible causes:")
            print("   - Position sizing too aggressive")
            print("   - Spread costs too high") 
            print("   - SL/TP calculation errors")
            print("   - Strategy generating bad signals")
        elif original_result.get('max_drawdown_percent', 0) > 90:
            print("❌ CRITICAL ISSUE: Original engine shows extreme drawdown!")
            print("   Possible causes:")
            print("   - Position sizing calculation error")
            print("   - SL/TP logic bug")
            print("   - Strategy overfitting")
        else:
            print("✅ Backtest engines working reasonably")
    
    print("\nRecommendations:")
    print("1. Check position sizing calculations")
    print("2. Verify SL/TP distance calculations")
    print("3. Test with more conservative parameters")
    print("4. Validate strategy signal quality")

if __name__ == '__main__':
    run_diagnostic()