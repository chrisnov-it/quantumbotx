# Ramadan Trading Mode Documentation

## Overview

The Ramadan Trading Mode is a culturally-sensitive feature designed specifically for Muslim traders during the holy month of Ramadan. This feature automatically activates based on the Islamic calendar and provides trading adjustments that respect the spiritual practices of fasting, prayer times, and charitable giving.

## Features

### 1. Automatic Activation
- Automatically activates when the Islamic month of Ramadan begins
- Deactivates after Eid al-Fitr celebrations
- Uses estimated Islamic calendar dates (can be enhanced with proper Hijri calendar library)

### 2. Prayer Time Trading Pauses
The system automatically pauses trading during the following prayer times to respect spiritual practices:

#### Sahur Pause (03:30 - 05:00 WIB)
- Time for pre-dawn meal before fasting begins
- Spiritual preparation time
- Trading bots will pause execution during this period

#### Iftar Pause (18:00 - 19:30 WIB)
- Time for breaking the daily fast
- Family and community time
- Trading bots will pause execution during this period

#### Tarawih Pause (20:00 - 21:30 WIB)
- Special nightly prayers during Ramadan
- Spiritual devotion time
- Trading bots will pause execution during this period

### 3. Risk Management Adjustments
- **Reduced Risk Mode**: 20% risk reduction during fasting hours
- **Patience Mode**: Emphasis on quality over quantity in trading decisions
- **Optimal Trading Hours**: Recommended trading times (22:00 - 03:00 WIB) when traders are most alert

### 4. Spiritual and Cultural Features
- **Iftar Countdown**: Real-time countdown to Iftar time
- **Zakat Calculator**: Information and reminders about trading zakat obligations
- **Charity Tracker**: Track charitable donations throughout Ramadan
- **Patience Reminders**: Inspirational messages connecting trading principles with Islamic values
- **Ramadan Greetings**: Culturally appropriate greetings in Bahasa Indonesia

### 5. UI/UX Enhancements
- **Islamic Color Theme**: Green and gold color scheme
- **Crescent Moon Decorations**: Visual elements appropriate for Ramadan
- **Islamic Patterns**: Background patterns inspired by Islamic art
- **Ramadan Decorations**: Special UI elements for the holy month

## API Endpoints

### Ramadan Status
- **Endpoint**: `GET /api/ramadan/status`
- **Description**: Get current Ramadan trading mode status
- **Response**:
  ```json
  {
    "success": true,
    "is_ramadan": true,
    "holiday_name": "Ramadan Trading Mode",
    "start_date": "2024-03-11",
    "end_date": "2024-04-09",
    "trading_adjustments": {
      "sahur_pause": [3, 30, 5, 0],
      "iftar_pause": [18, 0, 19, 30],
      "tarawih_pause": [20, 0, 21, 30],
      "risk_reduction": 0.8,
      "optimal_hours": [[22, 0], [3, 0]],
      "patience_mode": true,
      "halal_focus": true
    },
    "ui_theme": {
      "primary_color": "#006600",
      "secondary_color": "#ffd700",
      "accent_color": "#ffffff",
      "background_gradient": "linear-gradient(135deg, #006600 0%, #ffd700 100%)",
      "crescent_moon": true,
      "islamic_patterns": true
    },
    "greeting": "🌙 Ramadan Mubarak! Semoga trading dan ibadah berkah"
  }
  ```

### Ramadan Features
- **Endpoint**: `GET /api/ramadan/features`
- **Description**: Get Ramadan-specific features data
- **Response**:
  ```json
  {
    "success": true,
    "is_ramadan": true,
    "features": {
      "iftar_countdown": {
        "hours": 5,
        "minutes": 30,
        "next_prayer": "Iftar"
      },
      "zakat_info": {
        "nissab_gold": 85,
        "nissab_silver": 595,
        "zakat_percentage": 2.5,
        "reminder": "Zakat perdagangan: 2.5% dari profit trading selama 1 tahun hijriah"
      },
      "charity_tracker": {
        "total_donated": 0.0,
        "monthly_target": 100.0,
        "progress_percentage": 0,
        "suggested_amount": 10.0
      },
      "patience_reminder": "🧠 Sabar dalam trading seperti puasa - hasil terbaik datang dengan kesabaran",
      "optimal_trading_hours": [[22, 0], [3, 0]]
    }
  }
  ```

### Pause Status
- **Endpoint**: `GET /api/ramadan/pause-status`
- **Description**: Check if trading is currently paused due to Ramadan prayer times
- **Response**:
  ```json
  {
    "success": true,
    "is_paused": true,
    "pause_reason": "Iftar time - breaking fast and family time",
    "message": "Iftar time - breaking fast and family time"
  }
  ```

## Integration with Trading Bots

### Bot Controller Integration
The trading bot controller checks for Ramadan pause status before executing trades:

```python
from core.seasonal.holiday_manager import holiday_manager

def should_pause_trading():
    """Check if trading should be paused due to Ramadan prayer times"""
    return holiday_manager.is_trading_paused()
```

### Risk Adjustment
Bots automatically adjust their risk parameters during Ramadan:

```python
from core.seasonal.holiday_manager import holiday_manager

def get_risk_multiplier():
    """Get risk reduction multiplier for current holiday"""
    return holiday_manager.get_risk_multiplier()
```

## Dashboard Features

### Ramadan Dashboard Page
Access the Ramadan dashboard through the "Ramadan Mode" link in the sidebar.

#### Key Components:
1. **Status Display**: Shows current Ramadan period and greeting
2. **Iftar Countdown**: Real-time countdown to Iftar time
3. **Trading Adjustments**: Displays prayer time pauses and risk adjustments
4. **Zakat Calculator**: Information about trading zakat obligations
5. **Patience Reminders**: Inspirational messages connecting trading with Islamic values

## Configuration

### Holiday Manager
The Ramadan configuration is managed in `core/seasonal/holiday_manager.py`:

```python
def _get_ramadan_config(self) -> HolidayConfig:
    return HolidayConfig(
        name="Ramadan Trading Mode",
        start_date=ramadan_start,
        end_date=ramadan_end,
        trading_adjustments={
            'sahur_pause': (3, 30, 5, 0),    # 03:30-05:00 WIB
            'iftar_pause': (18, 0, 19, 30),  # 18:00-19:30 WIB
            'tarawih_pause': (20, 0, 21, 30), # 20:00-21:30 WIB
            'risk_reduction': 0.8,  # 20% risk reduction during fasting
            'optimal_hours': [(22, 0), (3, 0)],  # 22:00-03:00 WIB
            'patience_mode': True,
            'halal_focus': True
        },
        ui_theme={
            'primary_color': '#006600',  # Islamic green
            'secondary_color': '#ffd700',  # Gold
            'accent_color': '#ffffff',   # White
            'background_gradient': 'linear-gradient(135deg, #006600 0%, #ffd700 100%)',
            'crescent_moon': True,
            'islamic_patterns': True
        },
        greetings=[
            "🌙 Ramadan Mubarak! Semoga trading dan ibadah berkah",
            "🕌 Puasa mengajarkan sabar - apply dalam trading juga!",
            # ... more greetings
        ]
    )
```

## Best Practices

### For Developers
1. **Respect Prayer Times**: Always check pause status before executing trades
2. **Cultural Sensitivity**: Use appropriate language and imagery
3. **Risk Management**: Implement reduced risk during fasting hours
4. **User Experience**: Provide clear information about Ramadan adjustments

### For Traders
1. **Plan Ahead**: Schedule trades outside of prayer time pauses
2. **Risk Awareness**: Understand that risk is reduced during Ramadan
3. **Spiritual Connection**: Use patience reminders to connect trading with spiritual values
4. **Charitable Giving**: Track and consider charitable donations from trading profits

## Future Enhancements

### Planned Features
1. **Proper Hijri Calendar Integration**: Use accurate Islamic calendar library
2. **Customizable Prayer Times**: Allow users to set their local prayer times
3. **Community Features**: Ramadan trading challenges and community goals
4. **Advanced Zakat Calculator**: Detailed zakat calculations based on actual trading profits
5. **Multi-Language Support**: Additional languages for international Muslim traders

## Conclusion

The Ramadan Trading Mode provides a respectful and culturally-aware trading experience for Muslim traders during the holy month of Ramadan. By automatically adjusting trading behavior to align with spiritual practices, this feature helps traders maintain their religious observances while continuing to engage in trading activities.