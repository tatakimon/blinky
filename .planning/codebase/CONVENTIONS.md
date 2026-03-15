# Conventions

## Operational Conventions
- Start by reading `AGENTS.md`, then `TODO.md`, `PROJECT_STATE.md`, `RUNBOOK.md`, `LESSONS.md`, `planning.md`, and optionally `README.md`
- Follow the single current trusted workflow: `deploy.sh` -> `autofix.sh` -> `test_runner.py`
- Treat hardware proof as operator-authoritative only; agents must not claim flash or UART success without pasted evidence
- Keep `TODO.md` and `PROJECT_STATE.md` synchronized with meaningful changes and current phase status

## Edit Constraints
- Repo-maintenance mode is limited to control files and small docs called out in `AGENTS.md`
- Firmware-change mode allows edits only in `Dell_2_Steval/Core/Src/main.c`
- Even within `main.c`, edits are restricted to `/* USER CODE BEGIN ... */` and `/* USER CODE END ... */` blocks unless explicitly approved
- Generated STM32Cube code outside user blocks should be treated as tool-owned

## Coding Style Signals
- Shell scripts use `set -euo pipefail` and explicit env-variable defaults
- Python helpers are mostly small single-file scripts with direct standard-library usage
- Markdown control files prefer short sections, bullet lists, and evidence-first wording
- Important constants are centralized near the top of files, for example baud rates and GPIO timing constants in `Dell_2_Steval/Core/Src/main.c`

## Naming And Documentation Patterns
- Control files at the root use uppercase names for operational authority
- Reports and snapshots use timestamped or attempt-numbered naming for auditability
- The codebase explicitly distinguishes current trusted paths from historical or future paths using Layer A versus Layer B language
- Token terminology is treated carefully: `STWINBX1_ON_LINE` is the canonical current baseline token, while `Kerem` and `SoS` are called out as historical or legacy contexts

## Error-Handling Conventions
- `autofix.sh` fails early on missing tools, missing files, missing UART, or inaccessible ports
- `test_runner.py` exits with clear status codes and prints detection context on failure
- Firmware routes UART transmit failures to `Error_Handler()`
- Operational docs prefer exact command outputs and preserved reports over vague conclusions

## Evidence Conventions
- Success claims require a matching `logs/closed_loop_report_*.md`
- Current run context is mirrored into `verbose.log` and `strategy_log.txt`
- Baseline or LKG claims must be anchored to reports plus snapshot lineage in `versions/`
- Historical evidence is preserved rather than overwritten

## Repository-Behavior Conventions
- The repo accepts committed logs, build outputs, and snapshots as part of normal workflow state
- Alternate helpers may exist, but trusted status must be stated explicitly
- Sidecar `:Zone.Identifier` files are present and should usually be treated as hygiene noise unless the task is cleanup-focused
