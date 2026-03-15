HYPOTHESIS: The build fails because `main.c` uses RCC/CCIPR macro names that are not defined in the local STM32U5 shim.  
CHANGE: Added guarded fallback definitions for `RCC_CR_HSION`, `RCC_CR_HSIRDY`, `RCC_CCIPR1_USART2SEL_0`, `RCC_CCIPR1_USART2SEL_1`, and combined mask `RCC_CCIPR1_USART2SEL` in `stm32u5xx.h`.  
FILES: stm32u5xx.h  
NEXT: On boot at 115200 over ST-LINK VCP (USART2 PD5/PD6), UART should print exactly `STWINBX1_ON_LINE\n`.
