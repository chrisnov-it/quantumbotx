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

    # Ambil nilai profit, utamakan kunci baru 'total_profit'
    profit_to_save = results.get('total_profit')
    if profit_to_save is None:
        profit_to_save = results.get('total_profit_usd', 0) # Fallback ke kunci lama

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO backtest_results (
                    strategy_name, data_filename, total_profit_usd, total_trades, 
                    win_rate_percent, max_drawdown_percent, wins, losses, equity_curve, trade_log, parameters
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                strategy_name,
                filename,
                profit_to_save,
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
        
        # Extract symbol name from filename for accurate XAUUSD detection
        symbol_name = None
        if file.filename:
            # Try to extract symbol from filename (e.g., "XAUUSD_H1_data.csv" -> "XAUUSD")
            filename_parts = file.filename.replace('.csv', '').split('_')
            if filename_parts:
                symbol_name = filename_parts[0].upper()
                logger.info(f"Detected symbol from filename: {symbol_name}")
        
        # Jalankan backtest dengan symbol name untuk deteksi XAUUSD yang akurat
        results = run_backtest(strategy_id, params, df, symbol_name=symbol_name)

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
        processed_history = []
        for record in history:
            # Create a mutable copy (dictionary) from the database record
            new_record = dict(record)
            
            # Parse JSON fields safely
            if 'trade_log' in new_record and new_record['trade_log']:
                try:
                    trades = json.loads(new_record['trade_log'])
                    if isinstance(trades, list):
                        new_record['trade_log'] = trades
                except (json.JSONDecodeError, TypeError):
                    new_record['trade_log'] = []
            else:
                new_record['trade_log'] = []
            
            if 'equity_curve' in new_record and new_record['equity_curve']:
                try:
                    equity = json.loads(new_record['equity_curve'])
                    if isinstance(equity, list):
                        new_record['equity_curve'] = equity
                except (json.JSONDecodeError, TypeError):
                    new_record['equity_curve'] = []
            else:
                new_record['equity_curve'] = []
                
            if 'parameters' in new_record and new_record['parameters']:
                try:
                    params = json.loads(new_record['parameters'])
                    if isinstance(params, dict):
                        new_record['parameters'] = params
                except (json.JSONDecodeError, TypeError):
                    new_record['parameters'] = {}
            else:
                new_record['parameters'] = {}
            
            processed_history.append(new_record)
            
        return jsonify(processed_history)
    except Exception as e:
        logger.error(f"Error processing history: {str(e)}", exc_info=True)
        return jsonify({"error": f"Terjadi kesalahan saat mengambil riwayat: {str(e)}"}), 500