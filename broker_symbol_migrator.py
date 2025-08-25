#!/usr/bin/env python3
"""
🔄 Broker Symbol Migration System
Automatically updates bot symbol configurations when switching brokers
"""

import sys
import os
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
load_dotenv()

try:
    import MetaTrader5 as mt5
    from core.utils.mt5 import initialize_mt5, find_mt5_symbol
    from core.db import queries
    from core.bots.controller import hentikan_bot, mulai_bot, active_bots
    
    MT5_AVAILABLE = True
except ImportError as e:
    MT5_AVAILABLE = False
    print(f"⚠️ Import error: {e}")

def detect_current_broker():
    """Detect current broker and return standardized name"""
    try:
        account_info = mt5.account_info()
        if not account_info:
            return "Unknown"
        
        server = account_info.server.upper()
        company = account_info.company.upper()
        
        # Broker detection logic
        if 'XM' in server or 'XM' in company:
            return "XM Global"
        elif 'DEMO' in server or 'METAQUOTES' in server:
            return "MetaTrader Demo"
        elif 'EXNESS' in server or 'EXNESS' in company:
            return "Exness"
        elif 'ALPARI' in server or 'ALPARI' in company:
            return "Alpari"
        elif 'BINANCE' in server or 'BINANCE' in company:
            return "Binance"
        else:
            return f"Unknown ({server})"
    except Exception as e:
        print(f"Error detecting broker: {e}")
        return "Unknown"

def get_broker_preferred_symbols():
    """Get broker-specific preferred symbol mappings"""
    return {
        "XM Global": {
            "XAUUSD": "GOLD",
            "BTCUSD": "BTCUSD",
            "ETHUSD": "ETHUSD",
            "EURUSD": "EURUSD"
        },
        "MetaTrader Demo": {
            "XAUUSD": "XAUUSD",
            "BTCUSD": "BTCUSD", 
            "ETHUSD": "ETHUSD",
            "EURUSD": "EURUSD"
        },
        "Exness": {
            "XAUUSD": "XAUUSDm",
            "BTCUSD": "BTCUSD",
            "ETHUSD": "ETHUSD", 
            "EURUSD": "EURUSDm"
        },
        "Alpari": {
            "XAUUSD": "XAUUSD.c",
            "BTCUSD": "BTCUSD",
            "ETHUSD": "ETHUSD",
            "EURUSD": "EURUSD"
        }
    }

def analyze_current_bots():
    """Analyze current bot configurations and symbol availability"""
    print("🔍 Analyzing Current Bot Configurations")
    print("=" * 45)
    
    current_broker = detect_current_broker()
    preferred_symbols = get_broker_preferred_symbols().get(current_broker, {})
    
    print(f"📊 Current Broker: {current_broker}")
    print(f"🎯 Preferred Symbol Mapping: {preferred_symbols}")
    
    # Get all bots from database
    all_bots = queries.get_all_bots()
    
    symbol_issues = []
    
    for bot in all_bots:
        bot_id = bot['id']
        bot_name = bot['name']
        current_market = bot['market']
        
        print(f"\\n🤖 Bot: {bot_name} (ID: {bot_id})")
        print(f"   Current Market: {current_market}")
        
        # Test if current symbol works
        resolved_symbol = find_mt5_symbol(current_market)
        if resolved_symbol:
            print(f"   ✅ Symbol resolved to: {resolved_symbol}")
            if resolved_symbol != current_market:
                print(f"   💡 Could be updated from '{current_market}' to '{resolved_symbol}'")
                symbol_issues.append({
                    'bot_id': bot_id,
                    'bot_name': bot_name,
                    'current_symbol': current_market,
                    'resolved_symbol': resolved_symbol,
                    'action': 'update_resolved'
                })
        else:
            print(f"   ❌ Symbol '{current_market}' not found!")
            
            # Try to find broker-preferred alternative
            if current_market.upper() in preferred_symbols:
                preferred = preferred_symbols[current_market.upper()]
                test_symbol = find_mt5_symbol(preferred)
                if test_symbol:
                    print(f"   💡 Broker prefers: {preferred} -> resolves to: {test_symbol}")
                    symbol_issues.append({
                        'bot_id': bot_id,
                        'bot_name': bot_name,
                        'current_symbol': current_market,
                        'resolved_symbol': test_symbol,
                        'action': 'update_broker_preferred'
                    })
                else:
                    print(f"   ❌ Broker preferred '{preferred}' also not found")
                    symbol_issues.append({
                        'bot_id': bot_id,
                        'bot_name': bot_name,
                        'current_symbol': current_market,
                        'resolved_symbol': None,
                        'action': 'manual_fix_needed'
                    })
            else:
                symbol_issues.append({
                    'bot_id': bot_id,
                    'bot_name': bot_name,
                    'current_symbol': current_market,
                    'resolved_symbol': None,
                    'action': 'manual_fix_needed'
                })
    
    return current_broker, symbol_issues

def migrate_bot_symbols(symbol_issues):
    """Migrate bot symbols to correct broker-specific symbols"""
    print("\\n🔄 SYMBOL MIGRATION")
    print("=" * 25)
    
    if not symbol_issues:
        print("✅ No symbol issues found - all bots are properly configured!")
        return
    
    print(f"Found {len(symbol_issues)} bots with symbol issues:\\n")
    
    for i, issue in enumerate(symbol_issues, 1):
        print(f"{i}. {issue['bot_name']} (ID: {issue['bot_id']})")
        print(f"   Current: {issue['current_symbol']}")
        print(f"   Action: {issue['action']}")
        if issue['resolved_symbol']:
            print(f"   New Symbol: {issue['resolved_symbol']}")
        print()
    
    # Ask for confirmation
    try:
        choice = input("Do you want to migrate these symbols? (y/N): ").lower()
        if choice != 'y':
            print("\\n❌ Migration cancelled by user")
            return
    except KeyboardInterrupt:
        print("\\n\\n❌ Migration cancelled by user")
        return
    
    print("\\n🚀 Starting migration...")
    
    migrated = 0
    for issue in symbol_issues:
        bot_id = issue['bot_id']
        new_symbol = issue['resolved_symbol']
        
        if not new_symbol:
            print(f"⚠️ Skipping {issue['bot_name']} - no valid symbol found")
            continue
        
        # Stop bot if running
        if bot_id in active_bots:
            print(f"🛑 Stopping bot {bot_id} for migration...")
            hentikan_bot(bot_id)
        
        # Update database
        try:
            success = queries.update_bot(
                bot_id=bot_id,
                name=issue['bot_name'],  # Keep same name
                market=new_symbol,       # Update symbol
                lot_size=0.01,          # Keep safe defaults for other fields
                sl_pips=100,
                tp_pips=200,
                timeframe='H1',
                interval=60,
                strategy='RSI_CROSSOVER'
            )
            
            if success:
                print(f"✅ {issue['bot_name']}: {issue['current_symbol']} → {new_symbol}")
                migrated += 1
                
                # Restart if it was running
                if bot_id in active_bots:
                    print(f"🚀 Restarting bot {bot_id}...")
                    mulai_bot(bot_id)
            else:
                print(f"❌ Failed to update {issue['bot_name']} in database")
                
        except Exception as e:
            print(f"❌ Error updating {issue['bot_name']}: {e}")
    
    print(f"\\n🎉 Migration complete! Updated {migrated} bots.")

def create_broker_config_backup():
    """Create a backup of current broker configuration"""
    current_broker = detect_current_broker()
    
    backup_data = {
        'broker': current_broker,
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'bots': []
    }
    
    all_bots = queries.get_all_bots()
    for bot in all_bots:
        backup_data['bots'].append({
            'id': bot['id'],
            'name': bot['name'],
            'market': bot['market'],
            'status': bot['status']
        })
    
    import json
    backup_file = f"broker_config_backup_{current_broker.replace(' ', '_')}.json"
    
    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    print(f"💾 Backup created: {backup_file}")
    return backup_file

def main():
    """Main migration function"""
    print("🔄 Broker Symbol Migration System")
    print("=" * 40)
    print("Automatically updates bot symbols when switching brokers\\n")
    
    if not MT5_AVAILABLE:
        print("❌ MetaTrader5 package not available")
        return
    
    # Connect to MT5
    try:
        ACCOUNT = int(os.getenv('MT5_LOGIN'))
        PASSWORD = os.getenv('MT5_PASSWORD')
        SERVER = os.getenv('MT5_SERVER')
        
        if not initialize_mt5(ACCOUNT, PASSWORD, SERVER):
            print("❌ Failed to connect to MT5")
            return
    except Exception as e:
        print(f"❌ MT5 connection error: {e}")
        return
    
    # Create backup
    backup_file = create_broker_config_backup()
    
    # Analyze current configuration
    current_broker, symbol_issues = analyze_current_bots()
    
    # Migrate if needed
    if symbol_issues:
        migrate_bot_symbols(symbol_issues)
    else:
        print("\\n✅ All bots are properly configured for current broker!")
    
    print(f"\\n💡 TIPS FOR FUTURE BROKER SWITCHES:")
    print("1. Run this script after connecting to a new broker")
    print("2. Keep backup files for easy rollback")
    print("3. Test bot functionality after migration")
    print("4. The enhanced find_mt5_symbol() will auto-detect most symbols")
    
    mt5.shutdown()

if __name__ == "__main__":
    main()