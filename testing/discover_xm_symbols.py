#!/usr/bin/env python3
"""
🔍 XM Symbol Discovery - Find All Available Trading Opportunities
Let's see what markets you can trade with XM!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import MetaTrader5 as mt5
    
    def discover_xm_symbols():
        """Discover all available symbols on XM"""
        print("🔍 Discovering XM Trading Opportunities")
        print("=" * 50)
        
        if not mt5.initialize():
            print("❌ MT5 not connected")
            return
        
        # Get account info
        account = mt5.account_info()
        if account:
            print(f"🏢 Connected to: {account.server}")
            print(f"💰 Demo Balance: ${account.balance:,.2f}")
            print(f"⚡ Leverage: 1:{account.leverage}")
        
        # Get all symbols
        all_symbols = mt5.symbols_get()
        if not all_symbols:
            print("❌ No symbols found")
            mt5.shutdown()
            return
        
        print(f"\\n📊 Total Symbols Available: {len(all_symbols)}")
        
        # Categorize symbols
        categories = {
            'Forex': [],
            'Indices': [],
            'Commodities': [],
            'Metals': [],
            'Crypto': [],
            'Indonesian': [],
            'Other': []
        }
        
        for symbol in all_symbols:
            name = symbol.name
            
            # Categorize
            if any(x in name for x in ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']):
                if len(name) == 6 and name[3:] != name[:3]:  # Standard forex pair
                    categories['Forex'].append(name)
                elif 'IDR' in name:
                    categories['Indonesian'].append(name)
                else:
                    categories['Other'].append(name)
            elif any(x in name for x in ['US30', 'SPX', 'NAS', 'UK100', 'GER', 'JPN', 'AUS']):
                categories['Indices'].append(name)
            elif any(x in name for x in ['XAU', 'XAG', 'XPD', 'XPT', 'GOLD', 'SILVER']):
                categories['Metals'].append(name)
            elif any(x in name for x in ['OIL', 'BRENT', 'NGAS', 'COCOA', 'COFFEE', 'SUGAR']):
                categories['Commodities'].append(name)
            elif any(x in name for x in ['BTC', 'ETH', 'LTC', 'XRP', 'ADA']):
                categories['Crypto'].append(name)
            elif 'IDR' in name:
                categories['Indonesian'].append(name)
            else:
                categories['Other'].append(name)
        
        # Display categories
        for category, symbols in categories.items():
            if symbols:
                print(f"\\n📈 {category} ({len(symbols)} instruments):")
                for symbol in sorted(symbols)[:10]:  # Show first 10
                    symbol_info = mt5.symbol_info(symbol)
                    if symbol_info:
                        # Get current price
                        tick = mt5.symbol_info_tick(symbol)
                        if tick:
                            print(f"   ✅ {symbol:15} | Bid: {tick.bid:>10.5f} | Ask: {tick.ask:>10.5f}")
                        else:
                            print(f"   ✅ {symbol:15} | Available")
                
                if len(symbols) > 10:
                    print(f"   ... and {len(symbols) - 10} more {category.lower()} instruments")
        
        # Special focus on Indonesian opportunities
        print(f"\\n🇮🇩 INDONESIAN MARKET FOCUS:")
        print(f"=" * 40)
        
        indonesian_symbols = categories['Indonesian']
        if indonesian_symbols:
            print(f"🎉 Found {len(indonesian_symbols)} IDR-related instruments!")
            for symbol in indonesian_symbols:
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    print(f"   💰 {symbol}: {tick.bid:,.0f} IDR")
        else:
            print("⚠️ No IDR pairs found in this account type")
            print("💡 Some XM accounts may have different symbol availability")
        
        # Check for gold (with our protection)
        gold_symbols = categories['Metals']
        if gold_symbols:
            print(f"\\n🥇 GOLD TRADING (With Your Protection!):")
            print(f"=" * 45)
            for symbol in gold_symbols:
                if 'XAU' in symbol or 'GOLD' in symbol:
                    tick = mt5.symbol_info_tick(symbol)
                    if tick:
                        print(f"   🛡️ {symbol}: ${tick.bid:,.2f} (PROTECTED)")
        
        # Recommend best pairs for Indonesian traders
        print(f"\\n🎯 RECOMMENDED FOR INDONESIAN TRADERS:")
        print(f"=" * 50)
        
        recommendations = [
            ('EURUSD', 'Most liquid, good for learning'),
            ('USDJPY', 'Asian session favorite'),
            ('GBPUSD', 'High volatility, good profits'),
            ('AUDUSD', 'Commodity currency, good trends'),
            ('XAUUSD', 'Gold - perfect with your protection')
        ]
        
        for symbol, reason in recommendations:
            if symbol in [s.name for s in all_symbols]:
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    print(f"   ✅ {symbol:8} | {tick.bid:>8.5f} | {reason}")
                else:
                    print(f"   ✅ {symbol:8} | Available   | {reason}")
            else:
                print(f"   ❌ {symbol:8} | Not available")
        
        mt5.shutdown()
        return categories

    def test_your_best_strategy():
        """Quick test of your best strategy on XM"""
        print(f"\\n🤖 Quick Strategy Test on XM")
        print(f"=" * 35)
        
        print("🎯 Recommended Next Steps:")
        print("1. Test EURUSD with your QuantumBotX Hybrid strategy")
        print("2. Try USDJPY (good for Asian timezone)")
        print("3. Test XAUUSD with your perfect protection")
        print("4. Look for IDR pairs in Market Watch")
        
        print(f"\\n💡 To add more symbols:")
        print("   Right-click Market Watch → Show All")
        print("   Look for USDIDR, EURIDR, or similar")

    if __name__ == "__main__":
        categories = discover_xm_symbols()
        test_your_best_strategy()
        
        print(f"\\n🎉 CONGRATULATIONS!")
        print(f"You now have access to professional-grade")
        print(f"trading instruments via XM! 🚀")
        
except ImportError:
    print("MetaTrader5 package needed")