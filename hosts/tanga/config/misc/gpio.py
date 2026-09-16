#!/usr/bin/env python3
# script to enable an esp32 to trigger commands on the Pi via gpio pins
import paho.mqtt.client as mqtt
#import logging
#import logging.handlers
from time import sleep, time
from gpiozero import  LED, Button, PWMLED, MotionSensor
import os
import sys
import alias as al

four = Button(4)
five = Button(5)

def esp_cmd(func):

   if func == "four":
      al.run_cmd("au") #rbtn")
      response = "Rebooting RPI"
   elif func == "five":
      al.run_cmd("myconf") # nw")
      response = "Restarting WLAN0"
   else:
      response = "GPIO-CMD: Command ** "+func+" ** not recognised. Nothing done."
   print(response)
   
four.when_pressed = esp_cmd
five.when_pressed = esp_cmd

