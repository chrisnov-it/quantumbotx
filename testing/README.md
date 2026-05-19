# Testing Directory Guide

`testing/` is intended to be safe for public Git.

Keep files here when they:

- use synthetic or bundled sample data,
- run app/strategy/backtest smoke checks,
- validate public APIs without embedded credentials,
- avoid printing broker account identifiers, balances, or login details,
- do not mutate local bot/database state unless clearly isolated.

Move files to `testing_private/` when they:

- read real broker credentials from `.env`,
- print account details, server names, balances, or login IDs,
- troubleshoot a specific broker account,
- repair or mutate local database/bot state,
- contain business-sensitive claims or private operational notes.

`testing_private/` is ignored by Git and should stay local/private.

## Quick Smoke

Run the public-safe regression smoke before committing runtime changes:

```bash
python testing/regression_smoke.py
```

The script checks syntax compilation, app factory import, and core strategy validation without broker credentials or live order execution.
