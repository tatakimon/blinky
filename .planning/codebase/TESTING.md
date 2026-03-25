# Testing
## Authority Order
- In the trusted operational repo context, authority order is: `AGENTS.md`, `TODO.md`, `PROJECT_STATE.md`, `RUNBOOK.md`.
- Current phase, helper status, trusted baseline/LKG identity, token policy, and the next exact action must be taken from those root control files, not from this secondary codebase-map note.
- Current authoritative working repo context for this working copy is `/home/kerem/new_embedder_codex_app_gsd/blinky`.
- Earlier verified-host evidence from `~/stm32_sim_lab/blinky` remains historical audit lineage, not current repo authority for this working copy.
- If this file is read from another checkout such as `/home/kerem/copy/blinky`, treat that checkout as a non-authoritative analysis copy.


## Verification Model
- This project relies primarily on hardware-in-the-loop verification, not unit tests
- The pass condition is an end-to-end Layer A run: build, flash, optional readback verify, then UART token detection
- The canonical trusted operator path is documented in `RUNBOOK.md`

## Main Verification Entry Points
- `deploy.sh` is the human-facing command entrypoint
- `autofix.sh` performs tool checks, UART detection, ST-LINK preflight, build, flash, readback verification, and report writing
- `test_runner.py` is the UART token verifier
- `tools/attempt_summary.py` is a report-extraction helper for individual attempts

## What Counts As Success
- Terminal output should end with `SUCCESS | report=...` as documented in `RUNBOOK.md`
- The matching report in `logs/closed_loop_report_*.md` should show:
- `PRECHECK: OK`
- `build=OK`
- `flash=OK`
- `flash_verify=OK` when enabled
- `uart=OK`

## Test Inputs And Configuration
- UART behavior is configured by `UART_PORT`, `UART_BAUD`, `UART_TIMEOUT`, and `UART_TOKEN`
- Retry and flash behavior is configured by `MAX_RETRIES`, `ENABLE_FLASH_READBACK_VERIFY`, `FLASH_RETRIES`, `FLASH_RETRY_DELAY`, and `USE_SUDO_FLASH`
- Explicit UART token passing is preferred for baseline runs

## Evidence Outputs
- `verbose.log`: full command trace
- `strategy_log.txt`: current run summary
- `logs/closed_loop_report_*.md`: attempt summary and authoritative report
- `logs/attempt_*/`: captured build, flash, verify, prompt, reply, and diff artifacts
- `versions/attempt_*/`: before/after snapshots used for rollback and audit

## Testing Gaps
- No repository-level unit tests, integration-test harness, or CI pipeline were found
- There is no package manifest to recreate Python dependencies automatically
- Hardware verification is host-specific and constrained by real USB, serial, and permission state
- Some helper scripts, especially `tools/closed_loop_codex_verbose.py`, are not in a verified state

## Practical Testing Patterns
- Fail fast on missing hardware or inaccessible ports before running the full retry loop
- Distinguish build, flash, and UART stages clearly instead of treating them as one outcome
- Preserve logs even on failure so later analysis can explain rejected candidates
- Use snapshots under `versions/`, preserved successful reports, and recorded control-file state as the primary trusted rollback/testing lineage; current git history is supplementary and starts later
- When a future snapshot is intentionally promoted, restore/reference behavior should follow `PROJECT_STATE.md` under `## Current Promoted LKG Record`
