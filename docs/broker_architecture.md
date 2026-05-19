# Broker Architecture Direction

## Purpose

QuantumBotX should remain one trading operations app with pluggable broker backends, not separate MT5 and CCXT applications.

MT5 is kept because it has already proven demo-account execution. CCXT is the cross-platform expansion path, especially for crypto exchanges and environments where MetaTrader5 Terminal is not available.

## Product Rule

- Keep MT5 support for Windows users and existing Forex/CFD workflows.
- Support CCXT for cross-platform crypto workflows.
- Do not fork the product into separate apps unless the user experience becomes truly different.
- Keep the default claim demo-first and safety-first until live-money validation is proven.

## Target Layers

1. UI and routes
   - Should call broker-neutral services.
   - Should not import `MetaTrader5` or `ccxt` directly.

2. Bot orchestration
   - Starts, stops, monitors, and logs bots.
   - Should not know broker-specific order payload details.

3. Strategy layer
   - Receives normalized OHLCV data.
   - Returns a consistent analysis contract, such as signal, explanation, and optional price/context.
   - Should not depend on MT5-specific names like `market_for_mt5` long-term.

4. Broker adapter layer
   - Owns broker-specific details:
     - symbol normalization,
     - timeframe mapping,
     - balance/equity retrieval,
     - position retrieval,
     - order placement,
     - close-position behavior,
     - precision/min-notional/min-lot rules,
     - SL/TP support differences.

5. Risk layer
   - Should enforce common guardrails before adapter execution:
     - max daily loss,
     - max concurrent positions,
     - min/max position size,
     - dry-run/paper-trading safeguards.

## Adapter Contract

The eventual stable broker interface should cover:

- `initialize(credentials) -> bool`
- `get_account_info() -> dict | None`
- `get_rates(symbol, timeframe, count) -> DataFrame`
- `get_open_positions() -> list[dict]`
- `place_order(symbol, side, amount, order_type, price, sl, tp, context) -> result`
- `close_position(position_id, symbol, amount, context) -> result`
- `get_symbol_info(symbol) -> dict | None`
- `get_todays_profit() -> float`

Return values should be normalized. The rest of the app should not need to know whether the source is MT5, CCXT spot, or CCXT futures.

## Current Reality

- MT5 path is mature enough to execute demo trades.
- CCXT path exists and is intentionally incremental:
  - `CCXTTradingBot` is spot-focused,
  - `CCXT_DRY_RUN=1` should be the first validation mode,
  - public/private exchange smoke tests exist,
  - risk parity with MT5 is not complete yet.
- Some routes and utilities still contain direct MT5 or CCXT logic. These should be migrated gradually into broker-neutral services.

## Migration Order

1. Keep app bootable in both `BROKER_TYPE=MT5` and `BROKER_TYPE=CCXT`.
2. Make dependency boundaries cross-platform:
   - `MetaTrader5` must be Windows-only and lazy-loaded.
   - CCXT public market-data reads should not require API keys.
3. Move dashboard, indicator, portfolio, and history endpoints behind broker-neutral services.
4. Consolidate duplicate broker abstractions into one adapter path.
5. Unify bot execution so strategy and risk logic are shared, while order execution remains adapter-specific.
6. Only add new strategies after runtime, risk, and logging are stable.

## Non-Goals For Now

- No guaranteed-profit positioning.
- No real-money readiness claim.
- No forced removal of MT5.
- No large rewrite while demo flow is unverified.
- No new advanced strategy work before CCXT risk parity and broker-neutral endpoints are stable.

## Validation Gates

- App factory/import smoke test passes.
- Strategy validation passes.
- MT5 demo lifecycle works on Windows.
- CCXT dry-run lifecycle works cross-platform.
- CCXT private smoke test passes before any testnet order execution.
- No broker-specific import crash when running on an unsupported platform.
