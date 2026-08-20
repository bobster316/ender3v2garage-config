#!/usr/bin/python
import os
import sys
import time
import random
import logging
import argparse
from PIL import Image, ImageDraw, ImageFont

# Set up argument parser
parser = argparse.ArgumentParser(description='Run Matrix-style digital rain on Waveshare 1.69-inch LCD')
args = parser.parse_args()

# Add the LCD module path to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
lcd_module_path = os.path.join(current_dir, 'LCD_Module_RPI_code', 'RaspberryPi', 'python')
sys.path.append(lcd_module_path)

try:
    from lib import LCD_1inch69
except ModuleNotFoundError:
    print(f"Error: Unable to import LCD_1inch69 module from {lcd_module_path}")
    print("Please ensure that the LCD_Module_RPI_code folder is in the same directory as this script.")
    sys.exit(1)

# Raspberry Pi pin configuration
RST = 17
DC = 25
BL = 18
bus = 0
device = 0
logging.basicConfig(level=logging.DEBUG)

# Display dimensions
WIDTH = 240
HEIGHT = 280

# Initialize display with error handling
try:
    disp = LCD_1inch69.LCD_1inch69(rst=RST, dc=DC, bl=BL)
    disp.Init()
    disp.clear()
    disp.bl_DutyCycle(50)
except Exception as e:
    print(f"Error initializing display: {e}")
    print("Please check your GPIO connections and permissions.")
    sys.exit(1)

# Load the font
try:
    font_size = 28
    font_path = os.path.join(current_dir, 'msmincho.ttf')
    font = ImageFont.truetype(font_path, font_size)
except IOError:
    print(f"Error: Unable to load font from {font_path}")
    print("Using default font instead.")
    font = ImageFont.load_default()

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHT_GREEN = (0, 255, 0)

# Character set (specific characters from msmincho.ttf)
char_set = ['゠', 'ァ', 'ア', 'ィ', 'イ', 'ゥ', 'ウ', 'ェ', 'エ', 'ォ', 'オ', 'カ', 'ガ', 'キ', 'ギ', 'ク', 'グ', 'ケ', 'ゲ', 'コ',
            'ゴ', 'サ', 'ザ', 'シ', 'ジ', 'ス', 'ズ', 'セ', 'ゼ', 'ソ', 'ゾ', 'タ', 'ダ', 'チ', 'ヂ', 'ッ', 'ツ', 'ヅ', 'テ', 'デ',
            'ト', 'ド', 'ナ', 'ニ', 'ヌ', 'ネ', 'ノ', 'ハ', 'バ', 'パ', 'ヒ', 'ビ', 'ピ', 'フ', 'ブ', 'プ', 'ヘ', 'ベ', 'ペ', 'ホ',
            'ボ', 'ポ', 'マ', 'ミ', 'ム', 'メ', 'モ', 'ャ', 'ヤ', 'ュ', 'ユ', 'ョ', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ヮ', 'ワ',
            'ヰ', 'ヱ', 'ヲ', 'ン', 'ヴ', 'ヵ', 'ヶ', 'ヷ', 'ヸ', 'ヹ', 'ヺ', '・', 'ー', 'ヽ', 'ヾ', 'ヿ',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '!', '@', '#', '$', '%', '^', '&',
            '*', '(', ')', '_', '+', '-', '=', '[', ']', '{', '}', '|', ';', ':', ',', '.', '/', '<', '>', '?']

class RainColumn:
    def __init__(self, x, screen_height, is_front):
        self.x = x
        self.screen_height = screen_height
        self.is_front = is_front
        self.reset()

    def reset(self):
        self.speed = random.uniform(1.82, 3.64)  # Increased speed by 30%
        self.chars = [random.choice(char_set) for _ in range(self.screen_height // font_size + 1)]
        self.brightnesses = [random.randint(200, 255) for _ in range(len(self.chars))]
        self.head_pos = random.uniform(-font_size, 0)
        self.white_index = random.randint(0, len(self.chars) - 1)
        self.white_counter = random.randint(5, 15)  # Random duration for white character

    def update(self, delta_time):
        self.head_pos += self.speed * delta_time * 60
        while self.head_pos >= font_size:
            self.head_pos -= font_size
            self.chars.pop()
            self.chars.insert(0, random.choice(char_set))
            self.brightnesses.pop()
            self.brightnesses.insert(0, 255)
            self.white_index = (self.white_index - 1) % len(self.chars)

        # Change characters as they fall
        for i in range(len(self.chars)):
            if random.random() < 0.1:  # 10% chance to change each character
                self.chars[i] = random.choice(char_set)

        # Update white character position
        self.white_counter -= 1
        if self.white_counter <= 0:
            self.white_index = random.randint(0, len(self.chars) - 1)
            self.white_counter = random.randint(5, 15)  # Reset counter

        for i in range(len(self.brightnesses)):
            if i != self.white_index:
                self.brightnesses[i] = max(100, self.brightnesses[i] - 5)  # Faster dimming

    def draw(self, draw):
        for i, char in enumerate(self.chars):
            y = int(self.head_pos + i * font_size)
            if -font_size < y < self.screen_height:
                if i == self.white_index:
                    color = WHITE
                else:
                    green = self.brightnesses[i]
                    color = (0, green, 0)

                if self.is_front:
                    # Draw twice with slight offset to create bold effect
                    draw.text((self.x, y), char, font=font, fill=color)
                    draw.text((self.x + 1, y), char, font=font, fill=color)
                else:
                    draw.text((self.x, y), char, font=font, fill=color)

def main():
    logging.info("Starting main function...")
    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    columns = []
    column_width = int(font_size * 0.8)
    num_columns = WIDTH // column_width + 1
    front_columns = num_columns // 2  # Consider the right half as "front" columns

    for i in range(num_columns):
        x = i * column_width
        is_front = i >= (num_columns - front_columns)
        columns.append(RainColumn(x, HEIGHT, is_front))

    logging.info(f"Created {num_columns} columns")

    last_time = time.monotonic()
    frame_count = 0
    start_time = time.time()

    try:
        while True:
            current_time = time.monotonic()
            delta_time = current_time - last_time
            last_time = current_time

            draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=BLACK)

            for column in columns:
                column.update(delta_time)
                column.draw(draw)

            disp.ShowImage(image)
            frame_count += 1

            if frame_count % 100 == 0:
                end_time = time.time()
                fps = frame_count / (end_time - start_time)
                logging.info(f"FPS: {fps:.2f}")

            time.sleep(0.01)

    except KeyboardInterrupt:
        logging.info("Exiting...")
        disp.clear()
        disp.module_exit()
        logging.info("Display cleared and module exited.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.info(f"Display dimensions: {WIDTH}x{HEIGHT}")
        disp.module_exit()

