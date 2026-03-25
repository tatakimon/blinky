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
- `.planning/codebase/*.md`

Current narrow Layer B exception:
- `tools/layer_b_taskspec_stub.py` is allowed for the current tiny non-executing stub step only.
- It may normalize raw input into the documented TaskSpec fields only.
- It must not call `deploy.sh`, `autofix.sh`, or `test_runner.py`.
- It must not perform hardware access or weaken operator-authoritative proof boundaries.

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


## Closed-Loop Default + Physical Test Reminder Rule
For future implementation, bugfix, and completion prompts in this repo:

- Default to the existing trusted closed-loop path:
  - code change (if needed)
  - build
  - flash
  - readback verify
  - UART/runtime verification
  - report/log review
- Try to carry the task as far as possible toward a finished, testable result within the trusted Layer A workflow.
- Do not stop early at “code written” if the task is intended to be completed through the closed loop, unless a blocker prevents further progress.

When the code reaches a state that is physically testable on the real board, stop and clearly tell the operator:

`NOW TEST PLEASE`

Then state:
- what exactly should be tested on hardware
- what success behavior is expected
- what failure behavior would be important
- which exact command(s) must be run if operator action is required
- what exact output/report/log sections must be pasted back

If real hardware proof or privileged access is needed, also emit:

`OPERATOR ACTION REQUIRED`

Do not claim real hardware success without operator-pasted or report-backed evidence.