# testing/test_holiday_integration.py
"""
Test script for holiday integration features
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.seasonal.holiday_manager import holiday_manager
from datetime import date, datetime

def test_holiday_detection():
    """Test holiday detection functionality"""
    print("Testing Holiday Detection...")
    
    # Test current holiday detection
    current_holiday = holiday_manager.get_current_holiday_mode()
    if current_holiday:
        print(f"✓ Active holiday: {current_holiday.name}")
        print(f"✓ Period: {current_holiday.start_date} to {current_holiday.end_date}")
        print(f"✓ Greeting: {holiday_manager.get_holiday_greeting()}")
    else:
        print("✓ No active holiday")
    
    # Test Ramadan features when active
    ramadan_features = holiday_manager.get_ramadan_features()
    if ramadan_features:
        print("✓ Ramadan features available:")
        if 'iftar_countdown' in ramadan_features:
            countdown = ramadan_features['iftar_countdown']
            print(f"  - Iftar countdown: {countdown['hours']}h {countdown['minutes']}m until {countdown['next_prayer']}")
        if 'patience_reminder' in ramadan_features:
            print(f"  - Patience reminder: {ramadan_features['patience_reminder']}")
    else:
        print("✓ No Ramadan features (not active)")
    
    # Test risk multiplier
    risk_multiplier = holiday_manager.get_risk_multiplier()
    print(f"✓ Current risk multiplier: {risk_multiplier}")
    
    # Test trading pause status
    is_paused = holiday_manager.is_trading_paused()
    print(f"✓ Trading paused: {is_paused}")
    
    if is_paused:
        current_holiday = holiday_manager.get_current_holiday_mode()
        if current_holiday and current_holiday.name == "Ramadan Trading Mode":
            # Check which prayer time is causing the pause
            from datetime import datetime
            now = datetime.now()
            current_time = (now.hour, now.minute)
            
            adjustments = current_holiday.trading_adjustments
            
            # Check Sahur pause
            if 'sahur_pause' in adjustments:
                start_hour, start_min, end_hour, end_min = adjustments['sahur_pause']
                if (start_hour, start_min) <= current_time <= (end_hour, end_min):
                    print("  - Pause reason: Sahur time - time for spiritual reflection and preparation")
            
            # Check Iftar pause
            if 'iftar_pause' in adjustments:
                start_hour, start_min, end_hour, end_min = adjustments['iftar_pause']
                if (start_hour, start_min) <= current_time <= (end_hour, end_min):
                    print("  - Pause reason: Iftar time - breaking fast and family time")
            
            # Check Tarawih pause
            if 'tarawih_pause' in adjustments:
                start_hour, start_min, end_hour, end_min = adjustments['tarawih_pause']
                if (start_hour, start_min) <= current_time <= (end_hour, end_min):
                    print("  - Pause reason: Tarawih prayers - spiritual devotion time")

if __name__ == "__main__":
    print("Holiday Integration Test")
    print("=" * 30)
    test_holiday_detection()
    print("=" * 30)
    print("Test completed successfully!")