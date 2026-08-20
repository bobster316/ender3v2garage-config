#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$PROJECT_DIR/.venv/bin/python"
SCRIPT="$PROJECT_DIR/ledshim_matrix.py"
TEMPLATE="$PROJECT_DIR/ledshim-matrix.service.template"
SERVICE_FILE="/etc/systemd/system/ledshim-matrix.service"

if [ ! -x "$PYTHON" ]; then
  echo "ERROR: Python virtual environment not found at: $PYTHON"
  echo "Run ./install_raspberry_pi_os.sh first."
  exit 1
fi

if [ ! -f "$SCRIPT" ]; then
  echo "ERROR: Missing LED SHIM script: $SCRIPT"
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
sudo systemctl enable ledshim-matrix.service

echo
echo "LED SHIM Matrix service installed and enabled. It was not started automatically."
echo "If an old rainbow service exists, disable it with:"
echo "  sudo systemctl disable --now ledshim-rainbow.service || true"
echo
echo "Start and inspect it manually after LED SHIM testing succeeds:"
echo "  sudo systemctl start ledshim-matrix.service"
echo "  sudo systemctl status ledshim-matrix.service"
echo "  sudo journalctl -u ledshim-matrix.service -f"
