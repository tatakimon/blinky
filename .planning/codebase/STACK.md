# Stack
## Authority Order
- In the trusted operational repo context, authority order is: `AGENTS.md`, `TODO.md`, `PROJECT_STATE.md`, `RUNBOOK.md`.
- Current phase, helper status, trusted baseline/LKG identity, token policy, and the next exact action must be taken from those root control files, not from this secondary codebase-map note.
- Current authoritative working repo context for this working copy is `/home/kerem/new_embedder_codex_app_gsd/blinky`.
- Earlier verified-host evidence from `~/stm32_sim_lab/blinky` remains historical audit lineage, not current repo authority for this working copy.
- If this file is read from another checkout such as `/home/kerem/copy/blinky`, treat that checkout as a non-authoritative analysis copy.


## Scope
- Codebase map scope follows the current authoritative working repo context at `/home/kerem/new_embedder_codex_app_gsd/blinky`; copied checkouts are descriptive only unless their root control files explicitly establish authority
- Primary implemented workflow is Layer A: `deploy.sh` -> `autofix.sh` -> `test_runner.py`
- Layer B exists as planning and helper scripts, not as the trusted production path

## Languages
- Shell/Bash for orchestration in `deploy.sh` and `autofix.sh`
- Python 3 for verification and helper tooling in `test_runner.py` and `tools/*.py`
- C for firmware logic in `Dell_2_Steval/Core/Src/main.c`
- Generated Make-based embedded build files in `Dell_2_Steval/Debug/makefile`
- Markdown for operational state, runbooks, roadmap, and evidence files in `README.md`, `RUNBOOK.md`, `PROJECT_STATE.md`, `TODO.md`, and `logs/*.md`

## Runtime Environments
- Linux host environment is assumed by serial-path probing in `deploy.sh`, `autofix.sh`, `test_runner.py`, and `tools/closed_loop_codex.py`
- Bare-metal STM32U585 firmware target built from `Dell_2_Steval/`
- Python virtual environment present at `.venv/`, but no repository-level dependency manifest was found

## Firmware Toolchain
- STM32CubeIDE project metadata in `Dell_2_Steval/.project`, `Dell_2_Steval/.cproject`, and `Dell_2_Steval/Dell_2_Steval.ioc`
- GNU Tools for STM32 13.3 toolchain referenced by `Dell_2_Steval/Debug/makefile`
- Linker scripts in `Dell_2_Steval/STM32U585AIIXQ_FLASH.ld` and `Dell_2_Steval/STM32U585AIIXQ_RAM.ld`
- Startup code in `Dell_2_Steval/Core/Startup/startup_stm32u585aiixq.s`
- HAL and CMSIS sources included through `Dell_2_Steval/Drivers/STM32U5xx_HAL_Driver/` and `Dell_2_Steval/Drivers/CMSIS/`

## Host-Side Tools
- `codex` is required by `autofix.sh` and `tools/closed_loop_codex.py`
- `arm-none-eabi-gcc` and `arm-none-eabi-objcopy` are required by `autofix.sh`
- `st-flash` is required by `autofix.sh` and `tools/closed_loop_codex.py`
- `python3` is required by `autofix.sh`, `test_runner.py`, and all helper scripts
- `cmp`, `stat`, `sha256sum`, and standard POSIX utilities are used in `autofix.sh`

## Python Dependencies
- `pyserial` is required by `test_runner.py` and `tools/closed_loop_codex.py`
- Standard library modules dominate the helper tooling: `os`, `sys`, `glob`, `subprocess`, `pathlib`, `urllib`, `threading`, and `json`
- No `requirements.txt`, `pyproject.toml`, or `setup.py` was found at the repo root

## Build Outputs And Artifacts
- Firmware ELF/list/map outputs are committed under `Dell_2_Steval/Debug/`
- Runtime reports are stored under `logs/closed_loop_report_*.md`
- Per-attempt diagnostics are stored under `logs/attempt_*/`
- Snapshot artifacts are stored under `versions/attempt_*/` and `versions/base_2026-02-23_dell2_steval/`
- Future promoted snapshots follow the root-control convention under `versions/promoted_YYYYMMDD_HHMMSS_<label>/`
- Current run scratch artifacts are written to `/tmp`, including `/tmp/Dell_2_Steval.bin` and `/tmp/Dell_2_Steval.readback.bin`

## Configuration Sources
- CLI arguments in `deploy.sh` define the task string and optional UART token
- Environment variables configure retries, flash verification, baud, timeout, port, sudo behavior, Telegram bot behavior, and optional MiniMax integration
- Control-file state is stored in `TODO.md`, `PROJECT_STATE.md`, `RUNBOOK.md`, `LESSONS.md`, and `planning.md`

## Notable Absences
- Git now exists in the current harmonized repo copy, but trusted baseline/LKG identity still comes from preserved successful reports, promoted `versions/` snapshots, and recorded control-file state
- No package manager manifest for Python dependencies
- No CI configuration or automated test runner configuration file was found
