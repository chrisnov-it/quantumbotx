#!/usr/bin/env python3
"""
🔍 Test Analysis API for XAUUSD Bot
Quick test to see what the analysis API returns
"""

import sys
import os
import requests

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.bots.controller import active_bots, get_bot_analysis_data
    from core.db import queries
    
    def test_direct_controller():
        """Test controller function directly"""
        print("🔍 Testing Controller Function Directly")
        print("=" * 40)
        
        # Check active bots
        print(f"Active bots: {list(active_bots.keys())}")
        
        # Test bot ID 3
        bot_id = 3
        data = get_bot_analysis_data(bot_id)
        print(f"Analysis data for bot {bot_id}: {data}")
        
        # Check if bot 3 is in active_bots
        if bot_id in active_bots:
            bot_instance = active_bots[bot_id]
            print("Bot instance found:")
            print(f"  - Alive: {bot_instance.is_alive()}")
            print(f"  - Status: {bot_instance.status}")
            if hasattr(bot_instance, 'last_analysis'):
                print(f"  - Last Analysis: {bot_instance.last_analysis}")
        else:
            print(f"❌ Bot {bot_id} not found in active_bots")
            
        # Get bot from database
        bot_data = queries.get_bot_by_id(bot_id)
        if bot_data:
            print("\\nBot in database:")
            print(f"  - Name: {bot_data['name']}")
            print(f"  - Market: {bot_data['market']}")
            print(f"  - Status: {bot_data['status']}")
        
    def test_api_endpoint():
        """Test API endpoint via HTTP"""
        print("\\n🌐 Testing API Endpoint via HTTP")
        print("=" * 40)
        
        try:
            response = requests.get('http://127.0.0.1:5000/api/bots/3/analysis', timeout=5)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Flask server (not running)")
        except Exception as e:
            print(f"❌ Request error: {e}")
    
    def main():
        print("🧪 Analysis API Test for XAUUSD Bot")
        print("=" * 45)
        
        test_direct_controller()
        test_api_endpoint()
        
        print("\\n💡 SOLUTION:")
        print("If bot is not in active_bots but shows as 'Aktif' in database,")
        print("the bot needs to be restarted to sync the status.")
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the QuantumBotX directory")