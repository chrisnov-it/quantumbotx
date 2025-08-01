# core/routes/api_bots.py - VERSI PERBAIKAN LENGKAP

import json
import logging
from flask import Blueprint, jsonify, request
import pandas_ta as ta
import MetaTrader5 as mt5
from core.bots import controller
from core.db import queries
from core.data.fetch import get_rates
from core.utils.mt5 import TIMEFRAME_MAP
from core.strategies.strategy_map import STRATEGY_MAP

api_bots = Blueprint('api_bots', __name__)
logger = logging.getLogger(__name__)

@api_bots.route('/api/strategies', methods=['GET'])
def get_strategies_route():
    try:
        strategies = []
        for key, strategy_class in STRATEGY_MAP.items():
            strategies.append({
                'id': key,
                'name': getattr(strategy_class, 'name', key.replace('_', ' ').title()),
                'description': getattr(strategy_class, 'description', 'No description available.')
            })
        return jsonify(strategies)
    except Exception as e:
        logger.error(f"Gagal memuat daftar strategi: {e}", exc_info=True)
        return jsonify({"error": "Gagal memuat daftar strategi"}), 500

@api_bots.route('/api/strategies/<strategy_id>/params', methods=['GET'])
def get_strategy_params_route(strategy_id):
    """Mengembalikan parameter yang bisa diatur untuk sebuah strategi."""
    strategy_class = STRATEGY_MAP.get(strategy_id)
    if not strategy_class:
        return jsonify({"error": "Strategi tidak ditemukan"}), 404
    
    # Panggil metode class untuk mendapatkan parameter
    if hasattr(strategy_class, 'get_definable_params'):
        params = strategy_class.get_definable_params()
        return jsonify(params)
    
    return jsonify([]) # Kembalikan array kosong jika tidak ada parameter

@api_bots.route('/api/bots', methods=['GET'])
def get_bots_route():
    """Mengambil semua bot."""
    bots = queries.get_all_bots()
    # Perkaya data bot dengan nama strategi yang mudah dibaca
    for bot in bots:
        strategy_key = bot.get('strategy')
        strategy_class = STRATEGY_MAP.get(strategy_key)
        if strategy_class:
            bot['strategy_name'] = getattr(strategy_class, 'name', strategy_key)
        else:
            bot['strategy_name'] = strategy_key # Fallback jika tidak ditemukan
    return jsonify(bots)

@api_bots.route('/api/bots/<int:bot_id>', methods=['GET'])
def get_single_bot_route(bot_id):
    """Mengambil detail satu bot."""
    bot = queries.get_bot_by_id(bot_id)
    if bot and bot.get('strategy_params'):
        # Ubah string JSON menjadi objek untuk frontend
        bot['strategy_params'] = json.loads(bot['strategy_params'])
    return jsonify(bot) if bot else (jsonify({"error": "Bot tidak ditemukan"}), 404)

@api_bots.route('/api/bots', methods=['POST'])
def add_bot_route():
    """Membuat bot baru."""
    data = request.get_json()
    params_json = json.dumps(data.get('params', {}))

    new_bot_id = queries.add_bot(
        name=data.get('name'), market=data.get('market'), lot_size=data.get('lot_size'),
        sl_pips=data.get('sl_pips'), tp_pips=data.get('tp_pips'), timeframe=data.get('timeframe'),
        interval=data.get('check_interval_seconds'), strategy=data.get('strategy'),
        strategy_params=params_json
    )
    if new_bot_id:
        controller.add_new_bot_to_controller(new_bot_id)
        return jsonify({"message": "Bot berhasil dibuat", "bot_id": new_bot_id}), 201
    return jsonify({"error": "Gagal menyimpan bot"}), 500

@api_bots.route('/api/bots/<int:bot_id>', methods=['PUT'])
def update_bot_route(bot_id):
    """Memperbarui pengaturan bot."""
    bot_data = request.get_json()
    
    bot_instance = controller.get_bot_instance_by_id(bot_id)
    bot_was_running = bot_instance and bot_instance.status == 'Aktif'

    success, result = controller.perbarui_bot(bot_id, bot_data)
    
    if success:
        if bot_was_running:
            controller.mulai_bot(bot_id)
        return jsonify({"message": "Bot berhasil diperbarui."}), 200
    
    return jsonify({"error": result or "Gagal memperbarui bot"}), 500

@api_bots.route('/api/bots/<int:bot_id>', methods=['DELETE'])
def delete_bot_route(bot_id):
    """Menghapus bot."""
    if controller.hapus_bot(bot_id):
        return jsonify({"message": "Bot berhasil dihapus."}), 200
    else:
        return jsonify({"error": "Gagal menghapus bot dari database"}), 500

@api_bots.route('/api/bots/<int:bot_id>/start', methods=['POST'])
def start_bot_route(bot_id):
    """Memulai bot."""
    success, message = controller.mulai_bot(bot_id)
    return jsonify({'message': message}) if success else (jsonify({'error': message}), 500)

@api_bots.route('/api/bots/<int:bot_id>/stop', methods=['POST'])
def stop_bot_route(bot_id):
    """Menghentikan bot."""
    success, message = controller.stop_bot(bot_id)
    return jsonify({'message': message}) if success else (jsonify({'error': message}), 500)

@api_bots.route('/api/bots/start_all', methods=['POST'])
def start_all_bots_route():
    """Memulai semua bot yang dijeda."""
    success, message = controller.start_all_bots()
    return jsonify({'message': message}) if success else (jsonify({'error': message}), 400)

@api_bots.route('/api/bots/stop_all', methods=['POST'])
def stop_all_bots_route():
    """Menghentikan semua bot yang aktif."""
    success, message = controller.stop_all_bots()
    return jsonify({'message': message}) if success else (jsonify({'error': message}), 400)

@api_bots.route('/api/bots/<int:bot_id>/analysis', methods=['GET'])
def get_analysis_route(bot_id):
    """Mendapatkan data analisis terakhir."""
    data = controller.get_bot_analysis_data(bot_id)
    return jsonify(data if data else {"signal": "Data belum tersedia"})

@api_bots.route('/api/bots/<int:bot_id>/history', methods=['GET'])
def get_bot_history_route(bot_id):
    """Mengembalikan riwayat aktivitas untuk bot."""
    history = queries.get_history_by_bot_id(bot_id)
    return jsonify(history)

@api_bots.route('/api/rsi_data', methods=['GET'])
def get_rsi_data_route():
    """Menyediakan data RSI untuk grafik di dashboard."""
    symbol = request.args.get('symbol', 'EURUSD', type=str)
    timeframe_str = request.args.get('timeframe', 'H1', type=str)
    
    timeframe = TIMEFRAME_MAP.get(timeframe_str, mt5.TIMEFRAME_H1)
    
    df = get_rates(symbol, timeframe, 100)
    
    if df is None or df.empty:
        return jsonify({"error": f"Tidak dapat mengambil data untuk {symbol}"}), 404
        
    df['rsi'] = ta.rsi(df['close'], length=14)
    df.dropna(inplace=True)
    
    chart_data = {
        'timestamps': [dt.strftime('%H:%M') for dt in df['time'].tail(50)],
        'rsi_values': list(df['rsi'].tail(50))
    }
    return jsonify(chart_data)