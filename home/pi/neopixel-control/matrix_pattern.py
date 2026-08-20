#!/usr/bin/env python3
import random
import signal
import time

import board
import neopixel

PIXELS = 12
PIN = board.D18  # BCM18 / physical pin 12
BRIGHTNESS = 0.09
FPS_DELAY = 0.08

running = True


def stop(_signum=None, _frame=None):
    global running
    running = False


def green(level):
    level = max(0.0, min(1.0, level))
    return (0, int(255 * level), int(20 * level))


def main():
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    pixels = neopixel.NeoPixel(
        PIN,
        PIXELS,
        brightness=BRIGHTNESS,
        auto_write=False,
        pixel_order=neopixel.GRB,
    )
    levels = [0.0] * PIXELS
    drops = []

    try:
        print('NeoPixel ring matrix pattern running on BCM18 with 12 pixels', flush=True)
        while running:
            levels = [value * 0.76 for value in levels]

            if random.random() < 0.35:
                drops.append({
                    'pos': random.randrange(PIXELS),
                    'dir': random.choice([-1, 1]),
                    'tail': random.randint(2, 4),
                    'life': random.randint(12, 30),
                })

            active = []
            for drop in drops:
                for offset in range(drop['tail']):
                    idx = (drop['pos'] - (offset * drop['dir'])) % PIXELS
                    levels[idx] = max(levels[idx], 0.95 * (0.45 ** offset))
                drop['pos'] = (drop['pos'] + drop['dir']) % PIXELS
                drop['life'] -= 1
                if drop['life'] > 0:
                    active.append(drop)
            drops = active

            if random.random() < 0.12:
                idx = random.randrange(PIXELS)
                levels[idx] = max(levels[idx], random.uniform(0.08, 0.18))

            for index, level in enumerate(levels):
                pixels[index] = green(level)
            pixels.show()
            time.sleep(FPS_DELAY)
    finally:
        pixels.fill((0, 0, 0))
        pixels.show()
        pixels.deinit()
        print('NeoPixel ring matrix pattern stopped', flush=True)


if __name__ == '__main__':
    main()
