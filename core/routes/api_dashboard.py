# core/routes/api_dashboard.py

from flask import Blueprint, jsonify, request
from core.utils.mt5 import get_account_info_mt5, get_todays_profit_mt5, get_rates_mt5
from core.db import queries
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import pandas_ta as ta
import logging

api_dashboard = Blueprint('api_dashboard', __name__)
logger = logging.getLogger(__name__)

@api_dashboard.route('/api/dashboard/stats')
def api_dashboard_stats():
    try:
        account_info = get_account_info_mt5()
        todays_profit = get_todays_profit_mt5()

        # Get all bots data
        all_bots = queries.get_all_bots()
        active_bots = [bot for bot in all_bots if bot['status'] == 'Aktif']

        stats = {
            "equity": account_info.get('equity', 0) if account_info else 0,
            "todays_profit": todays_profit,
            "active_bots_count": len(active_bots),
            "total_bots": len(all_bots),
            "active_bots": [{'name': bot['name'], 'market': bot['market']} for bot in active_bots]
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({"error": f"Gagal mengambil statistik dashboard: {e}"}), 500

@api_dashboard.route('/api/account-info')
def api_account_info():
    """Enhanced account info endpoint for dashboard"""
    try:
        account_info = get_account_info_mt5()
        todays_profit = get_todays_profit_mt5()
        
        return jsonify({
            'success': True,
            'equity': account_info.get('equity', 0) if account_info else 0,
            'balance': account_info.get('balance', 0) if account_info else 0,
            'margin': account_info.get('margin', 0) if account_info else 0,
            'free_margin': account_info.get('margin_free', 0) if account_info else 0,
            'todays_profit': todays_profit,
            'profit_percentage': (todays_profit / account_info.get('balance', 1) * 100) if account_info and account_info.get('balance', 0) > 0 else 0
        })
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_dashboard.route('/api/bots/status')
def api_bots_status():
    """Get detailed bot status information"""
    try:
        all_bots = queries.get_all_bots()
        active_bots = [bot for bot in all_bots if bot['status'] == 'Aktif']
        
        # Enhanced bot info with mock data for now
        enhanced_active_bots = []
        for bot in active_bots:
            enhanced_active_bots.append({
                'id': bot.get('id', 0),
                'name': bot['name'],
                'symbol': bot['market'],
                'strategy': bot.get('strategy', 'Unknown'),
                'profit': bot.get('profit', 0.0),  # This would come from actual bot data
                'trades': bot.get('trades_count', 0),  # This would come from actual bot data
                'status': bot['status'],
                'last_trade': bot.get('last_trade_time', 'N/A')
            })
        
        return jsonify({
            'success': True,
            'active_count': len(active_bots),
            'total_count': len(all_bots),
            'active_bots': enhanced_active_bots
        })
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_dashboard.route('/api/market-data/<symbol>')
def api_market_data(symbol):
    """Get market data including price and RSI for charts"""
    try:
        # Get historical data for the symbol
        df = get_rates_mt5(symbol, mt5.TIMEFRAME_H1, 50)
        
        if df is None or df.empty:
            return jsonify({
                'success': False,
                'error': 'No data available for symbol'
            }), 404
        
        # Calculate RSI
        df['RSI'] = ta.rsi(df['close'], length=14)
        df = df.dropna().tail(20)  # Get last 20 data points
        
        # Format timestamps for charts
        timestamps = [t.strftime('%H:%M') for t in df.index]
        prices = df['close'].round(5).tolist()
        rsi_values = df['RSI'].round(2).tolist()
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'timestamps': timestamps,
            'prices': prices,
            'rsi': rsi_values,
            'current_price': prices[-1] if prices else 0,
            'current_rsi': rsi_values[-1] if rsi_values else 50
        })
    except Exception as e:
        logger.error(f"Error getting market data for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_dashboard.route('/api/recent-activities')
def api_recent_activities():
    """Get recent trading activities for dashboard sidebar"""
    try:
        # Get recent bot activities and trades
        activities = []
        
        # Get recent bot status changes
        all_bots = queries.get_all_bots()
        for bot in all_bots[-5:]:  # Last 5 bots
            activities.append({
                'icon': '🤖',
                'title': f"Bot {bot['name']} - {bot['status']}",
                'description': f"Market: {bot['market']}",
                'time': 'Baru saja',
                'type': 'bot_status'
            })
        
        # Add some sample trading activities
        sample_activities = [
            {
                'icon': '📈',
                'title': 'Trade Berhasil',
                'description': 'EUR/USD Buy +$12.50',
                'time': '5 menit lalu',
                'type': 'trade_success'
            },
            {
                'icon': '🔔',
                'title': 'Signal Alert',
                'description': 'RSI Overbought pada GBP/USD',
                'time': '15 menit lalu',
                'type': 'signal'
            },
            {
                'icon': '🧠',
                'title': 'AI Mentor Update',
                'description': 'Analisis emosi trading diperbarui',
                'time': '30 menit lalu',
                'type': 'ai_mentor'
            },
            {
                'icon': '⚡',
                'title': 'Bot Started',
                'description': 'Quantum Velocity strategy dimulai',
                'time': '1 jam lalu',
                'type': 'bot_start'
            }
        ]
        
        # Combine and limit to recent activities
        all_activities = activities + sample_activities
        recent_activities = all_activities[:8]  # Show last 8 activities
        
        return jsonify({
            'success': True,
            'activities': recent_activities
        })
    except Exception as e:
        logger.error(f"Error getting recent activities: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'activities': []  # Return empty activities on error
        })
