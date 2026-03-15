HYPOTHESIS: Build fails because the local STM32U5 shim is missing `USART_ISR_TEACK`, which `main.c` waits on before transmit.
CHANGE: Replaced `stm32u5xx.h` with a complete minimal STM32U575/U585 register/macro shim that includes `USART_ISR_TEACK` (bit 21) and preserves USART2/PD5/PD6/115200 support.
FILES: `stm32u5xx.h`
NEXT: On boot, UART should output exactly `STWINBX1_ON_LINE\n` on ST-LINK VCP (USART2, PD5/PD6, 115200).
