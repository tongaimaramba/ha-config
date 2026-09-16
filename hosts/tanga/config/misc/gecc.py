#!/usr/bin/env python3
# [by Claude] script to enable an esp32 to trigger commands on the Pi via gpio pins

import logging
import logging.handlers
import asyncio
import os
import sys
import alias as al
from gpiozero import Button
from signal import SIGINT, SIGTERM, signal

# Set the log file path
log_file_path = os.path.join('/home/pi/py_apps/logs', 'gpio_esp_cmd.log')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=1024 * 1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# GPIO pin setup
three = Button(23,pull_up=False,bounce_time=2)
four = Button(24,pull_up=False,bounce_time=2)

# State management
rpi_state = {
    "running": True,
    "rebooting": False,
    "wlan0_restarting": False
}

async def gpio_event_handler():
    while True:
        try:
            if three.is_pressed:
                await handle_gpio_event(23)
            elif four.is_pressed:
                await handle_gpio_event(24)
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in GPIO event handler: {e}")

async def handle_gpio_event(gpio_pin):
    try:
        logger.info(f"GPIO{gpio_pin} pressed")
        if gpio_pin == 23:
            #await al.run_cmd_async("rbtn")
            rpi_state["rebooting"] = True
            logger.info("Rebooting Raspberry Pi")
        elif gpio_pin == 24:
            #await al.run_cmd_async("nw")
            rpi_state["wlan0_restarting"] = True
            logger.info("Restarting WLAN0")
    except Exception as e:
        logger.error(f"Error executing command for GPIO{gpio_pin}: {e}")

async def main():
    logger.info("Script started")

    asyncio.create_task(gpio_event_handler())

    while True:
        if not rpi_state["running"]:
            logger.info("Raspberry Pi is not running, exiting script")
            break

        if rpi_state["rebooting"]:
            # Wait for the reboot to complete, then update the state
            await asyncio.sleep(60)  # Adjust this value as needed
            rpi_state["rebooting"] = False
            rpi_state["running"] = True
            logger.info("Raspberry Pi reboot completed")

        if rpi_state["wlan0_restarting"]:
            # Wait for the WLAN0 restart to complete, then update the state
            await asyncio.sleep(15)  # Adjust this value as needed
            rpi_state["wlan0_restarting"] = False
            logger.info("WLAN0 restart completed")

        await asyncio.sleep(1)

def handle_signals(signum, frame):
    logger.info("Received signal %d, exiting script", signum)
    rpi_state["running"] = False
    sys.exit(0)

if __name__ == "__main__":
    signal(SIGINT, handle_signals)
    signal(SIGTERM, handle_signals)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, exiting script")
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        sys.exit(1)