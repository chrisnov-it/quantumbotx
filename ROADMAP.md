# QuantumBotX Roadmap

## Phase 0: Stabilize Core Runtime (Now)

Target: keep the app functional and consistent in the development environment.

Exit criteria:

- App boot normal on WSL without MT5 crash path.
- Health endpoint and core bot APIs stable.
- No known medium/high dependency vulnerabilities.
- No medium/high bandit issues in default scan.

## Phase 1: Functional Demo Trading

Target: complete demo-account operational loop.

Exit criteria:

- Create/start/stop bot works reliably on demo account.
- CCXT testnet start/stop path works without MT5 runtime dependency.
- MT5 and CCXT runtime paths are documented as one modular broker architecture.
- Strategy analysis endpoint consistent across major strategies.
- Trade execution + close flow can run repeatedly without deadlock.
- Basic error handling and retry behavior defined for network failures.

## Phase 2: Risk and Reliability Layer

Target: avoid catastrophic behavior before real account consideration.

Exit criteria:

- Daily loss cap guardrail.
- Max concurrent positions per symbol/asset.
- Broker-agnostic risk guard behavior (same policy intent across MT5 and CCXT).
- Broker-neutral dashboard, portfolio, history, and indicator endpoints.
- Emergency stop and safe shutdown tested.
- Structured logs for audit and troubleshooting.

## Phase 3: Verification Discipline

Target: objective confidence before any live-money pilot.

Exit criteria:

- Regression test checklist documented and repeatable.
- Forward test report on demo account (minimum 4 weeks).
- Known limitations documented in README.
- Release checklist enforced before tagging.

## Phase 4: Optional Live Pilot

Target: small live test with strict exposure limits.

Entry conditions:

- All previous phases complete.
- Explicit risk disclaimer and operator SOP finalized.
- Capital-at-risk cap predefined and hard-enforced.
