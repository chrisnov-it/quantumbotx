#!/usr/bin/env python3
"""
🔧 XAUUSD Bot Database Configuration Fixer
Memperbaiki konfigurasi bot XAUUSD yang ada di database
"""

import sys
import os
import sqlite3

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_xauusd_bots():
    """Check for XAUUSD bots in database"""
    print("🔍 Checking Database for XAUUSD Bots")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect('bots.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Find all bots with XAUUSD or gold-related symbols
        cursor.execute("""
            SELECT * FROM bots 
            WHERE UPPER(market) LIKE '%XAUUSD%' 
               OR UPPER(market) LIKE '%GOLD%'
               OR UPPER(market) LIKE '%XAU%'
               OR UPPER(name) LIKE '%XAUUSD%'
               OR UPPER(name) LIKE '%GOLD%'
        """)
        
        gold_bots = cursor.fetchall()
        
        if not gold_bots:
            print("❌ No XAUUSD/Gold bots found in database")
            return []
        
        print(f"✅ Found {len(gold_bots)} XAUUSD/Gold bots:")
        print()
        
        bot_list = []
        for bot in gold_bots:
            bot_dict = dict(bot)
            bot_list.append(bot_dict)
            
            print(f"📋 Bot ID: {bot['id']}")
            print(f"   Name: {bot['name']}")
            print(f"   Market: {bot['market']}")
            print(f"   Status: {bot['status']}")
            print(f"   Strategy: {bot['strategy']}")
            print(f"   Timeframe: {bot['timeframe']}")
            print(f"   Lot Size: {bot['lot_size']}")
            print(f"   SL Pips: {bot['sl_pips']}")
            print(f"   TP Pips: {bot['tp_pips']}")
            print(f"   Check Interval: {bot['check_interval_seconds']}s")
            if bot['strategy_params']:
                print(f"   Strategy Params: {bot['strategy_params']}")
            print()
        
        conn.close()
        return bot_list
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return []

def suggest_symbol_fixes(bots):
    """Suggest symbol name fixes based on XM Global"""
    print("💡 SYMBOL NAME SUGGESTIONS")
    print("=" * 30)
    
    xm_gold_symbols = {
        'XAUUSD': {
            'alternatives': ['GOLD', 'GOLDmicro', 'XAUUSD.', 'XAU/USD'],
            'recommended': 'GOLD',
            'reason': 'XM Global usually uses "GOLD" instead of "XAUUSD"'
        },
        'GOLD': {
            'alternatives': ['XAUUSD', 'GOLDmicro', 'GOLD.'],
            'recommended': 'GOLD',
            'reason': 'Already using XM standard name'
        }
    }
    
    for bot in bots:
        market = bot['market'].upper()
        print(f"🤖 Bot: {bot['name']} (ID: {bot['id']})")
        print(f"   Current Market: {bot['market']}")
        
        if market in xm_gold_symbols:
            symbol_info = xm_gold_symbols[market]
            print(f"   💡 Recommendation: {symbol_info['recommended']}")
            print(f"   📝 Reason: {symbol_info['reason']}")
            print(f"   🔄 Alternatives to try: {', '.join(symbol_info['alternatives'])}")
        else:
            print(f"   💡 Try these XM symbols: GOLD, XAUUSD, GOLDmicro")
        print()

def update_bot_symbol(bot_id, new_symbol):
    """Update bot symbol in database"""
    try:
        conn = sqlite3.connect('bots.db')
        cursor = conn.cursor()
        
        cursor.execute("UPDATE bots SET market = ? WHERE id = ?", (new_symbol, bot_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Bot {bot_id} symbol updated to '{new_symbol}'")
            return True
        else:
            print(f"❌ Failed to update bot {bot_id}")
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        conn.close()

def interactive_fix():
    """Interactive bot fixing"""
    print("\\n🛠️ INTERACTIVE BOT FIXING")
    print("=" * 30)
    
    bots = check_xauusd_bots()
    if not bots:
        print("No bots to fix!")
        return
    
    suggest_symbol_fixes(bots)
    
    print("🔧 FIXING OPTIONS:")
    print("1. Update all XAUUSD bots to use 'GOLD'")
    print("2. Update specific bot manually")
    print("3. Show current bot status without changes")
    print("4. Exit")
    
    try:
        choice = input("\\nChoose an option (1-4): ")
        
        if choice == '1':
            # Update all XAUUSD bots to GOLD
            updated = 0
            for bot in bots:
                if bot['market'].upper() in ['XAUUSD', 'XAU/USD', 'XAUUSD.']:
                    if update_bot_symbol(bot['id'], 'GOLD'):
                        updated += 1
            print(f"\\n✅ Updated {updated} bots to use 'GOLD' symbol")
            
        elif choice == '2':
            # Manual update
            print("\\nAvailable bots:")
            for i, bot in enumerate(bots, 1):
                print(f"{i}. {bot['name']} (ID: {bot['id']}) - Current: {bot['market']}")
            
            try:
                bot_choice = int(input("\\nSelect bot number: ")) - 1
                if 0 <= bot_choice < len(bots):
                    new_symbol = input("Enter new symbol name: ").strip()
                    if new_symbol:
                        update_bot_symbol(bots[bot_choice]['id'], new_symbol)
                else:
                    print("Invalid bot selection")
            except ValueError:
                print("Invalid input")
                
        elif choice == '3':
            print("\\n📊 Current status shown above. No changes made.")
            
        elif choice == '4':
            print("\\n👋 Exiting without changes")
            
        else:
            print("\\n❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\\n\\n👋 Cancelled by user")

def show_fix_instructions():
    """Show manual fix instructions"""
    print("\\n📋 MANUAL FIX INSTRUCTIONS")
    print("=" * 35)
    
    instructions = [
        {
            'step': '1. Open MT5 Terminal',
            'action': 'Make sure you\'re logged in to XM Global',
            'details': 'Account should show XMGlobal-MT5 7 server'
        },
        {
            'step': '2. Check Market Watch',
            'action': 'Look for GOLD symbol in Market Watch',
            'details': 'If not visible, proceed to step 3'
        },
        {
            'step': '3. Add GOLD to Market Watch',
            'action': 'Right-click Market Watch → Symbols',
            'details': 'Navigate to Forex → Metals → Double-click GOLD'
        },
        {
            'step': '4. Update QuantumBotX Config',
            'action': 'Run this script and choose option 1',
            'details': 'This will update all XAUUSD bots to use GOLD'
        },
        {
            'step': '5. Restart QuantumBotX',
            'action': 'Close and restart the application',
            'details': 'Bots will now use the correct symbol name'
        },
        {
            'step': '6. Verify Bot Status',
            'action': 'Check bot detail page for "Analisis Real-Time"',
            'details': 'Should show price data instead of error message'
        }
    ]
    
    for instruction in instructions:
        print(f"\\n{instruction['step']}:")
        print(f"   🎯 Action: {instruction['action']}")
        print(f"   💡 Details: {instruction['details']}")

def main():
    """Main function"""
    print("🥇 XAUUSD Bot Database Configuration Fixer")
    print("=" * 50)
    print("Memperbaiki masalah konfigurasi bot XAUUSD di database...")
    print()
    
    # Check if database exists
    if not os.path.exists('bots.db'):
        print("❌ Database file 'bots.db' not found!")
        print("💡 Make sure you're running this from the QuantumBotX directory")
        return
    
    # Run interactive fix
    interactive_fix()
    
    # Show manual instructions
    show_fix_instructions()
    
    print("\\n" + "=" * 50)
    print("🎉 XAUUSD Bot Configuration Fixer Complete!")
    print("=" * 50)
    
    print("\\n🔄 NEXT STEPS:")
    print("1. Follow the manual instructions above")
    print("2. Restart QuantumBotX application")
    print("3. Check bot status in dashboard")
    print("4. Verify XAUUSD symbol is now working")
    print("\\n💡 Remember: XM Global uses 'GOLD' not 'XAUUSD'!")

if __name__ == "__main__":
    main()