#!/usr/bin/python3

import RPi_I2C_driver
from time import *


l = RPi_I2C_driver.lcd(0x27,16,2)
l.lcd_clear()
l.backlight(0)

