#!/usr/bin/env python3
"""
Simple isolated test to identify backtesting issues
Tests the exact scenario mentioned: Bollinger Squeeze on EURUSD
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_sample_eurusd_data():
    """Create realistic sample EURUSD data for testing"""
    # Generate 1000 hourly bars of realistic EURUSD data
    np.random.seed(42)  # For reproducible results
    
    # Base price around 1.1000
    base_price = 1.1000
    bars = 1000
    
    # Generate price changes with realistic volatility
    price_changes = np.random.normal(0, 0.0002, bars)  # ~20 pips average movement
    prices = [base_price]
    
    for change in price_changes:
        new_price = prices[-1] + change
        # Keep price within reasonable bounds (0.9000 to 1.3000)
        new_price = max(0.9000, min(1.3000, new_price))
        prices.append(new_price)
    
    prices = np.array(prices[1:])  # Remove initial price
    
    # Create OHLC data with realistic intrabar movements
    data = []
    for i, close in enumerate(prices):
        # Generate realistic OHLC from close price
        spread = np.random.uniform(0.00005, 0.00015)  # 0.5-1.5 pips spread
        
        high = close + np.random.uniform(0, 0.0005)   # Up to 5 pips above close
        low = close - np.random.uniform(0, 0.0005)    # Up to 5 pips below close
        open_price = low + (high - low) * np.random.random()
        
        time = datetime(2024, 1, 1) + timedelta(hours=i)
        
        data.append({
            'time': time,
            'open': round(open_price, 5),
            'high': round(high, 5),
            'low': round(low, 5),
            'close': round(close, 5),
            'volume': np.random.randint(1000, 10000)  # Random volume
        })
    
    df = pd.DataFrame(data)
    return df

def test_simple_calculations():
    """Test the basic calculations that might be causing issues"""
    print("🧮 Testing Basic Calculations")
    print("=" * 50)
    
    # Test position sizing calculation for EURUSD
    capital = 10000.0
    risk_percent = 1.0  # 1%
    atr_value = 0.0010   # 10 pips ATR (realistic for EURUSD)
    sl_atr_multiplier = 2.0
    contract_size = 100000  # Standard for forex majors
    
    print(f"Capital: ${capital:,.2f}")
    print(f"Risk: {risk_percent}%")
    print(f"ATR: {atr_value:.5f} ({atr_value * 10000:.1f} pips)")
    print(f"SL multiplier: {sl_atr_multiplier}x ATR")
    
    # Calculate position size
    amount_to_risk = capital * (risk_percent / 100.0)
    sl_distance = atr_value * sl_atr_multiplier
    risk_in_currency_per_lot = sl_distance * contract_size
    
    print(f"\nAmount to risk: ${amount_to_risk:.2f}")
    print(f"SL distance: {sl_distance:.5f} ({sl_distance * 10000:.1f} pips)")
    print(f"Risk per lot: ${risk_in_currency_per_lot:.2f}")
    
    if risk_in_currency_per_lot > 0:
        calculated_lot_size = amount_to_risk / risk_in_currency_per_lot
        final_lot_size = max(0.01, min(calculated_lot_size, 10.0))
        
        print(f"Calculated lot size: {calculated_lot_size:.4f}")
        print(f"Final lot size: {final_lot_size:.2f}")
        
        # Test a trade scenario
        entry_price = 1.1000
        if final_lot_size > 0:
            sl_price = entry_price - sl_distance
            tp_price = entry_price + (sl_distance * 2)  # 2:1 RR
            
            print(f"\nTrade scenario (BUY):")
            print(f"Entry: {entry_price:.5f}")
            print(f"SL: {sl_price:.5f}")
            print(f"TP: {tp_price:.5f}")
            
            # Test SL scenario
            profit_multiplier = final_lot_size * contract_size
            sl_profit = (sl_price - entry_price) * profit_multiplier
            tp_profit = (tp_price - entry_price) * profit_multiplier
            
            print(f"\nIf SL hit: ${sl_profit:.2f} (should be ~${-amount_to_risk:.2f})")
            print(f"If TP hit: ${tp_profit:.2f}")
            
            # Check if calculations make sense
            expected_loss = -amount_to_risk
            if abs(sl_profit - expected_loss) < 5:  # Within $5
                print("✅ Position sizing calculation looks correct")
                return True
            else:
                print(f"❌ Position sizing error! Expected loss: ${expected_loss:.2f}, Calculated: ${sl_profit:.2f}")
                return False
    else:
        print("❌ Risk calculation error!")
        return False

def test_strategy_with_sample_data():
    """Test strategy with our sample data"""
    print("\n📊 Testing Strategy with Sample Data")
    print("=" * 50)
    
    try:
        from core.strategies.bollinger_squeeze import BollingerSqueezeStrategy
        
        # Create sample data
        df = create_sample_eurusd_data()
        print(f"Created sample data: {len(df)} bars")
        print(f"Price range: {df['close'].min():.5f} to {df['close'].max():.5f}")
        
        # Test strategy
        class MockBot:
            def __init__(self):
                self.market_for_mt5 = "EURUSD"
                self.timeframe = "H1"
                self.tf_map = {}
        
        params = {
            'bb_length': 20,
            'bb_std': 2.0,
            'squeeze_window': 10,
            'squeeze_factor': 0.7,
            'rsi_period': 14
        }
        
        strategy_instance = BollingerSqueezeStrategy(bot_instance=MockBot(), params=params)
        df_with_signals = strategy_instance.analyze_df(df.copy())
        
        # Add ATR
        import pandas_ta as ta
        df_with_signals.ta.atr(length=14, append=True)
        df_with_signals.dropna(inplace=True)
        
        print(f"After analysis: {len(df_with_signals)} bars")
        
        # Check signals
        signal_counts = df_with_signals['signal'].value_counts()
        print(f"Signals: {dict(signal_counts)}")
        
        # Check ATR values
        atr_stats = df_with_signals['ATRr_14'].describe()
        print(f"ATR stats: min={atr_stats['min']:.6f}, max={atr_stats['max']:.6f}, mean={atr_stats['mean']:.6f}")
        
        return df_with_signals
        
    except ImportError as e:
        print(f"❌ Cannot import strategy: {e}")
        return None
    except Exception as e:
        print(f"❌ Error testing strategy: {e}")
        return None

def simulate_simple_backtest(df_with_signals):
    """Simulate a simple backtest manually to identify issues"""
    print("\n🔄 Simulating Simple Backtest")
    print("=" * 50)
    
    if df_with_signals is None:
        return
    
    # Parameters
    initial_capital = 10000.0
    capital = initial_capital
    risk_percent = 1.0
    sl_atr_multiplier = 2.0
    tp_atr_multiplier = 4.0
    contract_size = 100000
    
    trades = []
    equity_curve = [initial_capital]
    in_position = False
    
    print(f"Starting capital: ${capital:.2f}")
    print(f"Risk per trade: {risk_percent}%")
    
    trades_executed = 0
    
    for i in range(1, len(df_with_signals)):
        current_bar = df_with_signals.iloc[i]
        
        if capital <= 0:
            print("💀 Capital exhausted!")
            break
        
        if not in_position:
            signal = current_bar.get("signal", "HOLD")
            if signal in ['BUY', 'SELL']:
                trades_executed += 1
                entry_price = current_bar['close']
                atr_value = current_bar['ATRr_14']
                
                if atr_value > 0:
                    # Calculate position
                    amount_to_risk = capital * (risk_percent / 100.0)
                    sl_distance = atr_value * sl_atr_multiplier
                    risk_in_currency_per_lot = sl_distance * contract_size
                    
                    if risk_in_currency_per_lot > 0:
                        calculated_lot_size = amount_to_risk / risk_in_currency_per_lot
                        lot_size = max(0.01, min(calculated_lot_size, 10.0))
                        
                        # Set SL/TP
                        if signal == 'BUY':
                            sl_price = entry_price - sl_distance
                            tp_price = entry_price + (sl_distance * (tp_atr_multiplier / sl_atr_multiplier))
                        else:
                            sl_price = entry_price + sl_distance
                            tp_price = entry_price - (sl_distance * (tp_atr_multiplier / sl_atr_multiplier))
                        
                        print(f"\nTrade #{trades_executed}: {signal}")
                        print(f"  Entry: {entry_price:.5f}, Lot: {lot_size:.2f}")
                        print(f"  SL: {sl_price:.5f}, TP: {tp_price:.5f}")
                        print(f"  ATR: {atr_value:.5f}, Risk: ${amount_to_risk:.2f}")
                        
                        # Look ahead for exit (simplified)
                        exit_found = False
                        for j in range(i+1, min(i+50, len(df_with_signals))):  # Max 50 bars ahead
                            future_bar = df_with_signals.iloc[j]
                            
                            if signal == 'BUY':
                                if future_bar['low'] <= sl_price:
                                    exit_price = sl_price
                                    exit_reason = 'SL'
                                    exit_found = True
                                    break
                                elif future_bar['high'] >= tp_price:
                                    exit_price = tp_price
                                    exit_reason = 'TP'
                                    exit_found = True
                                    break
                            else:  # SELL
                                if future_bar['high'] >= sl_price:
                                    exit_price = sl_price
                                    exit_reason = 'SL'
                                    exit_found = True
                                    break
                                elif future_bar['low'] <= tp_price:
                                    exit_price = tp_price
                                    exit_reason = 'TP'
                                    exit_found = True
                                    break
                        
                        if exit_found:
                            # Calculate profit
                            profit_multiplier = lot_size * contract_size
                            if signal == 'BUY':
                                profit = (exit_price - entry_price) * profit_multiplier
                            else:
                                profit = (entry_price - exit_price) * profit_multiplier
                            
                            capital += profit
                            equity_curve.append(capital)
                            
                            print(f"  Exit: {exit_price:.5f} ({exit_reason}) | Profit: ${profit:.2f}")
                            print(f"  New capital: ${capital:.2f}")
                            
                            trades.append({
                                'signal': signal,
                                'entry': entry_price,
                                'exit': exit_price,
                                'profit': profit,
                                'reason': exit_reason
                            })
                            
                            if trades_executed >= 10:  # Limit to first 10 trades
                                break
    
    # Final results
    total_profit = capital - initial_capital
    winners = len([t for t in trades if t['profit'] > 0])
    losers = len(trades) - winners
    win_rate = (winners / len(trades) * 100) if trades else 0
    
    peak_capital = initial_capital
    max_drawdown = 0.0
    for equity in equity_curve:
        if equity > peak_capital:
            peak_capital = equity
        drawdown = (peak_capital - equity) / peak_capital if peak_capital > 0 else 0
        max_drawdown = max(max_drawdown, drawdown)
    
    print(f"\n📈 RESULTS SUMMARY:")
    print(f"Total trades: {len(trades)}")
    print(f"Final capital: ${capital:.2f}")
    print(f"Total profit: ${total_profit:.2f}")
    print(f"Win rate: {win_rate:.1f}%")
    print(f"Max drawdown: {max_drawdown*100:.1f}%")
    
    if max_drawdown > 0.5:  # > 50%
        print("❌ SEVERE DRAWDOWN DETECTED!")
        print("Possible causes:")
        print("- Position sizes too large")
        print("- SL/TP ratios incorrect") 
        print("- Strategy generating bad signals")
        print("- Market data issues")
        
        # Show losing trades
        losing_trades = [t for t in trades if t['profit'] < 0]
        if losing_trades:
            print(f"\nWorst losing trades:")
            worst_trades = sorted(losing_trades, key=lambda x: x['profit'])[:3]
            for i, trade in enumerate(worst_trades):
                print(f"  {i+1}. {trade['signal']}: ${trade['profit']:.2f}")
        
        return False
    else:
        print("✅ Drawdown within acceptable range")
        return True

def main():
    print("🔍 BACKTESTING ISSUE DIAGNOSIS")
    print("=" * 60)
    
    # Test 1: Basic calculations
    if not test_simple_calculations():
        print("\n❌ ISSUE FOUND: Basic position sizing calculations are wrong!")
        return
    
    print("\n" + "="*60)
    
    # Test 2: Strategy with sample data
    df_with_signals = test_strategy_with_sample_data()
    
    print("\n" + "="*60)
    
    # Test 3: Simple backtest simulation
    if not simulate_simple_backtest(df_with_signals):
        print("\n❌ ISSUE FOUND: Simulated backtest shows severe problems!")
    else:
        print("\n✅ Simulated backtest looks reasonable")
    
    print("\n📋 NEXT STEPS:")
    print("1. Check if the real backtesting engines use different parameters")
    print("2. Verify if enhanced engine spread costs are too high")
    print("3. Test with actual EURUSD data instead of simulated")
    print("4. Check if strategies are generating too many losing signals")

if __name__ == '__main__':
    main()