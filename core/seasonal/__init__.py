# core/seasonal/__init__.py
"""
🎄🌙 Seasonal Trading Modes
Auto-activating cultural and religious trading features for Indonesian traders
"""

from .holiday_manager import (
    holiday_manager,
    get_current_holiday_adjustments,
    is_holiday_trading_paused,
    get_holiday_risk_multiplier,
    get_holiday_greeting
)

__all__ = [
    'holiday_manager',
    'get_current_holiday_adjustments',
    'is_holiday_trading_paused', 
    'get_holiday_risk_multiplier',
    'get_holiday_greeting'
]