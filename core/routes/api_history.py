# core/routes/api_history.py

import os
from flask import Blueprint, jsonify
from core.utils.mt5 import get_trade_history_mt5
import sqlite3

api_history = Blueprint('api_history', __name__)

# Gunakan path absolut untuk file database untuk menghindari masalah CWD
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bots.db")

@api_history.route('/api/backtest/history')
def get_backtest_history():
    """Mengambil semua hasil backtest yang tersimpan dari database."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row # Ini memungkinkan akses kolom berdasarkan nama
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM backtest_results ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            # Ubah baris menjadi list of dictionaries
            results = [dict(row) for row in rows]
            return jsonify(results)
    except Exception as e:
        return jsonify({"error": f"Gagal mengambil riwayat backtest: {str(e)}"}), 500

@api_history.route('/api/history')
def api_global_history():
    history = get_trade_history_mt5()
    return jsonify(history)

@api_history.route('/api/bots/<int:bot_id>/history')
def api_bot_history(bot_id):
    try:
        from core.bots.controller import active_bots
        from datetime import datetime, timedelta
        import MetaTrader5 as mt5

        bot = active_bots.get(bot_id)
        if not bot:
            return jsonify({'error': 'Bot tidak ditemukan'}), 404

        magic = bot.bot_id
        from_date = datetime.now() - timedelta(days=30)
        to_date = datetime.now()
        deals = mt5.history_deals_get(from_date, to_date)

        if deals is None:
            return jsonify([])

        filtered = [
            {
                "ticket": d.ticket,
                "symbol": d.symbol,
                "volume": d.volume,
                "price": d.price,
                "profit": d.profit,
                "type": d.type,
                "time": datetime.fromtimestamp(d.time).isoformat()
            }
            for d in deals if d.magic == magic and d.entry == 1
        ]

        return jsonify(filtered)
    except Exception as e:
        print(f"[ERROR] Bot History {bot_id}: {e}")
        return jsonify({'error': str(e)}), 500
