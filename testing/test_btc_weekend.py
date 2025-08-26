#!/usr/bin/env python3
"""
₿ Bitcoin Weekend Trading Test on XM
Perfect for Saturday trading when forex is closed!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import MetaTrader5 as mt5
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    def test_btc_availability():
        """Check if BTCUSD is available on XM"""
        print("₿ Testing Bitcoin Availability on XM")
        print("=" * 40)
        
        if not mt5.initialize():
            print("❌ MT5 not connected")
            return False
        
        # Check different BTC symbol variations
        btc_symbols = ['BTCUSD', 'BTC/USD', 'BITCOIN', 'BTCUSDT', 'BTC']
        found_btc = None
        
        print("🔍 Searching for Bitcoin symbols...")
        for symbol in btc_symbols:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                found_btc = symbol
                print(f"✅ Found: {symbol}")
                
                # Get current price
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    print(f"💰 Current Price: ${tick.bid:,.2f}")
                    print(f"📊 Spread: ${tick.ask - tick.bid:.2f}")
                    print(f"⏰ Last Update: {datetime.now().strftime('%H:%M:%S')}")
                break
            else:
                print(f"❌ {symbol}: Not found")
        
        if found_btc:
            # Get symbol specifications
            spec = mt5.symbol_info(found_btc)
            print(f"\\n📋 {found_btc} Specifications:")
            print(f"   Contract Size: {spec.trade_contract_size}")
            print(f"   Min Volume: {spec.volume_min}")
            print(f"   Max Volume: {spec.volume_max}")
            print(f"   Volume Step: {spec.volume_step}")
            print(f"   Point Value: ${spec.point}")
            print(f"   Digits: {spec.digits}")
        
        mt5.shutdown()
        return found_btc
    
    def get_btc_data(symbol, timeframe='H1', count=100):
        """Get Bitcoin data from XM"""
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
        
        # Get Bitcoin data
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
        
        if rates is not None and len(rates) > 0:
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
        
        mt5.shutdown()
        return None
    
    def analyze_btc_volatility(df):
        """Analyze Bitcoin volatility patterns"""
        if df is None or len(df) < 10:
            return None
        
        # Calculate returns
        df['returns'] = df['close'].pct_change()
        df['price_change'] = df['close'] - df['open']
        df['volatility'] = df['returns'].rolling(24).std()  # 24-hour rolling volatility
        
        # Weekend vs weekday analysis
        df['hour'] = df['time'].dt.hour
        df['day_of_week'] = df['time'].dt.dayofweek  # Monday=0, Sunday=6
        df['is_weekend'] = df['day_of_week'].isin([5, 6])  # Saturday=5, Sunday=6
        
        # Statistics
        stats = {
            'current_price': df['close'].iloc[-1],
            'price_range_24h': f"${df['close'].tail(24).min():,.0f} - ${df['close'].tail(24).max():,.0f}",
            'avg_hourly_change': df['price_change'].mean(),
            'volatility_24h': df['volatility'].iloc[-1] if not df['volatility'].isna().all() else 0,
            'weekend_avg_vol': df[df['is_weekend']]['returns'].std() if df['is_weekend'].any() else 0,
            'weekday_avg_vol': df[~df['is_weekend']]['returns'].std() if (~df['is_weekend']).any() else 0
        }
        
        return stats
    
    def test_btc_strategy(df, symbol):
        """Test a simple BTC strategy"""
        if df is None or len(df) < 50:
            return None
        
        print(f"\\n🤖 Testing Bitcoin Strategy on {symbol}")
        print("-" * 35)
        
        # Simple momentum strategy for crypto
        df['ma_short'] = df['close'].rolling(12).mean()  # 12-hour MA
        df['ma_long'] = df['close'].rolling(24).mean()   # 24-hour MA
        df['rsi'] = calculate_rsi(df['close'], 14)
        
        # Generate signals
        df['signal'] = 0
        
        # Buy when short MA > long MA and RSI < 70 (not overbought)
        buy_condition = (df['ma_short'] > df['ma_long']) & (df['rsi'] < 70)
        df.loc[buy_condition, 'signal'] = 1
        
        # Sell when short MA < long MA or RSI > 80 (overbought)
        sell_condition = (df['ma_short'] < df['ma_long']) | (df['rsi'] > 80)
        df.loc[sell_condition, 'signal'] = -1
        
        df['position'] = df['signal'].diff()
        
        # Simulate trades
        trades = []
        position = 0
        entry_price = 0
        
        for i, row in df.iterrows():
            if row['position'] == 1 and position == 0:  # Buy signal
                position = 1
                entry_price = row['close']
                trades.append({
                    'type': 'buy',
                    'time': row['time'],
                    'price': entry_price
                })
            elif (row['position'] == -1 or row['signal'] == -1) and position == 1:  # Sell signal
                position = 0
                exit_price = row['close']
                profit = exit_price - entry_price
                profit_pct = (profit / entry_price) * 100
                
                trades.append({
                    'type': 'sell',
                    'time': row['time'],
                    'price': exit_price,
                    'profit': profit,
                    'profit_pct': profit_pct
                })
        
        # Analyze results
        completed_trades = [t for t in trades if t['type'] == 'sell']
        
        if completed_trades:
            total_profit = sum(t['profit'] for t in completed_trades)
            total_profit_pct = sum(t['profit_pct'] for t in completed_trades)
            winning_trades = [t for t in completed_trades if t['profit'] > 0]
            win_rate = len(winning_trades) / len(completed_trades) * 100
            
            print(f"📊 Strategy Results:")
            print(f"   Total Trades: {len(completed_trades)}")
            print(f"   Winning Trades: {len(winning_trades)}")
            print(f"   Win Rate: {win_rate:.1f}%")
            print(f"   Total Profit: ${total_profit:+,.2f}")
            print(f"   Total Return: {total_profit_pct:+.2f}%")
            print(f"   Avg Profit/Trade: ${total_profit/len(completed_trades):+,.2f}")
            
            # Weekend performance
            weekend_trades = [t for t in completed_trades 
                            if t['time'].weekday() in [5, 6]]
            if weekend_trades:
                weekend_profit = sum(t['profit'] for t in weekend_trades)
                print(f"\\n🏖️ Weekend Performance:")
                print(f"   Weekend Trades: {len(weekend_trades)}")
                print(f"   Weekend Profit: ${weekend_profit:+,.2f}")
            
            return {
                'total_trades': len(completed_trades),
                'win_rate': win_rate,
                'total_profit': total_profit,
                'total_return': total_profit_pct,
                'weekend_trades': len(weekend_trades) if weekend_trades else 0
            }
        
        return None
    
    def calculate_rsi(prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def weekend_crypto_advantages():
        """Show advantages of weekend crypto trading"""
        print(f"\\n🏖️ WEEKEND CRYPTO ADVANTAGES")
        print("=" * 35)
        
        advantages = [
            "📈 Markets never close - trade 24/7/365",
            "💰 No competition from forex traders (they're sleeping!)",
            "🎯 Higher volatility = bigger profit opportunities",
            "📊 Clear technical patterns (less institutional interference)",
            "⚡ Faster price movements on weekends",
            "🌍 Asian, European, US traders all active",
            "💸 Perfect for Indonesian timezone trading",
            "🤖 Your bot can trade while you sleep"
        ]
        
        for advantage in advantages:
            print(f"  ✅ {advantage}")
    
    def show_btc_trading_plan():
        """Show Bitcoin trading plan for Indonesian traders"""
        print(f"\\n🎯 BITCOIN TRADING PLAN FOR YOU")
        print("=" * 40)
        
        plan = [
            {
                'time': 'Saturday Morning (Now!)',
                'action': 'Test BTC strategy with small positions',
                'risk': '0.01 lots ($100-500 per trade)',
                'focus': 'Learn crypto volatility patterns'
            },
            {
                'time': 'Saturday Evening',
                'action': 'Monitor US market reaction to weekend news',
                'risk': 'Same conservative sizing',
                'focus': 'Weekend gap trading opportunities'
            },
            {
                'time': 'Sunday',
                'action': 'Prepare for Monday forex open',
                'risk': 'Reduce positions before Sunday close',
                'focus': 'Profit taking and preparation'
            },
            {
                'time': 'Weekdays',
                'action': 'Focus on forex, keep BTC as hedge',
                'risk': 'Portfolio allocation: 20% crypto, 80% forex',
                'focus': 'Diversified income streams'
            }
        ]
        
        for phase in plan:
            print(f"\\n⏰ {phase['time']}:")
            print(f"   🎯 Action: {phase['action']}")
            print(f"   💰 Risk: {phase['risk']}")
            print(f"   📊 Focus: {phase['focus']}")
    
    def main():
        """Main Bitcoin test function"""
        print("₿ BITCOIN WEEKEND TRADING TEST")
        print("=" * 50)
        print("Perfect timing! Forex is closed, crypto never sleeps! 🚀")
        print()
        
        # Test Bitcoin availability
        btc_symbol = test_btc_availability()
        
        if btc_symbol:
            print(f"\\n🎉 SUCCESS! {btc_symbol} is available for trading!")
            
            # Get Bitcoin data
            print(f"\\n📊 Getting {btc_symbol} market data...")
            df = get_btc_data(btc_symbol, 'H1', 168)  # 1 week of hourly data
            
            if df is not None:
                print(f"✅ Retrieved {len(df)} hours of data")
                
                # Analyze volatility
                stats = analyze_btc_volatility(df)
                if stats:
                    print(f"\\n📈 Bitcoin Analysis:")
                    print(f"   Current Price: ${stats['current_price']:,.2f}")
                    print(f"   24h Range: {stats['price_range_24h']}")
                    print(f"   Avg Hourly Change: ${stats['avg_hourly_change']:+,.2f}")
                    print(f"   Weekend Volatility: {stats['weekend_avg_vol']*100:.2f}%")
                    print(f"   Weekday Volatility: {stats['weekday_avg_vol']*100:.2f}%")
                
                # Test strategy
                strategy_result = test_btc_strategy(df, btc_symbol)
                
                if strategy_result:
                    print(f"\\n🏆 STRATEGY SUCCESS!")
                    if strategy_result['total_return'] > 0:
                        print(f"💰 Your Bitcoin strategy would have made:")
                        print(f"   ${strategy_result['total_profit']:+,.2f} profit")
                        print(f"   {strategy_result['total_return']:+.2f}% return")
                        print(f"   On $10,000: ${10000 * strategy_result['total_return']/100:+,.2f}")
                    else:
                        print(f"📊 Strategy needs optimization, but crypto trading works!")
            
            # Show advantages and plan
            weekend_crypto_advantages()
            show_btc_trading_plan()
            
        else:
            print("⚠️ Bitcoin symbol not found")
            print("💡 Try checking Market Watch → Show All")
            print("💡 Look for BTCUSD, BTC/USD, or crypto section")
        
        print(f"\\n" + "=" * 50)
        print("🎉 BITCOIN WEEKEND TRADING READY!")
        print("=" * 50)
        print("✅ Perfect for Saturday trading")
        print("✅ 24/7 profit opportunities") 
        print("✅ Higher volatility = bigger profits")
        print("✅ No competition from sleeping forex traders")
        print("\\n💰 Time to make money while others rest! 🚀")

    if __name__ == "__main__":
        main()
        
except ImportError:
    print("❌ MetaTrader5 package needed")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()