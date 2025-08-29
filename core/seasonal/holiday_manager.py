# core/seasonal/holiday_manager.py
"""
🎄🌙 Seasonal Trading Mode Manager - Auto Holiday Detection
Automatically activates Christmas, Ramadan, and other cultural trading modes
Built specifically for Indonesian Catholic and Muslim traders
"""

from datetime import datetime, date
from typing import Dict, List, Any, Optional
import calendar
from dataclasses import dataclass

@dataclass
class HolidayConfig:
    """Configuration for holiday trading modes"""
    name: str
    start_date: date
    end_date: date
    trading_adjustments: Dict[str, Any]
    ui_theme: Dict[str, str]
    greetings: List[str]

class IndonesianHolidayManager:
    """Manages seasonal trading modes for Indonesian traders"""
    
    def __init__(self):
        self.current_year = datetime.now().year
        self.holidays = self._initialize_holidays()
        
    def _initialize_holidays(self) -> Dict[str, HolidayConfig]:
        """Initialize all Indonesian holiday configurations"""
        return {
            'christmas': self._get_christmas_config(),
            'ramadan': self._get_ramadan_config(),
            'new_year': self._get_new_year_config(),
            'eid': self._get_eid_config()
        }
    
    def _get_christmas_config(self) -> HolidayConfig:
        """Christmas trading mode configuration"""
        return HolidayConfig(
            name="Christmas Trading Mode",
            start_date=date(self.current_year, 12, 20),
            end_date=date(self.current_year + 1, 1, 6),  # Until Epiphany
            trading_adjustments={
                'risk_reduction': 0.5,  # 50% risk reduction
                'pause_dates': [
                    date(self.current_year, 12, 24),  # Christmas Eve
                    date(self.current_year, 12, 25),  # Christmas Day
                    date(self.current_year, 12, 26),  # Boxing Day
                    date(self.current_year, 12, 31),  # New Year's Eve
                    date(self.current_year + 1, 1, 1)   # New Year's Day
                ],
                'early_close_dates': [
                    date(self.current_year, 12, 24),
                    date(self.current_year, 12, 31)
                ],
                'lot_size_multiplier': 0.7,  # Reduce lot sizes by 30%
                'max_trades_per_day': 3
            },
            ui_theme={
                'primary_color': '#c41e3a',  # Christmas red
                'secondary_color': '#228b22',  # Christmas green
                'accent_color': '#ffd700',   # Gold
                'background_gradient': 'linear-gradient(135deg, #c41e3a 0%, #228b22 100%)',
                'snow_effect': True,
                'christmas_icons': True
            },
            greetings=[
                "🎄 Selamat Hari Natal! Berkat Tuhan menyertai trading Anda",
                "✨ Natal penuh kasih, trading penuh berkah",
                "🎁 Hadiah terbaik adalah konsistensi dalam trading",
                "⭐ Seperti Bintang Betlehem, semoga trading Anda terarah",
                "🕯️ Terang Natal membawa wisdom dalam setiap keputusan trading",
                "🙏 Damai Natal, profit yang penuh berkah"
            ]
        )
    
    def _get_ramadan_config(self) -> HolidayConfig:
        """Ramadan trading mode configuration"""
        # Note: Ramadan dates change yearly based on lunar calendar
        # This is a simplified version - in production, use proper Islamic calendar library
        ramadan_start = self._estimate_ramadan_start()
        ramadan_end = self._estimate_ramadan_end()
        
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
                "✨ Lailatul Qadar trading wisdom: Quality over quantity",
                "🤲 Barakallahu fiikum dalam trading bulan suci ini",
                "💰 Ingat zakat dari profit trading - berkah berlipat",
                "🌅 Sahur dengan doa, trading dengan tawakal"
            ]
        )
    
    def _get_new_year_config(self) -> HolidayConfig:
        """New Year trading mode configuration"""
        return HolidayConfig(
            name="New Year Trading Mode",
            start_date=date(self.current_year, 12, 30),
            end_date=date(self.current_year + 1, 1, 3),
            trading_adjustments={
                'reflection_mode': True,
                'goal_setting': True,
                'risk_reduction': 0.6,
                'pause_dates': [date(self.current_year + 1, 1, 1)]
            },
            ui_theme={
                'primary_color': '#ff6b35',
                'secondary_color': '#f7931e',
                'accent_color': '#ffd700',
                'background_gradient': 'linear-gradient(135deg, #ff6b35 0%, #f7931e 100%)',
                'fireworks_effect': True
            },
            greetings=[
                "🎊 Selamat Tahun Baru! New year, new trading goals!",
                "✨ 2024: Tahun konsistensi dan profit berkah",
                "🎯 Resolution: Better risk management, bigger profits",
                "🙏 Dengan berkat Tuhan, tahun ini akan lebih baik"
            ]
        )
    
    def _get_eid_config(self) -> HolidayConfig:
        """Eid al-Fitr trading mode configuration"""
        from datetime import timedelta
        eid_date = self._estimate_eid_date()
        
        return HolidayConfig(
            name="Eid al-Fitr Trading Mode",
            start_date=eid_date,
            end_date=eid_date + timedelta(days=2),
            trading_adjustments={
                'celebration_mode': True,
                'risk_reduction': 0.3,  # Very conservative during celebration
                'family_time_priority': True,
                'pause_dates': [eid_date]
            },
            ui_theme={
                'primary_color': '#00a86b',
                'secondary_color': '#ffd700',
                'accent_color': '#ffffff',
                'background_gradient': 'linear-gradient(135deg, #00a86b 0%, #ffd700 100%)',
                'eid_decorations': True
            },
            greetings=[
                "🌙 Eid Mubarak! Selamat Hari Raya Idul Fitri!",
                "✨ Mohon maaf lahir batin, semoga trading semakin berkah",
                "🎊 Fitri celebration: Time for family and reflection",
                "💰 Alhamdulillah, calculate your Ramadan trading zakat!"
            ]
        )
    
    def get_current_holiday_mode(self) -> Optional[HolidayConfig]:
        """Get currently active holiday mode"""
        today = date.today()
        
        for holiday_name, config in self.holidays.items():
            if config.start_date <= today <= config.end_date:
                return config
        
        return None
    
    def get_holiday_adjustments(self) -> Dict[str, Any]:
        """Get trading adjustments for current holiday"""
        current_holiday = self.get_current_holiday_mode()
        
        if current_holiday:
            return {
                'active_holiday': current_holiday.name,
                'adjustments': current_holiday.trading_adjustments,
                'ui_theme': current_holiday.ui_theme,
                'greeting': self._get_random_greeting(current_holiday.greetings)
            }
        
        return {'active_holiday': None}
    
    def is_trading_paused(self) -> bool:
        """Check if trading should be paused today"""
        today = date.today()
        current_holiday = self.get_current_holiday_mode()
        
        if current_holiday and 'pause_dates' in current_holiday.trading_adjustments:
            return today in current_holiday.trading_adjustments['pause_dates']
        
        return False
    
    def get_risk_multiplier(self) -> float:
        """Get risk reduction multiplier for current holiday"""
        current_holiday = self.get_current_holiday_mode()
        
        if current_holiday and 'risk_reduction' in current_holiday.trading_adjustments:
            return current_holiday.trading_adjustments['risk_reduction']
        
        return 1.0  # No reduction
    
    def get_holiday_greeting(self) -> str:
        """Get appropriate greeting for current holiday"""
        current_holiday = self.get_current_holiday_mode()
        
        if current_holiday:
            return self._get_random_greeting(current_holiday.greetings)
        
        return "🚀 Selamat trading! Semoga hari ini profitable dan berkah!"
    
    def _get_random_greeting(self, greetings: List[str]) -> str:
        """Get random greeting from list"""
        import random
        return random.choice(greetings)
    
    def _estimate_ramadan_start(self) -> date:
        """Estimate Ramadan start date (simplified - use proper Islamic calendar in production)"""
        # This is a rough estimation - in production, use proper Hijri calendar library
        # Ramadan 2024 is estimated around March 11
        if self.current_year == 2024:
            return date(2024, 3, 11)
        elif self.current_year == 2025:
            return date(2025, 2, 28)  # Estimated
        else:
            # Fallback calculation
            return date(self.current_year, 3, 11)
    
    def _estimate_ramadan_end(self) -> date:
        """Estimate Ramadan end date"""
        from datetime import timedelta
        start = self._estimate_ramadan_start()
        return start + timedelta(days=29)  # Ramadan is 29-30 days
    
    def _estimate_eid_date(self) -> date:
        """Estimate Eid al-Fitr date"""
        from datetime import timedelta
        ramadan_end = self._estimate_ramadan_end()
        return ramadan_end + timedelta(days=1)

# Global holiday manager instance
holiday_manager = IndonesianHolidayManager()

def get_current_holiday_adjustments() -> Dict[str, Any]:
    """Get current holiday adjustments - main function for other modules"""
    return holiday_manager.get_holiday_adjustments()

def is_holiday_trading_paused() -> bool:
    """Check if trading is paused due to holiday"""
    return holiday_manager.is_trading_paused()

def get_holiday_risk_multiplier() -> float:
    """Get risk multiplier for holiday mode"""
    return holiday_manager.get_risk_multiplier()

def get_holiday_greeting() -> str:
    """Get current holiday greeting"""
    return holiday_manager.get_holiday_greeting()