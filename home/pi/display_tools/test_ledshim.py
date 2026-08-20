#!/usr/bin/env python3
import sys
import time
sys.path.insert(0, "/home/pi/Pimoroni/led-shim")
import ledshim

ledshim.set_clear_on_exit(False)
ledshim.set_brightness(0.25)
try:
    for color in [(255, 0, 0), (0, 255, 0), (0, 0, 255), (32, 32, 32)]:
        ledshim.clear()
        for x in range(28):
            ledshim.set_pixel(x, *color)
        ledshim.show()
        time.sleep(0.6)
    ledshim.clear()
    ledshim.show()
    print("LED SHIM test complete: 28 pixels via Pimoroni ledshim library")
except OSError as e:
    print(f"LED SHIM I2C error: {e}")
    raise
