#!/usr/bin/env python3
"""
💰 Quick USD/IDR Test with XM
Perfect for Indonesian traders!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import MetaTrader5 as mt5
    
    def test_usdidr_with_xm():
        """Test USD/IDR trading once connected to XM"""
        print("💰 Testing USD/IDR Trading with XM")
        print("=" * 40)
        
        if not mt5.initialize():
            print("❌ MT5 not connected")
            return
        
        # Check if we're on XM
        account = mt5.account_info()
        if account:
            print(f"🏢 Broker: {account.server}")
            if 'XM' in account.server.upper():
                print("🎉 Connected to XM!")
            else:
                print("💡 Switch to XM for USD/IDR access")
        
        # Test USD/IDR availability
        usdidr_symbols = ['USDIDR', 'USD/IDR', 'USDID']
        found_usdidr = None
        
        for symbol in usdidr_symbols:
            if mt5.symbol_info(symbol):
                found_usdidr = symbol
                print(f"✅ Found: {symbol}")
                break
        
        if found_usdidr:
            # Get current rate
            tick = mt5.symbol_info_tick(found_usdidr)
            if tick:
                print(f"💱 Current Rate: {tick.bid:,.0f} IDR per USD")
                print(f"📊 Spread: {tick.ask - tick.bid:.0f} points")
                
                # Show trading opportunity
                print(f"\\n🎯 Trading Opportunity:")
                print(f"   Position Size: 0.1 lot = $1,000")
                print(f"   For 50 pips move: ~$50 profit")
                print(f"   In IDR: ~{50 * tick.bid:,.0f} IDR profit")
                
        else:
            print("⚠️ USD/IDR not found yet")
            print("💡 Make sure you're connected to XM server")
        
        mt5.shutdown()
    
    if __name__ == "__main__":
        test_usdidr_with_xm()
        
except ImportError:
    print("MetaTrader5 package needed: pip install MetaTrader5")