#!/usr/bin/env python3
from time import sleep, time
import os
import sys
import bluetooth
import paho.mqtt.client as mqtt
import subprocess
import argparse
#import logging
#from logging.handlers import TimedRotatingFileHandler

def cmd_help():

  help = """***
nw: restart wlan0
au: check all unlock processes are running
myname: check for last name request for my phone
myconf: check for last mqtt message for confidence that was sent for my phone
anyname and anyconf: see myname and myconf
whichpi: ip and name of this pi device
***"""

  print(f"This script can run alias commands as follows:\n{help}")


def select_command(ip):
  alias = {
    'ls':("ls -la",(0,5)),
    'au':("ps axo user,pid,ppid,command -H -U root | grep -E -w 'PID|led2\.py|1\s+.+gpio_mqtt\.py|1\s+.+monitor\.sh' | grep -v -w grep",(8,16,21)),
    'myname':("journalctl -u monitor -r | grep -m1 '\[CMD-NAME\]\s\+1C:F8:D0:42:2E:7C'",(7,8,11,12)),
    'myconf':("journalctl -u monitor -r | grep -m1 'MQTT\]\s\+monitor\/frontdoor\/tongai'",(7,8,11,16)),
    'anyname':("journalctl -u monitor -r | grep -m1 CMD-NAME",(7,8,11,12)),
    'anyconf':("journalctl -u monitor -r | grep -m1 MQTT",(7,8,11,16)),
    'whichpi':("more  ~/*_pi.info",(1,3)),
    'rbtn':("sudo reboot now",(0,1)),
    'nw':("sudo python ~/py_apps/util/nw.py -i wlan0",(0,5))
  }
 # print(f"ip: {ip}")

  Command = alias[ip]
  return Command

def run_sub(command):
 # print(f"Running ** {command} **")
  res = subprocess.run(command, shell=True,capture_output=True)
  result = res.stdout.decode("utf-8")
  rez=result.split()
  return rez

def run_cmd(input):
  ipt = input if input else "help"
  op=[]  
  cmd = select_command(ipt)
  result = run_sub(cmd[0])

  if ipt == "help":
    print(f"Help note:\n{cmd[0]}")
    return cmd[0]
  else:
    if len(cmd[1]) > 0:
        for i in cmd[1]:
          op.append(result[i])
        print(f"Result for {ipt}: {op}")
        return op
    else:
        print(f"Result for {ipt}: Done - no output.")
        return "Done - no output"

async def run_cmd_async(input):
  ipt = input if input else "help"
  op=[]  
  cmd = select_command(ipt)
  result = run_sub(cmd[0])

  if ipt == "help":
    print(f"Help note:\n{cmd[0]}")
    return cmd[0]
  else:
    for i in cmd[1]:
      op.append(result[i])
    print(f"Result for {ipt}: {op}")
    return op
