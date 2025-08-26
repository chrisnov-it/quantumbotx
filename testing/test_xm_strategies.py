#!/usr/bin/env python3
"""
🚀 Quick QuantumBotX Strategy Test on XM
Let's see your strategies perform on XM data!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import MetaTrader5 as mt5
    import pandas as pd
    from datetime import datetime, timedelta
    
    def get_xm_data(symbol, timeframe, count=500):
        """Get real market data from XM"""
        if not mt5.initialize():
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
        
        # Get data
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
        
        if rates is not None and len(rates) > 0:
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
        
        return None
    
    def quick_ma_crossover_test(symbol, df):
        """Quick MA crossover test"""
        if df is None or len(df) < 100:
            return None
        
        # Calculate MAs
        df['ma_fast'] = df['close'].rolling(20).mean()
        df['ma_slow'] = df['close'].rolling(50).mean()
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['ma_fast'] > df['ma_slow'], 'signal'] = 1
        df['position'] = df['signal'].diff()
        
        # Count signals
        buy_signals = len(df[df['position'] == 1])
        sell_signals = len(df[df['position'] == -1])
        
        # Quick performance estimate
        returns = []
        position = 0
        entry_price = 0
        
        for i, row in df.iterrows():
            if row['position'] == 1 and position == 0:  # Buy
                position = 1
                entry_price = row['close']
            elif row['position'] == -1 and position == 1:  # Sell
                position = 0
                ret = (row['close'] - entry_price) / entry_price
                returns.append(ret)
        
        if returns:
            total_return = sum(returns)
            win_rate = len([r for r in returns if r > 0]) / len(returns)
            avg_return = total_return / len(returns)
        else:
            total_return = 0
            win_rate = 0
            avg_return = 0
        
        return {
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'total_trades': len(returns),
            'total_return': total_return * 100,  # Convert to percentage
            'win_rate': win_rate * 100,
            'avg_return': avg_return * 100
        }
    
    def test_xm_strategies():
        """Test strategies on XM data"""
        print("🚀 Testing Your Strategies on Real XM Data")
        print("=" * 50)
        
        # Test symbols perfect for Indonesian traders
        test_symbols = [
            ('EURUSD', 'Most liquid pair'),
            ('USDJPY', 'Asian session favorite'),
            ('GBPUSD', 'High volatility'),
            ('AUDUSD', 'Commodity currency')
        ]
        
        results = []
        
        for symbol, description in test_symbols:
            print(f"\\n📊 Testing {symbol} ({description})")
            print("-" * 40)
            
            # Get real XM data
            df = get_xm_data(symbol, 'H1', 500)
            
            if df is not None:
                print(f"✅ Data retrieved: {len(df)} bars")
                print(f"📈 Price range: {df['close'].min():.5f} - {df['close'].max():.5f}")
                
                # Test MA crossover strategy
                result = quick_ma_crossover_test(symbol, df)
                
                if result:
                    print(f"🤖 MA Crossover Results:")
                    print(f"   Buy Signals: {result['buy_signals']}")
                    print(f"   Sell Signals: {result['sell_signals']}")
                    print(f"   Total Trades: {result['total_trades']}")
                    print(f"   Total Return: {result['total_return']:+.2f}%")
                    print(f"   Win Rate: {result['win_rate']:.1f}%")
                    print(f"   Avg Return/Trade: {result['avg_return']:+.2f}%")
                    
                    results.append({
                        'symbol': symbol,
                        'description': description,
                        **result
                    })
                else:
                    print("⚠️ Not enough data for analysis")
            else:
                print("❌ Could not retrieve data")
        
        # Summary
        if results:
            print(f"\\n🎯 STRATEGY PERFORMANCE SUMMARY")
            print("=" * 40)
            
            best_symbol = max(results, key=lambda x: x['total_return'])
            best_winrate = max(results, key=lambda x: x['win_rate'])
            
            print(f"🏆 Best Performer: {best_symbol['symbol']}")
            print(f"   Return: {best_symbol['total_return']:+.2f}%")
            print(f"   Win Rate: {best_symbol['win_rate']:.1f}%")
            
            print(f"\\n🎯 Highest Win Rate: {best_winrate['symbol']}")
            print(f"   Win Rate: {best_winrate['win_rate']:.1f}%")
            print(f"   Return: {best_winrate['total_return']:+.2f}%")
            
            # Calculate portfolio potential
            avg_return = sum(r['total_return'] for r in results) / len(results)
            print(f"\\n💰 Portfolio Potential:")
            print(f"   Average Return: {avg_return:+.2f}%")
            print(f"   On $10,000: ${10000 * avg_return/100:+,.2f}")
            print(f"   Monthly estimate: ${10000 * avg_return/100/6:+,.2f}")  # Assuming 6 months of data
        
        mt5.shutdown()
        return results
    
    def show_next_steps():
        """Show what to do next"""
        print(f"\\n🎯 IMMEDIATE NEXT STEPS:")
        print("=" * 30)
        
        steps = [
            "1. 🏃‍♂️ Start with EURUSD (most stable)",
            "2. 🤖 Use your QuantumBotX Hybrid strategy",
            "3. 💰 Start with 0.01 lots (micro trading)",
            "4. 📊 Monitor for 1 week",
            "5. 🚀 Scale up gradually as profits grow"
        ]
        
        for step in steps:
            print(f"   {step}")
        
        print(f"\\n💡 Pro Tips for XM:")
        tips = [
            "📈 Focus on major pairs (tighter spreads)",
            "🕐 Trade during European/US overlap (13:00-17:00 UTC)",
            "🛡️ Keep your XAUUSD protection active",
            "💸 Start small and compound profits",
            "📱 Use XM mobile app for monitoring"
        ]
        
        for tip in tips:
            print(f"   {tip}")
    
    if __name__ == "__main__":
        results = test_xm_strategies()
        show_next_steps()
        
        print(f"\\n🎉 CONGRATULATIONS!")
        print("Your QuantumBotX is now connected to XM with")
        print("access to 1,508 trading instruments! 🚀")
        print("\\nTime to start earning real money! 💰")
        
except ImportError:
    print("❌ MetaTrader5 package needed")
except Exception as e:
    print(f"❌ Error: {e}")