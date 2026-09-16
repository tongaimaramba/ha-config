import subprocess
import time
import bluetooth
import logging
from logging.handlers import TimedRotatingFileHandler

# Set up logger
logger = logging.getLogger(__name__)  
logger.setLevel(logging.INFO)

# Log file handler with weekly rotation
handler = TimedRotatingFileHandler("/home/pi/py_apps/logs/hci_monitor.log", when="W0", backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_hci_devices():
    output = subprocess.check_output(["hciconfig"]).decode()
    devices = []
    for line in output.splitlines():
        if line.startswith("hci"):
            devices.append(line.split(":")[0].strip())
    logger.info("HCI devices found: %s", devices)
    return devices

def check_name_requests(device):
    try:
        bluetooth.lookup_name(device, timeout=5)
        return True
    except bluetooth.BluetoothError:
        return False

while True:
    devices = get_hci_devices()
    for device in devices:
        if not check_name_requests(device):
            logger.info("HCI device %s restarted due to failed name requests", device)
            subprocess.call(["sudo", "hciconfig", device, "down"])
            subprocess.call(["sudo", "hciconfig", device, "up"])
    time.sleep(60)