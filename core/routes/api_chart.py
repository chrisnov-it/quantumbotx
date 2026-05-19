# core/routes/api_chart.py

from flask import Blueprint, jsonify, request
from core.utils.market_data import get_market_rates
try:
    import pandas_ta as ta
except ImportError:
    from core.utils.pandas_ta_compat import ta
import logging

api_chart = Blueprint('api_chart', __name__)

@api_chart.route('/api/chart/data')
def api_chart_data():
    symbol = request.args.get('symbol', 'EURUSD')
    timeframe = request.args.get('timeframe', 'H1')
    
    # Get historical data through the broker-neutral market data facade.
    df = get_market_rates(symbol, timeframe, 100)
    
    if df is None or df.empty:
        return jsonify({"error": "Gagal mengambil data grafik"}), 500
    
    chart_data = {
        "labels": df.index.strftime('%H:%M').tolist(),
        "data": df['close'].tolist()
    }
    return jsonify(chart_data)
