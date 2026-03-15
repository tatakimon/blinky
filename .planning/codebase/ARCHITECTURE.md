# Architecture

## High-Level Model
- The implemented system is a closed-loop firmware deployment workflow centered on a single firmware project in `Dell_2_Steval/`
- Current trusted architecture is Layer A: `deploy.sh` -> `autofix.sh` -> `test_runner.py`
- Layer B is future-facing planning and helper infrastructure documented in `planning.md` and `BUILD_AGENT_TODO.md`

## Main Execution Path
1. `deploy.sh` is the operator entrypoint and prints effective configuration
2. `deploy.sh` delegates to `autofix.sh` with the task string and UART token
3. `autofix.sh` validates tools, detects UART, probes ST-LINK, and manages the retry loop
4. `autofix.sh` prompts Codex to edit `Dell_2_Steval/Core/Src/main.c` within STM32Cube user blocks only
5. `autofix.sh` builds the firmware from `Dell_2_Steval/Debug/`
6. `autofix.sh` flashes and optionally readback-verifies the device via `st-flash`
7. `test_runner.py` opens the ST-LINK virtual COM port and checks for the expected UART token
8. `autofix.sh` emits evidence into `logs/`, `verbose.log`, and `strategy_log.txt`

## Firmware Layer
- The main behavior lives in `Dell_2_Steval/Core/Src/main.c`
- STM32Cube-generated initialization surrounds user-maintained behavior
- The code uses HAL and CMSIS sources from `Dell_2_Steval/Drivers/`
- Firmware responsibilities are intentionally narrow: GPIO heartbeat/error LEDs plus USART2 token output

## Host Orchestration Layer
- `deploy.sh` is a thin wrapper and argument normalizer
- `autofix.sh` is the real orchestrator and policy engine
- `test_runner.py` is the runtime verifier and serial-port observer
- Helper scripts under `tools/` support alternate or future orchestration, summarization, and chat integration

## Control-State Layer
- `TODO.md` defines the active task and next exact action
- `PROJECT_STATE.md` records trusted baseline, evidence, risks, and verified behaviors
- `RUNBOOK.md` is the operator-facing truth for Layer A
- `LESSONS.md` records stable operational guidance
- `planning.md` and `BUILD_AGENT_TODO.md` describe future Layer B work

## Data And Evidence Flow
- Input intent enters through the `deploy.sh` task string
- Operational parameters flow through CLI args and environment variables
- Runtime evidence is captured into `logs/closed_loop_report_*.md`, `verbose.log`, `strategy_log.txt`, and `logs/attempt_*/`
- Snapshot evidence flows into `versions/attempt_*/` and the preserved baseline tree under `versions/base_2026-02-23_dell2_steval/`

## Architectural Constraints
- Real hardware proof is outside agent authority per `AGENTS.md`
- Firmware edits are limited to `Dell_2_Steval/Core/Src/main.c` USER CODE blocks in firmware-change mode
- Repo-maintenance work should stay in control files and small docs
- Without git history, rollback architecture depends on snapshot directories and reports rather than VCS

## Secondary And Deprecated Paths
- `tools/closed_loop_codex.py` models an older Python-driven loop and overlaps conceptually with `autofix.sh`
- `tools/telegram_closed_loop_bot.py` is an external command/chat interface that ultimately feeds the same deployment entrypoint
- `tools/closed_loop_codex_verbose.py` is quarantined and excluded from the trusted architecture
