#!/bin/bash
openocd -f board/stm32f7discovery.cfg -c "init" -c "tpiu config internal swo.log uart off 16000000" -c "itm port 0 on"
