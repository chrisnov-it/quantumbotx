# core/routes/api_backtest.py

import pandas as pd
import json
from flask import Blueprint, request, jsonify
from core.backtesting.engine import run_backtest

api_backtest = Blueprint('api_backtest', __name__)

@api_backtest.route('/api/backtest/run', methods=['POST'])
def run_backtest_route():
    if 'file' not in request.files:
        return jsonify({"error": "Tidak ada file data yang diunggah"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nama file kosong"}), 400

    try:
        # Baca data CSV yang diunggah
        df = pd.read_csv(file, parse_dates=['time'])
        
        # Ambil parameter dari form data
        strategy_id = request.form.get('strategy')
        params = json.loads(request.form.get('params', '{}'))
        
        results = run_backtest(strategy_id, params, df)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan saat backtesting: {str(e)}"}), 500