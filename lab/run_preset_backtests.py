import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

import MetaTrader5 as mt5
from core.backtesting.enhanced_engine import run_enhanced_backtest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRESET_DIR = PROJECT_ROOT / "config" / "presets"


def load_mt5_credentials() -> tuple[int, str, str]:
    load_dotenv(PROJECT_ROOT / ".env")
    login = int(os.getenv("MT5_LOGIN", "0"))
    password = os.getenv("MT5_PASSWORD", "")
    server = os.getenv("MT5_SERVER", "")
    if not login or not password or not server:
        raise RuntimeError("MT5 credentials missing in .env")
    return login, password, server


def detect_broker_server(login: int, password: str, server: str) -> str:
    if not mt5.initialize(login=login, password=password, server=server):  # type: ignore
        raise RuntimeError(f"MT5 init failed: {mt5.last_error()}")  # type: ignore
    info = mt5.account_info()  # type: ignore
    if not info:
        mt5.shutdown()  # type: ignore
        raise RuntimeError("MT5 account_info failed")
    return str(info.server).upper()


def choose_preset(broker_server: str, forced_preset: str | None) -> Path:
    if forced_preset:
        path = PRESET_DIR / forced_preset
        if not path.exists():
            raise FileNotFoundError(f"Preset not found: {path}")
        return path

    for preset_path in PRESET_DIR.glob("*.json"):
        with open(preset_path, "r", encoding="utf-8") as f:
            preset = json.load(f)
        for token in preset.get("broker_match", []):
            if token.upper() in broker_server:
                return preset_path

    return PRESET_DIR / "xm_demo.json"


def run_case(case: dict, symbol_map: dict, tail_rows: int) -> dict:
    raw_symbol = case["symbol"]
    resolved_symbol = symbol_map.get(raw_symbol, raw_symbol)
    data_file = PROJECT_ROOT / case["data_file"]
    if not data_file.exists():
        return {
            "name": case["name"],
            "symbol": resolved_symbol,
            "strategy": case["strategy_id"],
            "status": "missing_data",
            "error": f"Missing file: {data_file}",
        }

    df = pd.read_csv(data_file, parse_dates=["time"]).tail(tail_rows)
    result = run_enhanced_backtest(
        case["strategy_id"],
        case["params"],
        df,
        symbol_name=resolved_symbol,
        engine_config={
            "enable_spread_costs": True,
            "enable_slippage": True,
            "enable_realistic_execution": True,
        },
    )
    if "error" in result:
        return {
            "name": case["name"],
            "symbol": resolved_symbol,
            "strategy": case["strategy_id"],
            "status": "error",
            "error": result["error"],
        }

    return {
        "name": case["name"],
        "symbol": resolved_symbol,
        "strategy": case["strategy_id"],
        "status": "ok",
        "gross_profit_usd": result.get("gross_profit_usd", 0),
        "net_profit_usd": result.get("net_profit_after_costs", 0),
        "spread_costs_usd": result.get("total_spread_costs", 0),
        "win_rate_percent": result.get("win_rate_percent", 0),
        "max_drawdown_percent": result.get("max_drawdown_percent", 0),
        "total_trades": result.get("total_trades", 0),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run broker preset backtests")
    parser.add_argument("--preset", help="Preset file name in config/presets, e.g. xm_demo.json")
    parser.add_argument("--tail", type=int, default=5000, help="Number of latest rows to test per case")
    args = parser.parse_args()

    login, password, server = load_mt5_credentials()
    broker_server = detect_broker_server(login, password, server)
    preset_path = choose_preset(broker_server, args.preset)

    with open(preset_path, "r", encoding="utf-8") as f:
        preset = json.load(f)

    print(f"Using broker server: {broker_server}")
    print(f"Using preset: {preset_path.name} ({preset.get('preset_name', 'Unnamed')})")
    print("")

    rows = []
    for case in preset.get("cases", []):
        rows.append(run_case(case, preset.get("symbols", {}), args.tail))

    mt5.shutdown()  # type: ignore

    print("name | symbol | strategy | status | net | gross | spread | win_rate | drawdown | trades")
    for r in rows:
        if r["status"] != "ok":
            print(f"{r['name']} | {r['symbol']} | {r['strategy']} | {r['status']} | {r.get('error', '')}")
            continue
        print(
            f"{r['name']} | {r['symbol']} | {r['strategy']} | ok | "
            f"{r['net_profit_usd']:.2f} | {r['gross_profit_usd']:.2f} | {r['spread_costs_usd']:.2f} | "
            f"{r['win_rate_percent']:.2f}% | {r['max_drawdown_percent']:.2f}% | {r['total_trades']}"
        )

    out_dir = PROJECT_ROOT / "logs"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "preset_backtest_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "broker_server": broker_server,
                "preset_file": preset_path.name,
                "results": rows,
            },
            f,
            indent=2,
        )
    print(f"\nSaved: {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
