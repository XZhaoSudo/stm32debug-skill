#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: $0 <elf_file>"
    exit 1
fi
ELF_FILE=$1
openocd -f board/stm32f7discovery.cfg -c "program $ELF_FILE verify reset exit"
