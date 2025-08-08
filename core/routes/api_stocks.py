# core/routes/api_stocks.py

import logging
from datetime import datetime
from flask import Blueprint, jsonify
import MetaTrader5 as mt5
from core.utils.symbols import get_stock_symbols
from core.utils.external import get_mt5_symbol_profile
from core.utils.mt5 import get_rates_mt5

api_stocks = Blueprint('api_stocks', __name__)
logger = logging.getLogger(__name__)

@api_stocks.route('/api/stocks/<symbol>/profile')
def get_stock_profile(symbol):
    profile = get_mt5_symbol_profile(symbol)
    if profile:
        return jsonify(profile)
    return jsonify({"error": "Could not fetch symbol profile from MT5"}), 404

@api_stocks.route('/api/stocks')
def get_stocks():
    """
    Mengambil daftar harga saham terkini.
    Metode ini diubah agar lebih tangguh, terutama saat pasar tutup.
    Perubahan dihitung dari harga pembukaan harian (Open D1) ke harga ask terakhir.
    """
    # Ambil 20 saham paling populer (sudah diurutkan berdasarkan volume oleh fungsi)
    stock_symbols = get_stock_symbols(limit=20)
    if not stock_symbols:
        logger.warning("get_stock_symbols() tidak mengembalikan simbol saham.")
        return jsonify([])

    result = []
    symbols_to_process = [stock['name'] for stock in stock_symbols]

    for symbol in symbols_to_process:
        try:
            # 1. Ambil tick terakhir untuk harga saat ini
            tick = mt5.symbol_info_tick(symbol)
            if not tick or tick.ask == 0:
                logger.debug(f"Melewatkan {symbol}: tidak ada data tick atau harga ask 0.")
                continue

            # 2. Ambil data bar harian (D1) untuk harga pembukaan
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 1)
            if rates is None or len(rates) == 0:
                logger.warning(f"Melewatkan {symbol}: tidak bisa mendapatkan data harian (D1).")
                continue

            daily_open = rates[0]['open']
            last_price = tick.ask
            change = last_price - daily_open

            result.append({
                'symbol': symbol,
                'last_price': last_price,
                'change': round(change, 2),
                'time': datetime.fromtimestamp(tick.time).strftime('%H:%M:%S')
            })
        except Exception as e:
            # Log error jika terjadi masalah tak terduga saat memproses satu simbol
            logger.error(f"Error saat memproses simbol saham {symbol}: {e}", exc_info=True)

    return jsonify(result)

@api_stocks.route('/api/stocks/<symbol>')
def get_stock_detail(symbol):
    # Gunakan fungsi dari fetch.py
    df = get_rates_mt5(symbol, mt5.TIMEFRAME_M1, 1)

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

@api_stocks.route('/api/symbols/all')
def get_all_symbols_with_path():
    """
    Endpoint diagnostik untuk menampilkan SEMUA simbol dari MT5 beserta path-nya.
    Ini digunakan untuk mengidentifikasi path yang benar untuk saham di broker Anda.
    """
    try:
        all_symbols = mt5.symbols_get()
        symbols_info = [{"name": s.name, "path": s.path} for s in all_symbols]
        return jsonify(symbols_info)
    except Exception as e:
        logger.error(f"Gagal mengambil daftar simbol dari MT5: {e}", exc_info=True)
        return jsonify({"error": "Tidak dapat terhubung atau mengambil data dari MT5."}), 500
