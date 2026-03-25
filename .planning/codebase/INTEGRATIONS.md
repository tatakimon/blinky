# Integrations
## Authority Order
- In the trusted operational repo context, authority order is: `AGENTS.md`, `TODO.md`, `PROJECT_STATE.md`, `RUNBOOK.md`.
- Current phase, helper status, trusted baseline/LKG identity, token policy, and the next exact action must be taken from those root control files, not from this secondary codebase-map note.
- Current authoritative working repo context for this working copy is `/home/kerem/new_embedder_codex_app_gsd/blinky`.
- Earlier verified-host evidence from `~/stm32_sim_lab/blinky` remains historical audit lineage, not current repo authority for this working copy.
- If this file is read from another checkout such as `/home/kerem/copy/blinky`, treat that checkout as a non-authoritative analysis copy.


## Scope
- This document covers external systems, host interfaces, and optional service integrations for the current authoritative working repo context at `/home/kerem/new_embedder_codex_app_gsd/blinky`

## Hardware Integrations
- ST-LINK is the programming and probe path used by `autofix.sh` through `st-flash`
- UART verification is performed over the ST-LINK virtual COM port using `test_runner.py`
- Expected serial-device discovery uses `/dev/serial/by-id/*`, `/dev/ttyACM*`, and `/dev/ttyUSB*` in `autofix.sh`, `test_runner.py`, and `tools/closed_loop_codex.py`
- The target board is documented as STWIN.box / STM32U585AI in `AGENTS.md`, `RUNBOOK.md`, and `PROJECT_STATE.md`

## Build And Flash Interfaces
- `autofix.sh` shells out to `arm-none-eabi-gcc`, `arm-none-eabi-objcopy`, and `st-flash`
- `autofix.sh` performs a read probe with `st-flash read ... 0x08000000 4` before loop execution
- Optional privileged flashing is modeled through `USE_SUDO_FLASH=1` in `autofix.sh`

## AI And Editing Interfaces
- `autofix.sh` pipes generated prompts into `codex exec --skip-git-repo-check --sandbox workspace-write -`
- `tools/closed_loop_codex.py` also invokes `codex exec`, capturing the last message into `logs/codex_last_message.txt`
- The current trusted path is the shell-based Layer A flow, not the older Python loop helpers

## Messaging And Bot Integrations
- `tools/telegram_closed_loop_bot.py` integrates with the Telegram Bot HTTP API using `urllib.request`
- Telegram access depends on `TELEGRAM_BOT_TOKEN` and optional `TELEGRAM_ALLOWED_CHAT_IDS`
- The bot stores update offsets in `logs/telegram_bot.offset`

## Optional LLM Middleware
- `tools/telegram_closed_loop_bot.py` contains an optional MiniMax or OpenAI-compatible HTTP layer
- That path is controlled by `BOT_ENABLE_MINIMAX_LAYER`, `MINIMAX_API_KEY`, `MINIMAX_API_URL`, `MINIMAX_MODEL`, and `MINIMAX_TIMEOUT`
- The integration is dormant unless explicitly enabled

## File-System And Evidence Integrations
- Run reports are emitted into `logs/closed_loop_report_*.md`
- Verbose command transcripts are stored in `verbose.log`
- Short operator state is stored in `strategy_log.txt`
- Attempt snapshots are recorded in `versions/attempt_*/pre/` and `versions/attempt_*/post/`

## Configuration Entry Points
- `deploy.sh` receives the top-level task and token arguments
- `autofix.sh` reads environment variables such as `MAX_RETRIES`, `ENABLE_FLASH_READBACK_VERIFY`, `FLASH_RETRIES`, `FLASH_RETRY_DELAY`, `UART_BAUD`, `UART_TIMEOUT`, and `UART_PORT`
- `test_runner.py` reads `UART_PORT`, `UART_BAUD`, `UART_TOKEN`, and `UART_TIMEOUT`
- `tools/telegram_closed_loop_bot.py` reads a larger bot-specific env surface prefixed with `BOT_` or `MINIMAX_`

## Trust And Operational Boundaries
- Hardware success claims require operator evidence per `AGENTS.md`
- The verified operational contract is documented in `RUNBOOK.md` and `PROJECT_STATE.md`
- `tools/closed_loop_codex_verbose.py` is explicitly quarantined and should not be treated as an integration surface for trusted baseline decisions
