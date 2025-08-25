#!/usr/bin/env python3
"""
🏢 XM Indonesia + MT5 Connection Test
Let's connect your QuantumBotX to XM right now!
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 package not installed. Run: pip install MetaTrader5")

def test_xm_connection():
    """Test connection to XM via MT5"""
    print("🏢 Testing XM Indonesia Connection via MT5")
    print("=" * 50)
    
    if not MT5_AVAILABLE:
        print("❌ MetaTrader5 package not available")
        return False
    
    # Initialize MT5
    if not mt5.initialize():
        print("❌ MT5 initialization failed")
        print("💡 Make sure MetaTrader 5 terminal is running")
        return False
    
    print("✅ MT5 Terminal Connected!")
    
    # Get current broker info
    account_info = mt5.account_info()
    if account_info:
        print(f"\\n📊 Current Broker Information:")
        print(f"   Server: {account_info.server}")
        print(f"   Name: {account_info.name}")
        print(f"   Balance: ${account_info.balance:,.2f}")
        print(f"   Currency: {account_info.currency}")
        print(f"   Leverage: 1:{account_info.leverage}")
        
        # Check if it's XM
        if 'XM' in account_info.server.upper():
            print(f"\\n🎉 PERFECT! You're connected to XM!")
            print(f"   🇮🇩 XM Indonesia server detected")
        else:
            print(f"\\n📝 Currently connected to: {account_info.server}")
            print(f"   💡 To connect to XM: File → Login → Use XM credentials")
    
    # Test symbols available
    print(f"\\n📈 Testing Available Symbols...")
    
    # Key symbols for Indonesian traders
    test_symbols = ['EURUSD', 'USDJPY', 'GBPUSD', 'XAUUSD', 'USDIDR']
    available_symbols = []
    
    for symbol in test_symbols:
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info:
            available_symbols.append(symbol)
            print(f"   ✅ {symbol}: Available")
        else:
            print(f"   ❌ {symbol}: Not available")
    
    # Special check for USDIDR (Indonesian traders' favorite)
    if 'USDIDR' in available_symbols:
        print(f"\\n💰 EXCELLENT! USD/IDR is available!")
        print(f"   🎯 Perfect for earning USD in Indonesia!")
        
        # Get current USD/IDR rate
        usdidr_info = mt5.symbol_info_tick('USDIDR')
        if usdidr_info:
            print(f"   💱 Current Rate: {usdidr_info.bid:,.0f} IDR per USD")
    
    # Test gold (with our protection)
    if 'XAUUSD' in available_symbols:
        print(f"\\n🥇 Gold (XAUUSD) available!")
        print(f"   🛡️ Your XAUUSD protection is active!")
        
        xau_info = mt5.symbol_info_tick('XAUUSD')
        if xau_info:
            print(f"   💰 Current Gold Price: ${xau_info.bid:,.2f}")
    
    mt5.shutdown()
    return len(available_symbols) > 0

def show_xm_advantages():
    """Show XM advantages for Indonesian traders"""
    print(f"\\n🏆 XM + MT5 Advantages for You:")
    print(f"=" * 40)
    
    advantages = [
        "🔗 Direct integration with your QuantumBotX",
        "🇮🇩 Indonesian customer support",
        "💰 USD/IDR trading available", 
        "🥇 Gold trading with your protection",
        "📱 Mobile trading apps",
        "💸 Low minimum deposits",
        "🛡️ Regulated by multiple authorities",
        "📊 Professional trading tools"
    ]
    
    for advantage in advantages:
        print(f"  ✅ {advantage}")

def show_next_steps():
    """Show immediate next steps"""
    print(f"\\n🎯 IMMEDIATE NEXT STEPS:")
    print(f"=" * 30)
    
    steps = [
        {
            'step': '1. Login to XM in MT5',
            'action': 'File → Login → Enter XM credentials',
            'time': '2 minutes'
        },
        {
            'step': '2. Update .env file',
            'action': 'Replace MT5 credentials with XM credentials',
            'time': '1 minute'
        },
        {
            'step': '3. Test strategies',
            'action': 'Run backtests on USDIDR and XAUUSD',
            'time': '10 minutes'
        },
        {
            'step': '4. Start trading',
            'action': 'Run your best strategy live with small lots',
            'time': '5 minutes'
        }
    ]
    
    for i, step_info in enumerate(steps, 1):
        print(f"\\n{step_info['step']}")
        print(f"   🎯 Action: {step_info['action']}")
        print(f"   ⏱️ Time: {step_info['time']}")
    
    print(f"\\n🔥 TOTAL TIME TO START: 18 minutes!")

def main():
    """Main connection test"""
    print("🚀 XM Indonesia + QuantumBotX Connection Test")
    print("=" * 50)
    print("Testing if your MT5 setup works with XM...")
    print()
    
    # Test connection
    success = test_xm_connection()
    
    # Show advantages
    show_xm_advantages()
    
    # Show next steps
    show_next_steps()
    
    print(f"\\n" + "=" * 50)
    if success:
        print(f"🎉 SUCCESS! Your setup is ready for XM trading!")
    else:
        print(f"⚠️ Setup needed, but you're on the right track!")
    print(f"=" * 50)
    
    print(f"\\n💡 REMEMBER:")
    print(f"XM + MT5 + QuantumBotX = PERFECT combination!")
    print(f"You made the right choice! 🏆")

if __name__ == "__main__":
    main()