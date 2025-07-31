# core/routes/api_stocks.py

from flask import Blueprint, jsonify
import MetaTrader5 as mt5 # Dipertahankan untuk mt5.terminal_info() jika diperlukan
from core.utils.symbols import get_stock_symbols
from core.utils.external import get_mt5_symbol_profile
from core.data.fetch import get_rates # <-- Impor fungsi terpusat

api_stocks = Blueprint('api_stocks', __name__)

@api_stocks.route('/api/stocks/<symbol>/profile')
def get_stock_profile(symbol):
    profile = get_mt5_symbol_profile(symbol)
    if profile:
        return jsonify(profile)
    return jsonify({"error": "Could not fetch symbol profile from MT5"}), 404

@api_stocks.route('/api/stocks')
def get_stocks():
    stock_symbols = get_stock_symbols()
    result = []

    for stock in stock_symbols[:20]:  # Max 20 untuk UI
        symbol = stock['name']
        # Gunakan fungsi dari fetch.py
        df = get_rates(symbol, mt5.TIMEFRAME_M1, 2) # Ambil 2 bar untuk hitung change

        if df is not None and not df.empty and len(df) > 1:
            last_row = df.iloc[-1]
            prev_row = df.iloc[-2]
            result.append({
                'symbol': symbol,
                'last_price': last_row['close'],
                'change': round(last_row['close'] - prev_row['close'], 2), # Perubahan dari close sebelumnya
                'time': last_row['time'].strftime('%H:%M')
            })

    return jsonify(result)

@api_stocks.route('/api/stocks/<symbol>')
def get_stock_detail(symbol):
    # Gunakan fungsi dari fetch.py
    df = get_rates(symbol, mt5.TIMEFRAME_M1, 1)

    if df is None or df.empty:
        return jsonify({"error": f"Tidak bisa mengambil data untuk {symbol}"}), 404

    last = df.iloc[-1]
    return jsonify({
        "symbol": symbol,
        "time": last['time'].strftime('%Y-%m-%d %H:%M:%S'),
        "open": last['open'],
        "high": last['high'],
        "low": last['low'],
        "close": last['close'],
        "volume": last['tick_volume']
    })
