# core/routes/api_indicators.py

from flask import Blueprint, request, jsonify
from core.utils.mt5 import get_rates_mt5
import MetaTrader5 as mt5
import pandas_ta as ta

api_indicators = Blueprint('api_indicators', __name__)

@api_indicators.route('/api/rsi_data')
def get_rsi_data():
    symbol = request.args.get('symbol', 'EURUSD')
    tf = request.args.get('timeframe', 'H1')

    tf_map = {
        'M1': mt5.TIMEFRAME_M1,
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'H1': mt5.TIMEFRAME_H1,
        'H4': mt5.TIMEFRAME_H4,
        'D1': mt5.TIMEFRAME_D1
    }
    timeframe = tf_map.get(tf.upper(), mt5.TIMEFRAME_H1)

    df = get_rates_mt5(symbol, timeframe, 100)
    if df is None or len(df) < 20:
        return jsonify({'timestamps': [], 'rsi_values': []})

    df['RSI'] = ta.rsi(df['close'], length=14)
    df = df.dropna().tail(20)

    return jsonify({
        'timestamps': [x.strftime('%H:%M') for x in df['time']],
        'rsi_values': df['RSI'].round(2).tolist()
    })
