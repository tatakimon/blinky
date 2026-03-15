# AGENTS.md
# Agent Rules (STM32U585 - STWIN.box)

## Read First
At the start of every session, read in this order:
1. `AGENTS.md`
2. `TODO.md`
3. `PROJECT_STATE.md`
4. `RUNBOOK.md`
5. `LESSONS.md` (if present)
6. `planning.md`
7. `README.md` (optional bridge/context)

Then do only the current **Next Exact Action** unless a blocker makes that impossible.

## Hardware / Privileged Access Authority Rule
Assume this session does **not** have reliable authority for real hardware proof or privileged host checks involving:
- `st-info`
- `st-flash`
- `python3 test_runner.py`
- `./deploy.sh` when flash/UART/token proof is required
- `sudo`
- ST-LINK/libusb validation
- any claim that depends on real board access

Whenever hardware proof or privileged access is needed, stop and print exactly:
`OPERATOR ACTION REQUIRED`

Then provide the exact command(s) the operator must run manually from an unrestricted host shell, and wait for pasted output before making any claim about:
- flash success
- UART open success
- UART token verification
- ST-LINK detection success
- libusb access success
- baseline success
- board running the expected firmware

## Operating Modes

### Mode 1 — Repo Maintenance / Documentation
Use this mode when the active task is about:
- repo audit
- state tracking
- control files
- runbook/docs
- cleanup planning

Allowed files in this mode:
- `AGENTS.md`
- `PROJECT_STATE.md`
- `TODO.md`
- `LESSONS.md`
- `RUNBOOK.md`
- `planning.md`
- `.gitignore`
- small doc files under `docs/`

Do not modify workflow behavior in this mode unless explicitly requested.

### Mode 2 — Firmware Change / Closed-Loop Execution
Use this mode when the active task is to change firmware behavior.

In this mode:
- Do **NOT** modify any file except:
  - `Dell_2_Steval/Core/Src/main.c`
- Inside `main.c`, edit **only** STM32Cube user blocks:
  - `/* USER CODE BEGIN ... */`
  - `/* USER CODE END ... */`

Do not modify generated code outside user blocks unless explicitly requested.

## Hardware Constraints
- Board: STWIN.box / STM32U585AI
- Flash tool: `st-flash`
- Runtime verification path: USART2 over ST-LINK VCP
- UART settings: 115200 baud, 8N1
- Canonical current baseline token is `STWINBX1_ON_LINE`; `Kerem` is historical audit evidence only and `SoS` defaults remain deferred cleanup
- Real hardware proof may require operator execution from an unrestricted host shell
- Do not claim flash success, UART success, token success, or baseline success without operator-pasted and/or report-backed evidence
