#!/usr/bin/env python3
import os
import sys
import time
import socket
import shutil
from pathlib import Path

import psutil
from PIL import Image, ImageDraw, ImageFont

LCD_PATH = "/home/pi/LCD_Module_RPI_code/RaspberryPi/python"
sys.path.append(LCD_PATH)

from lib import LCD_1inch69

RST = 17
DC = 25
BL = 18

WIDTH = 240
HEIGHT = 280

BASE_DIR = Path(__file__).resolve().parent

BLACK = (0, 0, 0)
TEXT_GREEN = (210, 255, 95)
SHADOW_GREEN = (25, 95, 20)


def get_ip_address():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.2)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except Exception:
        return "No network"


def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return float(f.read().strip()) / 1000.0
    except Exception:
        return 0.0


def load_font(size):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        str(BASE_DIR / "mincho.ttf"),
        "/home/pi/matrix-pi/mincho.ttf",
    ]

    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass

    return ImageFont.load_default()


def centred_text(draw, y, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = int((WIDTH - text_width) / 2)

    # Glow/shadow to match the photo
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1)]:
        draw.text((x + dx, y + dy), text, font=font, fill=SHADOW_GREEN)

    draw.text((x, y), text, font=font, fill=TEXT_GREEN)


def build_stats_screen():
    image = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
    draw = ImageDraw.Draw(image)

    title_font = load_font(21)
    line_font = load_font(23)

    ip = get_ip_address()
    cpu = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory().percent
    disk_usage = shutil.disk_usage("/")
    disk = disk_usage.used / disk_usage.total * 100
    temp = get_cpu_temp()

    lines = [
        ("Ender3v2Garage", title_font, 48),
        (f"IP: {ip}", line_font, 92),
        (f"CPU: {cpu:.0f}%", line_font, 126),
        (f"MEM: {mem:.1f}%", line_font, 160),
        (f"DISK: {disk:.1f}%", line_font, 194),
        (f"TEMP: {temp:.1f}°C", line_font, 228),
    ]

    for text, font, y in lines:
        centred_text(draw, y, text, font)

    return image


def fade_to_black(disp, image):
    black = Image.new("RGB", (WIDTH, HEIGHT), BLACK)

    for step in range(20):
        alpha = step / 19
        frame = Image.blend(image, black, alpha)
        disp.ShowImage(frame)
        time.sleep(0.04)


def main():
    disp = LCD_1inch69.LCD_1inch69(rst=RST, dc=DC, bl=BL)
    disp.Init()
    disp.clear()
    disp.bl_DutyCycle(70)

    print("Showing stats screen for 20 seconds")
    stats_image = build_stats_screen()
    disp.ShowImage(stats_image)

    time.sleep(20)

    print("Fading to Matrix")
    fade_to_black(disp, stats_image)

    matrix_script = str(BASE_DIR / "matrix.py")
    print("Starting Matrix digital rain")

    os.execvpe(
        sys.executable,
        [sys.executable, matrix_script],
        {
            **os.environ,
            "PYTHONPATH": LCD_PATH,
        },
    )


if __name__ == "__main__":
    main()
