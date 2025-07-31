# core/routes/api_fundamentals.py

from flask import Blueprint, jsonify
import sqlite3


api_fundamentals = Blueprint('api_fundamentals', __name__)

def get_bot(bot_id):
    conn = sqlite3.connect('bots.db')
    conn.row_factory = sqlite3.Row
    bot = conn.execute('SELECT * FROM bots WHERE id = ?', (bot_id,)).fetchone()
    conn.close()
    return bot

@api_fundamentals.route('/api/bots/<int:bot_id>/fundamentals')
def get_bot_fundamentals(bot_id):
    bot = get_bot(bot_id)
    if not bot:
        return jsonify({'error': 'Bot tidak ditemukan'}), 404

    if '/' in bot['market']:
        return jsonify({})  # Skip if not stock

    symbol = bot['market']
    return jsonify({})
