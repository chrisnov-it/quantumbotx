# CLAUDE.md — QuantumBotX

## Project Overview
AI-powered modular trading bot for MetaTrader 5.
Windows-first, Python + Flask + Tailwind CSS + Chart.js.
Live demo validated on XM Global MT5.

## Branches
- **`main`** — MT5-only, stable, active. 4 bots running on XM demo.
- **`refactor/universal-architecture`** — broker-agnostic (CCXT + MT5), paused.

## Active Context (2026-06-23)
- 4 bots running: EURUSD (MA), GBPUSD (RSI), AUDUSD (Bollinger), GOLD (Turtle)
- 2 SELL positions executed, ~$1.80 floating profit
- All risk management active: break-even, spread guard, ATR cap
- Venv: Python 3.14.4, MetaTrader5 5.0.5735

## Key Files
| File | Purpose |
|------|---------|
| `run.py` | App entry + MT5 init |
| `core/bots/trading_bot.py` | Bot thread (main loop, risk mgmt) |
| `core/mt5/trade.py` | Order execution (SL/TP calc, I/O) |
| `core/utils/mt5.py` | MT5 helpers (symbol mapping, rates) |
| `core/strategies/` | 14 strategies |
| `templates/base.html` | Main layout + dark mode toggle |
| `.env` | MT5 creds + broker config |

## Critical Fixes (do not revert)
- `find_mt5_symbol()`: broker priority MUST be guarded with `base_symbol_cleaned == 'XAUUSD'`
- `ORDER_FILLING_FOK` → `ORDER_FILLING_IOC` for XM broker compat
- `place_trade()`: ATR multiplier capped at max 5× SL / 10× TP

## Commands
```bash
source venv/Scripts/activate && python run.py  # Start app
curl http://127.0.0.1:5000/api/health           # Check status
curl http://127.0.0.1:5000/api/bots/status       # Bot list
```

## Docs (excluded from git)
TASKS.md, MEMORY.md, WALKTHROUGH.md, RETROSPECT.md
