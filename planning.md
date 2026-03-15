# planning.md — Closed-loop Codex CLI + ST-LINK (STM32U575/U585)

Note:
- This file is part of the broader Layer B roadmap.
- Current Layer A operational truth remains in `RUNBOOK.md` (`deploy.sh` -> `autofix.sh` -> `test_runner.py`).

## Goal
Autonomous loop that:
1) builds (make clean && make)
2) flashes (st-flash ... write firmware.bin 0x08000000)
3) verifies via UART token on ST-LINK VCP
4) if fail: summarizes why, asks Codex for a fix, applies fix, retries
5) stops on success or MAX_TRIES (default 5)

## Hardware facts (fixed constraints)
- MCU: STM32U575/U585 (chipid 0x482)
- Flash base: 0x08000000 (2MB)
- UART for verification: USART2 on PD5=TX / PD6=RX (AF7), baud 115200
- LEDs: PH12 (green), PH10 (orange)

## Verification contract
- Firmware MUST print token repeatedly in main loop:
  "STWINBX1_ON_LINE\n"
- Host listens on /dev/serial/by-id/usb-STMicroelectronics_STLINK-V3_... -> ttyACM0
- PASS if token appears within UART_TIMEOUT seconds.

## Agent constraints (safety rails)
- Codex may only edit: main.c (optionally test_runner.py)
- Codex must NOT edit: Makefile, linker.ld, startup.s
- Codex must NOT introduce: stm32u5xx.h shims, constructor attributes, HAL, new dependencies
- If Codex violates constraints -> revert + retry with stricter prompt

## Logging requirements
Per attempt folder logs/attempt_XX/:
- build_stdout.txt, build_stderr.txt
- flash_stdout.txt, flash_stderr.txt
- verify.txt
- codex_prompt.txt, codex_stdout.txt, codex_stderr.txt
- diff.patch
Also:
- logs/history.md: 5–10 lines per attempt (hypothesis/change/next)

## Versioning requirements
versions/attempt_XX/pre/ and versions/attempt_XX/post/ snapshots for:
- main.c
- test_runner.py
- AGENTS.md (constraints)
- MANIFEST/PROJECT_STATE if present

## Env vars
- MAX_TRIES=5
- UART_BAUD=115200
- UART_TOKEN=STWINBX1_ON_LINE
- UART_TIMEOUT=10
- STLINK_SERIAL=0047001F...
