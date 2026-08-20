#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "Installing Raspberry Pi OS dependencies..."
sudo apt update
sudo apt install -y \
  python3 \
  python3-pip \
  python3-venv \
  python3-lgpio \
  python3-pil \
  python3-psutil \
  python3-spidev \
  git \
  fonts-dejavu-core \
  fontconfig \
  raspi-config

echo "Enabling SPI and I2C..."
sudo raspi-config nonint do_spi 0 || true
sudo raspi-config nonint do_i2c 0 || true

echo "Loading kernel modules..."
sudo modprobe spidev || true
sudo modprobe i2c-dev || true
sudo modprobe i2c-bcm2835 || true

echo "Persisting module loading..."
echo spidev | sudo tee /etc/modules-load.d/spi.conf
printf "i2c-dev\ni2c-bcm2835\n" | sudo tee /etc/modules-load.d/i2c.conf

chmod +x setup_font.sh
./setup_font.sh

echo "Creating Python virtual environment..."
python3 -m venv .venv

echo "Installing Python packages into .venv..."
.venv/bin/python -m pip install --upgrade pip wheel setuptools
.venv/bin/python -m pip install -r requirements-pi-os.txt
.venv/bin/python -m pip install ledshim || echo "WARNING: ledshim pip install failed. LED SHIM support is optional. Install Pimoroni LED SHIM library manually if needed."

echo
echo "Install complete. Next commands:"
echo "  source .venv/bin/activate"
echo "  python test_lcd.py"
echo "  python boot_sequence.py"
echo "  python ledshim_matrix.py"
