import subprocess
import time
import select
from evdev import InputDevice, list_devices
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

INACTIVITY_TIMEOUT = 60  # 1 minute in seconds
last_activity_time = time.time()
current_display = None
stats_process = None
matrix_process = None

def find_input_devices():
    devices = [InputDevice(path) for path in list_devices()]
    return [dev for dev in devices if dev.name.lower().find('mouse') != -1 or dev.name.lower().find('keyboard') != -1]

input_devices = find_input_devices()
logging.info(f"Found input devices: {[dev.name for dev in input_devices]}")

def on_activity():
    global last_activity_time
    last_activity_time = time.time()
    logging.info("Activity detected")

def switch_to_stats():
    global current_display, stats_process, matrix_process
    if current_display != 'stats':
        logging.info("Switching to stats display")
        if matrix_process:
            matrix_process.terminate()
            matrix_process = None
        stats_process = subprocess.Popen(['python3', 'stats.py'])
        current_display = 'stats'

def switch_to_matrix():
    global current_display, stats_process, matrix_process
    if current_display != 'matrix':
        logging.info("Switching to matrix screensaver")
        if stats_process:
            stats_process.terminate()
            stats_process = None
        matrix_process = subprocess.Popen(['python3', 'matrix.py'])
        current_display = 'matrix'

# Start with stats display
switch_to_stats()

try:
    while True:
        start_time = time.time()
        r, w, x = select.select(input_devices, [], [], 0.1)
        for dev in r:
            try:
                for event in dev.read():
                    on_activity()
                    if current_display == 'matrix':
                        switch_to_stats()
            except IOError:
                pass

        current_time = time.time()
        time_since_last_activity = current_time - last_activity_time

        if time_since_last_activity > INACTIVITY_TIMEOUT:
            if current_display != 'matrix':
                logging.info(f"Inactivity timeout reached. Time since last activity: {time_since_last_activity:.2f} seconds")
                switch_to_matrix()
        elif current_display != 'stats':
            switch_to_stats()

        # Precise sleep to maintain 1-second intervals
        time_to_sleep = 1 - (time.time() - start_time)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)

except KeyboardInterrupt:
    logging.info("Exiting...")
finally:
    # Clean up
    if stats_process:
        stats_process.terminate()
    if matrix_process:
        matrix_process.terminate()
    logging.info("Processes terminated")
