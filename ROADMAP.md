# QuantumBotX Roadmap

QuantumBotX `main` is currently maintained as a Windows-first MetaTrader 5
trading platform. Cross-platform broker work is intentionally developed outside
`main` until it is mature enough to merge cleanly.

## Current Focus

- Keep MT5 demo/live workflow stable on Windows.
- Keep strategy registration, backtesting, and dashboard modules installable on
  modern Python.
- Improve public-safe tests and documentation.
- Keep broker/account-specific diagnostics out of the public repository.

## Near-Term Work

- Harden setup for Python 3.12.
- Improve MT5 connection diagnostics and clearer user-facing error messages.
- Expand regression checks for strategy imports and backtesting.
- Review packaging scripts for Windows installer reliability.

## Deferred Work

- Cross-platform broker backends on dedicated development branches.
- Broker-neutral order and market-data interfaces outside `main`.
- Cloud/API trading platform concepts outside `main`.

Those items should stay on dedicated development branches until the MT5 platform
on `main` remains clean and stable.
