# Project State — STM32U585 Closed Loop

Updated: 2026-03-24 (Phase 3a Layer B invocation-contract preparation opened)

## Current Phase
Phase 3a: define the minimal Layer B -> Layer A invocation contract without changing trusted Layer A behavior; no firmware feature work.

## Repo Authority And Path
- Current authoritative working repo context for this working copy is `/home/kerem/new_embedder_codex_app_gsd/blinky`.
- Root control files remain authoritative in this order: `AGENTS.md`, `TODO.md`, `PROJECT_STATE.md`, `RUNBOOK.md`.
- Secondary descriptive aids such as `.planning/codebase/*.md` must defer to those root control files for current phase, helper status, trusted baseline/LKG identity, token policy, and the next exact action.
- Earlier authoritative repo context for the 2026-03-08 verified-host evidence was `~/stm32_sim_lab/blinky`; in this working copy that path is historical audit lineage, not current repo authority.
- If these docs are read from another checkout such as `/home/kerem/copy/blinky`, treat that checkout as a non-authoritative analysis copy unless its own root control files explicitly establish authority.

## Trusted Execution Substrate
Layer A (`deploy.sh` -> `autofix.sh` -> `test_runner.py`) remains the trusted execution substrate on the proven host configuration.

Current default-token-path proof for this working copy is anchored by:
- `logs/closed_loop_report_20260323_143122.md`

Earlier March 8 reports remain historical audit lineage for this line of work:
- `logs/closed_loop_report_20260308_162608.md`
- `logs/closed_loop_report_20260308_165114.md`

This statement is limited to the verified host configuration used for those runs. It does not generalize to other hosts without new evidence.

Phase 2 contradiction-cleanup work is effectively complete for this working copy. Layer A is stable and proven here, so the next preparation step moves to Layer B boundary definition rather than more cleanup sweeps.

## Trusted Baseline / LKG Identity
- Current trusted baseline/LKG for this working copy is anchored by:
  - `logs/closed_loop_report_20260323_143122.md`
  - `versions/promoted_20260323_143122_phase2i_default_token_path_lkg/`
- Earlier March 8 reports remain historical audit lineage supporting host continuity, not the current promoted LKG record for this working copy.
- Permanent LKG identity in this repo is anchored to preserved successful reports, promoted snapshots under `versions/`, and recorded control-file state.
- The mutable live tree at `Dell_2_Steval/` is not itself permanent LKG identity unless it is explicitly snapshotted and recorded as promoted in the control files.
- Canonical current baseline token is `STWINBX1_ON_LINE`.
- `Kerem` remains historical audit evidence only.
- Layer A default-token behavior is implemented and proven through the default-token path for this working copy.

## Current Promoted LKG Record
- The currently promoted LKG for this working copy is explicitly recorded in this subsection.
- Promoted snapshot naming pattern: `versions/promoted_YYYYMMDD_HHMMSS_<label>/`
- Minimum record fields:
  - Snapshot path
  - Successful report path
  - Token used
  - Host/evidence context
  - Promotion note or reason
- Snapshot path: `versions/promoted_20260323_143122_phase2i_default_token_path_lkg/`
- Successful report path: `logs/closed_loop_report_20260323_143122.md`
- Token used: `STWINBX1_ON_LINE` via default-token path (`UART token source: default`)
- Host/evidence context: proven host configuration for this working copy at `/home/kerem/new_embedder_codex_app_gsd/blinky`; report records `/dev/ttyACM0 @ 115200`, `UART token source: default`, and `PRECHECK: OK (ST-LINK probe read succeeded)`
- Promotion note or reason: first explicit promoted LKG for this working copy after successful Phase 2i default-token alignment proof on 2026-03-23; this record closes the earlier proof-pending state for token-default alignment.
- Historical lineage note: the 2026-03-08 reports from `~/stm32_sim_lab/blinky` remain historical audit lineage and are not themselves this promoted snapshot record.

## Token-Default Alignment Status
- Current behavior in the working tree:
  - `deploy.sh` default token: `STWINBX1_ON_LINE`
  - `autofix.sh` default token: `STWINBX1_ON_LINE`
  - `test_runner.py` fallback token: `STWINBX1_ON_LINE`
- Historical `Kerem` evidence remains historical only and is not used as normal operational fallback
- Successful default-token-path proof is recorded at:
  - `logs/closed_loop_report_20260323_143122.md`
  - `UART token source: default`
  - `TRY 1/5: codex=OK build=OK flash=OK flash_verify=OK uart=OK`

## Quarantined Helper Disposition
- `tools/closed_loop_codex_verbose.py` remains under quarantine.
- For this working copy it is archival/non-primary unless a later controlled phase explicitly revives it.
- It must not be treated as part of the trusted Layer A workflow or used for baseline/LKG or promotion decisions.

## Controlled Token-Default Alignment Checklist
1. Preserve pre-change evidence before implementation begins: keep the root control-file record of the historical 2026-03-08 report lineage, the current `## Current Promoted LKG Record` status, and the current mismatch statement intact until the later implementation result is proven.
2. Apply one controlled implementation step later, and limit the touch points to `deploy.sh`, `autofix.sh`, and `test_runner.py`.
3. Intended per-file end state for that later step:
   - `deploy.sh` default token becomes `STWINBX1_ON_LINE`
   - `autofix.sh` default token becomes `STWINBX1_ON_LINE`
   - `test_runner.py` fallback token remains `STWINBX1_ON_LINE` and must stay aligned with the orchestrator defaults
4. The later implementation must not change the trusted Layer A workflow structure (`deploy.sh` -> `autofix.sh` -> `test_runner.py`), the real-host evidence requirements, the helper quarantine status, or the promoted-snapshot convention.
5. Post-change proof requirement: do not claim success until a fresh real-host Layer A run on the proven host configuration succeeds through the default-token path, meaning success is shown without relying on an explicit CLI token override, and the run preserves a successful report plus matching `verbose.log`.
6. Rollback trigger and rollback reference: if the controlled implementation changes behavior outside the named touch points, if any touched file does not match the intended end state above, or if the post-change default-token-path run fails at any stage, restore the pre-change versions of `deploy.sh`, `autofix.sh`, and `test_runner.py` and use the preserved pre-change root-control-file evidence, the current promoted-LKG record, and the referenced reports/logs as rollback authority.

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
- Secondary `.planning/codebase/` docs now explicitly defer to the root control files for authority and trusted repo-path wording.
- Quarantined helper status is now explicit:
  - `tools/closed_loop_codex_verbose.py` is non-primary
  - it is not part of the trusted Layer A workflow
  - it is archival/non-primary for this working copy unless a later controlled phase explicitly revives it
  - `python3 -m py_compile tools/closed_loop_codex_verbose.py` currently fails with `TabError`
  - it must not be used for baseline/LKG or promotion decisions unless later explicitly rehabilitated
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
- Successful Phase 2i default-token-path proof report:
  - `logs/closed_loop_report_20260323_143122.md`
  - Attempt summary shows:
    - `PRECHECK: OK (ST-LINK probe read succeeded)`
    - `TRY 1/5: codex=OK build=OK flash=OK flash_verify=OK uart=OK`
  - Effective verification details:
    - port: `/dev/ttyACM0`
    - baud: `115200`
    - token: `STWINBX1_ON_LINE`
    - token source: `default`
  - `test_runner.py` within deploy reported: `SUCCESS (token seen)`
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
  - Layer A defaults in the working tree are aligned to `STWINBX1_ON_LINE` and proven by `logs/closed_loop_report_20260323_143122.md`.
- Git is now initialized at repo root; current local history begins with `b32f87c` (`chore: import project state and documentation`).

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
- Token defaults are now aligned across the working tree:
  - `deploy.sh` default token: `STWINBX1_ON_LINE`
  - `autofix.sh` default token: `STWINBX1_ON_LINE`
  - `test_runner.py` default token (env fallback): `STWINBX1_ON_LINE`
- Effective token path in normal Layer A flow is now explicit:
  - operator may omit `<UART_TOKEN>` to exercise the default-token path
  - `deploy.sh` forwards the effective token to `autofix.sh`
  - `autofix.sh` injects `UART_TOKEN` into `test_runner.py` invocation
  - `test_runner.py` fallback remains consistent for standalone invocation when `UART_TOKEN` is unset

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
  - if a future Layer B-driven change regresses Layer A, restore the last known good project snapshot from `versions/` and rely on report/log artifacts as the primary trusted lineage; current git history is supplementary and begins after the earlier baseline evidence
- Operator-action boundary:
  - any hardware proof or privileged action remains outside agent authority and requires `OPERATOR ACTION REQUIRED` plus operator-pasted output

## Known Risks / Uncertainties
- Current baseline token on this host is now confirmed as `STWINBX1_ON_LINE` through two full deploy/flash/UART verification runs.
- Historical `Kerem` success remains part of the audit trail and is not part of normal operational fallback.
- Hardware-dependent verification remains host-specific:
  - earlier restricted-session failures were environmental and are superseded by unrestricted-host evidence for this host.
- Token-default alignment risk is closed for this working copy:
  - the aligned defaults are proven through `logs/closed_loop_report_20260323_143122.md` and recorded in the promoted LKG snapshot
- Stale helper-script risk:
  - `tools/closed_loop_codex_verbose.py` is now quarantined and explicitly treated as archival/non-primary for this working copy unless a later controlled phase revives it.
- Auditability risk:
  - git now exists at repo root, but earlier baseline rollback and audit still rely primarily on `versions/` snapshots and preserved run logs because the git history starts later.

## Next Exact Action
Write the minimal Layer B -> Layer A invocation contract in the root control files: what Layer B passes into `deploy.sh`, what evidence it must read back from Layer A, and what it must not bypass in the trusted `deploy.sh` -> `autofix.sh` -> `test_runner.py` path.
