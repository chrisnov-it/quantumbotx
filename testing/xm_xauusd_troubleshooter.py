#!/usr/bin/env python3
"""
🥇 XM Global XAUUSD Troubleshooter
Khusus untuk mengatasi masalah XAUUSD di XM Global MT5
"""

import sys
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import MetaTrader5 as mt5
    from core.utils.mt5 import find_mt5_symbol, initialize_mt5
    MT5_AVAILABLE = True
except ImportError as e:
    MT5_AVAILABLE = False
    print(f"⚠️ Import error: {e}")

def connect_to_xm_global():
    """Connect specifically to XM Global with credentials from .env"""
    print("🏢 Connecting to XM Global MT5...")
    print("-" * 40)
    
    try:
        ACCOUNT = int(os.getenv('MT5_LOGIN'))
        PASSWORD = os.getenv('MT5_PASSWORD') 
        SERVER = os.getenv('MT5_SERVER')
        
        print(f"📊 Connection Details:")
        print(f"   Account: {ACCOUNT}")
        print(f"   Server: {SERVER}")
        print(f"   Password: {'*' * len(PASSWORD)}")
        
        success = initialize_mt5(ACCOUNT, PASSWORD, SERVER)
        
        if success:
            print("✅ XM Global connection successful!")
            return True
        else:
            print("❌ XM Global connection failed!")
            print("💡 Check your MT5 terminal is open and logged in")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def analyze_xm_xauusd():
    """Analyze XAUUSD availability on XM Global specifically"""
    print("\\n🔍 XM Global XAUUSD Analysis")
    print("-" * 40)
    
    # Get account info to confirm XM connection
    account_info = mt5.account_info()
    if not account_info:
        print("❌ Cannot get account info")
        return False
    
    print(f"✅ Connected to: {account_info.server}")
    print(f"   Company: {account_info.company}")
    print(f"   Currency: {account_info.currency}")
    
    # XM Global specific XAUUSD variants
    xm_gold_symbols = [
        'GOLD',          # Most common on XM
        'XAUUSD',        # Standard name
        'XAU/USD',       # Alternative format
        'GOLD.',         # With suffix
        'GOLDmicro',     # Micro lots
        'GOLDZ',         # XM variant
        'XAUUSDm'        # Micro version
    ]
    
    print("\\n🥇 Testing XM Gold Symbol Variants:")
    found_symbols = []
    
    for symbol in xm_gold_symbols:
        print(f"\\n   Testing: {symbol}")
        
        # Check if symbol exists
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info:
            found_symbols.append(symbol)
            print(f"   ✅ {symbol} EXISTS!")
            print(f"      Visible: {symbol_info.visible}")
            print(f"      Path: {symbol_info.path}")
            print(f"      Digits: {symbol_info.digits}")
            print(f"      Point: {symbol_info.point}")
            
            # Try to get current price
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                print(f"      💰 Current Price: ${tick.bid:.2f}")
                print(f"      📊 Spread: {(tick.ask - tick.bid):.2f}")
            
            # Try to activate if not visible
            if not symbol_info.visible:
                print(f"      🔄 Trying to activate...")
                success = mt5.symbol_select(symbol, True)
                if success:
                    print(f"      ✅ Successfully activated!")
                else:
                    print(f"      ❌ Activation failed")
        else:
            print(f"   ❌ {symbol} not found")
    
    if found_symbols:
        print(f"\\n🎉 Found {len(found_symbols)} gold symbols on XM!")
        return found_symbols[0]  # Return the first working symbol
    else:
        print("\\n❌ No gold symbols found!")
        return None

def xm_market_watch_guide():
    """Step-by-step guide for XM Market Watch"""
    print("\\n📋 XM Global Market Watch Setup Guide")
    print("=" * 50)
    
    steps = [
        {
            'step': 'Step 1: Open Market Watch',
            'action': 'Look at the left panel in MT5',
            'details': 'Market Watch window should be visible'
        },
        {
            'step': 'Step 2: Right-click Market Watch',
            'action': 'Right-click anywhere in Market Watch area',
            'details': 'Context menu will appear'
        },
        {
            'step': 'Step 3: Select "Symbols"',
            'action': 'Click "Symbols" from the menu',
            'details': 'This opens the complete symbols list'
        },
        {
            'step': 'Step 4: Navigate to Metals',
            'action': 'Expand "Forex" → "Metals" or look for "Spot Metals"',
            'details': 'XM usually puts gold in Metals category'
        },
        {
            'step': 'Step 5: Find GOLD or XAUUSD',
            'action': 'Look for "GOLD" symbol (most common on XM)',
            'details': 'May be named GOLD, XAUUSD, or GOLDmicro'
        },
        {
            'step': 'Step 6: Add to Market Watch',
            'action': 'Double-click the symbol or drag to Market Watch',
            'details': 'Symbol should now appear in Market Watch'
        },
        {
            'step': 'Step 7: Verify in QuantumBotX',
            'action': 'Restart your bot and check if XAUUSD is detected',
            'details': 'Bot should now find the symbol'
        }
    ]
    
    for i, step_info in enumerate(steps, 1):
        print(f"\\n{step_info['step']}:")
        print(f"   🎯 Action: {step_info['action']}")
        print(f"   💡 Details: {step_info['details']}")

def test_quantumbotx_finder():
    """Test QuantumBotX symbol finder with XM"""
    print("\\n🤖 Testing QuantumBotX Symbol Finder on XM")
    print("-" * 50)
    
    # Test with common XM gold symbols
    test_symbols = ['XAUUSD', 'GOLD', 'GOLDmicro']
    
    for symbol in test_symbols:
        print(f"\\n🔍 Testing: {symbol}")
        found = find_mt5_symbol(symbol)
        
        if found:
            print(f"   ✅ QuantumBotX found: {found}")
            
            # Test data retrieval
            try:
                rates = mt5.copy_rates_from_pos(found, mt5.TIMEFRAME_H1, 0, 10)
                if rates is not None and len(rates) > 0:
                    print(f"   📊 Historical data: ✅ Available ({len(rates)} bars)")
                else:
                    print(f"   📊 Historical data: ❌ Not available")
            except Exception as e:
                print(f"   📊 Historical data error: {e}")
        else:
            print(f"   ❌ QuantumBotX cannot find {symbol}")

def show_xm_solutions():
    """Show XM-specific solutions"""
    print("\\n🛠️ XM GLOBAL SOLUTIONS")
    print("=" * 30)
    
    solutions = [
        {
            'issue': 'GOLD symbol not visible',
            'solution': 'Right-click Market Watch → Symbols → Forex → Metals → Double-click GOLD'
        },
        {
            'issue': 'XAUUSD vs GOLD naming',
            'solution': 'XM usually uses "GOLD" instead of "XAUUSD" - update bot config'
        },
        {
            'issue': 'Symbol activation fails',
            'solution': 'Close MT5, reopen, login again, then add GOLD to Market Watch'
        },
        {
            'issue': 'No metals category',
            'solution': 'Contact XM support to enable metals trading on your account'
        },
        {
            'issue': 'Demo account limitations',
            'solution': 'Some demo accounts have limited symbols - try live account'
        }
    ]
    
    for i, solution in enumerate(solutions, 1):
        print(f"\\n{i}. {solution['issue']}:")
        print(f"   💡 {solution['solution']}")

def main():
    """Main XM troubleshooter"""
    print("🥇 XM Global XAUUSD Troubleshooter - QuantumBotX")
    print("=" * 60)
    print("Khusus untuk mengatasi masalah XAUUSD di XM Global...")
    print()
    
    if not MT5_AVAILABLE:
        print("❌ MetaTrader5 package not available")
        return
    
    # Step 1: Connect to XM
    if not connect_to_xm_global():
        print("\\n❌ Cannot connect to XM Global")
        print("💡 Make sure MT5 is open and logged in to XM")
        return
    
    # Step 2: Analyze XAUUSD
    gold_symbol = analyze_xm_xauusd()
    
    # Step 3: Test QuantumBotX finder
    test_quantumbotx_finder()
    
    # Step 4: Show guides
    xm_market_watch_guide()
    show_xm_solutions()
    
    # Cleanup
    mt5.shutdown()
    
    print("\\n" + "=" * 60)
    if gold_symbol:
        print(f"🎉 SUCCESS! Found gold symbol: {gold_symbol}")
        print(f"💡 Update your bot config to use '{gold_symbol}' instead of 'XAUUSD'")
    else:
        print("⚠️ XAUUSD/GOLD not found - follow the guide above")
    print("=" * 60)
    
    print("\\n🔄 NEXT STEPS:")
    print("1. Follow the Market Watch setup guide above")
    print("2. Add GOLD symbol to Market Watch")
    print("3. Run this script again to verify")
    print("4. Update bot config if symbol name is different")
    print("5. Test XAUUSD bot after fixing")

if __name__ == "__main__":
    main()