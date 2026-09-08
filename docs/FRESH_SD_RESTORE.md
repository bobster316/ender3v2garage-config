# Fresh SD restore instructions

These instructions rebuild the Raspberry Pi 4 named `ender3v2garage` from this repository after a micro SD card failure.

The repository stores configuration and local display/LED code. It does not store passwords, generated Python virtual environments, runtime logs, G-code, STL files, or a full disk image.

## Hardware and saved state

- Raspberry Pi 4
- Hostname: `ender3v2garage`
- Last known IP: `192.168.1.214`
- Required Linux user: `pi`
- Printer stack: Klipper, Moonraker, Mainsail
- Main printer config: `/home/pi/printer_data/config/printer.cfg`
- NeoPixel ring: 12 LEDs, BCM18 / physical pin 12, brightness `0.09`
- OLED display: SPI display using `/home/pi/LCD_Module_RPI_code`
- LED SHIM: Pimoroni LED SHIM library over I2C

## What this repo restores

- `/boot/firmware/config.txt` and `/boot/firmware/cmdline.txt`
- `/etc/systemd/system/*.service` files captured from the working Pi
- `/home/pi/printer_data/config/` Klipper/Moonraker/Mainsail/crowsnest/sonar config files
- `/home/pi/neopixel-control/` NeoPixel ring animation
- `/home/pi/matrix-pi/` LED SHIM display project files
- `/home/pi/matrix-pi-legacy-test/` active OLED display boot/matrix code
- `/home/pi/LCD_Module_RPI_code/` LCD driver library
- `/home/pi/display_tools/` hardware test scripts
- Package and service manifests under `manifests/`

## What must be installed separately

Start from either MainsailOS or Raspberry Pi OS with Klipper/Moonraker/Mainsail installed. This repository restores configuration and local scripts, but it does not contain the full Klipper, Moonraker, Mainsail, or crowsnest source installations.

If starting from plain Raspberry Pi OS, install Klipper/Moonraker/Mainsail first. KIAUH is the usual route:

```bash
cd ~
sudo apt-get update
sudo apt-get install -y git
git clone https://github.com/dw-0/kiauh.git
./kiauh/kiauh.sh
```

Use KIAUH to install at least:

- Klipper
- Moonraker
- Mainsail
- crowsnest, if camera support is needed

Then return to the restore steps below.

## Step 1: Flash the new micro SD card

Use Raspberry Pi Imager or a similar tool.

Recommended options:

- OS: MainsailOS, or Raspberry Pi OS Lite 64-bit if you will install Klipper/Mainsail manually
- Hostname: `ender3v2garage`
- User: `pi`
- SSH: enabled
- Wi-Fi or Ethernet: configure as needed for your network

Boot the Pi and confirm you can SSH in:

```bash
ssh pi@ender3v2garage.local
```

If mDNS is not working, find the Pi in your router and SSH to its IP address.

## Step 2: Basic OS preparation

Run this on the Pi:

```bash
sudo apt-get update
sudo apt-get install -y git
```

Confirm the `pi` user exists:

```bash
id pi
```

The restore script expects `/home/pi`. If using a different username, create `pi` or edit `scripts/restore.sh` before running it.

## Step 3: Clone this repository

```bash
cd ~
git clone https://github.com/bobster316/ender3v2garage-config.git
cd ender3v2garage-config
```

This is a private repository, so GitHub may ask you to authenticate.

## Step 4: Run the restore script

```bash
sudo bash scripts/restore.sh
```

The script will:

- install GPIO, SPI, I2C, font, and Python dependency packages
- copy boot firmware config into `/boot/firmware`
- copy systemd service units into `/etc/systemd/system`
- copy saved files into `/home/pi`
- recreate `/home/pi/matrix-pi/.venv`
- reinstall LED/OLED/NeoPixel Python libraries
- recreate the Mincho font symlink for `/home/pi/matrix-pi/mincho.ttf`
- set hostname `ender3v2garage`
- reload systemd
- enable Klipper, Moonraker, NeoPixel, OLED, and LED SHIM services

## Step 5: Reboot

```bash
sudo reboot
```

Wait for the Pi to come back online, then reconnect with SSH.

## Step 6: Verify services

```bash
cd ~/ender3v2garage-config
bash scripts/verify.sh
```

Expected key services:

- `klipper-mcu`: enabled and active
- `klipper`: enabled and active, assuming the printer MCU is connected
- `moonraker`: enabled and active
- `neopixel-matrix`: enabled and active
- `matrix-display`: enabled and active
- `ledshim-matrix`: enabled and active

Manual checks:

```bash
systemctl status neopixel-matrix
systemctl status matrix-display
systemctl status ledshim-matrix
systemctl status klipper
systemctl status moonraker
```

## Step 7: Hardware test commands

NeoPixel ring:

```bash
sudo python3 /home/pi/display_tools/test_neopixel_ring.py
```

LED SHIM:

```bash
/home/pi/matrix-pi/.venv/bin/python /home/pi/display_tools/test_ledshim.py
```

OLED display:

```bash
PYTHONPATH=/home/pi/LCD_Module_RPI_code/RaspberryPi/python \
/home/pi/matrix-pi/.venv/bin/python /home/pi/display_tools/test_lcd_1inch69.py
```

## Service mapping

NeoPixel ring:

- service: `/etc/systemd/system/neopixel-matrix.service`
- script: `/home/pi/neopixel-control/matrix_pattern.py`
- pin: `board.D18`, BCM18, physical pin 12
- brightness: `BRIGHTNESS = 0.09`

OLED display:

- service: `/etc/systemd/system/matrix-display.service`
- active script: `/home/pi/matrix-pi-legacy-test/boot_sequence.py`
- working directory: `/home/pi/matrix-pi-legacy-test`
- LCD library path: `/home/pi/LCD_Module_RPI_code/RaspberryPi/python`

LED SHIM:

- service: `/etc/systemd/system/ledshim-matrix.service`
- script: `/home/pi/matrix-pi/ledshim_matrix.py`
- working directory: `/home/pi/matrix-pi`

## Troubleshooting

If the NeoPixel ring does not light:

```bash
systemctl status neopixel-matrix
journalctl -u neopixel-matrix --no-pager -n 80
sudo python3 /home/pi/display_tools/test_neopixel_ring.py
grep -n '^BRIGHTNESS' /home/pi/neopixel-control/matrix_pattern.py
```

Check physical wiring:

- data wire to BCM18 / physical pin 12
- 5V and GND connected
- ring GND common with Raspberry Pi GND
- correct LED direction from data-in side

If the OLED display does not work:

```bash
systemctl status matrix-display
journalctl -u matrix-display --no-pager -n 120
ls /home/pi/LCD_Module_RPI_code/RaspberryPi/python/lib/LCD_1inch69.py
```

Confirm SPI is enabled:

```bash
grep -n 'dtparam=spi=on' /boot/firmware/config.txt
ls /dev/spidev*
```

If LED SHIM does not work:

```bash
systemctl status ledshim-matrix
journalctl -u ledshim-matrix --no-pager -n 120
i2cdetect -y 1
```

Confirm I2C is enabled:

```bash
grep -n 'dtparam=i2c_arm=on' /boot/firmware/config.txt
```

If Klipper cannot connect to the printer MCU:

```bash
systemctl status klipper
journalctl -u klipper --no-pager -n 120
ls -l /dev/serial/by-id/
```

The captured `printer.cfg` is for a Creality 4.2.7 board. If the MCU firmware was lost or changed, rebuild and flash Klipper firmware for that board.

## Updating this repository after future changes

After changing the Pi configuration, update the local repo from the Pi and push a new commit.

From the Windows workspace used to create this repo:

```powershell
cd D:\ender3v2garage\ender3v2garage-config
git status
```

Copy changed files from the Pi into the matching paths, then:

```powershell
git status --short
git add -- <specific files>
git commit -m "Update Raspberry Pi restore configuration"
git push
```

Do not commit:

- Pi passwords
- SSH keys
- GitHub tokens
- runtime logs
- `.venv` directories
- `__pycache__` directories
- large G-code/STL files unless they are intentionally needed for recovery

Before pushing, run:

```powershell
rg -n --hidden --glob '!.git/**' 'REPLACE_WITH_SECRET_PATTERNS'
```

The command should return no matches.
