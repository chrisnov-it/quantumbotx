# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Planned
- Add explicit Python compatibility test matrix for 3.12, 3.13, and 3.14.

## [2026-05-19]

### Changed
- Clarified startup flow in `README.md` to include first-run database initialization.
- Added troubleshooting steps for `no such table` database errors.
- Added troubleshooting steps for resolving local conflict after forced history updates.

### Fixed
- Fixed database initialization path in `core/__init__.py` so schema setup uses
  the project root `bots.db` in script mode.

### Repository Maintenance
- Rewrote `main` branch history to remove large generated artifacts and datasets:
  - `QuantumBotX-Installer.exe`
  - `QuantumBotX-Portable.zip`
  - `lab/*_data.csv`
  - `lab/backtest_data/*.csv`
- Updated `.gitignore` to keep generated backtest datasets out of Git.
- Removed obsolete remote branches:
  - `fix/update-numpy`
  - `fix-vercel-json-syntax`

## [2025-09]

### Notes
- Previous beta-era notes existed in a long-form marketing style document.
- Historical feature development from that period remains in git history and
  project docs, while this changelog now focuses on operational release notes.
