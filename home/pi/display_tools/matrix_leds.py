#!/usr/bin/env python3
import random
import signal
import sys
import time

sys.path.insert(0, '/home/pi/Pimoroni/led-shim')
sys.path.insert(0, '/home/pi/LCD_Module_RPI_code/RaspberryPi/python')

from PIL import Image, ImageDraw, ImageFont
from rpi_ws281x import PixelStrip, Color
import ledshim
from lib.LCD_1inch69 import LCD_1inch69

RING_COUNT = 12
RING_PIN = 18
RING_BRIGHTNESS = 70
RING_CHANNEL = 0
RING_DMA = 10
RING_FREQ = 800000
RING_INVERT = False

LCD_WIDTH = 240
LCD_HEIGHT = 280
CELL_W = 12
CELL_H = 14
COLS = LCD_WIDTH // CELL_W
ROWS = LCD_HEIGHT // CELL_H
GLYPHS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0@%&*+-='

running = True
strip = None
lcd = None


def stop(_signum=None, _frame=None):
    global running
    running = False


def scale_green(level):
    level = max(0.0, min(1.0, level))
    return (0, int(255 * level), int(18 * level))


def ring_color(level):
    r, g, b = scale_green(level)
    return Color(r, g, b)


def clear_all():
    try:
        if strip is not None:
            for i in range(RING_COUNT):
                strip.setPixelColor(i, Color(0, 0, 0))
            strip.show()
    except Exception:
        pass
    try:
        ledshim.clear()
        ledshim.show()
    except Exception:
        pass


def rain_impact(levels, count, probability):
    if random.random() >= probability:
        return
    x = random.randrange(count)
    levels[x] = max(levels[x], random.uniform(0.92, 1.0))
    for offset, low, high in [(-2, 0.12, 0.32), (-1, 0.35, 0.68), (1, 0.35, 0.68), (2, 0.12, 0.32)]:
        idx = x + offset
        if 0 <= idx < count:
            levels[idx] = max(levels[idx], random.uniform(low, high))


def draw_lcd(draw, drops, font):
    draw.rectangle((0, 0, LCD_WIDTH, LCD_HEIGHT), fill=(0, 0, 0))
    for drop in drops:
        x = drop['col'] * CELL_W
        head = drop['row']
        for tail in range(drop['tail']):
            row = head - tail
            if row < 0 or row >= ROWS:
                continue
            level = 1.0 if tail == 0 else max(0.10, 0.72 ** tail)
            if tail == 0:
                color = (150, 255, 150)
            else:
                color = (0, int(175 * level), int(20 * level))
            char = random.choice(GLYPHS) if random.random() < 0.28 or 'char' not in drop else drop['char']
            if tail == 0:
                drop['char'] = char
            draw.text((x, row * CELL_H - 1), char, fill=color, font=font)


def main():
    global strip, lcd
    random.seed()
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    strip = PixelStrip(RING_COUNT, RING_PIN, RING_FREQ, RING_DMA, RING_INVERT, RING_BRIGHTNESS, RING_CHANNEL)
    strip.begin()

    ledshim.set_clear_on_exit(False)
    ledshim.set_brightness(1.0)
    ledshim.clear()
    ledshim.show()

    lcd = LCD_1inch69()
    lcd.Init()
    lcd.bl_DutyCycle(100)
    font = ImageFont.load_default()
    image = Image.new('RGB', (LCD_WIDTH, LCD_HEIGHT), 'black')
    draw = ImageDraw.Draw(image)

    shim_levels = [0.0] * 28
    ring_levels = [0.0] * RING_COUNT
    ring_drops = []
    lcd_drops = [{'col': c, 'row': random.randrange(-ROWS, ROWS), 'speed': random.choice([1, 1, 2]), 'tail': random.randint(6, 15)} for c in range(COLS)]
    frame = 0

    print('Matrix theme running: LCD code rain, LED SHIM impact flicker, NeoPixel ring circular rain', flush=True)

    try:
        while running:
            shim_levels = [v * 0.78 for v in shim_levels]
            ring_levels = [v * 0.78 for v in ring_levels]

            rain_impact(shim_levels, 28, 0.88)
            rain_impact(shim_levels, 28, 0.62)
            rain_impact(shim_levels, 28, 0.36)

            if random.random() < 0.16:
                ring_drops.append({'pos': random.randrange(RING_COUNT), 'speed': random.choice([-1, 1]), 'tail': random.randint(2, 4), 'life': random.randint(14, 28)})

            next_ring = []
            for drop in ring_drops:
                for t in range(drop['tail']):
                    idx = (drop['pos'] - (t * drop['speed'])) % RING_COUNT
                    ring_levels[idx] = max(ring_levels[idx], 0.78 * (0.42 ** t))
                drop['pos'] = (drop['pos'] + drop['speed']) % RING_COUNT
                drop['life'] -= 1
                if drop['life'] > 0:
                    next_ring.append(drop)
            ring_drops = next_ring

            if frame % 5 == 0:
                ring_levels[random.randrange(RING_COUNT)] = max(ring_levels[random.randrange(RING_COUNT)], random.uniform(0.04, 0.12))

            for d in lcd_drops:
                if frame % d['speed'] == 0:
                    d['row'] += 1
                if d['row'] - d['tail'] > ROWS:
                    d['row'] = random.randrange(-16, -1)
                    d['speed'] = random.choice([1, 1, 2])
                    d['tail'] = random.randint(6, 15)
                    d.pop('char', None)
            draw_lcd(draw, lcd_drops, font)
            lcd.ShowImage(image)

            for i, level in enumerate(shim_levels):
                ledshim.set_pixel(i, *scale_green(level))
            ledshim.show()

            for i, level in enumerate(ring_levels):
                strip.setPixelColor(i, ring_color(level))
            strip.show()

            frame += 1
            time.sleep(0.14)
    finally:
        clear_all()
        print('Matrix LED animation stopped', flush=True)


if __name__ == '__main__':
    main()
