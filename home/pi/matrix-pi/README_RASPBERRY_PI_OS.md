# Matrix Pi Display on Raspberry Pi OS

## Overview

This project runs two independent visual components on standard Raspberry Pi OS:

- A 1.69 inch 240x280 ST7789V3 / LCD_1inch69 display that shows system stats, then Matrix-style digital rain.
- An optional Pimoroni LED SHIM animation that runs green Matrix-style moving pulses.

It does not integrate with Klipper, Mainsail, Moonraker, OctoPrint, or any printer control system.

## Required Hardware

- Raspberry Pi running Raspberry Pi OS
- 1.69 inch 240x280 ST7789V3 / LCD_1inch69 display
- Optional Pimoroni LED SHIM
- LCD driver folder from the display vendor, expected by default at:

```bash
~/LCD_Module_RPI_code/RaspberryPi/python
```

## Folder Layout

- `boot_sequence.py` - starts the LCD, shows stats for 20 seconds, then runs Matrix rain.
- `matrix.py` - `StatsDisplay` and `MatrixDisplay` rendering logic.
- `test_lcd.py` - first LCD hardware validation test.
- `ledshim_matrix.py` - optional LED SHIM Matrix animation.
- `requirements-pi-os.txt` - portable Python package list for Raspberry Pi OS.
- `setup_font.sh` - installs Mincho fonts and creates `./mincho.ttf`.
- `install_raspberry_pi_os.sh` - installs Raspberry Pi OS dependencies and creates `.venv`.
- `matrix-display.service.template` - LCD systemd service template.
- `ledshim-matrix.service.template` - LED SHIM systemd service template.
- `install_service.sh` - installs and enables the LCD systemd service without starting it.
- `install_ledshim_service.sh` - installs and enables the LED SHIM systemd service without starting it.
- `matrix-display.log` - LCD app log file created at runtime.
- `ledshim-matrix.log` - LED SHIM app log file created at runtime.

## Copy Project to Pi

From the local project directory, copy the files to:

```bash
pi@<hostname>.local:~/matrix-pi
```

Use `rsync` where available:

```bash
rsync -av --exclude .venv --exclude __pycache__ --exclude backup-originals ./ pi@<hostname>.local:~/matrix-pi/
```

## Install Dependencies

On the Raspberry Pi:

```bash
cd ~/matrix-pi
chmod +x install_raspberry_pi_os.sh setup_font.sh install_service.sh install_ledshim_service.sh
./install_raspberry_pi_os.sh
```

## Verify the Mincho Font

```bash
ls -la ./mincho.ttf
fc-match "IPAMincho"
```

## Test LCD

Run the hardware test before running the full LCD app:

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

## Run LCD App Manually

After `test_lcd.py` works:

```bash
python boot_sequence.py
```

The display should show system stats first, then Matrix rain.

## Test LED SHIM Manually

The LED SHIM is optional and independent from the LCD display:

```bash
python ledshim_matrix.py
```

If the `ledshim` module is missing, this command exits with a clear message and the LCD app remains unaffected.

## Install and Start LCD Service

Only install/start the service after manual LCD testing works:

```bash
./install_service.sh
sudo systemctl start matrix-display.service
```

## Install and Start LED SHIM Service

Only install/start the service after manual LED SHIM testing works:

```bash
./install_ledshim_service.sh
sudo systemctl start ledshim-matrix.service
```

## Check LCD Logs

```bash
sudo journalctl -u matrix-display.service -f
```

The app also writes:

```bash
./matrix-display.log
```

## Check LED SHIM Logs

```bash
sudo journalctl -u ledshim-matrix.service -f
```

The app also writes:

```bash
./ledshim-matrix.log
```

## Stop or Restart LCD

```bash
sudo systemctl stop matrix-display.service
sudo systemctl restart matrix-display.service
```

## Stop or Restart LED SHIM

```bash
sudo systemctl stop ledshim-matrix.service
sudo systemctl restart ledshim-matrix.service
```

## Disable Old LED SHIM Rainbow Service

The old rainbow service is not used by this project. If it exists:

```bash
sudo systemctl disable --now ledshim-rainbow.service || true
```

## Blank LCD Screen Troubleshooting

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

## LED SHIM Troubleshooting

Check the LED SHIM module:

```bash
python -c "import ledshim; print(ledshim.NUM_PIXELS)"
```

If import fails, install the Pimoroni LED SHIM library manually.

Check I2C:

```bash
sudo raspi-config nonint do_i2c 0
```

Run manually:

```bash
python ledshim_matrix.py
```

Check service logs:

```bash
sudo journalctl -u ledshim-matrix.service -f
```

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
