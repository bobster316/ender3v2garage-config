#!/usr/bin/env python3
"""Matrix Rain Effect - LED Shim Only - FASTER VERSION"""
import ledshim
import time
import random

class MatrixLEDShim:
    def __init__(self):
        ledshim.set_clear_on_exit()
        ledshim.set_brightness(0.7)
        self.num_pixels = 28
        self.drops = []
        
        # Create more drops for denser effect
        for i in range(self.num_pixels):
            self.drops.append({
                'position': random.randint(-10, 0),
                'speed': random.uniform(0.8, 2.0),  # Increased from 0.3-1.0
                'brightness': 0,
                'active': random.random() > 0.3  # More drops active (was > 0.5)
            })

    def update(self):
        for i in range(self.num_pixels):
            drop = self.drops[i]
            if drop['active']:
                drop['position'] += drop['speed']
                
                # Faster fade
                if drop['position'] >= 0 and drop['position'] < 3:  # Shorter bright period
                    drop['brightness'] = 255
                elif drop['position'] >= 3 and drop['position'] < 10:  # Faster fade
                    drop['brightness'] = max(0, 255 - int((drop['position'] - 3) * 36))
                else:
                    drop['brightness'] = 0
                
                # Reset when off screen
                if drop['position'] > 15:  # Shorter trail
                    drop['position'] = random.randint(-10, -3)
                    drop['speed'] = random.uniform(0.8, 2.0)  # Faster speeds
                    drop['active'] = random.random() > 0.2  # More likely to stay active
            else:
                # Activate drops more frequently
                if random.random() > 0.95:  # Was 0.98
                    drop['active'] = True
                    drop['position'] = random.randint(-8, 0)
                    drop['speed'] = random.uniform(0.8, 2.0)
                drop['brightness'] = 0

        # Update LEDs
        for i in range(self.num_pixels):
            drop = self.drops[i]
            brightness = int(drop['brightness'])
            if brightness > 200:
                r = brightness // 4
                g = brightness
                b = brightness // 4
                ledshim.set_pixel(i, r, g, b)
            else:
                ledshim.set_pixel(i, 0, brightness, 0)
        ledshim.show()

    def run(self):
        try:
            print("Matrix LED Shim - FAST MODE - Press Ctrl+C to exit")
            while True:
                self.update()
                time.sleep(0.03)  # Faster update (was 0.05)
        except KeyboardInterrupt:
            self.cleanup()

    def cleanup(self):
        ledshim.clear()
        ledshim.show()

if __name__ == "__main__":
    matrix = MatrixLEDShim()
    matrix.run()
