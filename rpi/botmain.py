# botmain.py -- top level program for on-board robot
# EPIC Robotz, dlb, Feb 2021
#
# This program should be run when the RPi is powered up.
# It communicates with the hardware and the drive station.
# All control logic decisions pass through this program,
# both in auto and teleoperated modes.  In addition,
# this program presents a UI for either development 
# purposes, or to be VNCed to the driver station to
# aid the driver.

import paho.mqtt.client as mqtt
import sys
import xpwm
import tkinter as tk
import tkinter.ttk as ttk

status_battery = 0.0
status_joyx = 0.0
status_joyy = 0.0

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker. Code: " + rc)

broker_url = "10.0.5.1"
broker_port = 1883
mqtt_client = mqtt.Client()
mqtt_client.connect(broker_url, broker_port)
mqtt_client.loop_start()

win1 = tk.Tk()
win1.title("Robot Main Program on RPi")
win1.geometry('800x400')
frame_main = tk.Frame(win1)
frame_main.pack(side=tk.LEFT)
frame_top = tk.Frame(frame_main)
frame_bot = tk.Frame(frame_main)
frame_top.pack(side=tk.TOP)
frame_bot.pack(side=tk.TOP)
frame_status = tk.Frame(frame_top)
frame_status.pack(side=tk.LEFT)
lbl_bat = tk.Label(frame_status, text="Bat: xx.x", font=("Arial Bold", 20))
lbl_bat.pack(side=tk.TOP)
lbl_joyx = tk.Label(frame_status, text="Joy X: px.xxx", font=("Arial Bold", 20))
lbl_joyy = tk.Label(frame_status, text="Joy Y: px.xxx", font=("Arial Bold", 20))
lbl_joyx.pack(side=tk.TOP)
lbl_joyy.pack(side=tk.TOP)

def update_status():
  lbl_bat.configure(text="Joy X: %6.3f" % status_battery)
  lbl_joyx.configure(text="Joy X: %6.3f" % status_joyx)
  lbl_joyy.configure(text="Joy Y: %6.3f" % status_joyy)
  win1.after(100, update_status)

win1.after(100, update_status)
win1.mainloop()


