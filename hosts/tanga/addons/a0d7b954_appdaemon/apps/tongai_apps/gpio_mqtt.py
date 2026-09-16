#!/usr/bin/env python3
# script to reboot the nuki node via mqtt by controlling GPIO Pin 4, the Enable pin
import paho.mqtt.client as mqtt
#import logging
#import logging.handlers
from time import sleep, time
from gpiozero import  LED, Button, PWMLED, MotionSensor
import os
import sys

nuki_en_pin = LED(4,initial_value=True)
reboot_sleep = 1
mqtt_broker_host = "192.168.179.41"
mqtt_broker_un = "<redacted>"
mqtt_broker_pw = "<redacted>"
topic = "/rpi/gpio/"


def run_gpio(func):

   if func == "nuki_reboot":
      nuki_en_pin.off()
      sleep(reboot_sleep)
      nuki_en_pin.on()
      response = "GPIO-MQTT: nukihub reboot success"
   elif func == "nuki_off":
      nuki_en_pin.off()
      response = "GPIO-MQTT: nukihub off success"
   elif func == "nuki_on":
      nuki_en_pin.on()
      response = "GPIO-MQTT: nukihub on success"
   elif func == "test":
      response = "GPIO-MQTT:kumbaya"
   else:
      response = "GPIO-MQTT: Function not recognised [payload was " + func + "]. Nothing done."

   return response

def on_connect(mqttc, obj, flags, rc):
    TOPIC = topic + "#"
    mqttc.subscribe(TOPIC, 0) # Subscribing in on_connect() means that if we lose the connection and reconnect then su$

def on_message(mqttc, obj, msg):
    if msg.topic == topic:
       action = str(msg.payload, 'utf-8')
       if not action.startswith("GPIO-MQTT"):
          result = run_gpio(action)
          mqttc.publish(topic, payload=result, qos=0, retain=False)
#           logger.info("Status from LED action: " + str(paylod))

def on_publish(mqttc, obj, mid):
   1
#    logger.info("mid: " + str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
   online_msg = "GPIO-MQTT: succesfully subscribed to this topic"
   mqttc.publish(topic, payload=online_msg, qos=0, retain=False)
#    logger.info("Subscribed: " + str(mid) + " " + str(granted_qos))


mqttc = mqtt.Client()						#create a client instance
mqttc.username_pw_set(mqtt_broker_un, password=mqtt_broker_pw)	#provide broker un and pw
mqttc.connect(mqtt_broker_host)					#connect to broker via ip address

mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message

mqttc.loop_forever()
