#!/usr/bin/env python3
"""Public-safe regression smoke checks for QuantumBotX.

This script intentionally avoids broker credentials and live order execution.
It is meant to answer one question quickly: can the app import, compile, and
validate core strategies in the current Python environment?
"""

from __future__ import annotations

import compileall
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def check_compileall() -> bool:
    print("[1/3] compileall core + testing")
    ok = compileall.compile_dir(str(ROOT / "core"), quiet=1)
    ok = compileall.compile_dir(str(ROOT / "testing"), quiet=1) and ok
    print("      OK" if ok else "      FAIL")
    return ok


def check_app_factory() -> bool:
    print("[2/3] app factory import")
    os.environ.setdefault("SKIP_MT5_INIT", "1")
    os.environ.setdefault("BROKER_TYPE", "CCXT")
    try:
        from core import create_app

        app = create_app()
        route_count = len(app.url_map._rules)
        print(f"      OK ({route_count} routes)")
        return route_count > 0
    except Exception as exc:
        print(f"      FAIL: {exc}")
        return False


def check_strategy_validation() -> bool:
    print("[3/3] strategy validation")
    try:
        from testing.validate_all_strategies import (
            check_strategy_id_consistency,
            validate_backtesting_compatibility,
            validate_strategy_classes,
            validate_strategy_registration,
        )

        registered, metadata = validate_strategy_registration()
        working, broken = validate_strategy_classes()
        id_issues = check_strategy_id_consistency()
        compatible, incompatible = validate_backtesting_compatibility()

        ok = bool(registered) and bool(metadata) and bool(working) and not broken and not id_issues and not incompatible
        print(
            "      OK"
            if ok
            else f"      FAIL: broken={broken}, id_issues={id_issues}, incompatible={incompatible}"
        )
        return ok and bool(compatible)
    except Exception as exc:
        print(f"      FAIL: {exc}")
        return False


def main() -> int:
    checks = [
        check_compileall(),
        check_app_factory(),
        check_strategy_validation(),
    ]
    if all(checks):
        print("Regression smoke PASSED")
        return 0
    print("Regression smoke FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
