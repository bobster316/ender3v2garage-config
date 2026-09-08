# Matrix Pi Display on Raspberry Pi OS

## Overview

This project runs a 1.69 inch 240x280 ST7789V3 / LCD_1inch69 display on standard Raspberry Pi OS. It starts with a system stats screen, then switches to Matrix-style digital rain forever.

It does not integrate with Klipper, Mainsail, Moonraker, OctoPrint, or any printer control system.

## Required Hardware

- Raspberry Pi running Raspberry Pi OS
- 1.69 inch 240x280 ST7789V3 / LCD_1inch69 display
- LCD driver folder from the display vendor, expected by default at:

```bash
~/LCD_Module_RPI_code/RaspberryPi/python
```

## Folder Layout

- `boot_sequence.py` - starts the LCD, shows stats for 20 seconds, then runs Matrix rain.
- `matrix.py` - `StatsDisplay` and `MatrixDisplay` rendering logic.
- `test_lcd.py` - first hardware validation test.
- `requirements-pi-os.txt` - portable Python package list for Raspberry Pi OS.
- `setup_font.sh` - installs Mincho fonts and creates `./mincho.ttf`.
- `install_raspberry_pi_os.sh` - installs Raspberry Pi OS dependencies and creates `.venv`.
- `matrix-display.service.template` - systemd service template.
- `install_service.sh` - installs and enables the systemd service without starting it.
- `matrix-display.log` - local app log file created at runtime.

## Copy Project to Pi

From the local project directory, copy the files to:

```bash
pi@ender3v2garage.local:~/matrix-pi
```

Use `rsync` where available:

```bash
rsync -av --exclude .venv --exclude __pycache__ --exclude backup-originals ./ pi@ender3v2garage.local:~/matrix-pi/
```

## Install Dependencies

On the Raspberry Pi:

```bash
cd ~/matrix-pi
chmod +x install_raspberry_pi_os.sh setup_font.sh install_service.sh
./install_raspberry_pi_os.sh
```

## Verify the Mincho Font

```bash
ls -la ./mincho.ttf
fc-match "IPAMincho"
```

## Test LCD

Run the hardware test before running the full app:

```bash
source .venv/bin/activate
python test_lcd.py
```

You should see a black screen with red, green, blue, and white blocks plus:

```text
LCD TEST
240x280
SPI OK
```

## Run Manually

After `test_lcd.py` works:

```bash
python boot_sequence.py
```

The display should show system stats first, then Matrix rain.

## Install and Start Service

Only install/start the service after manual testing works:

```bash
./install_service.sh
sudo systemctl start matrix-display.service
```

## Check Logs

```bash
sudo journalctl -u matrix-display.service -f
```

The app also writes:

```bash
./matrix-display.log
```

## Stop or Restart

```bash
sudo systemctl stop matrix-display.service
sudo systemctl restart matrix-display.service
```

## Blank Screen Troubleshooting

Check SPI:

```bash
ls /dev/spidev*
```

Check LCD driver folder:

```bash
ls -la ~/LCD_Module_RPI_code/RaspberryPi/python
ls -la ~/LCD_Module_RPI_code/RaspberryPi/python/lib
```

Check Mincho font:

```bash
ls -la ./mincho.ttf
```

Run the LCD test manually:

```bash
source .venv/bin/activate
python test_lcd.py
```

Check service logs:

```bash
sudo journalctl -u matrix-display.service -f
```

If permissions are suspected, try a manual run with `sudo`:

```bash
sudo .venv/bin/python test_lcd.py
sudo .venv/bin/python boot_sequence.py
```

Also check the display wiring, ribbon cable orientation, and backlight connection.

## Set LCD_DRIVER_PATH

If your LCD vendor driver folder is somewhere else:

```bash
export LCD_DRIVER_PATH=/path/to/LCD_Module_RPI_code/RaspberryPi/python
```

Then rerun:

```bash
python test_lcd.py
python boot_sequence.py
```
