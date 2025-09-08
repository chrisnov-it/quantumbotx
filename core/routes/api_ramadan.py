# core/routes/api_ramadan.py
"""
API endpoints for Ramadan Trading Mode features
"""

from flask import Blueprint, jsonify
from core.seasonal.holiday_manager import holiday_manager
import logging

api_ramadan = Blueprint('api_ramadan', __name__)
logger = logging.getLogger(__name__)

@api_ramadan.route('/api/ramadan/status')
def get_ramadan_status():
    """Get current Ramadan trading mode status"""
    try:
        current_holiday = holiday_manager.get_current_holiday_mode()
        
        if not current_holiday or current_holiday.name != "Ramadan Trading Mode":
            return jsonify({
                'success': True,
                'is_ramadan': False,
                'message': 'Currently not in Ramadan trading mode'
            })
        
        return jsonify({
            'success': True,
            'is_ramadan': True,
            'holiday_name': current_holiday.name,
            'start_date': current_holiday.start_date.isoformat(),
            'end_date': current_holiday.end_date.isoformat(),
            'trading_adjustments': current_holiday.trading_adjustments,
            'ui_theme': current_holiday.ui_theme,
            'greeting': holiday_manager.get_holiday_greeting()
        })
    except Exception as e:
        logger.error(f"Error getting Ramadan status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_ramadan.route('/api/ramadan/features')
def get_ramadan_features():
    """Get Ramadan-specific features data"""
    try:
        ramadan_features = holiday_manager.get_ramadan_features()
        
        if not ramadan_features:
            return jsonify({
                'success': True,
                'is_ramadan': False,
                'message': 'Currently not in Ramadan trading mode'
            })
        
        return jsonify({
            'success': True,
            'is_ramadan': True,
            'features': ramadan_features
        })
    except Exception as e:
        logger.error(f"Error getting Ramadan features: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_ramadan.route('/api/ramadan/pause-status')
def get_ramadan_pause_status():
    """Check if trading is currently paused due to Ramadan prayer times"""
    try:
        is_paused = holiday_manager.is_trading_paused()
        pause_reason = ""
        
        if is_paused:
            # Determine which prayer time is causing the pause
            current_holiday = holiday_manager.get_current_holiday_mode()
            if current_holiday and current_holiday.name == "Ramadan Trading Mode":
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
        logger.error(f"Error checking Ramadan pause status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_ramadan.route('/api/ramadan/zakat-calculator')
def get_zakat_calculator():
    """Get Zakat calculation information"""
    try:
        current_holiday = holiday_manager.get_current_holiday_mode()
        
        if not current_holiday or current_holiday.name != "Ramadan Trading Mode":
            return jsonify({
                'success': True,
                'is_ramadan': False,
                'message': 'Zakat calculator only available during Ramadan'
            })
        
        zakat_info = holiday_manager._calculate_zakat_info()
        
        return jsonify({
            'success': True,
            'is_ramadan': True,
            'zakat_info': zakat_info
        })
    except Exception as e:
        logger.error(f"Error getting Zakat calculator: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500