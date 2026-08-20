#!/usr/bin/env python3
import time
import board
import neopixel

PIXELS = 12
PIN = board.D18  # physical pin 12, BCM18
pixels = neopixel.NeoPixel(PIN, PIXELS, brightness=0.15, auto_write=False, pixel_order=neopixel.GRB)
try:
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (32, 32, 32)]
    for color in colors:
        pixels.fill(color)
        pixels.show()
        time.sleep(0.6)
    pixels.fill((0, 0, 0))
    pixels.show()
    print("NeoPixel ring test complete: 12 pixels on BCM18/physical pin 12")
finally:
    pixels.deinit()
