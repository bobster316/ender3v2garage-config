#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "========================================"
echo " Matrix Pi Raspberry Pi OS Installer"
echo " Project: $PROJECT_DIR"
echo "========================================"

echo ""
echo "Creating backup folder..."
BACKUP_DIR="$PROJECT_DIR/install-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

for file in boot_sequence.py matrix.py test_lcd.py ledshim_matrix.py requirements-pi-os.txt; do
  if [ -f "$file" ]; then
    cp "$file" "$BACKUP_DIR/" || true
  fi
done

echo "Backup created at:"
echo "$BACKUP_DIR"

echo ""
echo "Installing Raspberry Pi OS packages..."
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
  fonts-ipafont-mincho \
  fontconfig \
  raspi-config

echo ""
echo "Enabling SPI and I2C..."
sudo raspi-config nonint do_spi 0 || true
sudo raspi-config nonint do_i2c 0 || true

echo ""
echo "Loading SPI/I2C modules..."
sudo modprobe spidev || true
sudo modprobe i2c-dev || true
sudo modprobe i2c-bcm2835 || true

echo ""
echo "Persisting SPI/I2C modules..."
echo spidev | sudo tee /etc/modules-load.d/spi.conf >/dev/null
printf "i2c-dev\ni2c-bcm2835\n" | sudo tee /etc/modules-load.d/i2c.conf >/dev/null

echo ""
echo "Refreshing font cache..."
fc-cache -f || true

echo ""
echo "Setting up Mincho font as ./mincho.ttf..."
FONT_PATH=""

if [ -f "/usr/share/fonts/opentype/ipafont-mincho/ipam.ttf" ]; then
  FONT_PATH="/usr/share/fonts/opentype/ipafont-mincho/ipam.ttf"
else
  FONT_PATH="$(find /usr/share/fonts -type f \( -iname "*mincho*.ttf" -o -iname "*mincho*.otf" -o -iname "ipam.ttf" \) | head -n 1 || true)"
fi

if [ -n "$FONT_PATH" ]; then
  ln -sf "$FONT_PATH" "$PROJECT_DIR/mincho.ttf"
  echo "Mincho font ready:"
  echo "$PROJECT_DIR/mincho.ttf -> $FONT_PATH"
else
  echo "WARNING: Could not find Mincho font."
  echo "Matrix rain may use fallback font."
fi

echo ""
echo "Checking LCD driver path..."
LCD_DRIVER_PATH="${LCD_DRIVER_PATH:-$HOME/LCD_Module_RPI_code/RaspberryPi/python}"

if [ -d "$LCD_DRIVER_PATH" ]; then
  echo "LCD driver path found:"
  echo "$LCD_DRIVER_PATH"
else
  echo "WARNING: LCD driver path not found:"
  echo "$LCD_DRIVER_PATH"
  echo ""
  echo "The LCD scripts expect the Waveshare/LCD_Module_RPI_code driver."
  echo "If the display test fails, install or copy the driver folder to:"
  echo "$HOME/LCD_Module_RPI_code/RaspberryPi/python"
fi

echo ""
echo "Checking SPI devices..."
if ls /dev/spidev* >/dev/null 2>&1; then
  ls -la /dev/spidev*
else
  echo "WARNING: No /dev/spidev* devices found."
  echo "SPI may require a reboot before it appears."
fi

echo ""
echo "Creating Python virtual environment..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
else
  echo ".venv already exists, reusing it."
fi

echo ""
echo "Installing Python packages..."
.venv/bin/python -m pip install --upgrade pip wheel setuptools

if [ -f "requirements-pi-os.txt" ]; then
  .venv/bin/python -m pip install -r requirements-pi-os.txt
else
  echo "requirements-pi-os.txt missing, installing minimal packages..."
  .venv/bin/python -m pip install pillow psutil spidev gpiozero rpi-lgpio lgpio numpy
fi

echo ""
echo "Attempting optional LED SHIM install..."
if .venv/bin/python -m pip install ledshim; then
  echo "LED SHIM Python module installed."
else
  echo "WARNING: ledshim pip install failed."
  echo "LED SHIM is optional. LCD display can still work."
  echo "If needed, install Pimoroni LED SHIM library manually."
fi

echo ""
echo "Making helper scripts executable..."
chmod +x install_raspberry_pi_os.sh 2>/dev/null || true
chmod +x setup_font.sh 2>/dev/null || true
chmod +x install_service.sh 2>/dev/null || true
chmod +x install_ledshim_service.sh 2>/dev/null || true
chmod +x boot_sequence.py 2>/dev/null || true
chmod +x test_lcd.py 2>/dev/null || true
chmod +x ledshim_matrix.py 2>/dev/null || true

echo ""
echo "Disabling old LED SHIM rainbow service if present..."
sudo systemctl disable --now ledshim-rainbow.service 2>/dev/null || true

echo ""
echo "Installing LCD display systemd service..."
if [ -f "matrix-display.service.template" ]; then
  PYTHON="$PROJECT_DIR/.venv/bin/python"
  sed \
    -e "s#__PROJECT_DIR__#$PROJECT_DIR#g" \
    -e "s#__PYTHON__#$PYTHON#g" \
    matrix-display.service.template | sudo tee /etc/systemd/system/matrix-display.service >/dev/null

  sudo systemctl daemon-reload
  sudo systemctl enable matrix-display.service
  echo "LCD service installed and enabled."
else
  echo "WARNING: matrix-display.service.template not found. LCD service not installed."
fi

echo ""
echo "Installing LED SHIM Matrix systemd service..."
if [ -f "ledshim-matrix.service.template" ]; then
  PYTHON="$PROJECT_DIR/.venv/bin/python"
  sed \
    -e "s#__PROJECT_DIR__#$PROJECT_DIR#g" \
    -e "s#__PYTHON__#$PYTHON#g" \
    ledshim-matrix.service.template | sudo tee /etc/systemd/system/ledshim-matrix.service >/dev/null

  sudo systemctl daemon-reload
  sudo systemctl enable ledshim-matrix.service
  echo "LED SHIM Matrix service installed and enabled."
else
  echo "WARNING: ledshim-matrix.service.template not found. LED SHIM service not installed."
fi

echo ""
echo "Running Python syntax check..."
.venv/bin/python -m py_compile boot_sequence.py matrix.py test_lcd.py ledshim_matrix.py

echo ""
echo "========================================"
echo " Install complete"
echo "========================================"
echo ""
echo "IMPORTANT:"
echo "If this is the first time SPI/I2C was enabled, reboot before testing:"
echo ""
echo "  sudo reboot"
echo ""
echo "After reboot, test manually first:"
echo ""
echo "  cd $PROJECT_DIR"
echo "  source .venv/bin/activate"
echo "  python test_lcd.py"
echo "  python boot_sequence.py"
echo ""
echo "To test LED SHIM manually:"
echo ""
echo "  python ledshim_matrix.py"
echo ""
echo "After manual tests pass, start services:"
echo ""
echo "  sudo systemctl start matrix-display.service"
echo "  sudo systemctl status matrix-display.service"
echo ""
echo "  sudo systemctl start ledshim-matrix.service"
echo "  sudo systemctl status ledshim-matrix.service"
echo ""
echo "Logs:"
echo ""
echo "  sudo journalctl -u matrix-display.service -f"
echo "  sudo journalctl -u ledshim-matrix.service -f"
echo ""

