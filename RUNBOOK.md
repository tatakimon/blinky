# Operator Runbook

## Scope
Current operational flow only:
- `deploy.sh`
- `autofix.sh`
- `test_runner.py`

No alternate workflow is defined here.

## Repo Context
- Current authoritative working repo context for this working copy is `/home/kerem/new_embedder_codex_app_gsd/blinky`.
- Earlier successful Layer A reports from 2026-03-08 originated in the earlier repo context `~/stm32_sim_lab/blinky` and remain historical audit evidence for this line of work.

## Script Purposes
- `deploy.sh`
  - operator entrypoint
  - validates args, prints effective run settings, calls `autofix.sh`
- `autofix.sh`
  - closed-loop orchestrator
  - performs early UART/ST-LINK preflight checks before retry loop work
  - runs Codex-guided retry loop (default `MAX_RETRIES=5`)
  - compiles, links, objcopies, flashes, optional readback verify, then UART verify
  - writes report and verbose logs
- `test_runner.py`
  - UART token verifier
  - opens serial port, waits up to timeout, returns success only if token is observed

## Normal Operator Flow
1. Connect ST-LINK and ensure UART device is visible.
2. Run from repo root:
   `./deploy.sh "<task>" "<UART_TOKEN>"`
   - For the post-change proof run, omit `UART_TOKEN` so the default-token path is exercised.
   - Pass `UART_TOKEN` explicitly only for controlled diagnostics or audit replay.
3. Optional env controls:
   - `MAX_RETRIES` (default `5`)
   - `USE_SUDO_FLASH` (default `0`)
   - `ENABLE_FLASH_READBACK_VERIFY` (default `1`)
   - `FLASH_RETRIES` (default `3`)
   - `FLASH_RETRY_DELAY` (default `3`)
   - `UART_BAUD` (default `115200`)
   - `UART_TIMEOUT` (default `8` in deploy/autofix usage)
   - `UART_PORT` (auto-detected if unset)
4. Watch terminal summary lines (`TRY x/y | ...`).
5. Open generated report path shown by final `SUCCESS | report=...` or `FAILED | report=...`.

## Token Precedence (Layer A Current Behavior)
Canonical token policy:
- Canonical current baseline token: `STWINBX1_ON_LINE`.
- `Kerem` is historical audit evidence only.
- Layer A defaults in the working tree are aligned to `STWINBX1_ON_LINE` and proven by `logs/closed_loop_report_20260323_143122.md`.

1. `deploy.sh` CLI arg 2 (`<UART_TOKEN>`) if provided.
2. Otherwise `deploy.sh` default token: `STWINBX1_ON_LINE`.
3. `deploy.sh` passes token to `autofix.sh` arg 2.
4. `autofix.sh` exports that token as `UART_TOKEN` when invoking `test_runner.py`.
5. `test_runner.py` fallback token (`STWINBX1_ON_LINE`) is used only when `UART_TOKEN` is not provided in environment (for example direct standalone invocation).

## Token-Default Alignment Status
- Current behavior in the working tree:
  - `deploy.sh` and `autofix.sh` default to `STWINBX1_ON_LINE`
  - `test_runner.py` fallback token is `STWINBX1_ON_LINE`
- Historical `Kerem` evidence remains historical only and is not used as normal operational fallback
- Successful default-token-path proof is recorded at `logs/closed_loop_report_20260323_143122.md` with `UART token source: default`.

## Controlled Token-Default Alignment Checklist
1. Later touch points are limited to `deploy.sh`, `autofix.sh`, and `test_runner.py`.
2. Intended end state for that later implementation:
   - `deploy.sh` default token becomes `STWINBX1_ON_LINE`
   - `autofix.sh` default token becomes `STWINBX1_ON_LINE`
   - `test_runner.py` fallback token remains `STWINBX1_ON_LINE` and stays aligned with the orchestrator defaults
3. The later implementation must not change the trusted Layer A workflow structure, the real-host evidence requirements, the quarantined status of `tools/closed_loop_codex_verbose.py`, or the promoted-snapshot convention.
4. Preserve pre-change evidence before editing: keep the mismatch statement, the historical 2026-03-08 report lineage, and the current `PROJECT_STATE.md` promoted-LKG record available as reference.
5. Post-change proof requirement: do not claim cleanup success until a fresh real-host Layer A success report on the proven host configuration is preserved with matching `verbose.log`, and that proof must exercise the default-token path without relying on an explicit CLI token override.
6. Rollback trigger and rollback reference: if the later implementation touches files outside this checklist, if the intended end state above is not achieved, or if the post-change default-token-path proof fails, restore the pre-change versions of `deploy.sh`, `autofix.sh`, and `test_runner.py` and refer back to the preserved pre-change reports/logs plus `PROJECT_STATE.md` for rollback authority.

## Expected Artifacts / Logs
- `strategy_log.txt` (task/token/retries for current run)
- `verbose.log` (detailed step-by-step command log for current run)
- `logs/closed_loop_report_YYYYMMDD_HHMMSS.md` (run report + attempt summary)
- `/tmp/Dell_2_Steval.bin` and `/tmp/Dell_2_Steval.readback.bin` (temporary build/readback artifacts)

## Trusted Baseline / LKG Procedure
- Current trusted baseline/LKG for this working copy is defined by this exact artifact set:
  - `logs/closed_loop_report_20260323_143122.md`
  - `versions/promoted_20260323_143122_phase2i_default_token_path_lkg/`
  - the matching control-file state in `PROJECT_STATE.md` and `TODO.md`
- Earlier March 8 reports remain historical audit lineage and are not the current promoted LKG record for this working copy.
- The trusted baseline/LKG is defined by preserved successful reports, promoted `versions/` snapshots, and recorded control-file state. The live working tree at `Dell_2_Steval/` is not itself permanent LKG identity unless it is explicitly snapshotted and recorded as promoted.
- Promoted snapshots should be recorded under `versions/promoted_YYYYMMDD_HHMMSS_<label>/`.
- Each promotion must be recorded in `PROJECT_STATE.md` under `## Current Promoted LKG Record` with, at minimum: snapshot path, successful report path, token used, host/evidence context, and promotion note or reason.
- Historical 2026-03-08 evidence remains audit lineage only unless a future control-file record explicitly promotes a snapshot.
- A future candidate may be promoted to LKG only when:
  - it is run on the proven host configuration
  - `deploy.sh` is invoked without an explicit token override so the default-token path is exercised
  - terminal output ends with `SUCCESS | report=...`
  - the report shows `PRECHECK: OK`, `build=OK`, `flash=OK`, `flash_verify=OK`, and `uart=OK`
- When a candidate is promoted, preserve:
  - the successful report in `logs/`
  - the matching `verbose.log`
  - the promoted project snapshot under `versions/`
  - the current `PROJECT_STATE.md` and `TODO.md` state describing the promotion
- Promoted snapshots are expected to live under `versions/` using the repo's existing snapshot model.
- Restore in this repo means first reading `PROJECT_STATE.md` under `## Current Promoted LKG Record`, then restoring the named promoted snapshot path from `versions/` and using the referenced preserved reports/logs as the primary audit trail; current git history is supplementary and begins after the earlier baseline evidence.
- Failed candidates must preserve enough evidence to explain rejection:
  - the failed `logs/closed_loop_report_*.md` if produced
  - the relevant `verbose.log` output
  - the attempted token and host context
- Operator-authoritative steps remain:
  - flash/program execution
  - UART/token proof
  - ST-LINK/libusb proof
  - any claim that a candidate is verified on real hardware

## Quarantined Helper
- `tools/closed_loop_codex_verbose.py` is a quarantined non-primary helper.
- It is not part of the trusted Layer A workflow (`deploy.sh` -> `autofix.sh` -> `test_runner.py`).
- For this working copy, treat it as archival/non-primary unless a later controlled phase explicitly revives it.
- It currently fails `python3 -m py_compile` with `TabError`.
- Do not use it for baseline/LKG or promotion decisions unless it is later explicitly rehabilitated.

## Success Criteria
Success means both of these are true:
1. Terminal ends with `SUCCESS | report=...`
2. Report attempt summary includes:
   - `codex=OK`
   - `build=OK`
   - `flash=OK`
   - `flash_verify=OK` (if enabled)
   - `uart=OK`

## First Checks When a Run Fails
1. Tool availability:
   - `codex`, `arm-none-eabi-gcc`, `arm-none-eabi-objcopy`, `st-flash`, `python3`
2. ST-LINK connectivity/permissions:
   - USB attached, not busy in another app, retry with `USE_SUDO_FLASH=1` if required
   - if `sudo -n` reports `no new privileges`, run from a normal host shell/session with real sudo/elevated capability
3. UART verification inputs:
   - correct `UART_PORT`, `UART_BAUD=115200`, `UART_TIMEOUT`
   - correct `UART_TOKEN`
   - note: `autofix.sh` now fails early if UART endpoint is missing or not accessible
   - if `/dev/ttyACM0` exists but open still returns `Permission denied`, treat it as host/session access restriction and fix host context before rerun
4. ST-LINK preflight:
   - `autofix.sh` now performs a read probe before loop attempts
   - if this fails, resolve USB/libusb/device-access issues before retrying
5. Token handling after baseline closure:
   - canonical current baseline token is `STWINBX1_ON_LINE`
   - `Kerem` is historical audit evidence only
   - Layer A defaults in the working tree are now aligned to `STWINBX1_ON_LINE`; use explicit token overrides only for controlled diagnostics or audit replay
   - do not use Kerem in normal operation or routine retries
   - only consider a controlled diagnostic rerun with `Kerem` if:
     - `build=OK`
     - `flash=OK`
     - `flash_verify=OK`
     - UART is the only failing stage
     - and evidence strongly indicates token-detection mismatch rather than host-access failure
6. Read the exact failure stage in:
   - latest `logs/closed_loop_report_*.md`
   - `verbose.log` tail
   - if failure occurs before loop/report initialization (for example UART access precheck), terminal output may be the primary evidence and `strategy_log.txt` / `verbose.log` can remain empty


## Physical Test Handoff Rule
When a task reaches real-board testability, the agent must explicitly hand off to the operator with:

`NOW TEST PLEASE`

The handoff must include:
- the exact hardware behavior to test
- expected success signal(s)
- exact command(s) to run if needed
- the exact output/report/log evidence to paste back