HYPOTHESIS: Build failed because the local STM32U5 shim was missing RCC fields/macros (`CR` bits and `CCIPR1` USART2 clock-select symbols) required by `main.c`’s forced boot UART path.  
CHANGE: Replaced `stm32u5xx.h` with a fuller minimal register shim that defines `RCC_TypeDef` including `CCIPR1`, required RCC/USART/GPIO bit macros, and guarded base addresses/pointers for STM32U575/U585.  
FILES: stm32u5xx.h  
NEXT: ST-LINK VCP at 115200 on USART2 (PD5/PD6) should show exactly `STWINBX1_ON_LINE\n` at boot.
