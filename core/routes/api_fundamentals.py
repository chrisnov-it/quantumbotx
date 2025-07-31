# core/routes/api_fundamentals.py

from flask import Blueprint, jsonify
# Hapus 'import sqlite3' dan gunakan fungsi dari queries
from core.db import queries

api_fundamentals = Blueprint('api_fundamentals', __name__)

@api_fundamentals.route('/api/bots/<int:bot_id>/fundamentals')
def get_bot_fundamentals(bot_id):
    bot = queries.get_bot_by_id(bot_id) # Gunakan fungsi terpusat
    if not bot:
        return jsonify({'error': 'Bot tidak ditemukan'}), 404

    if '/' in bot['market']:
        return jsonify({})  # Skip if not stock

    symbol = bot['market']
    return jsonify({})
