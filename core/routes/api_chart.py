# core/routes/api_chart.py

from flask import Blueprint, jsonify, request
from core.utils.mt5 import get_rates_mt5
import MetaTrader5 as mt5

api_chart = Blueprint('api_chart', __name__)

@api_chart.route('/api/chart/data')
def api_chart_data():
    symbol = request.args.get('symbol', 'EURUSD')
    df = get_rates_mt5(symbol, mt5.TIMEFRAME_H1, 100)
    
    if df is None or df.empty:
        return jsonify({"error": "Gagal mengambil data grafik"}), 500
    
    chart_data = {
        "labels": df.index.strftime('%H:%M').tolist(),
        "data": df['close'].tolist()
    }
    return jsonify(chart_data)
