#!/usr/bin/env python3
"""
🔄 XAUUSD Bot Restart and Monitor Tool
Memulai ulang bot XAUUSD dan memonitor error startup
"""

import sys
import os
import time
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import MetaTrader5 as mt5
    from core.utils.mt5 import initialize_mt5, find_mt5_symbol
    from core.bots.controller import active_bots, mulai_bot, hentikan_bot
    from core.db import queries
    from dotenv import load_dotenv
    
    # Load environment
    load_dotenv()
    
    MT5_AVAILABLE = True
except ImportError as e:
    MT5_AVAILABLE = False
    print(f"⚠️ Import error: {e}")

def setup_logging():
    """Setup detailed logging to catch startup errors"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('xauusd_bot_debug.log')
        ]
    )

def check_mt5_connection():
    """Verify MT5 connection"""
    print("🔌 Checking MT5 Connection...")
    print("-" * 30)
    
    try:
        ACCOUNT = int(os.getenv('MT5_LOGIN'))
        PASSWORD = os.getenv('MT5_PASSWORD')
        SERVER = os.getenv('MT5_SERVER')
        
        success = initialize_mt5(ACCOUNT, PASSWORD, SERVER)
        if success:
            print("✅ MT5 connected successfully")
            return True
        else:
            print("❌ MT5 connection failed")
            return False
    except Exception as e:
        print(f"❌ MT5 connection error: {e}")
        return False

def check_gold_symbol():
    """Verify GOLD symbol availability"""
    print("\\n🥇 Checking GOLD Symbol...")
    print("-" * 30)
    
    symbol = find_mt5_symbol("GOLD")
    if symbol:
        print(f"✅ GOLD symbol found: {symbol}")
        
        # Test symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info:
            print(f"   Path: {symbol_info.path}")
            print(f"   Visible: {symbol_info.visible}")
            print(f"   Digits: {symbol_info.digits}")
            
            # Test tick data
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                print(f"   Current Price: ${tick.bid:.2f}")
                return True
            else:
                print("❌ Cannot get tick data")
                return False
        else:
            print("❌ Cannot get symbol info")
            return False
    else:
        print("❌ GOLD symbol not found")
        return False

def get_xauusd_bots():
    """Get all XAUUSD/Gold bots from database"""
    try:
        all_bots = queries.get_all_bots()
        gold_bots = []
        
        for bot in all_bots:
            market = bot['market'].upper()
            if any(term in market for term in ['XAUUSD', 'GOLD', 'XAU']):
                gold_bots.append(bot)
        
        return gold_bots
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []

def restart_gold_bot(bot_id):
    """Restart specific gold bot with detailed monitoring"""
    print(f"\\n🔄 Restarting Gold Bot ID: {bot_id}")
    print("-" * 40)
    
    # First stop if running
    if bot_id in active_bots:
        print("🛑 Stopping existing bot instance...")
        hentikan_bot(bot_id)
        time.sleep(2)
    
    # Get bot data
    bot_data = queries.get_bot_by_id(bot_id)
    if not bot_data:
        print(f"❌ Bot {bot_id} not found in database")
        return False
    
    print(f"📋 Bot Details:")
    print(f"   Name: {bot_data['name']}")
    print(f"   Market: {bot_data['market']}")
    print(f"   Strategy: {bot_data['strategy']}")
    print(f"   Status: {bot_data['status']}")
    
    # Try to start
    print("\\n🚀 Starting bot...")
    try:
        success, message = mulai_bot(bot_id)
        if success:
            print(f"✅ {message}")
            
            # Wait and check if bot is actually running
            time.sleep(3)
            if bot_id in active_bots:
                bot_instance = active_bots[bot_id]
                print(f"✅ Bot is running in active_bots")
                print(f"   Thread alive: {bot_instance.is_alive()}")
                print(f"   Status: {bot_instance.status}")
                if hasattr(bot_instance, 'last_analysis'):
                    print(f"   Last Analysis: {bot_instance.last_analysis}")
                return True
            else:
                print("❌ Bot not found in active_bots after startup")
                return False
        else:
            print(f"❌ {message}")
            return False
    except Exception as e:
        print(f"❌ Startup error: {e}")
        logging.exception("Bot startup error:")
        return False

def monitor_bot_for_errors(bot_id, duration=30):
    """Monitor bot for errors over specified duration"""
    print(f"\\n👁️ Monitoring Bot {bot_id} for {duration} seconds...")
    print("-" * 50)
    
    if bot_id not in active_bots:
        print("❌ Bot not in active_bots, cannot monitor")
        return
    
    bot_instance = active_bots[bot_id]
    start_time = time.time()
    
    while time.time() - start_time < duration:
        if not bot_instance.is_alive():
            print("❌ Bot thread died!")
            break
            
        if hasattr(bot_instance, 'last_analysis'):
            analysis = bot_instance.last_analysis
            signal = analysis.get('signal', 'N/A')
            explanation = analysis.get('explanation', 'N/A')
            
            if signal == 'ERROR':
                print(f"❌ Bot Error: {explanation}")
                break
            else:
                print(f"✅ Bot OK - Signal: {signal}")
        
        time.sleep(5)
    
    print("\\n📊 Final bot status:")
    if bot_instance.is_alive():
        print("✅ Bot thread is still alive")
        print(f"   Status: {bot_instance.status}")
        if hasattr(bot_instance, 'last_analysis'):
            print(f"   Last Analysis: {bot_instance.last_analysis}")
    else:
        print("❌ Bot thread is dead")

def main():
    """Main restart and monitor function"""
    setup_logging()
    
    print("🔄 XAUUSD Bot Restart and Monitor Tool")
    print("=" * 50)
    
    if not MT5_AVAILABLE:
        print("❌ MetaTrader5 package not available")
        return
    
    # Step 1: Check MT5 connection
    if not check_mt5_connection():
        print("\\n❌ Cannot proceed without MT5 connection")
        return
    
    # Step 2: Check GOLD symbol
    if not check_gold_symbol():
        print("\\n❌ Cannot proceed without GOLD symbol")
        return
    
    # Step 3: Get XAUUSD bots
    print("\\n📋 Finding XAUUSD/Gold Bots...")
    print("-" * 30)
    
    gold_bots = get_xauusd_bots()
    if not gold_bots:
        print("❌ No XAUUSD/Gold bots found")
        return
    
    print(f"✅ Found {len(gold_bots)} gold bots:")
    for bot in gold_bots:
        print(f"   ID: {bot['id']} - {bot['name']} ({bot['market']}) - {bot['status']}")
    
    # Step 4: Restart bots
    for bot in gold_bots:
        success = restart_gold_bot(bot['id'])
        if success:
            monitor_bot_for_errors(bot['id'], 30)
    
    # Step 5: Final status
    print("\\n" + "=" * 50)
    print("🎯 FINAL STATUS")
    print("=" * 50)
    
    print(f"Active bots count: {len(active_bots)}")
    for bot_id, bot_instance in active_bots.items():
        bot_data = queries.get_bot_by_id(bot_id)
        if bot_data and any(term in bot_data['market'].upper() for term in ['XAUUSD', 'GOLD', 'XAU']):
            print(f"✅ Gold Bot {bot_id}: {bot_data['name']} - {bot_instance.status}")
    
    print("\\n💡 RECOMMENDATIONS:")
    print("1. Check logs in 'xauusd_bot_debug.log' for detailed errors")
    print("2. If bot keeps failing, restart QuantumBotX application")
    print("3. Verify GOLD symbol is in Market Watch")
    print("4. Check bot parameters in dashboard")

if __name__ == "__main__":
    main()