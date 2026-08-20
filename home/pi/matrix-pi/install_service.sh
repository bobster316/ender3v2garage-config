#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$PROJECT_DIR/.venv/bin/python"
TEMPLATE="$PROJECT_DIR/matrix-display.service.template"
SERVICE_FILE="/etc/systemd/system/matrix-display.service"

if [ ! -x "$PYTHON" ]; then
  echo "ERROR: Python virtual environment not found at: $PYTHON"
  echo "Run ./install_raspberry_pi_os.sh first."
  exit 1
fi

if [ ! -f "$TEMPLATE" ]; then
  echo "ERROR: Missing service template: $TEMPLATE"
  exit 1
fi

TMP_FILE="$(mktemp)"
sed \
  -e "s#__PROJECT_DIR__#$PROJECT_DIR#g" \
  -e "s#__PYTHON__#$PYTHON#g" \
  "$TEMPLATE" > "$TMP_FILE"

echo "Installing systemd service to $SERVICE_FILE"
sudo cp "$TMP_FILE" "$SERVICE_FILE"
rm -f "$TMP_FILE"

sudo systemctl daemon-reload
sudo systemctl enable matrix-display.service

echo
echo "Service installed and enabled. It was not started automatically."
echo "Start and inspect it manually after LCD testing succeeds:"
echo "  sudo systemctl start matrix-display.service"
echo "  sudo systemctl status matrix-display.service"
echo "  sudo journalctl -u matrix-display.service -f"
