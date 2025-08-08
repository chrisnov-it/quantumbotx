# core/routes/api_dashboard.py

from flask import Blueprint, jsonify
from core.utils.mt5 import get_account_info_mt5, get_todays_profit_mt5
from core.db import queries # <-- 1. Impor modul queries

api_dashboard = Blueprint('api_dashboard', __name__)

@api_dashboard.route('/api/dashboard/stats')
def api_dashboard_stats():
    try:
        account_info = get_account_info_mt5()
        todays_profit = get_todays_profit_mt5()

        # 2. Ambil semua bot sekali saja untuk efisiensi
        all_bots = queries.get_all_bots()
        active_bots = [bot for bot in all_bots if bot['status'] == 'Aktif']

        stats = {
            "equity": account_info.get('equity', 0) if account_info else 0,
            "todays_profit": todays_profit,
            "active_bots_count": len(active_bots),
            "total_bots": len(all_bots), # <-- 3. Tambahkan total bot ke respon
            "active_bots": [{'name': bot['name'], 'market': bot['market']} for bot in active_bots]
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": f"Gagal mengambil statistik dashboard: {e}"}), 500
