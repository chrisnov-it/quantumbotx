# core/routes/api_stocks.py

import logging
import os
from datetime import datetime
from flask import Blueprint, jsonify
from core.utils.symbols import get_stock_symbols
from core.utils.external import get_mt5_symbol_profile
from core.utils import market_data
from core.utils.ccxt_spot import create_spot_exchange

logger = logging.getLogger(__name__)

api_stocks = Blueprint('api_stocks', __name__)


def _runtime_broker_type() -> str:
    return (os.getenv("BROKER_TYPE", "MT5") or "MT5").strip().upper()


def _create_public_ccxt_exchange():
    exchange_id = (os.getenv("EXCHANGE_ID") or os.getenv("CCXT_EXCHANGE") or "binance").strip().lower()
    exchange = create_spot_exchange(exchange_id=exchange_id, require_credentials=False)
    exchange.load_markets()
    return exchange


def _format_bar_timestamp(df, row) -> str:
    timestamp = row.get("time") if hasattr(row, "get") else None
    if timestamp is None:
        timestamp = row.name
    try:
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    except AttributeError:
        return str(timestamp)

@api_stocks.route('/api/stocks/<symbol>/profile')
def get_stock_profile(symbol):
    # Profile fetching is currently external/MT5 specific. 
    # For CCXT we might need a different source or just return empty.
    if _runtime_broker_type() == "CCXT":
        return jsonify({"description": symbol, "sector": "Crypto", "industry": "Digital Assets"})
        
    profile = get_mt5_symbol_profile(symbol)
    if profile:
        return jsonify(profile)
    return jsonify({"error": "Could not fetch symbol profile from MT5"}), 404

@api_stocks.route('/api/stocks')
def get_stocks():
    """
    Mengambil daftar harga saham/crypto terkini.
    """
    broker_type = _runtime_broker_type()
    
    if broker_type == "CCXT":
        try:
            exchange = _create_public_ccxt_exchange()

            # Fetch top crypto pairs (hardcoded for now or fetch from exchange)
            # Fetching all tickers is heavy, so we fetch a few popular ones
            top_symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT', 'SOL/USDT', 'DOGE/USDT']
            top_symbols = [symbol for symbol in top_symbols if symbol in exchange.markets]
            
            result = []
            # Use fetch_tickers if supported for batch fetching
            try:
                tickers = exchange.fetch_tickers(top_symbols)
                for symbol, ticker in tickers.items():
                    result.append({
                        'symbol': symbol,
                        'last_price': ticker.get('last') or ticker.get('bid') or ticker.get('ask'),
                        'change': ticker['percentage'] if ticker.get('percentage') else 0.0, # CCXT percentage is usually 24h change
                        'time': datetime.fromtimestamp(ticker['timestamp']/1000).strftime('%H:%M:%S') if ticker.get('timestamp') else datetime.now().strftime('%H:%M:%S')
                    })
            except Exception as e:
                logger.error(f"Error fetching CCXT tickers: {e}")
                
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in get_stocks (CCXT): {e}")
            return jsonify([])

    # MT5 Logic
    # Ambil 20 saham paling populer (sudah diurutkan berdasarkan volume oleh fungsi)
    stock_symbols = get_stock_symbols(limit=20)
    if not stock_symbols:
        logger.warning("get_stock_symbols() tidak mengembalikan simbol saham.")
        return jsonify([])

    result = []
    symbols_to_process = [stock['name'] for stock in stock_symbols]

    # We need to use MT5 functions directly here because get_stock_symbols returns MT5 objects/paths
    # and the logic is specific to calculating daily change from D1 open.
    # Ideally this should be moved to MT5Adapter, but for now we keep it here if MT5 is available.
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            return jsonify([])
            
        for symbol in symbols_to_process:
            try:
                # 1. Ambil tick terakhir untuk harga saat ini
                tick = mt5.symbol_info_tick(symbol)
                if not tick or tick.ask == 0:
                    continue

                # 2. Ambil data bar harian (D1) untuk harga pembukaan
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 1)
                if rates is None or len(rates) == 0:
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
                logger.error(f"Error saat memproses simbol saham {symbol}: {e}")
    except ImportError:
        pass

    return jsonify(result)

@api_stocks.route('/api/stocks/<symbol>')
def get_stock_detail(symbol):
    # Gunakan market_data facade
    df = market_data.get_market_rates(symbol, "D1", 100)

    if df is None or df.empty:
        return jsonify({"error": f"Tidak bisa mengambil data untuk {symbol}"}), 404

    last = df.iloc[-1]
    timestamp = _format_bar_timestamp(df, last)
    volume = last.get('tick_volume', last.get('volume', 0)) if hasattr(last, "get") else 0
    return jsonify({
        "symbol": symbol,
        "time": timestamp,
        "open": last['open'],
        "high": last['high'],
        "low": last['low'],
        "close": last['close'],
        "volume": volume
    })

@api_stocks.route('/api/symbols/all')
def get_all_symbols_with_path():
    """
    Endpoint diagnostik.
    """
    broker_type = _runtime_broker_type()
    if broker_type == "CCXT":
        try:
            exchange = _create_public_ccxt_exchange()
            symbols_info = [{"name": s, "path": "Crypto"} for s in exchange.markets.keys()]
            return jsonify(symbols_info)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    try:
        import MetaTrader5 as mt5
        all_symbols = mt5.symbols_get()
        if all_symbols:
            symbols_info = [{"name": s.name, "path": s.path} for s in all_symbols]
            return jsonify(symbols_info)
        return jsonify([])
    except Exception as e:
        logger.error(f"Gagal mengambil daftar simbol dari MT5: {e}", exc_info=True)
        return jsonify({"error": "Tidak dapat terhubung atau mengambil data dari MT5."}), 500
