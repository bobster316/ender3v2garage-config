#!/usr/bin/env python3
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/home/pi/LCD_Module_RPI_code/RaspberryPi/python")
sys.path.insert(0, str(ROOT))
from lib.LCD_1inch69 import LCD_1inch69

WIDTH = 240
HEIGHT = 280

lcd = LCD_1inch69()
lcd.Init()
lcd.bl_DutyCycle(80)
img = Image.new("RGB", (WIDTH, HEIGHT), "black")
d = ImageDraw.Draw(img)
bands = [
    ("RED", (255, 0, 0)),
    ("GREEN", (0, 255, 0)),
    ("BLUE", (0, 0, 255)),
    ("WHITE", (255, 255, 255)),
]
band_h = HEIGHT // len(bands)
for i, (name, color) in enumerate(bands):
    y0 = i * band_h
    y1 = HEIGHT if i == len(bands) - 1 else (i + 1) * band_h
    d.rectangle((0, y0, WIDTH, y1), fill=color)
    text_color = (0, 0, 0) if name == "WHITE" else (255, 255, 255)
    d.text((10, y0 + 22), name, fill=text_color)
d.text((10, HEIGHT - 24), "1.69 ST7789 GPIO17 BL", fill=(0, 0, 0))
lcd.ShowImage(img)
print("LCD test complete: red/green/blue/white bands sent to Waveshare 1.69 config")
