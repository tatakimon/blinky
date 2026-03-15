# TODO.md

## Active Task
Phase 2a: freeze Layer A as the trusted execution substrate on the proven host configuration and prepare the Layer B handoff contract.

## Objective
Preserve the confirmed Layer A baseline result, state the Layer B entry contract clearly, and keep the next step limited to the smallest risk-reducing non-feature task.

## Constraints
- Keep the current repo structure at `~/stm32_sim_lab/blinky`
- Prefer evidence-driven, minimal updates only
- Do not redesign docs or workflows
- Do not modify STM32 generated code outside USER CODE blocks
- Do not modify firmware or workflow scripts unless a new verified failure proves it is necessary
- Treat hardware proof as authoritative only from operator-pasted unrestricted-host output

## Acceptance Criteria
- Two unrestricted-host deploy runs with `STWINBX1_ON_LINE` are recorded as `build=OK flash=OK flash_verify=OK uart=OK`
- `PROJECT_STATE.md` states that Layer A is the trusted execution substrate on the proven host configuration
- Canonical token policy is documented as `STWINBX1_ON_LINE`, with `Kerem` historical-only and `SoS` treated as legacy cleanup
- A short Layer B entry contract is recorded without starting Layer B implementation

## Blockers
- No current Layer A blocker on this host.

## Latest Evidence
- Authoritative unrestricted-host evidence now shows:
  - `/dev/ttyACM0` visible and not busy
  - `st-info --probe` -> `Found 1 stlink programmers`
  - `st-flash read ...` succeeded
  - standalone `python3 test_runner.py` opened the port and timed out cleanly before flashing
- Fresh baseline deploy report:
  - `logs/closed_loop_report_20260308_162608.md`
  - `TRY 1/1: codex=OK build=OK flash=OK flash_verify=OK uart=OK`
  - verified token: `STWINBX1_ON_LINE`
  - no firmware changes were needed
- Confirming no-change rerun report:
  - `logs/closed_loop_report_20260308_165114.md`
  - `TRY 1/1: codex=OK build=OK flash=OK flash_verify=OK uart=OK`
  - verified token: `STWINBX1_ON_LINE`
  - no firmware changes were needed
- Remaining pre-Layer-B risks:
  - no git at repo root
  - stale helper script `tools/closed_loop_codex_verbose.py`
  - legacy token default mismatch in scripts

## Next Exact Action
Define the trusted baseline/LKG freeze-promote-restore procedure for this repo using the proven host reports and existing `versions/` snapshots, without changing firmware or workflow scripts.
