CC      = arm-none-eabi-gcc
OBJCOPY = arm-none-eabi-objcopy

CFLAGS  = -mcpu=cortex-m33 -mthumb -O0 -g -Wall -ffreestanding -fno-builtin
LDFLAGS = -T linker.ld -nostartfiles

all: firmware.bin

firmware.elf: main.c startup.s
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

firmware.bin: firmware.elf
	$(OBJCOPY) -O binary $< $@

clean:
	rm -f *.elf *.bin
