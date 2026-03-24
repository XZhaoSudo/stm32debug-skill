#!/bin/bash
CPU_FREQ=${1:-16000000}
openocd -f board/stm32f7discovery.cfg -c "init" -c "tpiu config internal swo.log uart off $CPU_FREQ" -c "itm port 0 on"
