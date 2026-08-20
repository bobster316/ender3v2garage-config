#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "Installing Mincho font package..."
sudo apt update
sudo apt install -y fonts-ipafont-mincho fonts-dejavu-core fontconfig

echo "Refreshing font cache..."
fc-cache -f || true

FONT_PATH=""

if [ -f "/usr/share/fonts/opentype/ipafont-mincho/ipam.ttf" ]; then
  FONT_PATH="/usr/share/fonts/opentype/ipafont-mincho/ipam.ttf"
else
  FONT_PATH="$(find /usr/share/fonts -type f \( -iname "*mincho*.ttf" -o -iname "*mincho*.otf" -o -iname "ipam.ttf" \) | head -n 1 || true)"
fi

if [ -z "$FONT_PATH" ]; then
  echo "ERROR: Could not find a Mincho font after installing fonts-ipafont-mincho."
  echo "Try: sudo apt install fonts-ipafont fonts-ipaexfont-mincho fonts-noto-cjk"
  exit 1
fi

ln -sf "$FONT_PATH" "$PROJECT_DIR/mincho.ttf"

echo "Mincho font ready:"
echo "$PROJECT_DIR/mincho.ttf -> $FONT_PATH"
ls -la "$PROJECT_DIR/mincho.ttf"
