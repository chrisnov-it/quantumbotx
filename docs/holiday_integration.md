# Holiday Integration System

## Overview

The QuantumBotX platform includes an automatic holiday detection system that seamlessly activates culturally-appropriate trading modes for both Christian and Muslim traders. This system automatically adjusts trading parameters, UI themes, and risk management settings based on calendar dates.

## Features

### Automatic Activation
- **Christmas Mode**: Automatically activates from December 20th through January 6th
- **Ramadan Mode**: Automatically activates during the Islamic holy month of Ramadan
- **New Year Mode**: Automatically activates around New Year's Day
- **Eid al-Fitr Mode**: Automatically activates during the Eid al-Fitr celebration

### Dynamic UI Visibility
- **Conditional Navigation**: Holiday-specific pages (like Ramadan) only appear in navigation when active
- **Dashboard Widgets**: Holiday-specific widgets appear automatically on the main dashboard
- **Thematic Elements**: Visual themes and effects activate based on the current holiday

### Ramadan Trading Mode

When Ramadan is detected, the system automatically applies:

1. **Trading Pauses**:
   - Sahur: 03:30-05:00 WIB
   - Iftar: 18:00-19:30 WIB
   - Tarawih: 20:00-21:30 WIB

2. **Risk Adjustments**:
   - 20% risk reduction during fasting hours
   - Reduced position sizing
   - Conservative trade execution

3. **UI Enhancements**:
   - Islamic green and gold color scheme
   - Crescent moon decorations
   - Iftar countdown timer
   - Patience reminders

4. **Special Features**:
   - Zakat calculator
   - Charity tracker
   - Optimal trading hours guidance
   - Patience-focused trading advice

### Christmas Trading Mode

When Christmas is detected, the system automatically applies:

1. **Trading Pauses**:
   - December 24th (Christmas Eve)
   - December 25th (Christmas Day)
   - December 26th (Boxing Day)
   - December 31st (New Year's Eve)
   - January 1st (New Year's Day)

2. **Risk Adjustments**:
   - 50% risk reduction during the holiday period
   - 30% reduction in lot sizes
   - Maximum of 3 trades per day

3. **UI Enhancements**:
   - Christmas red and green color scheme
   - Snow effect animation
   - Christmas countdown timer

## Implementation Details

### Backend Components

1. **Holiday Manager** (`core/seasonal/holiday_manager.py`):
   - Detects active holidays based on current date
   - Provides holiday-specific configurations
   - Calculates prayer times for Ramadan
   - Manages trading adjustments

2. **API Endpoints**:
   - `/api/holiday/status` - Get current holiday status
   - `/api/holiday/pause-status` - Check if trading is paused
   - `/api/ramadan/features` - Get Ramadan-specific features

### Frontend Integration

1. **Base Template** (`templates/base.html`):
   - Global holiday detection script
   - Dynamic CSS theme application
   - Holiday banner display
   - Conditional navigation visibility

2. **Dashboard** (`templates/index.html`):
   - Holiday-specific widgets
   - Iftar countdown timer (Ramadan)
   - Christmas countdown timer
   - Risk adjustment indicators
   - Patience reminders (Ramadan)

3. **Holiday Pages**:
   - Dedicated Ramadan page (only visible when active)
   - Informational content about automatic activation

## Benefits

1. **Cultural Sensitivity**: Automatically respects religious observances
2. **Risk Management**: Reduces trading activity during distracted periods
3. **User Experience**: Seamless integration without manual configuration
4. **Inclusivity**: Supports both Christian and Muslim trading traditions
5. **Automation**: No user intervention required for activation
6. **Clean Interface**: Holiday-specific navigation only appears when relevant

## Technical Notes

- Holiday dates are estimated for Ramadan due to the lunar calendar
- Production implementations should use proper Islamic calendar libraries
- UI themes are applied dynamically through CSS variables
- Trading pauses are checked in real-time during bot execution
- Navigation elements are conditionally displayed based on holiday status