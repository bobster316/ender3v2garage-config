from __future__ import annotations

import logging
import math
import os
import random
import sys
import time
from pathlib import Path
from typing import Iterable

import psutil
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
WIDTH = 240
HEIGHT = 280
LOG_PATH = BASE_DIR / "matrix-display.log"
LCD_DRIVER_PATH = os.environ.get(
    "LCD_DRIVER_PATH",
    str(Path.home() / "LCD_Module_RPI_code/RaspberryPi/python"),
)

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    if logging.getLogger().handlers:
        return
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def add_lcd_driver_path() -> None:
    driver_path = Path(LCD_DRIVER_PATH).expanduser()
    if driver_path.exists():
        path_text = str(driver_path)
        if path_text not in sys.path:
            sys.path.append(path_text)
        logger.info("Using LCD driver path: %s", driver_path)
    else:
        logger.warning(
            "LCD driver path does not exist: %s. Set LCD_DRIVER_PATH to the "
            "folder containing the lib/LCD_1inch69.py driver.",
            driver_path,
        )


def import_lcd_driver():
    add_lcd_driver_path()
    try:
        from lib import LCD_1inch69  # type: ignore

        return LCD_1inch69
    except Exception:
        logger.exception(
            "Could not import LCD_1inch69 from attempted driver path: %s. "
            "Check that this folder exists and contains lib/LCD_1inch69.py, "
            "or run: export LCD_DRIVER_PATH=/path/to/LCD_Module_RPI_code/RaspberryPi/python",
            LCD_DRIVER_PATH,
        )
        raise


def _scan_font_paths() -> Iterable[Path]:
    fonts_dir = Path("/usr/share/fonts")
    if not fonts_dir.exists():
        return []
    matches: list[Path] = []
    for pattern in ("*mincho*.ttf", "*mincho*.otf", "ipam.ttf"):
        matches.extend(fonts_dir.rglob(pattern))
    return matches


def load_matrix_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        BASE_DIR / "mincho.ttf",
        Path("/usr/share/fonts/opentype/ipafont-mincho/ipam.ttf"),
        *_scan_font_paths(),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]

    seen: set[Path] = set()
    for candidate in candidates:
        candidate = candidate.expanduser()
        if candidate in seen:
            continue
        seen.add(candidate)
        if not candidate.exists():
            continue
        try:
            font = ImageFont.truetype(str(candidate), size)
            logger.info("Loaded font: %s", candidate)
            return font
        except Exception:
            logger.exception("Failed to load font: %s", candidate)

    logger.warning("No usable font found; falling back to Pillow default font.")
    return ImageFont.load_default()


def load_logo() -> Image.Image | None:
    logo_path = BASE_DIR / "raspberry.png"
    if not logo_path.exists():
        logger.info("Logo not found at %s; continuing without logo.", logo_path)
        return None
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo.thumbnail((42, 42), Image.Resampling.LANCZOS)
        logger.info("Loaded logo: %s", logo_path)
        return logo
    except Exception:
        logger.exception("Failed to load logo at %s; continuing without logo.", logo_path)
        return None


class StatsDisplay:
    def __init__(self, width: int = WIDTH, height: int = HEIGHT) -> None:
        self.width = width
        self.height = height
        self.title_font = load_matrix_font(22)
        self.body_font = load_matrix_font(15)
        self.small_font = load_matrix_font(12)
        self.logo = load_logo()

    def _safe_temp(self) -> str:
        try:
            temps = psutil.sensors_temperatures()
            for key in ("cpu_thermal", "coretemp"):
                values = temps.get(key)
                if values:
                    return f"{values[0].current:.1f}C"
        except Exception:
            logger.exception("Failed to read temperature sensors.")
        return "n/a"

    def _draw_bar(
        self,
        draw: ImageDraw.ImageDraw,
        label: str,
        value: float,
        y: int,
        color: tuple[int, int, int],
    ) -> None:
        x = 18
        w = self.width - 36
        h = 12
        draw.text((x, y - 16), f"{label} {value:.0f}%", font=self.small_font, fill=(180, 255, 210))
        draw.rounded_rectangle((x, y, x + w, y + h), radius=3, outline=(25, 80, 45), fill=(5, 20, 10))
        fill_w = max(0, min(w, int(w * value / 100)))
        draw.rounded_rectangle((x, y, x + fill_w, y + h), radius=3, fill=color)

    def render(self) -> Image.Image:
        image = Image.new("RGB", (self.width, self.height), "black")
        draw = ImageDraw.Draw(image)

        draw.text((16, 14), "SYSTEM", font=self.title_font, fill=(170, 255, 190))
        draw.text((16, 40), "STATS", font=self.title_font, fill=(0, 255, 90))
        if self.logo:
            image.paste(self.logo, (self.width - 56, 16), self.logo)

        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        boot_delta = time.time() - psutil.boot_time()
        uptime_hours = boot_delta / 3600

        self._draw_bar(draw, "CPU", cpu, 92, (0, 255, 95))
        self._draw_bar(draw, "RAM", mem, 132, (80, 220, 255))
        self._draw_bar(draw, "DISK", disk, 172, (255, 255, 255))

        lines = [
            f"TEMP  {self._safe_temp()}",
            f"UP    {uptime_hours:.1f}h",
            f"HOST  {os.uname().nodename if hasattr(os, 'uname') else 'raspberrypi'}",
        ]
        y = 210
        for line in lines:
            draw.text((18, y), line, font=self.body_font, fill=(150, 255, 190))
            y += 19

        draw.text((18, self.height - 20), "MATRIX RAIN STARTING", font=self.small_font, fill=(0, 150, 60))
        return image


class MatrixDisplay:
    def __init__(self, width: int = WIDTH, height: int = HEIGHT) -> None:
        self.width = width
        self.height = height
        self.font_size = 16
        self.font = load_matrix_font(self.font_size)
        self.characters = list(
            "アイウエオカキクケコサシスセソタチツテトナニヌネノ"
            "ハヒフヘホマミムメモヤユヨラリルレロワヲン"
            "零壱弐参肆伍陸漆捌玖日月火水木金土0123456789"
        )
        self.column_width = max(10, self.font_size)
        self.columns = math.ceil(self.width / self.column_width)
        self.drops = [random.randint(-self.height, 0) for _ in range(self.columns)]
        self.speeds = [random.uniform(2.0, 5.5) for _ in range(self.columns)]
        self.trail_lengths = [random.randint(7, 18) for _ in range(self.columns)]

    def render(self) -> Image.Image:
        image = Image.new("RGB", (self.width, self.height), "black")
        draw = ImageDraw.Draw(image)

        for column in range(self.columns):
            x = column * self.column_width
            head_y = int(self.drops[column])
            trail = self.trail_lengths[column]

            for index in range(trail):
                y = head_y - index * self.font_size
                if y < -self.font_size or y >= self.height:
                    continue
                char = random.choice(self.characters)
                fade = max(0, 255 - index * int(255 / max(1, trail)))
                if index == 0:
                    fill = (220, 255, 220)
                else:
                    fill = (0, fade, max(25, fade // 3))
                draw.text((x, y), char, font=self.font, fill=fill)

            self.drops[column] += self.speeds[column]
            if self.drops[column] - trail * self.font_size > self.height:
                self.drops[column] = random.randint(-self.height, 0)
                self.speeds[column] = random.uniform(2.0, 5.5)
                self.trail_lengths[column] = random.randint(7, 18)

        return image


configure_logging()
