# Agent rules (do not break)

Target: STM32U575/U585 (chipid 0x482)
Flash base: 0x08000000

UART verification MUST use:
- USART2
- PD5 = TX (AF7)
- PD6 = RX (AF7)
Baud: 115200
Boot token: "STWINBX1_ON_LINE\n"

Success = after flashing, host sees STWINBX1_ON_LINE on ST-LINK VCP within timeout.

Do NOT change UART peripheral or pins unless explicitly instructed.

ADDITIONAL HARD RULES:
- Do NOT use __attribute__((constructor)) or any C++/libc init features (startup.s does not run constructors).
- Do NOT invent local CMSIS/register “shim” headers. If a header is missing, use only existing code OR add STM32CubeU5 CMSIS headers under third_party and update Makefile includes.

DO NOT:
- add #include "stm32u5xx.h" or any invented shim headers
- use __attribute__((constructor)) or rely on libc init sections
- change UART away from USART2 PD5/PD6 AF7 @115200

DO:
- keep a simple bare-metal init already present in main.c
- print STWINBX1_ON_LINE repeatedly in the main loop so host cannot miss it
