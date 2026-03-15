===BEGIN_MAIN_C===
#include <stdint.h>

#define TOKEN "STWINBX1_ON_LINE\n"

/* STM32U575/U585 base addresses */
#define RCC_BASE        0x46020C00UL
#define USART2_BASE     0x40004400UL
#define GPIO_AHB2_BASE  0x42020000UL
#define GPIOD_BASE      (GPIO_AHB2_BASE + 0x0C00UL)
#define GPIOH_BASE      (GPIO_AHB2_BASE + 0x1C00UL)

/* RCC register offsets */
#define RCC_CR          (*(volatile uint32_t *)(RCC_BASE + 0x000UL))
#define RCC_AHB2ENR1    (*(volatile uint32_t *)(RCC_BASE + 0x08CUL))
#define RCC_APB1ENR1    (*(volatile uint32_t *)(RCC_BASE + 0x09CUL))
#define RCC_CCIPR1      (*(volatile uint32_t *)(RCC_BASE + 0x0D4UL))

/* RCC bits */
#define RCC_CR_HSION                (1UL << 8)
#define RCC_CR_HSIRDY               (1UL << 10)
#define RCC_AHB2ENR1_GPIODEN        (1UL << 3)
#define RCC_AHB2ENR1_GPIOHEN        (1UL << 7)
#define RCC_APB1ENR1_USART2EN       (1UL << 17)
#define RCC_CCIPR1_USART2SEL_Pos    2U
#define RCC_CCIPR1_USART2SEL_Msk    (3UL << RCC_CCIPR1_USART2SEL_Pos)
#define RCC_CCIPR1_USART2SEL_HSI16  (2UL << RCC_CCIPR1_USART2SEL_Pos)

/* USART bits */
#define USART_CR1_UE                (1UL << 0)
#define USART_CR1_RE                (1UL << 2)
#define USART_CR1_TE                (1UL << 3)
#define USART_ISR_RXNE_RXFNE        (1UL << 5)
#define USART_ISR_TC                (1UL << 6)
#define USART_ISR_TXE_TXFNF         (1UL << 7)

/* GPIO + USART register layout */
typedef struct {
  volatile uint32_t MODER;
  volatile uint32_t OTYPER;
  volatile uint32_t OSPEEDR;
  volatile uint32_t PUPDR;
  volatile uint32_t IDR;
  volatile uint32_t ODR;
  volatile uint32_t BSRR;
  volatile uint32_t LCKR;
  volatile uint32_t AFR[2];
  volatile uint32_t BRR;
} GPIO_TypeDef;

typedef struct {
  volatile uint32_t CR1;
  volatile uint32_t CR2;
  volatile uint32_t CR3;
  volatile uint32_t BRR;
  volatile uint32_t GTPR;
  volatile uint32_t RTOR;
  volatile uint32_t RQR;
  volatile uint32_t ISR;
  volatile uint32_t ICR;
  volatile uint32_t RDR;
  volatile uint32_t TDR;
  volatile uint32_t PRESC;
  volatile uint32_t AUTOCR;
} USART_TypeDef;

#define GPIOD   ((GPIO_TypeDef *)GPIOD_BASE)
#define GPIOH   ((GPIO_TypeDef *)GPIOH_BASE)
#define USART2  ((USART_TypeDef *)USART2_BASE)

static void delay(volatile uint32_t n) {
  while (n--) {
    __asm volatile ("nop");
  }
}

static void leds_init(void) {
  RCC_AHB2ENR1 |= RCC_AHB2ENR1_GPIOHEN;

  /* PH12 green, PH10 orange -> output mode */
  GPIOH->MODER &= ~((3UL << (12U * 2U)) | (3UL << (10U * 2U)));
  GPIOH->MODER |=  ((1UL << (12U * 2U)) | (1UL << (10U * 2U)));

  GPIOH->OTYPER &= ~((1UL << 12U) | (1UL << 10U));
  GPIOH->OSPEEDR |= ((2UL << (12U * 2U)) | (2UL << (10U * 2U)));
  GPIOH->PUPDR &= ~((3UL << (12U * 2U)) | (3UL << (10U * 2U)));

  GPIOH->BSRR = (1UL << (12U + 16U)) | (1UL << (10U + 16U));
}

static void led_green_toggle(void) {
  GPIOH->ODR ^= (1UL << 12U);
}

static void led_orange_pulse(void) {
  GPIOH->BSRR = (1UL << 10U);
  delay(120000);
  GPIOH->BSRR = (1UL << (10U + 16U));
}

static void uart2_init_115200_pd5_pd6(void) {
  RCC_CR |= RCC_CR_HSION;
  while ((RCC_CR & RCC_CR_HSIRDY) == 0U) {
  }

  RCC_AHB2ENR1 |= RCC_AHB2ENR1_GPIODEN;
  RCC_APB1ENR1 |= RCC_APB1ENR1_USART2EN;

  RCC_CCIPR1 = (RCC_CCIPR1 & ~RCC_CCIPR1_USART2SEL_Msk) | RCC_CCIPR1_USART2SEL_HSI16;

  /* PD5/PD6 alternate function AF7 (USART2 TX/RX) */
  GPIOD->MODER &= ~((3UL << (5U * 2U)) | (3UL << (6U * 2U)));
  GPIOD->MODER |=  ((2UL << (5U * 2U)) | (2UL << (6U * 2U)));

  GPIOD->OTYPER &= ~((1UL << 5U) | (1UL << 6U));
  GPIOD->OSPEEDR |= ((3UL << (5U * 2U)) | (3UL << (6U * 2U)));
  GPIOD->PUPDR &= ~((3UL << (5U * 2U)) | (3UL << (6U * 2U)));

  GPIOD->AFR[0] &= ~((0xFUL << (5U * 4U)) | (0xFUL << (6U * 4U)));
  GPIOD->AFR[0] |=  ((7UL   << (5U * 4U)) | (7UL   << (6U * 4U)));

  USART2->CR1 = 0U;
  USART2->CR2 = 0U;
  USART2->CR3 = 0U;
  USART2->PRESC = 0U;   /* /1 prescaler */
  USART2->BRR = 139U;   /* 16 MHz / 115200 */
  USART2->CR1 = USART_CR1_TE | USART_CR1_RE | USART_CR1_UE;
}

static void uart2_write_char(char c) {
  while ((USART2->ISR & USART_ISR_TXE_TXFNF) == 0U) {
  }
  USART2->TDR = (uint8_t)c;
}

static void uart2_write_str(const char *s) {
  while (*s != '\0') {
    uart2_write_char(*s++);
  }
  while ((USART2->ISR & USART_ISR_TC) == 0U) {
  }
}

static int uart2_try_read_char(char *out) {
  if ((USART2->ISR & USART_ISR_RXNE_RXFNE) != 0U) {
    *out = (char)(USART2->RDR & 0xFFU);
    return 1;
  }
  return 0;
}

int main(void) {
  leds_init();
  uart2_init_115200_pd5_pd6();

  for (;;) {
    uart2_write_str(TOKEN);
    led_green_toggle();

    {
      char c;
      if (uart2_try_read_char(&c) && c == 'p') {
        led_orange_pulse();
      }
    }

    delay(250000);
  }
}
===END_MAIN_C===