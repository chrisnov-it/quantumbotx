# core/routes/api_holiday.py
"""
API endpoints for holiday detection and integration
"""

from flask import Blueprint, jsonify
from core.seasonal.holiday_manager import holiday_manager
import logging

api_holiday = Blueprint('api_holiday', __name__)
logger = logging.getLogger(__name__)

@api_holiday.route('/api/holiday/status')
def get_holiday_status():
    """Get current holiday status for dashboard integration"""
    try:
        current_holiday = holiday_manager.get_current_holiday_mode()
        
        if not current_holiday:
            return jsonify({
                'success': True,
                'is_holiday': False,
                'message': 'No active holiday'
            })
        
        # Prepare holiday data for frontend
        holiday_data = {
            'success': True,
            'is_holiday': True,
            'holiday_name': current_holiday.name,
            'greeting': holiday_manager.get_holiday_greeting(),
            'ui_theme': current_holiday.ui_theme,
            'trading_adjustments': current_holiday.trading_adjustments
        }
        
        # Add Ramadan-specific features if active
        if current_holiday.name == "Ramadan Trading Mode":
            ramadan_features = holiday_manager.get_ramadan_features()
            holiday_data['ramadan_features'] = ramadan_features
        
        return jsonify(holiday_data)
    except Exception as e:
        logger.error(f"Error getting holiday status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_holiday.route('/api/holiday/pause-status')
def get_holiday_pause_status():
    """Check if trading is currently paused due to holiday"""
    try:
        is_paused = holiday_manager.is_trading_paused()
        pause_reason = ""
        
        if is_paused:
            current_holiday = holiday_manager.get_current_holiday_mode()
            if current_holiday:
                pause_reason = f"Trading paused due to {current_holiday.name}"
                
                # For Ramadan, provide more specific pause reasons
                if current_holiday.name == "Ramadan Trading Mode":
                    # Determine which prayer time is causing the pause
                    from datetime import datetime
                    now = datetime.now()
                    current_time = (now.hour, now.minute)
                    
                    adjustments = current_holiday.trading_adjustments
                    
                    # Check Sahur pause
                    if 'sahur_pause' in adjustments:
                        start_hour, start_min, end_hour, end_min = adjustments['sahur_pause']
                        if (start_hour, start_min) <= current_time <= (end_hour, end_min):
                            pause_reason = "Sahur time - time for spiritual reflection and preparation"
                    
                    # Check Iftar pause
                    if 'iftar_pause' in adjustments:
                        start_hour, start_min, end_hour, end_min = adjustments['iftar_pause']
                        if (start_hour, start_min) <= current_time <= (end_hour, end_min):
                            pause_reason = "Iftar time - breaking fast and family time"
                    
                    # Check Tarawih pause
                    if 'tarawih_pause' in adjustments:
                        start_hour, start_min, end_hour, end_min = adjustments['tarawih_pause']
                        if (start_hour, start_min) <= current_time <= (end_hour, end_min):
                            pause_reason = "Tarawih prayers - spiritual devotion time"
        
        return jsonify({
            'success': True,
            'is_paused': is_paused,
            'pause_reason': pause_reason,
            'message': pause_reason if is_paused else "Trading is active"
        })
    except Exception as e:
        logger.error(f"Error checking holiday pause status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500