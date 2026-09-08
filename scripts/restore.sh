#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Run this script with sudo: sudo bash scripts/restore.sh" >&2
    exit 1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! id pi >/dev/null 2>&1; then
    echo "The user 'pi' does not exist. Create it first or adjust this script." >&2
    exit 1
fi

echo "Installing base packages for GPIO, SPI, I2C, display, and LED control..."
apt-get update
apt-get install -y \
    git \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-pil \
    python3-numpy \
    python3-spidev \
    python3-smbus \
    python3-lgpio \
    python3-rpi-lgpio \
    python3-gpiozero \
    i2c-tools \
    gpiod \
    pigpio \
    pigpio-tools \
    pigpiod \
    fonts-ipafont-mincho

echo "Copying boot configuration..."
if [ -d "$repo_root/boot/firmware" ]; then
    mkdir -p /boot/firmware
    cp -a "$repo_root/boot/firmware/." /boot/firmware/
fi

echo "Copying systemd service units..."
mkdir -p /etc/systemd/system
cp -a "$repo_root/etc/systemd/system/." /etc/systemd/system/

echo "Copying pi home configuration and source files..."
mkdir -p /home/pi
cp -a "$repo_root/home/pi/." /home/pi/
chown -R pi:pi /home/pi/neopixel-control /home/pi/display_tools /home/pi/matrix-pi /home/pi/matrix-pi-legacy-test /home/pi/LCD_Module_RPI_code /home/pi/printer_data

echo "Creating LED/display Python virtual environment..."
sudo -u pi python3 -m venv /home/pi/matrix-pi/.venv
sudo -u pi /home/pi/matrix-pi/.venv/bin/python -m pip install --upgrade pip wheel

if [ -f /home/pi/matrix-pi/requirements-pi-os.txt ]; then
    sudo -u pi /home/pi/matrix-pi/.venv/bin/python -m pip install -r /home/pi/matrix-pi/requirements-pi-os.txt
fi

sudo -u pi /home/pi/matrix-pi/.venv/bin/python -m pip install \
    adafruit-blinka \
    adafruit-circuitpython-neopixel \
    rpi-ws281x \
    ledshim \
    pillow \
    psutil \
    spidev \
    gpiozero \
    rpi-lgpio \
    lgpio \
    numpy

if [ -f /usr/share/fonts/opentype/ipafont-mincho/ipam.ttf ]; then
    ln -sf /usr/share/fonts/opentype/ipafont-mincho/ipam.ttf /home/pi/matrix-pi/mincho.ttf
    chown -h pi:pi /home/pi/matrix-pi/mincho.ttf
fi

echo "Installing system Python NeoPixel dependencies..."
python3 -m pip install --break-system-packages \
    adafruit-blinka \
    adafruit-circuitpython-neopixel \
    rpi-ws281x || \
python3 -m pip install \
    adafruit-blinka \
    adafruit-circuitpython-neopixel \
    rpi-ws281x

echo "Setting hostname..."
# Set your printer's hostname here, or run:  PRINTER_HOSTNAME=myhost ./restore.sh
hostnamectl set-hostname "${PRINTER_HOSTNAME:-mainsail}" || true

echo "Reloading and enabling services..."
systemctl daemon-reload
systemctl enable klipper-mcu.service klipper.service moonraker.service || true
systemctl enable neopixel-matrix.service matrix-display.service ledshim-matrix.service
systemctl enable crowsnest.service sonar.service || true

echo "Restore complete. Reboot with: sudo reboot"
