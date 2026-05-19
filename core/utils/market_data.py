import os
import logging
from typing import Optional

import pandas as pd
from core.db import queries
from core.utils.ccxt_spot import create_spot_exchange
from core.utils.mt5 import (
    TIMEFRAME_MAP,
    get_account_info_mt5,
    get_open_positions_mt5,
    get_rates_mt5,
    get_todays_profit_mt5,
)

logger = logging.getLogger(__name__)
_CCXT_CLIENT = None


def _runtime_broker_type() -> str:
    return (os.getenv("BROKER_TYPE", "MT5") or "MT5").strip().upper()


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_ccxt_symbol(raw_symbol: str) -> str:
    if not raw_symbol:
        return raw_symbol
    if "/" in raw_symbol:
        return raw_symbol.upper()

    symbol = raw_symbol.strip().upper().replace("-", "").replace("_", "")
    quote_candidates = ("USDT", "USDC", "BUSD", "USD", "BTC", "ETH", "BNB", "EUR", "TRY")
    for quote in quote_candidates:
        if symbol.endswith(quote) and len(symbol) > len(quote):
            return f"{symbol[:-len(quote)]}/{quote}"
    return raw_symbol.upper()


def _timeframe_to_ccxt(timeframe: str) -> str:
    return {
        "M1": "1m",
        "M5": "5m",
        "M15": "15m",
        "M30": "30m",
        "H1": "1h",
        "H4": "4h",
        "D1": "1d",
    }.get((timeframe or "H1").upper(), "1h")


def _get_ccxt_client() -> Optional[object]:
    global _CCXT_CLIENT
    if _CCXT_CLIENT is not None:
        return _CCXT_CLIENT

    try:
        import ccxt
    except Exception:
        logger.warning("ccxt module tidak tersedia untuk market_data CCXT.")
        return None

    exchange_id = (os.getenv("EXCHANGE_ID") or os.getenv("CCXT_EXCHANGE") or "binance").strip().lower()
    api_key = (os.getenv("CCXT_API_KEY") or "").strip()
    api_secret = (os.getenv("CCXT_API_SECRET") or "").strip()
    api_password = (os.getenv("CCXT_API_PASSWORD") or "").strip()

    try:
        client = create_spot_exchange(
            exchange_id=exchange_id,
            api_key=api_key,
            api_secret=api_secret,
            api_password=api_password,
            require_credentials=False,
        )
    except Exception as e:
        logger.error("Gagal membuat client CCXT: %s", e)
        return None

    try:
        client.load_markets()
    except Exception as e:
        logger.error("Gagal inisialisasi client CCXT: %s", e)
        return None

    _CCXT_CLIENT = client
    return _CCXT_CLIENT


def _create_private_ccxt_client() -> object:
    exchange_id = (os.getenv("EXCHANGE_ID") or os.getenv("CCXT_EXCHANGE") or "binance").strip().lower()
    api_key = (os.getenv("CCXT_API_KEY") or "").strip()
    api_secret = (os.getenv("CCXT_API_SECRET") or "").strip()
    api_password = (os.getenv("CCXT_API_PASSWORD") or "").strip()
    return create_spot_exchange(
        exchange_id=exchange_id,
        api_key=api_key,
        api_secret=api_secret,
        api_password=api_password,
        require_credentials=True,
    )


def _has_ccxt_private_credentials() -> bool:
    return bool((os.getenv("CCXT_API_KEY") or "").strip() and (os.getenv("CCXT_API_SECRET") or "").strip())


def _empty_ccxt_account_info():
    return {
        "equity": 0.0,
        "balance": 0.0,
        "margin": 0.0,
        "free_margin": 0.0,
        "todays_profit": 0.0,
        "requires_credentials": True,
    }


def _last_price(exchange, tickers, symbol: str):
    ticker = tickers.get(symbol) if isinstance(tickers, dict) else None
    if not ticker:
        try:
            ticker = exchange.fetch_ticker(symbol)
        except Exception:
            return None
    return _safe_float(ticker.get("last") or ticker.get("bid") or ticker.get("ask"), default=None)


def _estimate_spot_avg_entry_price(exchange, symbol: str, qty_now: float, limit: int = 300):
    """Estimate current spot inventory average price from account trade history."""
    if qty_now <= 0:
        return None, False
    try:
        trades = exchange.fetch_my_trades(symbol, limit=limit)
    except Exception:
        return None, False
    if not trades:
        return None, False

    trades = sorted(trades, key=lambda t: t.get("timestamp") or 0)
    qty = 0.0
    cost = 0.0
    for trade in trades:
        side = str(trade.get("side", "")).lower()
        amount = _safe_float(trade.get("amount"), 0.0)
        price = _safe_float(trade.get("price"), 0.0)
        if amount <= 0 or price <= 0:
            continue

        if side == "buy":
            qty += amount
            cost += amount * price
        elif side == "sell" and qty > 0:
            reduce_qty = min(amount, qty)
            avg = cost / qty if qty > 0 else 0.0
            qty -= reduce_qty
            cost -= avg * reduce_qty

    if qty <= 0:
        return None, True
    return (cost / qty if cost > 0 else None), True


def _get_ccxt_account_info():
    if not _has_ccxt_private_credentials():
        return _empty_ccxt_account_info()

    exchange = _create_private_ccxt_client()
    markets = exchange.load_markets()
    balance = exchange.fetch_balance()

    total_bal = balance.get("total", {}) if isinstance(balance, dict) else {}
    free_bal = balance.get("free", {}) if isinstance(balance, dict) else {}
    used_bal = balance.get("used", {}) if isinstance(balance, dict) else {}

    try:
        tickers = exchange.fetch_tickers()
    except Exception:
        tickers = {}

    stable_quotes = {"USDT", "USDC", "BUSD", "FDUSD", "TUSD", "USD"}

    def asset_to_usdt(asset: str):
        asset = (asset or "").upper()
        if asset in stable_quotes:
            return 1.0
        direct = f"{asset}/USDT"
        if direct in markets:
            return _last_price(exchange, tickers, direct)
        via_btc = f"{asset}/BTC"
        if via_btc in markets and "BTC/USDT" in markets:
            asset_btc = _last_price(exchange, tickers, via_btc)
            btc_usdt = _last_price(exchange, tickers, "BTC/USDT")
            if asset_btc is not None and btc_usdt is not None:
                return asset_btc * btc_usdt
        return None

    def sum_in_usdt(balance_map):
        total = 0.0
        if not isinstance(balance_map, dict):
            return total
        for asset, qty in balance_map.items():
            amount = _safe_float(qty, default=0.0)
            if amount <= 0:
                continue
            rate = asset_to_usdt(str(asset))
            if rate is None:
                continue
            total += amount * rate
        return total

    equity_usdt = sum_in_usdt(total_bal)
    used_usdt = sum_in_usdt(used_bal)
    free_usdt = sum_in_usdt(free_bal)
    if free_usdt <= 0 and equity_usdt > 0:
        free_usdt = max(0.0, equity_usdt - used_usdt)

    return {
        "equity": equity_usdt,
        "balance": equity_usdt,
        "margin": used_usdt,
        "free_margin": free_usdt,
        "todays_profit": 0.0,
    }


def _get_ccxt_open_positions():
    if not _has_ccxt_private_credentials():
        return []

    exchange = _create_private_ccxt_client()
    exchange.load_markets()
    include_balance_only = _env_bool("CCXT_PORTFOLIO_INCLUDE_BALANCE_ONLY", False)
    markets = getattr(exchange, "markets", {})
    try:
        tickers = exchange.fetch_tickers()
    except Exception:
        tickers = {}

    symbols = []
    for bot in queries.get_all_bots():
        raw = bot.get("market")
        if not raw:
            continue
        symbol = _normalize_ccxt_symbol(raw)
        if symbol in markets:
            symbols.append(symbol)
    symbols = sorted(set(symbols))

    balance = exchange.fetch_balance()
    total_bal = balance.get("total", {}) if isinstance(balance, dict) else {}
    stable_quotes = {"USDT", "USDC", "BUSD", "FDUSD", "TUSD", "USD"}

    def quote_to_usdt(quote_asset: str):
        quote = (quote_asset or "").upper()
        if quote in stable_quotes:
            return 1.0

        direct = f"{quote}/USDT"
        if direct in markets:
            return _last_price(exchange, tickers, direct)

        inverse = f"USDT/{quote}"
        if inverse in markets:
            inverse_price = _last_price(exchange, tickers, inverse)
            if inverse_price and inverse_price > 0:
                return 1.0 / inverse_price

        via_btc = f"{quote}/BTC"
        if via_btc in markets and "BTC/USDT" in markets:
            quote_btc = _last_price(exchange, tickers, via_btc)
            btc_usdt = _last_price(exchange, tickers, "BTC/USDT")
            if quote_btc is not None and btc_usdt is not None:
                return quote_btc * btc_usdt
        return None

    positions = []
    for symbol in symbols:
        base, quote = symbol.split("/")
        qty = _safe_float((total_bal or {}).get(base, 0.0), 0.0)
        if qty <= 0:
            continue

        current_price = _safe_float(_last_price(exchange, tickers, symbol), 0.0)
        if current_price <= 0:
            continue

        avg_entry, has_trade_history = _estimate_spot_avg_entry_price(exchange, symbol, qty_now=qty)
        if not include_balance_only and not has_trade_history:
            continue
        if avg_entry is None or avg_entry <= 0:
            avg_entry = current_price

        unrealized_quote = (current_price - avg_entry) * qty
        quote_rate = quote_to_usdt(quote)
        unrealized_usdt = unrealized_quote * quote_rate if quote_rate is not None else unrealized_quote
        notional_quote = qty * current_price
        notional_usdt = notional_quote * quote_rate if quote_rate is not None else None

        positions.append(
            {
                "symbol": symbol,
                "type": "SPOT",
                "volume": qty,
                "price_open": avg_entry,
                "price_current": current_price,
                "profit": unrealized_usdt,
                "profit_usdt": unrealized_usdt,
                "profit_quote": unrealized_quote,
                "quote_asset": quote,
                "quote_to_usdt": quote_rate,
                "notional_usdt": notional_usdt,
                "magic": "-",
                "broker_type": "CCXT",
            }
        )

    return positions


def get_market_rates(symbol: str, timeframe: str, count: int = 100):
    try:
        if _runtime_broker_type() == "CCXT":
            client = _get_ccxt_client()
            if client is None:
                return pd.DataFrame()
            ccxt_symbol = _normalize_ccxt_symbol(symbol)
            tf = _timeframe_to_ccxt(timeframe)
            rows = client.fetch_ohlcv(ccxt_symbol, timeframe=tf, limit=count)
            if not rows:
                return pd.DataFrame()
            df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"])
            df["time"] = pd.to_datetime(df["time"], unit="ms", utc=True)
            df.set_index("time", inplace=True)
            return df

        tf = TIMEFRAME_MAP.get(timeframe, TIMEFRAME_MAP["H1"])
        return get_rates_mt5(symbol, tf, count)
    except Exception as e:
        logger.error(f"Error fetching market rates for {symbol}: {e}")
        return None


def get_symbol_info(symbol: str):
    try:
        if _runtime_broker_type() == "CCXT":
            client = _get_ccxt_client()
            if client is None:
                return None
            ccxt_symbol = _normalize_ccxt_symbol(symbol)
            market = client.market(ccxt_symbol)
            return {
                "name": market.get("symbol", ccxt_symbol),
                "digits": (market.get("precision") or {}).get("price"),
                "min_volume": ((market.get("limits") or {}).get("amount") or {}).get("min"),
                "max_volume": ((market.get("limits") or {}).get("amount") or {}).get("max"),
                "volume_step": (market.get("precision") or {}).get("amount"),
            }

        from core.utils.mt5 import mt5
        return mt5.symbol_info(symbol)
    except Exception as e:
        logger.error(f"Error fetching symbol info for {symbol}: {e}")
        return None


def get_account_info():
    if _runtime_broker_type() == "CCXT":
        return _get_ccxt_account_info()
    return get_account_info_mt5()


def get_open_positions():
    if _runtime_broker_type() == "CCXT":
        return _get_ccxt_open_positions()
    return get_open_positions_mt5()


def get_todays_profit() -> float:
    if _runtime_broker_type() == "CCXT":
        return 0.0
    return get_todays_profit_mt5()
