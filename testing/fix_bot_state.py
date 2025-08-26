#!/usr/bin/env python3
"""
🔧 Fix Bot State Synchronization
Fixes the active_bots dictionary to match running bot threads
"""

import sys
import os
import threading

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.bots.controller import active_bots, mulai_bot, hentikan_bot
    from core.db import queries
    from core.bots.trading_bot import TradingBot
    
    def diagnose_bot_state():
        """Diagnose current bot state"""
        print("🔍 DIAGNOSING BOT STATE")
        print("=" * 30)
        
        # Check database bots
        all_bots = queries.get_all_bots()
        active_db_bots = [bot for bot in all_bots if bot['status'] == 'Aktif']
        
        print(f"Database active bots: {len(active_db_bots)}")
        for bot in active_db_bots:
            print(f"  - ID: {bot['id']}, Name: {bot['name']}, Market: {bot['market']}")
        
        # Check controller active bots
        print(f"\\nController active_bots: {len(active_bots)}")
        for bot_id, bot_instance in active_bots.items():
            print(f"  - ID: {bot_id}, Alive: {bot_instance.is_alive()}, Status: {bot_instance.status}")
        
        # Check running threads
        all_threads = threading.enumerate()
        trading_bot_threads = [t for t in all_threads if isinstance(t, TradingBot)]
        
        print(f"\\nRunning TradingBot threads: {len(trading_bot_threads)}")
        for thread in trading_bot_threads:
            print(f"  - ID: {thread.id}, Name: {thread.name}, Alive: {thread.is_alive()}")
            print(f"    Market: {thread.market}, Status: {thread.status}")
        
        return active_db_bots, active_bots, trading_bot_threads
    
    def fix_bot_state():
        """Fix bot state synchronization"""
        print("\\n🔧 FIXING BOT STATE")
        print("=" * 25)
        
        # Get current state
        db_bots, controller_bots, thread_bots = diagnose_bot_state()
        
        # Find bots that are running but not in controller
        orphaned_threads = []
        for thread in thread_bots:
            if thread.id not in controller_bots and thread.is_alive():
                orphaned_threads.append(thread)
        
        if orphaned_threads:
            print(f"\\n🚨 Found {len(orphaned_threads)} orphaned bot threads:")
            for thread in orphaned_threads:
                print(f"  - Bot {thread.id} ({thread.name}) is running but not in active_bots")
                
                # Add to active_bots
                active_bots[thread.id] = thread
                print(f"  ✅ Added Bot {thread.id} to active_bots")
        
        # Find bots in controller but not alive
        dead_bots = []
        for bot_id, bot_instance in list(controller_bots.items()):
            if not bot_instance.is_alive():
                dead_bots.append(bot_id)
        
        if dead_bots:
            print(f"\\n💀 Found {len(dead_bots)} dead bots in controller:")
            for bot_id in dead_bots:
                print(f"  - Bot {bot_id} is in active_bots but thread is dead")
                del active_bots[bot_id]
                queries.update_bot_status(bot_id, 'Dijeda')
                print(f"  ✅ Removed Bot {bot_id} from active_bots and set status to 'Dijeda'")
        
        return len(orphaned_threads), len(dead_bots)
    
    def test_analysis_after_fix():
        """Test analysis API after fix"""
        print("\\n🧪 TESTING ANALYSIS AFTER FIX")
        print("=" * 35)
        
        from core.bots.controller import get_bot_analysis_data
        
        bot_id = 3
        analysis_data = get_bot_analysis_data(bot_id)
        
        if analysis_data:
            print(f"✅ Bot {bot_id} analysis data:")
            print(f"   Signal: {analysis_data.get('signal', 'N/A')}")
            print(f"   Price: {analysis_data.get('price', 'N/A')}")
            print(f"   Explanation: {analysis_data.get('explanation', 'N/A')}")
        else:
            print(f"❌ Bot {bot_id} analysis data is None")
    
    def main():
        print("🔧 Bot State Synchronization Fix")
        print("=" * 40)
        
        # Diagnose
        diagnose_bot_state()
        
        # Fix
        orphaned, dead = fix_bot_state()
        
        # Test
        test_analysis_after_fix()
        
        # Summary
        print("\\n" + "=" * 40)
        print("🎯 FIX SUMMARY")
        print("=" * 40)
        print(f"Orphaned threads fixed: {orphaned}")
        print(f"Dead bots cleaned: {dead}")
        print(f"Current active_bots: {len(active_bots)}")
        
        if orphaned > 0:
            print("\\n✅ SUCCESS: Bot state synchronized!")
            print("💡 The 'Analisis Real-Time' should now work in the dashboard")
        else:
            print("\\n⚠️ No orphaned threads found")
            print("💡 If issue persists, restart the QuantumBotX application")
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()