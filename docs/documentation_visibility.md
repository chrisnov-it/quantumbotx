# Documentation Visibility Guide

## Purpose

This guide defines which QuantumBotX documents are safe for public Git, which should stay private, and which should never be committed.

Use this before publishing the repository, preparing releases, or moving docs between private and public branches.

## Branch Visibility Warning

Do not rely on `main` being public and other branches being private inside the same remote repository. On common Git hosting platforms, repository visibility applies to the whole repository, and pushed branches inherit that visibility.

Recommended setup:

- Keep the full working repository private.
- Publish a separate sanitized public repository, or push only a sanitized `main` branch to a dedicated public remote.
- Never push private branches, internal docs, generated knowledge bases, databases, or local config files to the public remote.

## Public-Safe Documents

These can be committed to a public repository after normal review:

- `README.md`
- `README_NEW.md` if it becomes the active README
- `LICENSE.md`
- `CHANGELOG.md`
- `ROADMAP.md`
- `DOCKER_GUIDE.md`
- `MT5_SETUP_GUIDE.md`
- `PACKAGING_README.md`
- `QUICK_START_GUIDE.md`
- `docs/*.md` when they describe architecture, usage, or general development workflow
- `testing/` files that use synthetic data, app smoke checks, or public API validation without embedded credentials

Public docs must avoid:

- real API keys or account IDs,
- personal financial details,
- private pricing experiments,
- claims of guaranteed profitability,
- screenshots or logs that expose broker accounts,
- private deployment URLs or machine paths.

## Internal-Only Documents

These are useful for development but should stay out of public Git unless sanitized:

- `MEMORY.md`
- `TASKS.md`
- `RETROSPECT.md`
- `WALKTHROUGH.md`
- `PAYMENT_SETUP.md`
- `INVESTMENT_RETURN.md`
- `DESKTOP_DEPLOYMENT.md`
- `STRATEGY_IDEAS.md`
- `testing_private/`

Keep broker-specific diagnostics, local account troubleshooting, state-changing repair scripts, and files that read or print account details in `testing_private/`.

Reason:

- They may expose product strategy, monetization plans, internal decision history, unfinished work, or non-public positioning.
- They are excellent for private development continuity, but public readers may interpret rough notes as product promises.

If a public version is needed, create sanitized files such as:

- `docs/roadmap_public.md`
- `docs/contributing.md`
- `docs/architecture.md`
- `docs/broker_architecture.md`

## Never Commit

These should not be committed to public or private Git unless there is a very specific secure-storage reason:

- `.env`
- `.env.*` except `.env.example`
- `bots.db`
- `*.db`
- `logs/`
- `testing/*.log`
- `last_broker.json`
- API keys, broker credentials, payment credentials
- real account statements or trade exports
- private installer signing keys
- generated local backups, including WSL recovery dumps

## Generated Documentation

Generated documentation folders such as `.qoder/repowiki/` should be treated as generated artifacts.

Recommendation:

- Do not publish them by default.
- If they are already tracked, review and untrack them separately.
- Keep only curated docs in `docs/`.

## Roadmap Status

`ROADMAP.md` is currently aligned with the functional-first direction:

- Phase 0 covers runtime stabilization.
- Phase 1 covers demo trading and CCXT testnet flow.
- Phase 2 covers risk and reliability.
- Phase 3 covers verification discipline.
- Phase 4 correctly gates any live pilot behind strict readiness criteria.

Suggested future addition:

- Add an explicit broker-modularization milestone under Phase 1 or Phase 2:
  - MT5 remains supported for Windows users.
  - CCXT becomes the cross-platform broker path.
  - Routes and bot execution should depend on broker-neutral services.
