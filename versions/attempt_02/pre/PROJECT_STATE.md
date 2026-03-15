# Project State — STM32U5 Closed Loop (WSL + stlink + UART)

## Hardware
- MCU: STM32U575/U585 (chipid 0x482)
- ST-LINK: V3J16
- ST-LINK serial: 0047001F3133511037363734
- Flash base: 0x08000000 (2MB)
- SRAM: ~786KB

## UART (Closed-loop verification)
- Peripheral: USART2
- Pins: PD5 = USART2_TX, PD6 = USART2_RX (AF7)
- Baud: 115200
- Handshake token: STWINBX1_ON_LINE   (firmware prints this on boot)

## Loop goal
1) make clean && make
2) st-flash write firmware.bin 0x08000000
3) test_runner.py reads token from /dev/ttyACM* (or /dev/serial/by-id)
4) If build/flash/verify fails: feed logs back to Codex and retry (max 5)

## Files we rely on
- main.c (HSI16 + USART2 PD5/PD6 AF7 + prints token)
- startup.s / linker.ld / Makefile
- test_runner.py (UART judge, baud=115200)
- autonomous_agent.py (or loop script) does build->flash->verify->Codex-fix loop
