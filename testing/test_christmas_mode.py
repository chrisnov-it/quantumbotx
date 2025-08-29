#!/usr/bin/env python3
# test_christmas_mode.py
"""
🎄 Christmas Trading Mode Test
Test the automatic holiday detection and Christmas features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from core.seasonal.holiday_manager import IndonesianHolidayManager

def test_christmas_mode():
    """Test Christmas trading mode functionality"""
    print("🎄 Testing Christmas Trading Mode Features...")
    
    holiday_manager = IndonesianHolidayManager()
    
    # Test current date
    print(f"\n📅 Current Date: {date.today()}")
    
    # Test holiday detection
    current_holiday = holiday_manager.get_current_holiday_mode()
    if current_holiday:
        print(f"🎉 Active Holiday: {current_holiday.name}")
        print(f"🎨 Theme: {current_holiday.ui_theme}")
        print(f"⚠️ Risk Reduction: {current_holiday.trading_adjustments.get('risk_reduction', 1.0) * 100:.0f}%")
    else:
        print("📈 No active holiday mode - normal trading")
    
    # Test Christmas-specific features
    print("\n🎄 Christmas Mode Features:")
    
    # Test Christmas dates (simulate December dates)
    test_dates = [
        date(2024, 12, 20),  # Start of Christmas mode
        date(2024, 12, 24),  # Christmas Eve
        date(2024, 12, 25),  # Christmas Day
        date(2024, 12, 31),  # New Year's Eve
        date(2025, 1, 1),    # New Year's Day
        date(2025, 1, 6)     # Epiphany
    ]
    
    for test_date in test_dates:
        # Temporarily override current year for testing
        original_year = holiday_manager.current_year
        holiday_manager.current_year = test_date.year
        holiday_manager.holidays = holiday_manager._initialize_holidays()
        
        # Test if date falls in Christmas mode
        christmas_config = holiday_manager.holidays['christmas']
        is_christmas_period = christmas_config.start_date <= test_date <= christmas_config.end_date
        is_paused = test_date in christmas_config.trading_adjustments.get('pause_dates', [])
        
        status = "🎄 CHRISTMAS MODE"
        if is_paused:
            status += " - TRADING PAUSED ⏸️"
        elif not is_christmas_period:
            status = "📈 Normal Trading"
        
        print(f"  {test_date.strftime('%Y-%m-%d')}: {status}")
        
        # Restore original year
        holiday_manager.current_year = original_year
        holiday_manager.holidays = holiday_manager._initialize_holidays()
    
    # Test greetings
    print("\n🎅 Christmas Greetings:")
    christmas_config = holiday_manager.holidays['christmas']
    for i, greeting in enumerate(christmas_config.greetings[:3]):
        print(f"  {i+1}. {greeting}")
    
    # Test risk adjustments
    print("\n📊 Trading Adjustments:")
    adjustments = christmas_config.trading_adjustments
    print(f"  • Risk Reduction: {adjustments['risk_reduction'] * 100:.0f}%")
    print(f"  • Lot Size Multiplier: {adjustments['lot_size_multiplier'] * 100:.0f}%")
    print(f"  • Max Trades/Day: {adjustments['max_trades_per_day']}")
    print(f"  • Pause Dates: {len(adjustments['pause_dates'])} days")
    
    # Test UI theme
    print("\n🎨 Christmas UI Theme:")
    theme = christmas_config.ui_theme
    print(f"  • Primary Color: {theme['primary_color']} (Christmas Red)")
    print(f"  • Secondary Color: {theme['secondary_color']} (Christmas Green)")
    print(f"  • Snow Effect: {theme['snow_effect']}")
    print(f"  • Christmas Icons: {theme['christmas_icons']}")
    
    print("\n🎉 Christmas Mode Test Complete!")
    print("✨ Ready to auto-activate in December 2024!")

def test_all_holidays():
    """Test all holiday modes"""
    print("\n🌟 Testing All Holiday Modes...")
    
    holiday_manager = IndonesianHolidayManager()
    
    for holiday_name, config in holiday_manager.holidays.items():
        print(f"\n🎯 {holiday_name.upper()} MODE:")
        print(f"  📅 Period: {config.start_date} to {config.end_date}")
        print(f"  🎨 Theme Colors: {config.ui_theme.get('primary_color', 'N/A')}")
        print(f"  📝 Sample Greeting: {config.greetings[0] if config.greetings else 'N/A'}")
        
        if 'risk_reduction' in config.trading_adjustments:
            risk_reduction = config.trading_adjustments['risk_reduction']
            print(f"  ⚠️ Risk Reduction: {risk_reduction * 100:.0f}%")

if __name__ == "__main__":
    test_christmas_mode()
    test_all_holidays()
    
    print("\n🚀 READY TO LAUNCH!")
    print("🎄 Christmas mode will auto-activate on December 20th!")
    print("🌙 Ramadan mode will auto-activate when Ramadan begins!")
    print("✨ Your Catholic and Muslim friends will LOVE this!")