# TODO.md

## Active Task
Phase 2c: quarantine `tools/closed_loop_codex_verbose.py` as a stale non-primary helper and tighten trusted baseline/LKG wording so the mutable live working tree is not treated as permanent LKG identity.

## Objective
Remove future confusion from the stale helper and make the trusted baseline definition stricter by anchoring LKG identity to preserved reports and promoted `versions/` snapshots rather than the mutable working tree.

## Constraints
- Keep the current repo structure at `~/stm32_sim_lab/blinky`
- Prefer evidence-driven, minimal updates only
- Do not redesign docs or workflows
- Do not modify STM32 generated code outside USER CODE blocks
- Do not modify firmware or core workflow scripts in this phase
- Do not rerun baseline in this phase
- Treat hardware proof as authoritative only from operator-pasted unrestricted-host output
- Treat Layer A as frozen trusted substrate on the proven host configuration

## Acceptance Criteria
- `TODO.md` reflects Phase 2c rather than the already-completed Phase 2b procedure-definition work
- `tools/closed_loop_codex_verbose.py` is explicitly classified as quarantined, not part of the trusted Layer A path
- Repo control files clearly state that the trusted baseline/LKG is anchored to preserved successful reports and promoted `versions/` snapshots
- The mutable live tree at `Dell_2_Steval/` is not described as permanent LKG identity unless explicitly snapshotted and recorded as promoted
- `RUNBOOK.md` remains focused on the trusted Layer A operator path only
- Canonical token policy remains unchanged:
  - `STWINBX1_ON_LINE` is the canonical current baseline token
  - `Kerem` is historical audit evidence only
  - `SoS` defaults remain legacy behavior deferred for later controlled cleanup

## Blockers
- No current Layer A blocker on the proven host.
- Main remaining structural risks before later Layer B work:
  - no git at repo root
  - stale helper `tools/closed_loop_codex_verbose.py`
  - legacy token default mismatch in scripts

## Latest Evidence
- Proven unrestricted-host baseline report:
  - `logs/closed_loop_report_20260308_162608.md`
  - `TRY 1/1: codex=OK build=OK flash=OK flash_verify=OK uart=OK`
  - verified token: `STWINBX1_ON_LINE`
- Confirming no-change rerun report:
  - `logs/closed_loop_report_20260308_165114.md`
  - `TRY 1/1: codex=OK build=OK flash=OK flash_verify=OK uart=OK`
  - verified token: `STWINBX1_ON_LINE`
- Trusted baseline/LKG procedure is already documented.
- `tools/closed_loop_codex_verbose.py` currently fails `py_compile` with `TabError` and is not part of the trusted Layer A workflow.
- Quarantine decision is now evidence-backed:
  - the helper is non-primary
  - it is excluded from trusted baseline/LKG decisions
  - the mutable live tree at `Dell_2_Steval/` is no longer described as permanent LKG identity

## Next Exact Action
Define a small, explicit naming/recording convention for promoted `versions/` snapshots so future LKG promotions are unambiguous without changing firmware or workflow scripts.
