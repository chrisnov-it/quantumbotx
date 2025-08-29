#!/usr/bin/env python3
"""
Debug backtesting execution to find why trades aren't being executed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def debug_enhanced_backtest():
    """Debug the enhanced backtest step by step"""
    print("🔍 DEBUGGING ENHANCED BACKTEST EXECUTION")
    print("=" * 70)
    
    try:
        # Import components
        from core.backtesting.enhanced_engine import EnhancedBacktestEngine, InstrumentConfig
        from core.strategies.ma_crossover import MACrossoverStrategy
        
        # Create simple test data
        np.random.seed(42)
        base_price = 1.1000
        
        data = []
        for i in range(50):
            # Create simple price movement
            if i < 25:
                price = base_price + i * 0.0001  # Uptrend
            else:
                price = base_price + (50-i) * 0.0001  # Downtrend
            
            time = datetime(2024, 1, 1) + timedelta(hours=i)
            data.append({
                'time': time,
                'open': price,
                'high': price + 0.00005,
                'low': price - 0.00005,
                'close': price,
                'volume': 10000
            })
        
        df = pd.DataFrame(data)
        print(f"Created {len(df)} bars of simple test data")
        
        # Strategy setup
        class MockBot:
            def __init__(self):
                self.market_for_mt5 = "EURUSD"
                self.timeframe = "H1"
        
        params = {
            'fast_period': 5,
            'slow_period': 15,
            'risk_percent': 1.0,
            'sl_atr_multiplier': 2.0,
            'tp_atr_multiplier': 4.0
        }
        
        # Generate signals
        strategy = MACrossoverStrategy(bot_instance=MockBot(), params=params)
        df_with_signals = strategy.analyze_df(df.copy())
        
        # Add ATR
        import pandas_ta as ta
        df_with_signals.ta.atr(length=14, append=True)
        df_with_signals.dropna(inplace=True)
        df_with_signals.reset_index(inplace=True)
        
        print(f"After processing: {len(df_with_signals)} bars")
        
        # Check signals
        signal_counts = df_with_signals['signal'].value_counts()
        print(f"Signals: {dict(signal_counts)}")
        
        # Show signal bars
        signal_bars = df_with_signals[df_with_signals['signal'] != 'HOLD']
        print(f"Signal bars:")
        for i, row in signal_bars.iterrows():
            print(f"  Index {i}: {row['signal']} | Close: {row['close']:.5f} | ATR: {row.get('ATRr_14', 'Missing')}")
        
        if len(signal_bars) == 0:
            print("❌ No signals generated - can't debug execution")
            return
        
        # Manual backtest loop simulation
        print(f"\\n🔄 SIMULATING BACKTEST LOOP...")
        
        # Initialize
        engine = EnhancedBacktestEngine()
        config = InstrumentConfig.get_config('EURUSD')
        
        capital = 10000.0
        trades = []
        in_position = False
        
        # Enhanced parameter handling (matching the real engine)
        risk_percent = float(params.get('risk_percent', params.get('lot_size', 1.0)))
        sl_atr_multiplier = float(params.get('sl_atr_multiplier', params.get('sl_pips', 2.0)))
        tp_atr_multiplier = float(params.get('tp_atr_multiplier', params.get('tp_pips', 4.0)))
        
        print(f"Engine parameters:")
        print(f"  Risk: {risk_percent}%")
        print(f"  SL: {sl_atr_multiplier}x ATR") 
        print(f"  TP: {tp_atr_multiplier}x ATR")
        print(f"  Config: {config}")
        
        # Loop through data
        for i in range(1, len(df_with_signals)):
            current_bar = df_with_signals.iloc[i]
            
            if capital <= 0:
                print(f"💀 Capital exhausted at bar {i}")
                break
            
            if not in_position:
                signal = current_bar.get("signal", "HOLD")
                
                if signal in ['BUY', 'SELL']:
                    print(f"\\n📊 Processing signal at bar {i}:")
                    print(f"  Signal: {signal}")
                    print(f"  Price: {current_bar['close']}")
                    print(f"  Capital: ${capital:.2f}")
                    
                    atr_value = current_bar.get('ATRr_14', 0)
                    print(f"  ATR: {atr_value}")
                    
                    if atr_value <= 0:
                        print(f"  ❌ Invalid ATR - skipping")
                        continue
                    
                    # Calculate distances
                    sl_distance = atr_value * sl_atr_multiplier
                    tp_distance = atr_value * tp_atr_multiplier
                    
                    print(f"  SL distance: {sl_distance:.5f}")
                    print(f"  TP distance: {tp_distance:.5f}")
                    
                    # Calculate position size
                    lot_size = engine.calculate_position_size(
                        'EURUSD', capital, risk_percent, sl_distance, atr_value, config
                    )
                    
                    print(f"  Calculated lot size: {lot_size}")
                    
                    if lot_size <= 0:
                        print(f"  ❌ Invalid lot size - skipping")
                        continue
                    
                    # Calculate entry price
                    entry_price = engine.calculate_realistic_entry_price(
                        signal, current_bar['close'], config['typical_spread_pips'], 
                        config['pip_size'], config.get('slippage_pips', 0)
                    )
                    
                    print(f"  Entry price: {entry_price:.5f}")
                    
                    # Set SL/TP levels
                    if signal == 'BUY':
                        sl_price = entry_price - sl_distance
                        tp_price = entry_price + tp_distance
                    else:
                        sl_price = entry_price + sl_distance
                        tp_price = entry_price - tp_distance
                    
                    print(f"  SL: {sl_price:.5f}")
                    print(f"  TP: {tp_price:.5f}")
                    
                    # Check for emergency brake (from enhanced engine)
                    if config == InstrumentConfig.GOLD:
                        estimated_risk = sl_distance * lot_size * config['contract_size']
                        max_risk_dollar = capital * config.get('emergency_brake_percent', 0.05)
                        if estimated_risk > max_risk_dollar:
                            print(f"  🚨 Emergency brake triggered - skipping")
                            continue
                    
                    print(f"  ✅ Trade would be executed!")
                    
                    # For debugging, let's see if we can find the next exit
                    for j in range(i+1, len(df_with_signals)):
                        future_bar = df_with_signals.iloc[j]
                        
                        if signal == 'BUY':
                            if future_bar['low'] <= sl_price:
                                print(f"  📉 SL would hit at bar {j}")
                                break
                            elif future_bar['high'] >= tp_price:
                                print(f"  📈 TP would hit at bar {j}")
                                break
                        else:  # SELL
                            if future_bar['high'] >= sl_price:
                                print(f"  📉 SL would hit at bar {j}")
                                break
                            elif future_bar['low'] <= tp_price:
                                print(f"  📈 TP would hit at bar {j}")
                                break
                        
                        if j > i + 10:  # Only check next 10 bars
                            print(f"  ⏰ No exit in next 10 bars")
                            break
                    
                    trades.append({'signal': signal, 'entry': entry_price})
                    
                    if len(trades) >= 3:  # Limit debug output
                        break
        
        print(f"\\n📋 DEBUG SUMMARY:")
        print(f"Processed {len(trades)} potential trades")
        
        if len(trades) > 0:
            print(f"✅ Trade logic is working - trades should execute")
            print(f"❓ The issue might be in the actual enhanced_engine implementation")
        else:
            print(f"❌ No trades processed - issue in trade logic")
        
    except Exception as e:
        print(f"Error in debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_enhanced_backtest()