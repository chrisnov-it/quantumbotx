# CLAUDE.md — QuantumBotX

## Project Overview
AI-powered modular trading bot built with Python & Flask.
Supports MetaTrader 5 + CCXT with backtesting, strategy testing, and web dashboard.

## Architecture
```
Flask Web UI (Jinja2 + Tailwind CSS + Chart.js)
    ↓
API Routes (core/routes/ — 21 endpoints)
    ↓
Controller (core/bots/controller.py)
    ↓
TradingBot / CCXTTradingBot (core/bots/)
    ↓
23 Strategies (core/strategies/)
    ↓
BrokerFactory (core/brokers/broker_factory.py)
    ↓
10 Broker Adapters (MT5, Binance, cTrader, IBKR...)
    ↓
BrokerInterface (core/interfaces/broker_interface.py)
```

## Branches
- `main` — MT5-only, stable, working
- `refactor/universal-architecture` — active development, CCXT + broker-agnostic

## Key Files
| File | Purpose |
|------|---------|
| `run.py` | App entry point |
| `core/bots/controller.py` | Bot lifecycle (start/stop/update) |
| `core/brokers/broker_factory.py` | Broker instantiation |
| `core/interfaces/broker_interface.py` | Broker abstraction contract |
| `core/strategies/` | 23 trading strategies |
| `core/backtesting/enhanced_engine.py` | Backtesting engine |
| `templates/base.html` | Main layout (sidebar + header + dark mode) |
| `static/js/main.js` | Dark mode toggle + notification system |

## UI Conventions
- Dark mode: Tailwind `class` strategy, localStorage `dark-mode` key
- Icons: Font Awesome 6 via CDN
- Charts: Chart.js via CDN
- i18n: Custom system (ID/EN toggle in header)

## Commands
```bash
python run.py              # Start dev server
python testing/ccxt_smoke_test.py  # Test CCXT connection
```

## VPS / Deploy
- Docker setup: `docker compose up` (Python 3.13)
- No automated CI/CD yet (unlike `landing` repo)

## Docs (excluded from git — in .gitignore)
- `TASKS.md` — sprint tasks
- `MEMORY.md` — product memory
- `WALKTHROUGH.md` — daily guide
- `RETROSPECT.md` — decision log

## Memory
Stored at `C:\Users\umeck\.claude\projects\D--dev-chrisnov-it-chrisnov-landing\memory\quantumbotx\`
