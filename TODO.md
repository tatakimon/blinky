# TODO.md

## Active Task
Phase 3d: add a tiny built-in self-check for the non-executing Layer B TaskSpec stub.

## Objective
The tiny non-executing stub now exists at `tools/layer_b_taskspec_stub.py`. The next low-risk step is adding a tiny built-in self-check in that same file that covers one successful normalization path and one refusal path without invoking `deploy.sh`.

## Constraints
- Keep the current repo structure at `/home/kerem/new_embedder_codex_app_gsd/blinky`
- Prefer evidence-driven, minimal updates only
- Do not redesign docs or workflows
- Do not modify STM32 generated code outside USER CODE blocks
- Do not modify firmware or core workflow scripts in this phase
- Only `tools/layer_b_taskspec_stub.py` is newly authorized for the next step, and it must remain non-executing
- Do not rerun baseline in this phase
- Treat hardware proof as authoritative only from operator-pasted unrestricted-host output
- Treat Layer A as frozen trusted substrate on the proven host configuration

## Acceptance Criteria
- `TODO.md` reflects Phase 3d rather than the completed Phase 3c stub-implementation step
- `tools/layer_b_taskspec_stub.py` exists and emits the documented TaskSpec fields
- The stub remains non-executing and does not call Layer A or perform hardware access
- No broader Layer B implementation authority is introduced in this update
- The next step stays within the same stub file and adds a tiny built-in self-check
- `TODO.md` advances to one concrete next exact action for that self-check step
- Historical `Kerem` evidence remains historical only and is not used as normal operational fallback
- `tools/closed_loop_codex_verbose.py` remains explicitly classified as quarantined, non-primary, and not part of the trusted Layer A path
- Canonical token policy remains unchanged in this phase:
  - `STWINBX1_ON_LINE` is the canonical current baseline token
  - `Kerem` is historical audit evidence only
  - historical `SoS` defaults are now superseded in the working tree by the aligned canonical default

## Blockers
- No current Layer A blocker on the proven host.
- Main remaining structural risks before later Layer B work:
  - stale helper `tools/closed_loop_codex_verbose.py` remains archival/non-primary until a later controlled revival phase is explicitly approved
  - future Layer A changes must continue to preserve the promoted snapshot/LKG record and report-backed evidence discipline
  - future doc maintenance should keep secondary descriptive aids synchronized with the authoritative root control files
  - future historical references to `SoS` should remain clearly marked as legacy context rather than current behavior
  - Layer B still needs a tiny built-in self-check that exercises one success path and one refusal path inside `tools/layer_b_taskspec_stub.py`

## Latest Evidence
- Successful Phase 2i default-token-path proof report:
  - `logs/closed_loop_report_20260323_143122.md`
  - `UART token: STWINBX1_ON_LINE`
  - `UART token source: default`
  - `TRY 1/5: codex=OK build=OK flash=OK flash_verify=OK uart=OK`
- Proven unrestricted-host baseline report:
  - `logs/closed_loop_report_20260308_162608.md`
  - `TRY 1/1: codex=OK build=OK flash=OK flash_verify=OK uart=OK`
  - verified token: `STWINBX1_ON_LINE`
- Confirming no-change rerun report:
  - `logs/closed_loop_report_20260308_165114.md`
  - `TRY 1/1: codex=OK build=OK flash=OK flash_verify=OK uart=OK`
  - verified token: `STWINBX1_ON_LINE`
- These 2026-03-08 reports remain valid historical audit evidence for this line of work, but they originated in the earlier repo context `~/stm32_sim_lab/blinky`.
- Trusted baseline/LKG procedure is already documented.
- `tools/closed_loop_codex_verbose.py` currently fails `py_compile` with `TabError` and is not part of the trusted Layer A workflow.
- Quarantine decision is now evidence-backed:
  - the helper is non-primary
  - it is excluded from trusted baseline/LKG decisions
  - the mutable live tree at `Dell_2_Steval/` is no longer described as permanent LKG identity

## Next Exact Action
Add a tiny built-in self-check to `tools/layer_b_taskspec_stub.py` that demonstrates one successful normalization path and one refusal path without calling `deploy.sh`.
