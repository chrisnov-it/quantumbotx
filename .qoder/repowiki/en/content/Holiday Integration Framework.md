# Holiday Integration Framework

<cite>
**Referenced Files in This Document**   
- [holiday_manager.py](file://core/seasonal/holiday_manager.py#L1-L388)
- [api_holiday.py](file://core/routes/api_holiday.py#L1-L99)
- [api_ramadan.py](file://core/routes/api_ramadan.py#L1-L141)
- [base.html](file://templates/base.html#L80-L182)
- [ramadan.html](file://templates/ramadan.html#L1-L244)
- [main.js](file://static/js/main.js#L1-L96)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [Holiday Configuration Structure](#holiday-configuration-structure)
5. [API Integration](#api-integration)
6. [Frontend Integration](#frontend-integration)
7. [Holiday Modes and Features](#holiday-modes-and-features)
8. [Testing and Validation](#testing-and-validation)
9. [Troubleshooting Guide](#troubleshooting-guide)

## Introduction

The Holiday Integration Framework is a specialized system designed to automatically detect and adapt to cultural and religious holidays, particularly focusing on Indonesian Catholic and Muslim traders. The framework provides seasonal trading modes for major holidays including Christmas, Ramadan, Eid al-Fitr, and New Year, implementing appropriate trading adjustments and UI themes for each period.

The system automatically activates holiday modes based on date ranges and applies various trading restrictions, risk adjustments, and visual themes to create a culturally sensitive trading environment. It includes special features for Ramadan such as prayer time pauses, Iftar countdowns, and Zakat calculation tools.

**Section sources**
- [holiday_manager.py](file://core/seasonal/holiday_manager.py#L1-L20)

## Architecture Overview

The Holiday Integration Framework follows a modular architecture with clear separation between business logic, API interfaces, and frontend presentation. The system is built around a central HolidayManager that detects active holidays and provides configuration data to other components.

``mermaid
graph TD
subgraph "Frontend"
UI[User Interface]
Theme[Theme Engine]
Countdown[Iftar Countdown]
Zakat[Zakat Calculator]
end
subgraph "Backend API"
HolidayAPI[/api/holiday/status\]
RamadanAPI[/api/ramadan/*\]
PauseAPI[/api/holiday/pause-status\]
end
subgraph "Core Logic"
Manager[IndonesianHolidayManager]
Config[HolidayConfig]
Detector[Holiday Detector]
end
UI --> HolidayAPI
UI --> RamadanAPI
HolidayAPI --> Manager
RamadanAPI --> Manager
PauseAPI --> Manager
Manager --> Config
Theme --> Manager
Countdown --> Manager
Zakat --> Manager
style Manager fill:#f9f,stroke:#333
style HolidayAPI fill:#bbf,stroke:#333
style UI fill:#9f9,stroke:#333
```

**Diagram sources**
- [holiday_manager.py](file://core/seasonal/holiday_manager.py#L22-L365)
- [api_holiday.py](file://core/routes/api_holiday.py#L1-L99)
- [api_ramadan.py](file://core/routes/api_ramadan.py#L1-L141)

## Core Components

The framework consists of several key components that work together to provide holiday integration functionality:

### IndonesianHolidayManager Class

The central component of the framework is the `IndonesianHolidayManager` class, which manages all holiday-related functionality. This class initializes holiday configurations, detects active holidays, and provides access to holiday-specific features.

``mermaid
classDiagram
class IndonesianHolidayManager {
+current_year int
+holidays Dict[str, HolidayConfig]
+__init__()
+_initialize_holidays() Dict[str, HolidayConfig]
+get_current_holiday_mode() HolidayConfig
+get_holiday_adjustments() Dict[str, Any]
+is_trading_paused() bool
+get_ramadan_features() Dict[str, Any]
+get_risk_multiplier() float
+get_holiday_greeting() str
+_is_ramadan_pause_time() bool
+_estimate_ramadan_start() date
+_estimate_ramadan_end() date
+_estimate_eid_date() date
}
class HolidayConfig {
+name str
+start_date date
+end_date date
+trading_adjustments Dict[str, Any]
+ui_theme Dict[str, Any]
+greetings List[str]
}
class HolidayIntegrationFramework {
+holiday_manager IndonesianHolidayManager
+get_current_holiday_adjustments() Dict[str, Any]
+is_holiday_trading_paused() bool
+get_holiday_risk_multiplier() float
+get_holiday_greeting() str
+get_current_holiday_mode() HolidayConfig
}
HolidayIntegrationFramework --> IndonesianHolidayManager : "contains"
IndonesianHolidayManager --> HolidayConfig : "contains"
```

**Diagram sources**
- [holiday_manager.py](file://core/seasonal/holiday_manager.py#L22-L365)

**Section sources**
- [holiday_manager.py](file://core/seasonal/holiday_manager.py#L22-L365)

## Holiday Configuration Structure

The framework uses a structured configuration system to define holiday properties through the `HolidayConfig` dataclass. Each holiday configuration includes several key components:

### Configuration Properties

- **name**: Display name of the holiday mode
- **start_date**: When the holiday mode begins
- **end_date**: When the holiday mode ends
- **trading_adjustments**: Trading parameters specific to the holiday
- **ui_theme**: Visual theme for the holiday period
- **greetings**: Cultural greetings displayed during the holiday

### Trading Adjustments

Each holiday can define specific trading adjustments that modify trading behavior:

``mermaid
flowchart TD
Start([Holiday Detection]) --> TradingAdjustments["Apply Trading Adjustments"]
TradingAdjustments --> RiskReduction["Apply Risk Reduction"]
TradingAdjustments --> PauseDates["Check Pause Dates"]
TradingAdjustments --> LotSize["Adjust Lot Size"]
TradingAdjustments --> MaxTrades["Limit Daily Trades"]
RiskReduction --> Continue
PauseDates --> CheckRamadan["Is Ramadan?"]
CheckRamadan --> |Yes| RamadanPauses["Check Prayer Time Pauses"]
CheckRamadan --> |No| CheckPauseDates["Check Fixed Pause Dates"]
RamadanPauses --> Continue
CheckPauseDates --> Continue
LotSize --> Continue
MaxTrades --> Continue
Continue --> ApplyTheme["Apply UI Theme"]
ApplyTheme --> DisplayGreeting["Display Cultural Greeting"]
DisplayGreeting --> End([Holiday Mode Active])
```

**Diagram sources**
- [holiday_manager.py](file://core/seasonal/holiday_manager.py#L13-L20)
- [holiday_manager.py](file://core/seasonal/holiday_manager.py#L60-L365)

**Section sources**
- [holiday_manager.py](file://core/seasonal/holiday_manager.py#L13-L20)

## API Integration

The framework provides RESTful API endpoints that allow frontend components to access holiday information and status.

### Main Holiday API Endpoints

``mermaid
sequenceDiagram
participant Frontend
participant HolidayAPI
participant HolidayManager
Frontend->>HolidayAPI : GET /api/holiday/status
HolidayAPI->>HolidayManager : get_current_holiday_mode()
HolidayManager-->>HolidayAPI : HolidayConfig or None
HolidayAPI->>HolidayManager : get_holiday_greeting()
HolidayManager-->>HolidayAPI : Greeting string
alt Holiday Active
HolidayAPI->>HolidayManager : get_ramadan_features() if Ramadan
HolidayManager-->>HolidayAPI : Ramadan features
HolidayAPI-->>Frontend : {success : true, is_holiday : true, holiday_data}
else No Holiday
HolidayAPI-->>Frontend : {success : true, is_holiday : false}
end
```

**Diagram sources**
- [api_holiday.py](file://core/routes/api_holiday.py#L15-L70)

### Ramadan-Specific API Endpoints

The framework includes specialized endpoints for Ramadan features:

``mermaid
sequenceDiagram
participant Frontend
participant RamadanAPI
participant HolidayManager
Frontend->>RamadanAPI : GET /api/ramadan/features
RamadanAPI->>HolidayManager : get_ramadan_features()
HolidayManager-->>RamadanAPI : Ramadan features data
RamadanAPI-->>Frontend : {success : true, features : {...}}
Frontend->>RamadanAPI : GET /api/ramadan/zakat-calculator
RamadanAPI->>HolidayManager : _calculate_zakat_info()
HolidayManager-->>RamadanAPI : Zakat information
RamadanAPI-->>Frontend : {success : true, zakat_info : {...}}
```

**Diagram sources**
- [api_ramadan.py](file://core/routes/api_ramadan.py#L45-L70)

**Section sources**
- [api_holiday.py](file://core/routes/api_holiday.py#L15-L70)
- [api_ramadan.py](file://core/routes/api_ramadan.py#L15-L141)

## Frontend Integration

The frontend components integrate with the holiday framework to provide visual feedback and specialized features during holiday periods.

### Theme Application Process

``mermaid
sequenceDiagram
participant DOM
participant JavaScript
participant API
DOM->>JavaScript : DOMContentLoaded
JavaScript->>API : fetch('/api/holiday/status')
API-->>JavaScript : Holiday status data
alt Holiday Active
JavaScript->>JavaScript : applyHolidayTheme(data.ui_theme)
JavaScript->>DOM : Update CSS variables
JavaScript->>DOM : Show holiday banner
alt Ramadan Active
JavaScript->>DOM : Show Ramadan navigation link
JavaScript->>DOM : Update Iftar countdown
end
alt Christmas Active
JavaScript->>DOM : Show Christmas countdown
JavaScript->>DOM : Create snow effect
end
else No Holiday
JavaScript->>DOM : Hide Ramadan navigation link
end
```

**Diagram sources**
- [base.html](file://templates/base.html#L85-L182)
- [main.js](file://static/js/main.js#L1-L96)

### UI Theme Application

The framework applies holiday themes by dynamically updating CSS variables in the document:

```javascript
function applyHolidayTheme(theme) {
    const styleElement = document.getElementById('holiday-styles');
    if (!styleElement) return;
    
    let css = '';
    if (theme.background_gradient) {
        css += `body { background: ${theme.background_gradient}; }`;
    }
    if (theme.primary_color) {
        css += `:root { --holiday-primary: ${theme.primary_color}; }`;
    }
    if (theme.secondary_color) {
        css += `:root { --holiday-secondary: ${theme.secondary_color}; }`;
    }
    if (theme.accent_color) {
        css += `:root { --holiday-accent: ${theme.accent_color}; }`;
    }
    
    styleElement.textContent = css;
}
```

**Section sources**
- [base.html](file://templates/base.html#L85-L118)

## Holiday Modes and Features

The framework supports multiple holiday modes, each with specific features and trading adjustments.

### Supported Holiday Modes

| Holiday | Period | Key Features |
|--------|-------|------------|
| Christmas | Dec 20 - Jan 6 | 50% risk reduction, trading pauses on holidays, Christmas theme with snow effect |
| Ramadan | Lunar-based | Prayer time pauses, Iftar countdown, Zakat calculator, 20% risk reduction |
| Eid al-Fitr | 3 days after Ramadan | Celebration mode, family time priority, conservative trading |
| New Year | Dec 30 - Jan 3 | Reflection mode, goal setting, 40% risk reduction |

### Ramadan-Specific Features

The Ramadan mode includes several specialized features to support traders during the holy month:

``mermaid
flowchart TD
RamadanStart([Ramadan Begins]) --> PrayerPauses["Implement Prayer Time Pauses"]
PrayerPauses --> SahurPause["03:30-05:00 WIB: Sahur Pause"]
PrayerPauses --> IftarPause["18:00-19:30 WIB: Iftar Pause"]
PrayerPauses --> TarawihPause["20:00-21:30 WIB: Tarawih Pause"]
RamadanStart --> RiskAdjustment["Apply Reduced Risk Mode"]
RiskAdjustment --> 20PercentReduction["20% Risk Reduction"]
RamadanStart --> OptimalHours["Identify Optimal Trading Hours"]
OptimalHours --> 2200to0300["22:00-03:00 WIB"]
RamadanStart --> ZakatCalculator["Provide Zakat Calculation Tools"]
ZakatCalculator --> NissabInfo["Nissab Gold: 85g"]
ZakatCalculator --> Percentage["Zakat: 2.5% of profits"]
RamadanStart --> PatienceMode["Encourage Patience"]
PatienceMode --> QualityOverQuantity["Focus on quality trades"]
PatienceMode --> PatienceReminders["Display patience reminders"]
PrayerPauses --> Continue
20PercentReduction --> Continue
2200to0300 --> Continue
ZakatCalculator --> Continue
PatienceReminders --> Continue
Continue --> EnhancedTrading["Enhanced Ramadan Trading Experience"]
```

**Section sources**
- [holiday_manager.py](file://core/seasonal/holiday_manager.py#L120-L170)
- [ramadan.html](file://templates/ramadan.html#L1-L244)

## Testing and Validation

The framework includes comprehensive testing to ensure proper functionality across different holiday scenarios.

### Integration Test Workflow

``mermaid
flowchart TD
TestStart([Test Execution]) --> HolidayDetection["Test Holiday Detection"]
HolidayDetection --> ActiveHoliday["Check for Active Holiday"]
ActiveHoliday --> DisplayHolidayInfo["Display Holiday Name and Period"]
HolidayDetection --> RamadanFeatures["Test Ramadan Features"]
RamadanFeatures --> IftarCountdown["Verify Iftar Countdown"]
RamadanFeatures --> PatienceReminder["Check Patience Reminder"]
HolidayDetection --> RiskMultiplier["Test Risk Multiplier"]
RiskMultiplier --> CurrentMultiplier["Display Current Risk Multiplier"]
HolidayDetection --> PauseStatus["Test Trading Pause Status"]
PauseStatus --> CurrentStatus["Display Pause Status"]
PauseStatus --> PauseReason["Show Pause Reason if Paused"]
ActiveHoliday --> End
IftarCountdown --> End
PatienceReminder --> End
CurrentMultiplier --> End
CurrentStatus --> End
PauseReason --> End
End([Test Completed Successfully])
```

**Section sources**
- [test_holiday_integration.py](file://testing/test_holiday_integration.py#L1-L78)

## Troubleshooting Guide

This section provides guidance for common issues and their solutions when working with the Holiday Integration Framework.

### Common Issues and Solutions

**Issue: Holiday mode not activating**
- **Check**: Verify the current date falls within the holiday period
- **Check**: Ensure the holiday configuration dates are correct for the current year
- **Solution**: Update the holiday start and end dates in the configuration

**Issue: Trading not pausing during Ramadan prayer times**
- **Check**: Verify the current time matches the defined prayer time windows
- **Check**: Confirm the system timezone is set to WIB (Western Indonesian Time)
- **Solution**: Adjust the sahur_pause, iftar_pause, or tarawih_pause time ranges

**Issue: UI theme not applying correctly**
- **Check**: Verify the API response includes ui_theme data
- **Check**: Ensure the CSS style element with ID 'holiday-styles' exists in the DOM
- **Solution**: Add the style element to the HTML template if missing

**Issue: Iftar countdown showing incorrect values**
- **Check**: Verify the system clock is synchronized
- **Check**: Confirm the iftar time is set to 18:00 WIB in the code
- **Solution**: Adjust the iftar_time variable in the get_ramadan_features method

**Issue: Zakat calculator not displaying**
- **Check**: Verify the user is within the Ramadan period
- **Check**: Ensure the /api/ramadan/zakat-calculator endpoint is accessible
- **Solution**: Check server logs for errors in the Zakat calculator route

**Section sources**
- [holiday_manager.py](file://core/seasonal/holiday_manager.py#L250-L350)
- [api_ramadan.py](file://core/routes/api_ramadan.py#L118-L141)