# Ender3V2 Garage Raspberry Pi configuration

Snapshot date: 2026-08-20

This repository stores the rebuild configuration for the Raspberry Pi at:

- Hostname: `ender3v2garage`
- Last known IP: `192.168.1.214`
- Hardware: Raspberry Pi 4 running Klipper/Mainsail

The repository is intended to recover from a failed or corrupted micro SD card. It includes the active display and LED configuration, Klipper/Mainsail configuration files, boot GPIO/SPI/I2C settings, systemd units, and package manifests captured from the working Pi.

## Included

- `boot/firmware/`
  - Raspberry Pi boot config files, including SPI/I2C/audio/GPIO related settings.
- `etc/systemd/system/`
  - Saved service units for Klipper, Moonraker, crowsnest, sonar, OLED display, LED SHIM, and NeoPixel ring.
- `home/pi/printer_data/config/`
  - Klipper, Moonraker, Mainsail, crowsnest, sonar, and historical `.cfg`/`.conf` config files.
- `home/pi/neopixel-control/`
  - NeoPixel 12 LED ring animation, currently using BCM18 / physical pin 12 with `BRIGHTNESS = 0.09`.
- `home/pi/matrix-pi/`
  - LED SHIM animation source and setup files.
- `home/pi/matrix-pi-legacy-test/`
  - OLED display boot/matrix animation source.
- `home/pi/LCD_Module_RPI_code/`
  - LCD driver library used by the OLED display scripts.
- `home/pi/display_tools/`
  - Hardware test helpers for LCD, LED SHIM, and NeoPixel ring.
- `manifests/`
  - System package list, Python package freeze files, service status, and host/kernel metadata.

## Not included

This repo deliberately excludes runtime logs, Python virtual environments, Python bytecode caches, G-code files, STL files, and passwords.

## Fresh SD restore

Use the full restore guide:

[docs/FRESH_SD_RESTORE.md](docs/FRESH_SD_RESTORE.md)

Short version: start with a fresh Raspberry Pi OS or MainsailOS image, make sure the user `pi` exists, install/confirm Klipper and Moonraker, clone this repo on the new Pi, then run:

```bash
cd ender3v2garage-config
sudo bash scripts/restore.sh
```

After the script finishes, reboot:

```bash
sudo reboot
```

After reboot, verify:

```bash
bash scripts/verify.sh
```

## Manual service checks

```bash
systemctl status neopixel-matrix
systemctl status matrix-display
systemctl status ledshim-matrix
systemctl status klipper
systemctl status moonraker
```

## Notes

- The NeoPixel ring is driven by `/home/pi/neopixel-control/matrix_pattern.py`.
- The OLED service runs `/home/pi/matrix-pi-legacy-test/boot_sequence.py`.
- The LED SHIM service runs `/home/pi/matrix-pi/ledshim_matrix.py`.
- The active service files are under `/etc/systemd/system/`.
- If the printer MCU firmware also needs reflashing, use the Klipper firmware build process for the Creality 4.2.7 board described in `home/pi/printer_data/config/printer.cfg`.
- After future configuration changes, see `docs/FRESH_SD_RESTORE.md#updating-this-repository-after-future-changes`.
