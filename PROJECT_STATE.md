# Project State — STM32U585 Closed Loop

Updated: 2026-03-08 (Phase 2c helper quarantined; LKG wording tightened)

## Current Phase
Phase 2c: quarantine stale non-primary helper usage and tighten trusted baseline/LKG wording for the frozen Layer A substrate; no feature work.

## Trusted Execution Substrate
Layer A (`deploy.sh` -> `autofix.sh` -> `test_runner.py`) is now the trusted execution substrate on the proven host configuration represented by:
- `logs/closed_loop_report_20260308_162608.md`
- `logs/closed_loop_report_20260308_165114.md`

This statement is limited to the verified host configuration used for those runs. It does not generalize to other hosts without new evidence.

## Trusted Baseline / LKG Identity
- Current trusted baseline/LKG for the proven host configuration is anchored by:
  - `logs/closed_loop_report_20260308_162608.md`
  - `logs/closed_loop_report_20260308_165114.md`
- Permanent LKG identity in this repo is anchored to preserved successful reports, promoted snapshots under `versions/`, and recorded control-file state.
- The mutable live tree at `Dell_2_Steval/` is not itself permanent LKG identity unless it is explicitly snapshotted and recorded as promoted.
- Canonical current baseline token is `STWINBX1_ON_LINE`.
- `Kerem` remains historical audit evidence only.
- `SoS` defaults in current scripts remain legacy behavior and are deferred cleanup.

## Verified
- Current top-level structure exists and is preserved:
  - `Dell_2_Steval/`, `docs/`, `logs/`, `tools/`, `versions/`
  - `AGENTS.md`, `TODO.md`, `PROJECT_STATE.md`, `planning.md`
  - `deploy.sh`, `autofix.sh`, `test_runner.py`
- Control files now present:
  - `LESSONS.md`
  - `RUNBOOK.md`
  - `README.md`
  - `BUILD_AGENT_TODO.md`
- Active workflow scripts remain the same tools and entrypoints:
  - `deploy.sh` (entrypoint)
  - `autofix.sh` (retry/orchestration)
  - `test_runner.py` (UART verification)
- Layer A reliability hardening changes remain in place:
  - `deploy.sh` now prints effective UART token (with source), baud, timeout, and port display.
  - `autofix.sh` now prints effective UART settings before loop work.
  - `autofix.sh` now fails early if UART endpoint is missing or not accessible.
  - `autofix.sh` now performs ST-LINK read preflight before Codex/build/flash loop.
  - `test_runner.py` now reports token/port sources and clearer open-failure diagnostics.
- Layer boundary documentation is now explicit:
  - `RUNBOOK.md` for Layer A current operator flow
  - `PROJECT_STATE.md` for Layer A evidence/risk tracking
  - `planning.md` and `BUILD_AGENT_TODO.md` for Layer B roadmap
- Quarantined helper status is now explicit:
  - `tools/closed_loop_codex_verbose.py` is non-primary
  - it is not part of the trusted Layer A workflow
  - `python3 -m py_compile tools/closed_loop_codex_verbose.py` currently fails with `TabError`
  - it must not be used for baseline/LKG decisions unless later explicitly rehabilitated
- Historical successful report remains:
  - `logs/closed_loop_report_20260224_114152.md`
  - Attempt summary shows: `codex=OK build=OK flash=OK flash_verify=OK uart=OK`
  - Report token: `Kerem`
- Fresh authoritative real-host evidence from operator-pasted unrestricted-shell output:
  - UART visibility:
    - `/dev/ttyACM0` exists as `crw-rw-rw- root dialout`
    - `/dev/serial/by-id/usb-STMicroelectronics_STLINK-V3_0047001F3133511037363734-if01 -> ../../ttyACM0`
  - UART busy/openability:
    - `fuser /dev/ttyACM0` produced no output
    - standalone `python3 test_runner.py` opened the port and timed out with `last bytes=b''` while looking for default token `STWINBX1_ON_LINE`
  - ST-LINK access:
    - `st-info --probe` -> `Found 1 stlink programmers`
    - device identified as `STM32U575_U585`, serial `0047001F3133511037363734`
    - `st-flash read /tmp/stm32_probe_read.bin 0x08000000 16` succeeded
- Fresh successful baseline report:
  - `logs/closed_loop_report_20260308_162608.md`
  - Attempt summary shows:
    - `PRECHECK: OK (ST-LINK probe read succeeded)`
    - `TRY 1/1: codex=WARN (infrastructure/stream issue; continuing with current code)`
    - `TRY 1/1: codex=OK build=OK flash=OK flash_verify=OK uart=OK`
  - Effective verification details:
    - port: `/dev/ttyACM0`
    - baud: `115200`
    - token: `STWINBX1_ON_LINE`
    - token source: `cli-arg`
  - `test_runner.py` within deploy reported: `SUCCESS (token seen)`
- Confirming no-change rerun also succeeded on the same unrestricted host:
  - `logs/closed_loop_report_20260308_165114.md`
  - Attempt summary shows:
    - `PRECHECK: OK (ST-LINK probe read succeeded)`
    - `TRY 1/1: codex=WARN (infrastructure/stream issue; continuing with current code)`
    - `TRY 1/1: codex=OK build=OK flash=OK flash_verify=OK uart=OK`
  - Effective verification details:
    - port: `/dev/ttyACM0`
    - baud: `115200`
    - token: `STWINBX1_ON_LINE`
    - token source: `cli-arg`
- Canonical token policy:
  - Canonical current baseline token: `STWINBX1_ON_LINE`.
  - `Kerem` is historical audit evidence only.
  - `SoS` defaults in current scripts are legacy behavior and are deferred cleanup for a later controlled step.
- Repository root currently has no `.git` directory (not a git working tree at this path).

## Verified Operational Contract
- Current operational flow is verified on the proven host configuration:
  1. `deploy.sh "<task>" [UART_TOKEN]`
  2. `deploy.sh` calls `autofix.sh`
  3. `autofix.sh` runs retry loop:
     - Codex attempt against `Dell_2_Steval/Core/Src/main.c` user blocks
     - compile/link/objcopy
     - flash (`st-flash`)
     - optional flash readback + compare
     - UART token check via `test_runner.py`
  4. artifacts written to `strategy_log.txt`, `verbose.log`, and `logs/closed_loop_report_*.md`
- Token defaults remain mismatched across components unless operator passes explicit token:
  - `deploy.sh` and `autofix.sh` default token: `SoS`
  - `test_runner.py` default token (env fallback): `STWINBX1_ON_LINE`
- Effective token path in normal Layer A flow is now explicit:
  - operator passes `<UART_TOKEN>` to `deploy.sh`
  - `deploy.sh` forwards it to `autofix.sh`
  - `autofix.sh` injects `UART_TOKEN` into `test_runner.py` invocation
  - therefore `test_runner.py` fallback token is bypassed in normal deploy flow

## Layer B Entry Contract
- Input:
  - a task string for `deploy.sh`
  - an explicit UART token
  - the proven host configuration with working ST-LINK access and UART visibility/openability
- Success evidence:
  - terminal `SUCCESS | report=...`
  - a report showing `PRECHECK: OK`, `build=OK`, `flash=OK`, `flash_verify=OK`, and `uart=OK`
- Promotion criteria:
  - report-backed success on the proven host configuration for the intended explicit token
  - no unresolved host-access blocker at ST-LINK or UART stage
- Rollback expectation:
  - if a future Layer B-driven change regresses Layer A, restore the last known good project snapshot from `versions/` and rely on report/log artifacts because repo root has no git history
- Operator-action boundary:
  - any hardware proof or privileged action remains outside agent authority and requires `OPERATOR ACTION REQUIRED` plus operator-pasted output

## Known Risks / Uncertainties
- Current baseline token on this host is now confirmed as `STWINBX1_ON_LINE` through two full deploy/flash/UART verification runs.
- Historical `Kerem` success remains part of the audit trail and is not part of normal operational fallback.
- Hardware-dependent verification remains host-specific:
  - earlier restricted-session failures were environmental and are superseded by unrestricted-host evidence for this host.
- Legacy token-default mismatch remains a controlled cleanup item before or during later Layer B work:
  - script defaults still reference `SoS` even though the canonical baseline token is `STWINBX1_ON_LINE`
- Stale helper-script risk:
  - `tools/closed_loop_codex_verbose.py` is now quarantined rather than trusted, but still remains a confusion risk until its longer-term disposition is decided.
- Auditability risk:
  - without git history at this root, rollback relies on `versions/` snapshots and run logs.

## Next Exact Action
Define a small, explicit naming/recording convention for promoted `versions/` snapshots so future LKG promotions are unambiguous without changing firmware or workflow scripts.
