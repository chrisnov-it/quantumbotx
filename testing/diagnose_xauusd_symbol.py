#!/usr/bin/env python3
"""
🥇 XAUUSD Symbol Diagnostic Tool
Diagnosis kenapa XAUUSD tidak terdeteksi di Market Watch MT5
"""

import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import MetaTrader5 as mt5
    from core.utils.mt5 import find_mt5_symbol, initialize_mt5
    from core.utils.logger import setup_logger
    MT5_AVAILABLE = True
except ImportError as e:
    MT5_AVAILABLE = False
    print(f"⚠️ Import error: {e}")

def diagnose_xauusd_comprehensive():
    """Comprehensive XAUUSD diagnosis"""
    print("🥇 XAUUSD Symbol Comprehensive Diagnosis")
    print("=" * 60)
    
    if not MT5_AVAILABLE:
        print("❌ MetaTrader5 package not available")
        return False
    
    # Step 1: Initialize MT5
    print("\\n🔌 Step 1: MT5 Connection Test")
    print("-" * 40)
    
    if not mt5.initialize():
        print("❌ MT5 initialization failed")
        print("💡 Solutions:")
        print("   1. Make sure MetaTrader 5 terminal is running")
        print("   2. Try closing and reopening MT5")
        print("   3. Check if MT5 is logged in to broker account")
        return False
    
    print("✅ MT5 Terminal Connected!")
    
    # Step 2: Account info
    print("\\n📊 Step 2: Account Information")
    print("-" * 40)
    
    account_info = mt5.account_info()
    if account_info:
        print(f"   Server: {account_info.server}")
        print(f"   Broker: {account_info.company}")
        print(f"   Currency: {account_info.currency}")
        print(f"   Balance: ${account_info.balance:,.2f}")
        print(f"   Login: {account_info.login}")
    else:
        print("❌ Cannot get account info")
        return False
    
    # Step 3: Symbol search methods
    print("\\n🔍 Step 3: XAUUSD Detection Methods")
    print("-" * 40)
    
    # Method 1: Direct check
    print("\\n🎯 Method 1: Direct Symbol Check")
    direct_symbols = ['XAUUSD', 'GOLD', 'XAU/USD', 'XAU_USD', 'XAUUSD.']
    found_direct = []
    
    for symbol in direct_symbols:
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info:
            found_direct.append(symbol)
            print(f"   ✅ {symbol}: FOUND!")
            
            # Get tick data
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                print(f"      💰 Price: ${tick.bid:.2f}")
                print(f"      👁️ Visible: {symbol_info.visible}")
                print(f"      📂 Path: {symbol_info.path}")
        else:
            print(f"   ❌ {symbol}: Not found")
    
    # Method 2: Search all symbols for gold-related
    print("\\n🔍 Method 2: Gold-Related Symbol Search")
    all_symbols = mt5.symbols_get()
    if all_symbols:
        gold_symbols = []
        for symbol in all_symbols:
            name = symbol.name.upper()
            if any(term in name for term in ['XAU', 'GOLD', 'AU']):
                gold_symbols.append(symbol)
                status = "VISIBLE" if symbol.visible else "HIDDEN"
                print(f"   🥇 {symbol.name}: {status} (Path: {symbol.path})")
        
        print(f"\\n📊 Found {len(gold_symbols)} gold-related symbols")
    else:
        print("❌ Cannot retrieve symbols list")
    
    # Method 3: Use our find_mt5_symbol function
    print("\\n🔧 Method 3: QuantumBotX Symbol Finder")
    found_symbol = find_mt5_symbol("XAUUSD")
    if found_symbol:
        print(f"   ✅ Found: {found_symbol}")
    else:
        print("   ❌ Not found by QuantumBotX finder")
    
    # Step 4: Market Watch analysis
    print("\\n👁️ Step 4: Market Watch Analysis")
    print("-" * 40)
    
    visible_symbols = [s for s in all_symbols if s.visible]
    print(f"   📊 Total symbols available: {len(all_symbols)}")
    print(f"   👁️ Visible in Market Watch: {len(visible_symbols)}")
    print(f"   📈 Visibility ratio: {len(visible_symbols)/len(all_symbols)*100:.1f}%")
    
    # Check specific categories
    categories = {
        'Forex': 0,
        'Metals': 0,
        'Indices': 0,
        'Commodities': 0,
        'Crypto': 0
    }
    
    for symbol in visible_symbols:
        name = symbol.name.upper()
        if any(x in name for x in ['USD', 'EUR', 'GBP', 'JPY']):
            categories['Forex'] += 1
        elif any(x in name for x in ['XAU', 'XAG', 'GOLD', 'SILVER']):
            categories['Metals'] += 1
        elif any(x in name for x in ['SPX', 'US30', 'NAS']):
            categories['Indices'] += 1
        elif any(x in name for x in ['OIL', 'BRENT']):
            categories['Commodities'] += 1
        elif any(x in name for x in ['BTC', 'ETH']):
            categories['Crypto'] += 1
    
    print("\\n📊 Visible symbols by category:")
    for category, count in categories.items():
        print(f"   {category:12}: {count}")
    
    # Step 5: Broker-specific solutions
    print("\\n🛠️ Step 5: Broker-Specific Solutions")
    print("-" * 40)
    
    server = account_info.server if account_info else "Unknown"
    
    if 'XM' in server.upper():
        print("🏢 XM Broker Detected")
        print("   💡 Solutions for XM:")
        print("      1. Right-click Market Watch → Show All")
        print("      2. Look for 'GOLD' instead of 'XAUUSD'")
        print("      3. Check 'Metals' or 'Spot Metals' category")
    elif 'ALPARI' in server.upper():
        print("🏢 Alpari Broker Detected")
        print("   💡 Solutions for Alpari:")
        print("      1. Symbol might be named 'XAUUSD.c'")
        print("      2. Check CFD metals section")
    elif 'EXNESS' in server.upper():
        print("🏢 Exness Broker Detected")
        print("   💡 Solutions for Exness:")
        print("      1. Symbol is usually 'XAUUSDm'")
        print("      2. Check 'Metals' group")
    else:
        print(f"🏢 Broker: {server}")
        print("   💡 General solutions:")
        print("      1. Right-click Market Watch → Show All")
        print("      2. Search for gold-related symbols")
        print("      3. Check different symbol naming")
    
    # Step 6: Activation attempt
    print("\\n🔄 Step 6: Symbol Activation Attempt")
    print("-" * 40)
    
    if gold_symbols:
        for symbol in gold_symbols[:3]:  # Try first 3 gold symbols
            print(f"\\n   Trying to activate: {symbol.name}")
            success = mt5.symbol_select(symbol.name, True)
            if success:
                print(f"   ✅ Successfully activated {symbol.name}!")
                
                # Test data retrieval
                tick = mt5.symbol_info_tick(symbol.name)
                if tick:
                    print(f"      💰 Current price: ${tick.bid:.2f}")
                
                # Test historical data
                rates = mt5.copy_rates_from_pos(symbol.name, mt5.TIMEFRAME_H1, 0, 10)
                if rates is not None and len(rates) > 0:
                    print(f"      📊 Historical data: ✅ Available")
                else:
                    print(f"      📊 Historical data: ❌ Not available")
            else:
                print(f"   ❌ Failed to activate {symbol.name}")
    
    mt5.shutdown()
    return found_direct or gold_symbols

def show_solutions():
    """Show step-by-step solutions"""
    print("\\n🛠️ SOLUSI LANGKAH DEMI LANGKAH")
    print("=" * 50)
    
    solutions = [
        {
            'problem': 'XAUUSD tidak ditemukan sama sekali',
            'solutions': [
                'Klik kanan di Market Watch → Show All',
                'Cari "Gold" atau "XAU" di daftar simbol',
                'Drag simbol ke Market Watch',
                'Restart QuantumBotX setelah menambah simbol'
            ]
        },
        {
            'problem': 'Symbol ditemukan tapi tidak visible',
            'solutions': [
                'Double-click simbol di Symbols list',
                'Atau drag simbol ke Market Watch window',
                'Pastikan centang "Show in Market Watch"',
                'Refresh Market Watch (F5)'
            ]
        },
        {
            'problem': 'Symbol ada tapi nama berbeda',
            'solutions': [
                'Update bot config dengan nama simbol yang benar',
                'Contoh: ganti "XAUUSD" menjadi "GOLD"',
                'Atau "XAUUSDm" tergantung broker',
                'Test dulu dengan script ini'
            ]
        },
        {
            'problem': 'Broker tidak support gold trading',
            'solutions': [
                'Hubungi customer service broker',
                'Minta aktivasi metal trading',
                'Atau ganti ke broker yang support gold',
                'XM, Exness, Alpari biasanya support'
            ]
        }
    ]
    
    for i, solution in enumerate(solutions, 1):
        print(f"\\n{i}. {solution['problem']}:")
        for j, step in enumerate(solution['solutions'], 1):
            print(f"   {j}. {step}")

def main():
    """Main diagnostic function"""
    print("🚀 XAUUSD Diagnostic Tool - QuantumBotX")
    print("=" * 60)
    print("Mari kita cari tahu kenapa XAUUSD tidak terdeteksi...")
    print()
    
    success = diagnose_xauusd_comprehensive()
    
    show_solutions()
    
    print("\\n" + "=" * 60)
    if success:
        print("🎉 DIAGNOSIS COMPLETE! Solutions provided above.")
    else:
        print("⚠️ ISSUES FOUND! Follow solutions above.")
    print("=" * 60)
    
    print("\\n💡 NEXT STEPS:")
    print("1. Follow the solutions based on your broker")
    print("2. Restart MT5 after making changes")
    print("3. Run this script again to verify")
    print("4. Test XAUUSD bot after fixing")

if __name__ == "__main__":
    main()