# Operator Runbook

## Scope
Current operational flow only:
- `deploy.sh`
- `autofix.sh`
- `test_runner.py`

No alternate workflow is defined here.

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
   - Always pass `UART_TOKEN` explicitly for baseline runs.
   - If omitted, `deploy.sh`/`autofix.sh` default to `SoS`, which is not the currently intended baseline token.
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
- `SoS` defaults in current scripts are legacy behavior and are deferred cleanup for a later controlled step.

1. `deploy.sh` CLI arg 2 (`<UART_TOKEN>`) if provided.
2. Otherwise `deploy.sh` default token: `SoS`.
3. `deploy.sh` passes token to `autofix.sh` arg 2.
4. `autofix.sh` exports that token as `UART_TOKEN` when invoking `test_runner.py`.
5. `test_runner.py` fallback token (`STWINBX1_ON_LINE`) is used only when `UART_TOKEN` is not provided in environment (for example direct standalone invocation).

## Expected Artifacts / Logs
- `strategy_log.txt` (task/token/retries for current run)
- `verbose.log` (detailed step-by-step command log for current run)
- `logs/closed_loop_report_YYYYMMDD_HHMMSS.md` (run report + attempt summary)
- `/tmp/Dell_2_Steval.bin` and `/tmp/Dell_2_Steval.readback.bin` (temporary build/readback artifacts)

## Trusted Baseline / LKG Procedure
- Current trusted baseline/LKG is defined by this exact artifact set:
  - `logs/closed_loop_report_20260308_162608.md`
  - `logs/closed_loop_report_20260308_165114.md`
  - the promoted snapshot lineage under `versions/`
  - the matching control-file state in `PROJECT_STATE.md` and `TODO.md`
- The trusted baseline/LKG is defined by preserved successful reports, promoted `versions/` snapshots, and recorded control-file state. The live working tree at `Dell_2_Steval/` is not itself permanent LKG identity unless it is explicitly snapshotted and recorded as promoted.
- A future candidate may be promoted to LKG only when:
  - it is run on the proven host configuration
  - `deploy.sh` is invoked with explicit token `STWINBX1_ON_LINE`
  - terminal output ends with `SUCCESS | report=...`
  - the report shows `PRECHECK: OK`, `build=OK`, `flash=OK`, `flash_verify=OK`, and `uart=OK`
- When a candidate is promoted, preserve:
  - the successful report in `logs/`
  - the matching `verbose.log`
  - the promoted project snapshot under `versions/`
  - the current `PROJECT_STATE.md` and `TODO.md` state describing the promotion
- Promoted snapshots are expected to live under `versions/` using the repo's existing snapshot model.
- Restore in this repo means copying the selected promoted snapshot from `versions/` back into the working project tree and using preserved reports/logs as the audit trail, because repo root has no git history.
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
- It currently fails `python3 -m py_compile` with `TabError`.
- Do not use it for baseline/LKG decisions unless it is later explicitly rehabilitated.

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
   - `SoS` defaults are legacy script behavior and not the intended baseline token
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
