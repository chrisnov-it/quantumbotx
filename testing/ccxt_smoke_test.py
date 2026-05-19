#!/usr/bin/env python3
"""Minimal CCXT connectivity smoke test for QuantumBotX."""

import argparse
import os
import sys
from typing import Any
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.utils.ccxt_spot import create_spot_exchange, get_spot_mode


def str_to_bool(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def build_exchange(exchange_id: str, api_key: str, api_secret: str, password: str, testnet: bool) -> Any:
    # testnet arg kept for backward compatibility in existing calls.
    del testnet
    return create_spot_exchange(
        exchange_id=exchange_id,
        api_key=api_key,
        api_secret=api_secret,
        api_password=password,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="CCXT API smoke test")
    parser.add_argument("--exchange", default=os.getenv("EXCHANGE_ID") or os.getenv("CCXT_EXCHANGE") or "binance")
    parser.add_argument("--symbol", default="BTC/USDT")
    parser.add_argument("--private", action="store_true", help="Run private endpoint tests (fetch_balance)")
    args = parser.parse_args()

    load_dotenv()

    exchange_id = args.exchange
    api_key = (os.getenv("CCXT_API_KEY") or "").strip()
    api_secret = (os.getenv("CCXT_API_SECRET") or "").strip()
    api_password = (os.getenv("CCXT_API_PASSWORD") or "").strip()
    testnet = str_to_bool(os.getenv("CCXT_TESTNET"), True)

    if not api_key or not api_secret:
        print("ERROR: CCXT_API_KEY/CCXT_API_SECRET belum diisi di .env")
        return 2

    print(f"Exchange: {exchange_id}")
    print(f"Spot env: {get_spot_mode()} (legacy CCXT_TESTNET={testnet})")
    print("API key : configured")

    try:
        exchange = build_exchange(exchange_id, api_key, api_secret, api_password, testnet)
        # Time sync is intentionally skipped for public smoke tests. Some networks
        # block exchange time endpoints even when ticker/OHLCV endpoints work.
    except Exception as exc:
        print(f"ERROR: failed to build exchange client: {exc}")
        return 3

    # Public endpoint test
    try:
        ticker = exchange.fetch_ticker(args.symbol)
        last = ticker.get("last")
        bid = ticker.get("bid")
        ask = ticker.get("ask")
        print(f"Public OK  : {args.symbol} last={last} bid={bid} ask={ask}")
    except Exception as exc:
        print(f"Public FAIL: {exc}")
        return 4

    # Private endpoint test
    if args.private:
        try:
            bal = exchange.fetch_balance()
            total = bal.get("total", {}) if isinstance(bal, dict) else {}
            usdt = total.get("USDT") if isinstance(total, dict) else None
            print(f"Private OK : fetch_balance success (USDT={usdt})")
        except Exception as exc:
            print(f"Private FAIL: {exc}")
            return 5

    print("Smoke test PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
