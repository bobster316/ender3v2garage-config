from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path

from matrix import HEIGHT, WIDTH, LOG_PATH, MatrixDisplay, StatsDisplay

BASE_DIR = Path(__file__).resolve().parent
LCD_DRIVER_PATH = os.environ.get(
    "LCD_DRIVER_PATH",
    str(Path.home() / "LCD_Module_RPI_code/RaspberryPi/python"),
)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )


logger = logging.getLogger("boot_sequence")


def import_lcd_driver():
    driver_path = Path(LCD_DRIVER_PATH).expanduser()
    if driver_path.exists():
        driver_text = str(driver_path)
        if driver_text not in sys.path:
            sys.path.append(driver_text)
        logger.info("Using LCD driver path: %s", driver_path)
    else:
        logger.warning("LCD driver path does not exist: %s", driver_path)

    try:
        from lib import LCD_1inch69  # type: ignore

        return LCD_1inch69
    except Exception as exc:
        message = (
            "Could not import LCD_1inch69.\n"
            f"Attempted LCD driver path: {driver_path}\n"
            f"Path exists: {driver_path.exists()}\n"
            "Expected a driver folder containing: lib/LCD_1inch69.py\n"
            "To override the path, run:\n"
            "  export LCD_DRIVER_PATH=/path/to/LCD_Module_RPI_code/RaspberryPi/python\n"
            "To check the default driver folder, run:\n"
            "  ls -la ~/LCD_Module_RPI_code/RaspberryPi/python\n"
            "  ls -la ~/LCD_Module_RPI_code/RaspberryPi/python/lib"
        )
        logger.exception(message)
        print(message, file=sys.stderr)
        raise SystemExit(1) from exc


def show_image(disp, image) -> None:
    if hasattr(disp, "ShowImage"):
        disp.ShowImage(image)
    elif hasattr(disp, "show_image"):
        disp.show_image(image)
    else:
        raise AttributeError("LCD display object has no ShowImage/show_image method")


def main() -> int:
    configure_logging()
    logger.info("Starting Matrix Pi display from %s", BASE_DIR)

    LCD_1inch69 = import_lcd_driver()

    try:
        disp = LCD_1inch69.LCD_1inch69()
        disp.Init()
        disp.clear()
        if hasattr(disp, "bl_DutyCycle"):
            disp.bl_DutyCycle(80)

        stats = StatsDisplay(WIDTH, HEIGHT)
        matrix = MatrixDisplay(WIDTH, HEIGHT)

        logger.info("Showing stats screen for 20 seconds.")
        end_at = time.monotonic() + 20
        while time.monotonic() < end_at:
            show_image(disp, stats.render())
            time.sleep(1)

        logger.info("Starting Matrix rain loop.")
        while True:
            show_image(disp, matrix.render())
            time.sleep(0.045)

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received; clearing display and exiting.")
        try:
            disp.clear()
        except Exception:
            logger.exception("Failed to clear display during shutdown.")
        return 0
    except Exception:
        logger.exception("Matrix display failed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
