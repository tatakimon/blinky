.syntax unified
.cpu cortex-m33
.fpu softvfp
.thumb

.global g_pfnVectors
.global Reset_Handler

.section .isr_vector,"a",%progbits
g_pfnVectors:
  .word   0x20004000      /* Stack Top (RAM sonu - yaklaşık) */
  .word   Reset_Handler   /* Reset Handler */

.section .text.Reset_Handler
.weak Reset_Handler
.type Reset_Handler, %function
Reset_Handler:
  bl main
  b .
