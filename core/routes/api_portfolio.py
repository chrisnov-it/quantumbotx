# core/routes/api_portfolio.py

import logging
import os

from flask import Blueprint, jsonify

from core.utils.market_data import get_open_positions

api_portfolio = Blueprint("api_portfolio", __name__, url_prefix="/api/portfolio")
logger = logging.getLogger(__name__)


def _runtime_broker_type() -> str:
    return (os.getenv("BROKER_TYPE", "MT5") or "MT5").strip().upper()


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _allocation_from_positions(positions):
    allocation_summary = {
        "Forex": 0.0,
        "Emas": 0.0,
        "Saham": 0.0,
        "Crypto": 0.0,
        "Lainnya": 0.0,
    }

    for pos in positions or []:
        symbol = str(pos.get("symbol", "")).upper()
        weight = _safe_float(pos.get("volume", 0.0), 0.0)
        if "/" in symbol:
            # For CCXT spot, use notional if available.
            maybe_notional = _safe_float(pos.get("price_current", 0.0), 0.0) * _safe_float(pos.get("volume", 0.0), 0.0)
            if maybe_notional > 0:
                weight = maybe_notional

        if "USD" in symbol and "XAU" not in symbol and "BTC" not in symbol:
            allocation_summary["Forex"] += weight
        elif "XAU" in symbol:
            allocation_summary["Emas"] += weight
        elif any(stock in symbol for stock in ["AAPL", "GOOGL", "TSLA", "ND100", "SP500"]):
            allocation_summary["Saham"] += weight
        elif any(crypto in symbol for crypto in ["BTC", "ETH", "SOL", "XRP", "LTC", "/"]):
            allocation_summary["Crypto"] += weight
        else:
            allocation_summary["Lainnya"] += weight

    final_allocation = {k: v for k, v in allocation_summary.items() if v > 0}
    return {
        "labels": list(final_allocation.keys()) or ["Belum Ada Posisi"],
        "values": list(final_allocation.values()) or [1],
    }


@api_portfolio.route("/open-positions")
def api_open_positions():
    """Provide open positions for MT5 or CCXT runtime."""
    try:
        broker_type = _runtime_broker_type()
        positions = get_open_positions() or []

        return jsonify({"success": True, "broker_type": broker_type, "positions": positions})
    except Exception as e:
        logger.error("Portfolio open-positions error: %s", e, exc_info=True)
        return jsonify({"success": False, "error": str(e), "positions": []}), 500


@api_portfolio.route("/allocation")
def get_asset_allocation():
    """Calculate asset allocation from open positions."""
    try:
        broker_type = _runtime_broker_type()
        positions = get_open_positions() or []

        data = _allocation_from_positions(positions)
        data["success"] = True
        data["broker_type"] = broker_type
        return jsonify(data)
    except Exception as e:
        logger.error("Portfolio allocation error: %s", e, exc_info=True)
        return jsonify({"success": False, "error": str(e), "labels": ["Error"], "values": [1]}), 500
