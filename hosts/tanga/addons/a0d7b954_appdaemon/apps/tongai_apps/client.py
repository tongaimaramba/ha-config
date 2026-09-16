import adbase as ad
from datetime import datetime, timedelta, timezone, time
from time import sleep
import traceback
import requests
import socket

class ClientApp(ad.ADBase):
#
#####
#
    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")
        self.access = self.adbase.get_app("guest_access")
        self.au = self.adbase.get_app("auto_unlock")
        
        self.adbase.log("\n\n************\n*\n* Welcome to Test App\n*\n************\n") #Launch message
        
        HOST = '192.168.179.63'  # The server's hostname or IP address
        PORT = 65432        # The port used by the server

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'Hello, world')
            while True:
                data = s.recv(1024)
                self.adbase.log(f"Message from server:\n {repr(data)}")
            