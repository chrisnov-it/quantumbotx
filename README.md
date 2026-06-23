# QuantumBotX

QuantumBotX is a **Windows-first trading bot and backtesting platform** for
MetaTrader 5. The `main` branch is intentionally kept focused on MT5 so users
can install, test, and run the current app without confusion from experimental
cross-platform work.

> 🚧 **Development Status:** Actively maintained but built in spare time.
> New features and fixes land when the developer's schedule allows.
> Contributions, ideas, and bug reports are always welcome.

Use this project for education, research, demo trading, and strategy validation.
Always test on a demo account before considering any live trading.

## Current Scope

- Primary runtime: MetaTrader 5 terminal on Windows.
- Backend: Python and Flask.
- Database: SQLite.
- Frontend: Flask templates, TailwindCSS, and Chart.js.
- Strategy tools: local technical indicator compatibility layer plus pandas.
- Development baseline: Python 3.12 is supported.

Experimental cross-platform work belongs on dedicated development branches, not
on `main`.

## Recent Changes

For operational updates, setup-impacting fixes, and repository maintenance
notes, see [CHANGELOG.md](CHANGELOG.md).

## Features

- MT5 account connection and symbol validation.
- Live bot management for MT5 instruments.
- Strategy parameter forms and beginner-friendly defaults.
- Historical data download from MT5.
- Realistic backtesting with ATR-based risk management, spread/slippage
  modeling, equity curves, drawdown, win rate, and trade history.
- Multiple built-in strategies for forex, gold, indices, and MT5-supported
  crypto CFD symbols.
- Dashboard and portfolio views for monitoring bot status and results.
- Indonesian AI mentor features for trade journaling and learning support.
- Holiday and session-aware helpers for safer trading routines.

## Platform Support

### Supported

- Windows 10/11, 64-bit recommended.
- MetaTrader 5 terminal installed locally.
- Python 3.12 recommended.

### Python Version Status

- Recommended and verified: Python `3.12.x` (tested with `3.12.10`).
- Newer versions such as `3.13` and `3.14` may work, but are currently treated
  as compatibility tests, not primary baseline.

### Experimental

- Linux with Wine may work for MT5, but it is not the primary support target.
- macOS requires a Windows VM, CrossOver, Wine, or a separate Windows machine.

### Not Supported On `main`

- Cloud/VPS without a local MT5 terminal session.
- Native non-MT5 broker execution.
- Cross-platform broker runtimes.

## Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/chrisnov-it/quantumbotx.git
   cd quantumbotx
   ```

2. Create and activate a virtual environment:

   ```bash
   py -3.12 -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Install and open MetaTrader 5.

   Log in to a demo account first and keep the terminal running while using
   QuantumBotX.

5. Configure `.env`:

   ```bash
   copy .env.example .env
   ```

   Then fill in:

   ```env
   MT5_LOGIN=your_mt5_login
   MT5_PASSWORD=your_mt5_password
   MT5_SERVER=your_broker_server
   SECRET_KEY=change_me
   DB_NAME=bots.db
   ```

6. Initialize local database schema (first run):

   ```bash
   python init_db.py
   ```

7. Start the app:

   ```bash
   python run.py
   ```

## Optional MT5 Helper

The project includes an MT5 setup helper:

```bash
python install_mt5_integration.py
```

Use it to check Python compatibility, MetaTrader5 package availability, MT5
terminal installation, and basic environment setup.

For more detail, see `MT5_SETUP_GUIDE.md`.

## Data And Backtesting

QuantumBotX can download historical OHLCV data through MT5 and use it for
strategy testing. Typical workflows:

- Use the web interface on the backtesting page.
- Run `python lab/download_data.py`.
- Upload CSV files through the backtesting UI.

### Broker Preset Backtests (XM/FBS)

You can run a preset batch backtest tuned for broker environments:

```bash
py -3.12 lab/run_preset_backtests.py
```

Optional:

```bash
py -3.12 lab/run_preset_backtests.py --preset xm_demo.json --tail 5000
```

Preset files are stored in:

- `config/presets/xm_demo.json`
- `config/presets/fbs_demo.json`

Results are saved to `logs/preset_backtest_results.json`.

Supported markets depend on the connected MT5 broker. Common examples include:

- Forex pairs such as EURUSD, GBPUSD, USDJPY.
- Gold symbols such as XAUUSD and broker-specific variants.
- Indices such as US30, US100, US500, DE30, UK100, when available.
- Crypto CFD symbols such as BTCUSD or ETHUSD, when available through MT5.

## Strategy Collection (14 Active)

| Difficulty | Strategies |
|------------|------------|
| 🟢 Beginner | MA Crossover, RSI Crossover, Turtle Breakout |
| 🟡 Intermediate | Bollinger Reversion, Bollinger Squeeze, Ichimoku Cloud, Pulse Sync, Index Momentum, QuantumBotX Hybrid, QuantumBotX Crypto |
| 🔴 Advanced | Quantum Velocity, Mercy Edge, Dynamic Breakout, Index Breakout Pro |

Strategy availability and behavior are validated by:

```bash
python testing/validate_all_strategies.py
```

## Testing Policy

Public-safe tests and diagnostics belong in `testing/`.

Local account-specific scripts, broker diagnostics, recovery scripts, logs, and
anything with private account context belong in `testing_private/`, which is
ignored by Git.

## Repository Notes

- `README.md` is the canonical public README.
- `ROADMAP.md` describes the current MT5-focused direction for `main`.
- Internal notes such as `MEMORY.md`, `TASKS.md`, `RETROSPECT.md`, and
  `WALKTHROUGH.md` are ignored and should not be committed publicly.
- The app intentionally keeps local `.env`, database files, logs, and broker
  state files out of Git.

## Troubleshooting

If MT5 connection fails:

- Make sure MetaTrader 5 is open and logged in.
- Confirm the account, password, and server in `.env`.
- Check that the symbol exists in Market Watch.
- Try a demo account first.
- Restart MT5 before restarting QuantumBotX.

If dependency installation fails:

- Use Python 3.12.
- Upgrade pip: `python -m pip install --upgrade pip`.
- Re-run `pip install -r requirements.txt`.

If you see database errors like `no such table: bots`:

- Run `python init_db.py` once in the project root.
- Make sure you run `python run.py` from the same project folder.

If `git pull` shows many conflicts after a forced remote update:

- Abort merge: `git merge --abort`
- Realign to remote main:
  `git fetch origin && git reset --hard origin/main && git clean -fd`

## Disclaimer

Trading foreign exchange, CFDs, crypto CFDs, and other leveraged products
involves significant risk. This software is provided for educational and
research purposes only. The author is not responsible for financial losses,
missed trades, broker issues, execution errors, or misuse of the software.

Always validate on a demo account and use conservative risk settings.

## License

This project is licensed under the MIT License. See `LICENSE.md`.

## Author

Developed by Chrisnov IT Solutions.
