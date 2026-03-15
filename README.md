# blinky

This repo currently has two distinct documentation layers:

## Layer A (Current Inner Repo Loop — exists today)
- Real operational path: `deploy.sh` -> `autofix.sh` -> `test_runner.py`
- Purpose: run closed-loop build/flash/UART verification inside this repo.
- Source of truth for operators: `RUNBOOK.md`
- Current evidence/risk tracking: `PROJECT_STATE.md`
- Immediate work queue: `TODO.md`

## Layer B (Future Outer Firmware-Agent System — planned)
- Purpose: build a larger autonomous firmware-agent system around Layer A.
- This layer is not implemented as the primary workflow yet.
- High-level roadmap lives in:
  - `planning.md`
  - `BUILD_AGENT_TODO.md`

## How to use docs
1. For current execution and troubleshooting, start with `RUNBOOK.md`.
2. For current repo truth, read `PROJECT_STATE.md`.
3. For immediate next step, follow `TODO.md`.
4. For future architecture planning, use `planning.md` and `BUILD_AGENT_TODO.md`.
