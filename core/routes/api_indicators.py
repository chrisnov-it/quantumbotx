# core/routes/api_indicators.py

from flask import Blueprint, request, jsonify
from core.utils.market_data import get_market_rates
try:
    import pandas_ta as ta
except ImportError:
    from core.utils.pandas_ta_compat import ta
import logging

api_indicators = Blueprint('api_indicators', __name__)

@api_indicators.route('/api/rsi_data')
def get_rsi_data():
    symbol = request.args.get('symbol', 'EURUSD')
    tf = request.args.get('timeframe', 'H1')

    df = get_market_rates(symbol, tf.upper(), 100)
    if df is None or len(df) < 20:
        return jsonify({'timestamps': [], 'rsi_values': []})

    df['RSI'] = ta.rsi(df['close'], length=14)
    df = df.dropna().tail(20)

    return jsonify({
        'timestamps': [x.strftime('%H:%M') for x in df.index],
        'rsi_values': df['RSI'].round(2).tolist()
    })
