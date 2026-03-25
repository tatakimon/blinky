# Structure
## Authority Order
- In the trusted operational repo context, authority order is: `AGENTS.md`, `TODO.md`, `PROJECT_STATE.md`, `RUNBOOK.md`.
- Current phase, helper status, trusted baseline/LKG identity, token policy, and the next exact action must be taken from those root control files, not from this secondary codebase-map note.
- Current authoritative working repo context for this working copy is `/home/kerem/new_embedder_codex_app_gsd/blinky`.
- Earlier verified-host evidence from `~/stm32_sim_lab/blinky` remains historical audit lineage, not current repo authority for this working copy.
- If this file is read from another checkout such as `/home/kerem/copy/blinky`, treat that checkout as a non-authoritative analysis copy.


## Root Layout
- `AGENTS.md`: session rules, hardware authority limits, and edit-mode constraints
- `TODO.md`: current phase, acceptance criteria, and next exact action
- `PROJECT_STATE.md`: trusted baseline, evidence, and risk register
- `RUNBOOK.md`: operator execution contract for Layer A
- `LESSONS.md`: compact operational lessons
- `planning.md` and `BUILD_AGENT_TODO.md`: Layer B roadmap and future-system planning
- `README.md` and `readme.md`: high-level orientation documents

## Executable And Script Areas
- `deploy.sh`: top-level operator entrypoint
- `autofix.sh`: retry-loop orchestrator, build/flash flow, and report generator
- `test_runner.py`: UART token verifier
- `tools/`: helper and integration scripts including Telegram and summary tooling

## Firmware Project Tree
- `Dell_2_Steval/`: STM32CubeIDE project root
- `Dell_2_Steval/Core/Src/`: main firmware sources including `main.c`
- `Dell_2_Steval/Core/Inc/`: headers including `main.h`
- `Dell_2_Steval/Core/Startup/`: startup assembly
- `Dell_2_Steval/Drivers/`: HAL and CMSIS vendor code
- `Dell_2_Steval/Debug/`: generated makefiles plus current build outputs
- `Dell_2_Steval/.settings/`: IDE project settings

## Evidence And History Areas
- `logs/`: authoritative run reports and attempt-level artifacts
- `logs/attempt_01/` through `logs/attempt_05/`: per-attempt build, flash, verify, and Codex artifacts
- `versions/attempt_*/pre/` and `versions/attempt_*/post/`: before/after snapshots for loop attempts
- `versions/base_2026-02-23_dell2_steval/`: preserved historical baseline snapshot
- `versions/promoted_YYYYMMDD_HHMMSS_<label>/`: promoted snapshot location defined by the root control files when a future candidate is intentionally promoted

## Naming Patterns
- Attempt artifacts use zero-padded suffixes such as `attempt_01`
- Reports use timestamped names such as `logs/closed_loop_report_20260308_162608.md`
- Snapshot folders separate `pre/` and `post/` states
- Layer A docs use uppercase control-file names at repo root

## Generated Versus Hand-Maintained Areas
- Hand-maintained root docs and scripts include `AGENTS.md`, `TODO.md`, `PROJECT_STATE.md`, `RUNBOOK.md`, `deploy.sh`, `autofix.sh`, `test_runner.py`, and most of `tools/`
- Generated or tool-owned STM32 assets include `Dell_2_Steval/.project`, `.cproject`, `.ioc`, `Core/Startup/`, linker scripts, and `Debug/makefile`
- `Dell_2_Steval/Core/Src/main.c` is mixed ownership: Cube-generated scaffold with user-editable sections

## Repo Hygiene Notes
- Many files have Windows metadata sidecars ending in `:Zone.Identifier`
- The repo keeps transient logs and build outputs in-tree rather than separating source from artifacts
- `.planning/codebase/` is an analysis artifact area added for codebase mapping
