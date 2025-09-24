# core/routes/api_backtest.py

import numpy as np
import pandas as pd
import json
import logging
import subprocess
import os
from flask import Blueprint, request, jsonify
from core.backtesting.enhanced_engine import run_enhanced_backtest as run_backtest
from core.db.queries import get_all_backtest_history
from core.db.connection import get_db_connection

api_backtest = Blueprint('api_backtest', __name__)
logger = logging.getLogger(__name__)

def save_backtest_result(strategy_name, filename, params, results):
    # Sanitasi data sebelum menyimpan
    for key, value in results.items():
        if isinstance(value, (np.floating, float)) and (np.isinf(value) or np.isnan(value)):
            results[key] = None # Ganti inf/nan dengan None (NULL di DB)

    # Enhanced engine provides more detailed results
    profit_to_save = results.get('total_profit_usd', 0)
    spread_costs = results.get('total_spread_costs', 0)
    instrument = results.get('instrument', 'UNKNOWN')
    
    # Add enhanced engine info to parameters for tracking
    enhanced_params = params.copy()
    enhanced_params['engine_type'] = 'enhanced'
    enhanced_params['spread_costs'] = spread_costs
    enhanced_params['instrument'] = instrument
    
    if 'engine_config' in results:
        engine_config = results['engine_config']
        enhanced_params['realistic_execution'] = engine_config.get('realistic_execution', True)
        enhanced_params['spread_costs_enabled'] = engine_config.get('spread_costs_enabled', True)
        
        # Include instrument-specific config for analysis
        if 'instrument_config' in engine_config:
            inst_config = engine_config['instrument_config']
            enhanced_params['max_risk_percent'] = inst_config.get('max_risk_percent', 2.0)
            enhanced_params['typical_spread_pips'] = inst_config.get('typical_spread_pips', 2.0)
            enhanced_params['max_lot_size'] = inst_config.get('max_lot_size', 10.0)

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
                json.dumps(enhanced_params)
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
        df = pd.read_csv(file.stream, parse_dates=['time'])
        strategy_id = request.form.get('strategy')
        params = json.loads(request.form.get('params', '{}'))
        
        # Map web interface parameter names to enhanced engine parameter names
        enhanced_params = params.copy()
        
        # Map old parameter names to new enhanced engine names
        if 'lot_size' in params and 'risk_percent' not in params:
            enhanced_params['risk_percent'] = float(params['lot_size'])
            
        if 'sl_pips' in params and 'sl_atr_multiplier' not in params:
            enhanced_params['sl_atr_multiplier'] = float(params['sl_pips'])
            
        if 'tp_pips' in params and 'tp_atr_multiplier' not in params:
            enhanced_params['tp_atr_multiplier'] = float(params['tp_pips'])
        
        logger.info(f"Parameter mapping: {params} -> {enhanced_params}")
        
        # Extract symbol name from filename for accurate XAUUSD detection
        symbol_name = None
        if file.filename:
            # Try to extract symbol from filename (e.g., "XAUUSD_H1_data.csv" -> "XAUUSD")
            filename_parts = file.filename.replace('.csv', '').split('_')
            if filename_parts:
                symbol_name = filename_parts[0].upper()
                logger.info(f"Detected symbol from filename: {symbol_name}")
        
        # Enhanced backtesting with realistic cost modeling and risk management
        # Use enhanced engine for more accurate results
        engine_config = {
            'enable_spread_costs': True,    # Model realistic spread costs
            'enable_slippage': True,        # Include slippage simulation
            'enable_realistic_execution': True  # Realistic bid/ask execution
        }
        
        results = run_backtest(strategy_id, enhanced_params, df, symbol_name=symbol_name, engine_config=engine_config)

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

@api_backtest.route('/api/download-data', methods=['POST'])
def download_data_route():
    """Download historical market data using the standalone script"""
    try:
        # Path to the download script
        script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'lab', 'download_data.py')
        script_path = os.path.abspath(script_path)

        if not os.path.exists(script_path):
            return jsonify({"error": "Download script not found"}), 404

        # Check if the script can import MT5 (basic validation)
        try:
            result_check = subprocess.run(
                ['python', '-c', 'import MetaTrader5 as mt5; print("MT5 available")'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result_check.returncode != 0:
                return jsonify({
                    "error": "MetaTrader5 module not available. Make sure you run the download script manually in an environment where MT5 is installed.",
                    "solution": "Run 'python lab/download_data.py' from command line instead."
                }), 500
        except subprocess.TimeoutExpired:
            return jsonify({
                "error": "MT5 availability check timed out",
                "solution": "Ensure MT5 terminal is running and accessible"
            }), 408

        # Run the download script
        logger.info(f"Starting data download with script: {script_path}")

        # Use subprocess to run the script and capture output
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            # Success - parse output to extract info
            output_lines = result.stdout.strip().split('\n')
            downloaded_files = []
            failed_count = 0

            for line in output_lines:
                if line.startswith('✅') and 'bars saved to' in line:
                    # Extract filename from success message
                    parts = line.split('bars saved to')
                    if len(parts) > 1:
                        filepath = parts[1].strip()
                        filename = os.path.basename(filepath)
                        downloaded_files.append(filename)
                elif line.startswith('❌ Failed downloads:'):
                    # Extract failed count
                    parts = line.split(':')
                    if len(parts) > 1:
                        try:
                            failed_count = len(parts[1].strip().split(', ')) if parts[1].strip() else 0
                        except:
                            failed_count = 0

            return jsonify({
                "success": True,
                "message": f"Downloaded {len(downloaded_files)} files successfully" + (f", {failed_count} failed" if failed_count > 0 else ""),
                "downloaded_files": downloaded_files,
                "failed_count": failed_count,
                "output": result.stdout
            })
        else:
            # Process failed
            error_msg = result.stderr or "Unknown error occurred"
            logger.error(f"Data download failed: {error_msg}")
            return jsonify({
                "error": f"Download failed: {error_msg}",
                "output": result.stderr,
                "stdout": result.stdout
            }), 500

    except subprocess.TimeoutExpired:
        logger.error("Data download timed out")
        return jsonify({"error": "Download timed out after 5 minutes"}), 408
    except Exception as e:
        logger.error(f"Error in download data route: {str(e)}", exc_info=True)
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
