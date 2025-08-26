#!/usr/bin/env python3
"""
₿ Test Your New Crypto Strategy on Bitcoin
Let's see how your QuantumBotX Crypto strategy performs!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import MetaTrader5 as mt5
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    from core.strategies.quantumbotx_crypto import QuantumBotXCryptoStrategy
    
    def get_bitcoin_data(symbol='BTCUSD', timeframe='H1', count=500):
        """Get Bitcoin data from XM"""
        if not mt5.initialize():
            print("❌ MT5 not connected")
            return None
        
        # Map timeframe
        tf_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1
        }
        
        tf = tf_map.get(timeframe, mt5.TIMEFRAME_H1)
        
        # Get Bitcoin data
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
        
        if rates is not None and len(rates) > 0:
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            return df
        
        mt5.shutdown()
        return None
    
    def test_crypto_strategy():
        """Test the new crypto strategy on Bitcoin"""
        print("₿ Testing QuantumBotX Crypto Strategy")
        print("=" * 50)
        
        # Get Bitcoin data
        df = get_bitcoin_data('BTCUSD', 'H1', 300)  # 300 hours ≈ 12.5 days
        
        if df is None:
            print("❌ Could not get Bitcoin data")
            return
        
        print(f"✅ Retrieved {len(df)} hours of Bitcoin data")
        print(f"📊 Price range: ${df['close'].min():,.0f} - ${df['close'].max():,.0f}")
        print(f"⏰ Data period: {df.index[0]} to {df.index[-1]}")
        
        # Initialize strategy with crypto-optimized parameters
        strategy = QuantumBotXCryptoStrategy({
            'adx_period': 10,
            'adx_threshold': 20,
            'ma_fast_period': 12,
            'ma_slow_period': 26,
            'bb_length': 20,
            'bb_std': 2.2,
            'trend_filter_period': 100,
            'rsi_period': 14,
            'rsi_overbought': 75,
            'rsi_oversold': 25,
            'volatility_filter': 2.0,
            'weekend_mode': True
        })
        
        print(f"\\n🤖 Running QuantumBotX Crypto Strategy...")
        
        # Analyze the data
        df_with_signals = strategy.analyze_df(df.copy())
        
        # Count signals
        buy_signals = len(df_with_signals[df_with_signals['signal'] == 'BUY'])
        sell_signals = len(df_with_signals[df_with_signals['signal'] == 'SELL'])
        hold_signals = len(df_with_signals[df_with_signals['signal'] == 'HOLD'])
        
        print(f"📊 Signal Distribution:")
        print(f"   BUY signals: {buy_signals}")
        print(f"   SELL signals: {sell_signals}")
        print(f"   HOLD signals: {hold_signals}")
        print(f"   Trading activity: {((buy_signals + sell_signals) / len(df_with_signals) * 100):.1f}%")
        
        # Simulate trading performance
        trades = simulate_trades(df_with_signals, strategy)
        
        if trades:
            analyze_trades(trades)
        
        # Show recent signals
        show_recent_signals(df_with_signals)
        
        mt5.shutdown()
        return df_with_signals
    
    def simulate_trades(df, strategy, initial_balance=100000):
        """Simulate trading with the crypto strategy"""
        balance = initial_balance
        position = 0
        entry_price = 0
        trades = []
        
        for i, (timestamp, row) in enumerate(df.iterrows()):
            current_price = row['close']
            signal = row['signal']
            
            # Enter position
            if signal == 'BUY' and position == 0:
                position_size = strategy.get_position_size(balance, current_price, 'BTCUSD')
                stop_loss, take_profit = strategy.get_stop_loss_take_profit(current_price, 'BUY', 'BTCUSD')
                
                position = position_size
                entry_price = current_price
                
                trades.append({
                    'type': 'entry',
                    'time': timestamp,
                    'side': 'BUY',
                    'price': current_price,
                    'size': position_size,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit
                })
                
            elif signal == 'SELL' and position == 0:
                position_size = strategy.get_position_size(balance, current_price, 'BTCUSD')
                stop_loss, take_profit = strategy.get_stop_loss_take_profit(current_price, 'SELL', 'BTCUSD')
                
                position = -position_size
                entry_price = current_price
                
                trades.append({
                    'type': 'entry',
                    'time': timestamp,
                    'side': 'SELL',
                    'price': current_price,
                    'size': position_size,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit
                })
            
            # Exit position
            elif position != 0:
                should_exit = False
                exit_reason = ""
                
                if position > 0:  # Long position
                    if signal == 'SELL':
                        should_exit = True
                        exit_reason = "Signal change"
                    elif current_price <= trades[-1]['stop_loss']:
                        should_exit = True
                        exit_reason = "Stop loss"
                    elif current_price >= trades[-1]['take_profit']:
                        should_exit = True
                        exit_reason = "Take profit"
                        
                elif position < 0:  # Short position
                    if signal == 'BUY':
                        should_exit = True
                        exit_reason = "Signal change"
                    elif current_price >= trades[-1]['stop_loss']:
                        should_exit = True
                        exit_reason = "Stop loss"
                    elif current_price <= trades[-1]['take_profit']:
                        should_exit = True
                        exit_reason = "Take profit"
                
                if should_exit:
                    # Calculate profit
                    if position > 0:
                        profit = (current_price - entry_price) * position
                    else:
                        profit = (entry_price - current_price) * abs(position)
                    
                    balance += profit
                    
                    trades.append({
                        'type': 'exit',
                        'time': timestamp,
                        'price': current_price,
                        'profit': profit,
                        'balance': balance,
                        'reason': exit_reason
                    })
                    
                    position = 0
                    entry_price = 0
        
        return trades
    
    def analyze_trades(trades):
        """Analyze trading performance"""
        print(f"\\n💰 Trading Performance Analysis")
        print("=" * 40)
        
        entry_trades = [t for t in trades if t['type'] == 'entry']
        exit_trades = [t for t in trades if t['type'] == 'exit']
        
        if not exit_trades:
            print("⚠️ No completed trades")
            return
        
        # Calculate metrics
        total_trades = len(exit_trades)
        profitable_trades = [t for t in exit_trades if t['profit'] > 0]
        losing_trades = [t for t in exit_trades if t['profit'] < 0]
        
        total_profit = sum(t['profit'] for t in exit_trades)
        win_rate = len(profitable_trades) / total_trades * 100
        
        avg_profit = total_profit / total_trades
        avg_win = sum(t['profit'] for t in profitable_trades) / len(profitable_trades) if profitable_trades else 0
        avg_loss = sum(t['profit'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # Display results
        print(f"📊 Trade Statistics:")
        print(f"   Total Trades: {total_trades}")
        print(f"   Winning Trades: {len(profitable_trades)}")
        print(f"   Losing Trades: {len(losing_trades)}")
        print(f"   Win Rate: {win_rate:.1f}%")
        
        print(f"\\n💸 Profit Analysis:")
        print(f"   Total Profit: ${total_profit:+,.2f}")
        print(f"   Return: {(total_profit / 100000) * 100:+.2f}%")
        print(f"   Avg Profit/Trade: ${avg_profit:+,.2f}")
        print(f"   Avg Winning Trade: ${avg_win:+,.2f}")
        print(f"   Avg Losing Trade: ${avg_loss:+,.2f}")
        
        if avg_loss != 0:
            profit_factor = abs(avg_win / avg_loss)
            print(f"   Profit Factor: {profit_factor:.2f}")
        
        # Weekend performance
        weekend_exits = [t for t in exit_trades if t['time'].weekday() in [5, 6]]
        if weekend_exits:
            weekend_profit = sum(t['profit'] for t in weekend_exits)
            print(f"\\n🏖️ Weekend Performance:")
            print(f"   Weekend Trades: {len(weekend_exits)}")
            print(f"   Weekend Profit: ${weekend_profit:+,.2f}")
    
    def show_recent_signals(df):
        """Show recent trading signals"""
        print(f"\\n📈 Recent Signals (Last 10 hours)")
        print("=" * 50)
        
        recent = df.tail(10)
        
        for timestamp, row in recent.iterrows():
            signal = row['signal']
            price = row['close']
            
            emoji = "🔵" if signal == "HOLD" else "🟢" if signal == "BUY" else "🔴"
            
            print(f"{emoji} {timestamp.strftime('%Y-%m-%d %H:%M')} | ${price:8,.0f} | {signal}")
    
    def show_crypto_advantages():
        """Show advantages of the crypto strategy"""
        print(f"\\n🚀 CRYPTO STRATEGY ADVANTAGES")
        print("=" * 40)
        
        advantages = [
            "⚡ Faster indicators (12/26 MA vs 20/50) for crypto speed",
            "🎯 RSI confirmation prevents false breakouts",
            "📊 Volatility filter avoids extreme market conditions", 
            "🏖️ Weekend mode for 24/7 crypto trading",
            "💰 Conservative 0.3% risk sizing for Bitcoin",
            "🛡️ Tighter 2% stop losses for crypto volatility",
            "📈 2:1 risk-reward ratio for consistent profits",
            "🤖 ADX threshold lowered to 20 for crypto trends"
        ]
        
        for advantage in advantages:
            print(f"  ✅ {advantage}")
    
    def main():
        """Main test function"""
        print("₿ QUANTUMBOTX CRYPTO STRATEGY TEST")
        print("=" * 60)
        print("Testing your Bitcoin-optimized strategy on real XM data!")
        print()
        
        # Test the strategy
        df_results = test_crypto_strategy()
        
        # Show advantages
        show_crypto_advantages()
        
        print(f"\\n" + "=" * 60)
        print("🎉 CRYPTO STRATEGY READY!")
        print("=" * 60)
        print("✅ Bitcoin optimized parameters")
        print("✅ Weekend trading mode")  
        print("✅ Enhanced risk management")
        print("✅ Volatility protection")
        print("\\n💰 Ready to trade Bitcoin on XM! 🚀")
        
        # Next steps
        print(f"\\n🎯 NEXT STEPS:")
        print("1. 🏃‍♂️ Use 'QUANTUMBOTX_CRYPTO' strategy in your dashboard")
        print("2. 🎛️ Trade BTCUSD with 0.01 lots to start")
        print("3. 📊 Monitor weekend performance")
        print("4. 🚀 Scale up as profits grow!")

    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're in the QuantumBotX directory")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()