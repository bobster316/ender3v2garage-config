from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 240
HEIGHT = 280
LCD_DRIVER_PATH = os.environ.get(
    "LCD_DRIVER_PATH",
    str(Path.home() / "LCD_Module_RPI_code/RaspberryPi/python"),
)


def import_lcd_driver():
    driver_path = Path(LCD_DRIVER_PATH).expanduser()
    if driver_path.exists():
        sys.path.append(str(driver_path))

    try:
        from lib import LCD_1inch69  # type: ignore

        return LCD_1inch69
    except Exception as exc:
        print("Could not import LCD_1inch69.", file=sys.stderr)
        print(f"Attempted driver path: {driver_path}", file=sys.stderr)
        print(f"Path exists: {driver_path.exists()}", file=sys.stderr)
        print("Expected: lib/LCD_1inch69.py inside that folder.", file=sys.stderr)
        print(
            "Override with: export LCD_DRIVER_PATH=/path/to/LCD_Module_RPI_code/RaspberryPi/python",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc


def main() -> int:
    LCD_1inch69 = import_lcd_driver()
    disp = LCD_1inch69.LCD_1inch69()
    disp.Init()
    disp.clear()
    if hasattr(disp, "bl_DutyCycle"):
        disp.bl_DutyCycle(100)

    image = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    blocks = [
        ((10, 20, 65, 75), "red", "R"),
        ((70, 20, 125, 75), "green", "G"),
        ((130, 20, 185, 75), "blue", "B"),
        ((190, 20, 230, 75), "white", "W"),
    ]
    for rect, color, label in blocks:
        draw.rectangle(rect, fill=color)
        draw.text((rect[0] + 8, rect[1] + 20), label, font=font, fill="black")

    draw.text((50, 115), "LCD TEST", font=font, fill=(255, 255, 255))
    draw.text((52, 145), "240x280", font=font, fill=(0, 255, 0))
    draw.text((58, 175), "SPI OK", font=font, fill=(0, 180, 255))
    draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=(255, 255, 255))

    if hasattr(disp, "ShowImage"):
        disp.ShowImage(image)
    else:
        disp.show_image(image)

    time.sleep(5)
    disp.clear()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
