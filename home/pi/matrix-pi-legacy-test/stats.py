#!/usr/bin/python
import os
import sys
import time
import logging
import subprocess
import psutil
import netifaces
import shutil
from PIL import Image, ImageDraw, ImageFont
from gpiozero import CPUTemperature

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Possible paths for the LCD module
possible_paths = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LCD_Module_RPI_code', 'RaspberryPi', 'python'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'),
    '/home/pi/LCD_Module_RPI_code/RaspberryPi/python',
    '/home/pi/display_controller/LCD_Module_RPI_code/RaspberryPi/python'
]

LCD_1inch69 = None
for path in possible_paths:
    sys.path.append(path)
    try:
        from lib import LCD_1inch69
        logging.info(f"Successfully imported LCD_1inch69 from {path}")
        break
    except ImportError:
        continue

if LCD_1inch69 is None:
    logging.error("Unable to import LCD_1inch69 module. Please ensure the module is installed correctly.")
    print("Error: Unable to import LCD_1inch69 module.")
    print("Please make sure the LCD_Module_RPI_code folder is in one of the following locations:")
    for path in possible_paths:
        print(f"- {path}")
    sys.exit(1)

# Raspberry Pi pin configuration
RST = 17
DC = 25
BL = 18
bus = 0
device = 0

# Display dimensions
WIDTH = 240
HEIGHT = 280

# Initialize display with error handling
try:
    disp = LCD_1inch69.LCD_1inch69(rst=RST, dc=DC, bl=BL)
    disp.Init()
    disp.clear()
    disp.bl_DutyCycle(50)
except Exception as e:
    logging.error(f"Error initializing display: {e}")
    print(f"Error initializing display: {e}")
    print("Please check your GPIO connections and permissions.")
    sys.exit(1)

# Load the fonts
try:
    font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
except IOError:
    logging.warning("Unable to load custom fonts. Using default font.")
    font_large = ImageFont.load_default()
    font = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

def get_system_info():
    try:
        hostname = subprocess.check_output("hostname", shell=True).decode().strip()
        model = subprocess.check_output("cat /proc/device-tree/model", shell=True).decode().strip()
        ram = round(psutil.virtual_memory().total / (1024.0 ** 3), 1)
        os_info = subprocess.check_output("cat /etc/os-release | grep PRETTY_NAME", shell=True).decode().split('"')[1]
        return hostname, model, ram, os_info
    except Exception as e:
        logging.error(f"Error in get_system_info: {str(e)}")
        return "Error", "Error", 0, "Error"

def get_network_info():
    def get_ip_info(interface):
        try:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                ip = addrs[netifaces.AF_INET][0]['addr']
                if not ip.startswith("169.254."):
                    subnet = addrs[netifaces.AF_INET][0]['netmask']
                    gateways = netifaces.gateways()
                    gateway = gateways['default'][netifaces.AF_INET][0] if 'default' in gateways else "N/A"
                    return ip, subnet, gateway
            return None
        except Exception as e:
            logging.error(f"Error getting IP info for {interface}: {str(e)}")
            return None

    wlan_info = get_ip_info('wlan0')
    eth_info = get_ip_info('eth0')

    try:
        ssid = subprocess.check_output("iwgetid -r", shell=True).decode().strip()
    except:
        ssid = "N/A"

    return wlan_info, eth_info, ssid

def get_cpu_info():
    try:
        cpu = CPUTemperature()
        freq = psutil.cpu_freq().current
        temp = cpu.temperature
        load = psutil.cpu_percent(interval=1)
        return freq, temp, load
    except Exception as e:
        logging.error(f"Error in get_cpu_info: {str(e)}")
        return 0, 0, 0

def get_disk_info():
    try:
        sd_total, sd_used, sd_free = shutil.disk_usage("/")
        sd_total_gb = round(sd_total / (2**30), 1)
        sd_free_gb = round(sd_free / (2**30), 1)
        sd_used_gb = round(sd_used / (2**30), 1)

        usb_path = "/media/pi/USB"  # Adjust this path as necessary
        if os.path.ismount(usb_path):
            usb_total, usb_used, usb_free = shutil.disk_usage(usb_path)
            usb_total_gb = round(usb_total / (2**30), 1)
            usb_free_gb = round(usb_free / (2**30), 1)
            usb_used_gb = round(usb_used / (2**30), 1)
            return [("SD", sd_total_gb, sd_used_gb, sd_free_gb),
                    ("USB", usb_total_gb, usb_used_gb, usb_free_gb)]
        else:
            return [("SD", sd_total_gb, sd_used_gb, sd_free_gb)]
    except Exception as e:
        logging.error(f"Error in get_disk_info: {str(e)}")
        return []

def display_system_info(draw):
    hostname, model, ram, os_info = get_system_info()
    draw.text((10, 10), "System Info", font=font_large, fill=WHITE)
    draw.text((10, 50), f"Hostname: {hostname}", font=font, fill=GREEN)
    draw.text((10, 80), f"Model:", font=font, fill=GREEN)
    draw.text((10, 100), f"{model}", font=font_small, fill=GREEN)
    draw.text((10, 140), f"RAM: {ram} GB", font=font, fill=GREEN)
    draw.text((10, 170), f"OS:", font=font, fill=GREEN)
    draw.text((10, 190), f"{os_info}", font=font_small, fill=GREEN)

def display_network_info(draw):
    wlan_info, eth_info, ssid = get_network_info()
    draw.text((10, 10), "Network Info", font=font_large, fill=WHITE)
    draw.text((10, 50), f"SSID: {ssid}", font=font, fill=GREEN)
    y = 80
    if wlan_info:
        wlan_ip, wlan_subnet, wlan_gateway = wlan_info
        draw.text((10, y), f"WLAN IP: {wlan_ip}", font=font, fill=GREEN)
        y += 30
        draw.text((10, y), f"Subnet: {wlan_subnet}", font=font_small, fill=GREEN)
        y += 20
        draw.text((10, y), f"Gateway: {wlan_gateway}", font=font_small, fill=GREEN)
        y += 30
    if eth_info:
        eth_ip, eth_subnet, eth_gateway = eth_info
        draw.text((10, y), f"ETH IP: {eth_ip}", font=font, fill=GREEN)
        y += 30
        draw.text((10, y), f"Subnet: {eth_subnet}", font=font_small, fill=GREEN)
        y += 20
        draw.text((10, y), f"Gateway: {eth_gateway}", font=font_small, fill=GREEN)

def display_cpu_info(draw):
    freq, temp, load = get_cpu_info()
    draw.text((10, 10), "CPU Info", font=font_large, fill=WHITE)
    draw.text((10, 50), f"Frequency: {freq:.0f} MHz", font=font, fill=GREEN)
    draw.text((10, 90), f"Temperature: {temp:.1f}°C", font=font, fill=GREEN)
    draw.text((10, 130), f"Load: {load:.1f}%", font=font, fill=GREEN)

    # Draw CPU load bar
    bar_width = int(load / 100 * (WIDTH - 20))
    draw.rectangle((10, 170, WIDTH - 10, 190), outline=WHITE, fill=BLACK)
    draw.rectangle((10, 170, 10 + bar_width, 190), outline=WHITE, fill=GREEN)

def display_disk_info(draw):
    disk_info = get_disk_info()
    draw.text((10, 10), "Disk Info", font=font_large, fill=WHITE)
    y = 50
    for device, total, used, free in disk_info:
        draw.text((10, y), f"{device} Drive:", font=font, fill=WHITE)
        y += 30
        draw.text((10, y), f"Total: {total:.1f} GB", font=font_small, fill=GREEN)
        y += 20
        draw.text((10, y), f"Used: {used:.1f} GB", font=font_small, fill=GREEN)
        y += 20
        draw.text((10, y), f"Free: {free:.1f} GB", font=font_small, fill=GREEN)
        y += 30

        # Draw disk usage bar
        used_percentage = (used / total) * 100
        bar_width = int(used_percentage / 100 * (WIDTH - 20))
        draw.rectangle((10, y, WIDTH - 10, y + 20), outline=WHITE, fill=BLACK)
        draw.rectangle((10, y, 10 + bar_width, y + 20), outline=WHITE, fill=GREEN)
        y += 40

def main():
    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    display_functions = [
        display_system_info,
        display_network_info,
        display_cpu_info,
        display_disk_info
    ]
    current_display = 0

    try:
        while True:
            draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=BLACK)
            display_functions[current_display](draw)
            disp.ShowImage(image)
            time.sleep(5)  # Display each section for 5 seconds
            current_display = (current_display + 1) % len(display_functions)
    except KeyboardInterrupt:
        logging.info("Exiting...")
        disp.clear()
        disp.module_exit()
        logging.info("Display cleared and module exited.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        disp.module_exit()
