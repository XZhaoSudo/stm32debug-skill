---
name: "stm32-debug"
description: "Compiles, flashes, debugs, and monitors STM32 firmware. Invoke for build, flash, GDB, SWO logs, or real-time variable/register monitoring."
---

# STM32 Debug Skill

This skill provides a comprehensive suite of tools for STM32 development, including compilation, flashing, debugging, SWO logging, and real-time monitoring of variables and registers.

## Prerequisites
- `arm-none-eabi-gcc`
- `openocd`
- `gdb-multiarch`
- `python3`
- SVD file (e.g., `STM32F746.svd`)

## Commands

### 1. Build Firmware
Compile the project:
```bash
make
```

### 2. Flash Firmware
Flash the ELF file to the device:
```bash
./scripts/flash.sh <elf_file>
```
Example:
```bash
./scripts/flash.sh test_project/test_swo.elf
```

### 3. Real-Time Monitoring (Variables & Registers)
Monitor global variables (including struct members) or peripheral registers without halting the CPU. Requires OpenOCD running (start with `openocd -f board/stm32f7discovery.cfg` in background).

**Monitor a Variable or Struct Member:**
```bash
./scripts/stm32_monitor.py --elf <elf_file> --var "<expression>" --type <type> --interval <seconds>
```
- `<expression>`: C expression, e.g., `counter`, `my_struct.member`, `array[0]`.
- `<type>`: `hex` (default), `int`, `float`.

Examples:
```bash
# Monitor an integer counter
./scripts/stm32_monitor.py --elf test_project/test_swo.elf --var counter --type int

# Monitor a struct member (float)
./scripts/stm32_monitor.py --elf test_project/test_swo.elf --var "my_sensor.value" --type float

# Monitor an array element
./scripts/stm32_monitor.py --elf test_project/test_swo.elf --var "data_buffer[2]" --type hex
```

**Monitor a Register:**
```bash
./scripts/stm32_monitor.py --svd <svd_file> --reg <peripheral> [register] --interval <seconds>
```
Example:
```bash
./scripts/stm32_monitor.py --svd STM32F746.svd --reg GPIOA MODER --interval 1
```

### 4. Monitor SWO Output
Capture printf logs via SWO pin:
```bash
./scripts/monitor_swo.sh
```
Read the log:
```bash
tail -f swo.log
```

### 5. Inspect Register Definitions
View register details (address, fields, description) from SVD:
```bash
./scripts/read_svd.py <svd_file> <peripheral> [register]
```
Example:
```bash
./scripts/read_svd.py STM32F746.svd RCC CR
```

### 6. Debug with GDB
Start interactive debugging:
1. Start OpenOCD: `openocd -f board/stm32f7discovery.cfg`
2. Start GDB: `gdb-multiarch <elf_file>`
3. Connect: `target remote :3333`, `monitor reset halt`, `load`

## Troubleshooting
- **OpenOCD Init Failed**: Ensure no other OpenOCD instance is running (`pkill openocd`).
- **Connection Refused**: Ensure OpenOCD is running before using monitoring scripts.
- **Symbol Not Found**: Ensure the variable is global (not static/local) and the ELF file is up-to-date.
- **GDB Error**: Ensure `gdb-multiarch` is installed to resolve complex types like structs.
