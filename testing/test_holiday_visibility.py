# testing/test_holiday_visibility.py
"""
Test script for holiday visibility features
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.seasonal.holiday_manager import holiday_manager

def test_holiday_visibility():
    """Test holiday visibility functionality"""
    print("Testing Holiday Visibility...")
    
    # Test current holiday detection
    current_holiday = holiday_manager.get_current_holiday_mode()
    if current_holiday:
        print(f"✓ Active holiday: {current_holiday.name}")
        print(f"✓ Period: {current_holiday.start_date} to {current_holiday.end_date}")
        
        # Test if Ramadan is active
        if "Ramadan" in current_holiday.name:
            print("✓ Ramadan mode is active - navigation link should be visible")
        else:
            print("✓ Non-Ramadan holiday active - Ramadan navigation link should be hidden")
    else:
        print("✓ No active holiday - Ramadan navigation link should be hidden")
    
    # Test Ramadan features when active
    ramadan_features = holiday_manager.get_ramadan_features()
    if ramadan_features:
        print("✓ Ramadan features available:")
        if 'iftar_countdown' in ramadan_features:
            countdown = ramadan_features['iftar_countdown']
            print(f"  - Iftar countdown: {countdown['hours']}h {countdown['minutes']}m until {countdown['next_prayer']}")
    else:
        print("✓ No Ramadan features (not active)")

if __name__ == "__main__":
    print("Holiday Visibility Test")
    print("=" * 30)
    test_holiday_visibility()
    print("=" * 30)
    print("Test completed successfully!")