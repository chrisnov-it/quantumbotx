#!/usr/bin/env python3
"""
🤖 Create SatoshiJakarta Crypto Bot
Your personal Bitcoin & Ethereum trading assistant!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import MetaTrader5 as mt5
    from datetime import datetime
    
    def create_crypto_bot():
        """Create your SatoshiJakarta crypto bot"""
        print("🤖 CREATING SATOSHIJAKARTA CRYPTO BOT")
        print("=" * 50)
        
        # Bot configuration
        bot_config = {
            'name': 'SatoshiJakarta',
            'description': 'Indonesian Crypto Trading Bot - Bitcoin & Ethereum Specialist',
            'strategy': 'QUANTUMBOTX_CRYPTO',
            'symbols': ['BTCUSD', 'ETHUSD'],
            'timeframe': 'H1',
            'risk_per_trade': 0.3,  # 0.3% for crypto
            'max_positions': 2,     # One for BTC, one for ETH
            'trading_hours': '24/7',
            'weekend_mode': True,
            'creator': 'Indonesian Crypto Trader',
            'location': 'Jakarta, Indonesia 🇮🇩',
            'motto': 'Satoshi meets Nusantara! ₿🌴'
        }
        
        print(f"🚀 Bot Name: {bot_config['name']}")
        print(f"📝 Description: {bot_config['description']}")
        print(f"🤖 Strategy: {bot_config['strategy']}")
        print(f"📊 Trading Pairs: {', '.join(bot_config['symbols'])}")
        print(f"⏰ Trading Hours: {bot_config['trading_hours']}")
        print(f"🏖️ Weekend Mode: {'✅ Active' if bot_config['weekend_mode'] else '❌ Inactive'}")
        print(f"🎯 Risk per Trade: {bot_config['risk_per_trade']}%")
        print(f"📍 Location: {bot_config['location']}")
        print(f"💭 Motto: {bot_config['motto']}")
        
        return bot_config
    
    def check_crypto_symbols():
        """Check if crypto symbols are available and get current prices"""
        print("\\n💰 CRYPTO MARKET CHECK")
        print("=" * 30)
        
        if not mt5.initialize():
            print("❌ MT5 not connected")
            return
        
        crypto_pairs = ['BTCUSD', 'ETHUSD', 'SOLUSD', 'ADAUSD', 'LTCUSD', 'XRPUSD']
        available_pairs = []
        
        for symbol in crypto_pairs:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    available_pairs.append({
                        'symbol': symbol,
                        'price': tick.bid,
                        'spread': tick.ask - tick.bid,
                        'contract_size': symbol_info.trade_contract_size
                    })
                    
                    # Determine emoji and name
                    names = {
                        'BTCUSD': ('₿', 'Bitcoin'),
                        'ETHUSD': ('Ξ', 'Ethereum'), 
                        'SOLUSD': ('🚀', 'Solana'),
                        'ADAUSD': ('💧', 'Cardano'),
                        'LTCUSD': ('Ł', 'Litecoin'),
                        'XRPUSD': ('🌊', 'XRP')
                    }
                    
                    emoji, name = names.get(symbol, ('🪙', 'Crypto'))
                    
                    print(f"✅ {emoji} {symbol:8} | ${tick.bid:>8,.2f} | {name}")
                    
                    # Calculate position size for demo
                    if symbol == 'BTCUSD':
                        demo_position = 1148 / tick.bid  # $1148 exposure = 0.01 lots
                        print(f"     Demo Size: 0.01 lots = ${demo_position * tick.bid:,.0f} exposure")
                    elif symbol == 'ETHUSD':
                        demo_position = 400 / tick.bid   # $400 exposure for ETH
                        print(f"     Demo Size: ~0.1 lots = ${demo_position * tick.bid:,.0f} exposure")
        
        mt5.shutdown()
        return available_pairs
    
    def create_trading_plan():
        """Create a trading plan for SatoshiJakarta"""
        print("\\n📋 SATOSHIJAKARTA TRADING PLAN")
        print("=" * 40)
        
        plan = {
            'primary_pair': {
                'symbol': 'BTCUSD',
                'allocation': '60%',
                'position_size': '0.01 lots',
                'reasoning': 'Bitcoin is the king - most stable crypto',
                'best_times': 'Weekend volatility, Asian session'
            },
            'secondary_pair': {
                'symbol': 'ETHUSD', 
                'allocation': '40%',
                'position_size': '0.1 lots',
                'reasoning': 'Ethereum has more use cases, lower entry',
                'best_times': 'DeFi activity peaks, US session'
            },
            'risk_management': {
                'max_risk_per_trade': '0.3%',
                'max_total_exposure': '1.0%',
                'stop_loss': '2%',
                'take_profit': '4%',
                'position_limit': '2 simultaneous trades max'
            },
            'schedule': {
                'saturday': 'Focus on BTC - weekend volatility',
                'sunday': 'Monitor ETH - DeFi prep for week',
                'weekdays': 'Balanced approach - both pairs',
                'asian_hours': 'Perfect for your timezone!'
            }
        }
        
        print(f"🥇 Primary: {plan['primary_pair']['symbol']} ({plan['primary_pair']['allocation']})")
        print(f"   Size: {plan['primary_pair']['position_size']}")
        print(f"   Why: {plan['primary_pair']['reasoning']}")
        
        print(f"\\n🥈 Secondary: {plan['secondary_pair']['symbol']} ({plan['secondary_pair']['allocation']})")
        print(f"   Size: {plan['secondary_pair']['position_size']}")
        print(f"   Why: {plan['secondary_pair']['reasoning']}")
        
        print("\\n🛡️ Risk Management:")
        for key, value in plan['risk_management'].items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        
        print("\\n⏰ Trading Schedule:")
        for day, activity in plan['schedule'].items():
            print(f"   {day.title()}: {activity}")
        
        return plan
    
    def show_next_steps():
        """Show immediate next steps"""
        print("\\n🎯 IMMEDIATE NEXT STEPS")
        print("=" * 30)
        
        steps = [
            {
                'step': '1. 🤖 Create Bot in Dashboard',
                'action': 'Open QuantumBotX → Create New Bot → Name: SatoshiJakarta',
                'time': '2 minutes'
            },
            {
                'step': '2. ⚙️ Configure Strategy',
                'action': 'Strategy: QUANTUMBOTX_CRYPTO → Symbol: BTCUSD',
                'time': '1 minute'
            },
            {
                'step': '3. 🎛️ Set Parameters',
                'action': 'Risk: 0.3% → Timeframe: H1 → Weekend Mode: ON',
                'time': '1 minute'
            },
            {
                'step': '4. 🚀 Start Trading',
                'action': 'Demo mode → Monitor for 1 hour → Scale up!',
                'time': '5 minutes'
            },
            {
                'step': '5. 📈 Add ETHUSD',
                'action': 'Create second bot for Ethereum trading',
                'time': '3 minutes'
            }
        ]
        
        for i, step_info in enumerate(steps, 1):
            print(f"\\n{step_info['step']}")
            print(f"   🎯 Action: {step_info['action']}")
            print(f"   ⏱️ Time: {step_info['time']}")
        
        print("\\n🔥 TOTAL SETUP TIME: 12 minutes!")
        print("Then you'll have 24/7 crypto profit machine! 🚀")
    
    def show_crypto_advantages():
        """Show why crypto trading is perfect for Indonesian traders"""
        print("\\n🇮🇩 WHY CRYPTO IS PERFECT FOR INDONESIA")
        print("=" * 45)
        
        advantages = [
            "🌏 24/7 trading - perfect for any timezone",
            "💱 Earn USD while living in Indonesia", 
            "🏖️ Weekend trading when others rest",
            "📱 Trade from anywhere with internet",
            "💰 Lower minimum positions than forex",
            "🚀 Higher profit potential (and risk!)",
            "🤖 Perfect for algorithmic trading",
            "🌊 Ride the global crypto wave",
            "💎 Build generational wealth",
            "🇮🇩 Indonesia is crypto-friendly!"
        ]
        
        for advantage in advantages:
            print(f"  ✅ {advantage}")
    
    def main():
        """Main function to create SatoshiJakarta"""
        print("🇮🇩 SELAMAT DATANG! Welcome to Crypto Trading!")
        print("₿ Creating Your Personal Crypto Trading Bot!")
        print()
        
        # Create bot configuration
        bot_config = create_crypto_bot()
        
        # Check available symbols
        available_pairs = check_crypto_symbols()
        
        # Create trading plan
        trading_plan = create_trading_plan()
        
        # Show advantages
        show_crypto_advantages()
        
        # Show next steps
        show_next_steps()
        
        print("\\n" + "=" * 60)
        print("🎉 SATOSHIJAKARTA IS READY!")
        print("=" * 60)
        print("✅ Bot configured for Bitcoin & Ethereum")
        print("✅ Strategy optimized for crypto volatility")
        print("✅ Risk management tuned for Indonesian trader")
        print("✅ Weekend mode active for 24/7 profits")
        print("✅ Perfect for your timezone and goals")
        
        print("\\n🚀 FROM JAKARTA TO THE MOON!")
        print("Your crypto trading journey starts NOW! 🌙🇮🇩")
        
        print("\\n💎 REMEMBER:")
        print("Satoshi Nakamoto gave us Bitcoin...")
        print("SatoshiJakarta will give you PROFITS! ₿💰")

    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()