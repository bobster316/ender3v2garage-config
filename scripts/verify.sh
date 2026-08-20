#!/usr/bin/env bash
set -u

services=(
    klipper-mcu
    klipper
    moonraker
    neopixel-matrix
    matrix-display
    ledshim-matrix
)

for service in "${services[@]}"; do
    printf '%-22s enabled=%-8s active=%s\n' \
        "$service" \
        "$(systemctl is-enabled "$service" 2>/dev/null || echo unknown)" \
        "$(systemctl is-active "$service" 2>/dev/null || echo unknown)"
done

echo
echo "NeoPixel brightness:"
grep -n '^BRIGHTNESS' /home/pi/neopixel-control/matrix_pattern.py 2>/dev/null || echo "NeoPixel script not found"

echo
echo "Expected hardware pins:"
echo "- NeoPixel ring: BCM18 / physical pin 12"
echo "- OLED display: SPI display via LCD_Module_RPI_code"
echo "- LED SHIM: Pimoroni LED SHIM library / I2C"

