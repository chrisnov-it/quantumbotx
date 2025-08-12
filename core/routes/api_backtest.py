# core/routes/api_backtest.py

import numpy as np
import pandas as pd
import json
import logging
from flask import Blueprint, request, jsonify
from core.backtesting.engine import run_backtest
from core.db.queries import get_all_backtest_history
from core.db.connection import get_db_connection

api_backtest = Blueprint('api_backtest', __name__)
logger = logging.getLogger(__name__)

def save_backtest_result(strategy_name, filename, params, results):
    # Sanitasi data sebelum menyimpan
    for key, value in results.items():
        if isinstance(value, (np.floating, float)) and (np.isinf(value) or np.isnan(value)):
            results[key] = None # Ganti inf/nan dengan None (NULL di DB)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO backtest_results (
                    strategy_name, data_filename, total_profit_pips, total_trades, 
                    win_rate_percent, max_drawdown_percent, wins, losses, equity_curve, trade_log, parameters
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                strategy_name,
                filename,
                results.get('total_profit_pips', 0),
                results.get('total_trades', 0),
                results.get('win_rate_percent', 0),
                results.get('max_drawdown_percent', 0),
                results.get('wins', 0),
                results.get('losses', 0),
                json.dumps(results.get('equity_curve', [])),
                json.dumps(results.get('trades', [])),
                json.dumps(params)
            ))
            conn.commit()
    except Exception as e:
        logger.error(f"[DB ERROR] Gagal menyimpan hasil backtest: {e}", exc_info=True)

@api_backtest.route('/api/backtest/run', methods=['POST'])
def run_backtest_route():
    if 'file' not in request.files:
        return jsonify({"error": "Tidak ada file data yang diunggah"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nama file kosong"}), 400

    try:
        df = pd.read_csv(file, parse_dates=['time'])
        strategy_id = request.form.get('strategy')
        params = json.loads(request.form.get('params', '{}'))
        
        # Jalankan backtest
        results = run_backtest(strategy_id, params, df)

        # Simpan hasil jika berhasil
        if results and not results.get('error'):
            strategy_name = results.get('strategy_name', strategy_id)
            save_backtest_result(strategy_name, file.filename, params, results)

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan saat backtesting: {str(e)}"}), 500

@api_backtest.route('/api/backtest/history', methods=['GET'])
def get_history_route():
    try:
        history = get_all_backtest_history()
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan saat mengambil riwayat: {str(e)}"}), 500