# drivestation.py -- Drive Station Program for Reference Water Bot
# Epic Robotz, dlb, Mar 2021

import sys
import tkinter as tk
import tkinter.font as tkFont
import gameclockwidget
import joystickwidget
import joystick
import threading
import time
import paho.mqtt.client as mqtt

title = "EPIC ROBOTZ"
teamname = "Reference Bot"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker. Code: " + rc)

broker_url = "10.0.5.1"
broker_port = 1883

if joystick.openGamepad(): joy_status = "Joystick Detected."

class DriveStation(tk.Frame):

    def __init__(self, parent, mqtt_client):
        tk.Frame.__init__(self, parent)
        self.mqtt_client = mqtt_client
        self.titlefont = tkFont.Font(family="Copperplate Gothic Bold", size=28)
        self.namefont = tkFont.Font(family="Copperplate Gothic Light", size=22)
        self.titlelabel = tk.Label(self, text=title, anchor="center", font=self.titlefont)
        self.namelabel = tk.Label(self, text=teamname, anchor="center", font=self.namefont)
        self.gameclock = gameclockwidget.GameClockWidget(self)
        self.joystick = joystickwidget.JoystickWidget(self)

        self.titlelabel.pack(side="top", fill="x", padx=4, pady=4)
        self.namelabel.pack(side="top", fill="x", padx=4, pady=4)
        self.gameclock.pack(side="top", fill="x", padx=4, pady=4)
        self.joystick.pack(side="top", fill="x", padx=4, pady=4)
        self.quit = False
        self.bg_count = 0
        self.last_btns = []
        self.last_xyz = []
        self.last_ruv = []
      
    def background_joystick(self):
        global joystick_quit
        while True:
            btns = joystick.getGamepadButtons()
            xyz = joystick.getGamepadAxis()
            ruv = joystick.getGamepadRot()
            self.joystick.setaxis(*xyz)
            if self.mqtt_client:
                # send out joystick values to robot here...
                if self.last_btns != btns:
                    self.last_btns = btns
                    s = ""
                    for i in btns:
                        if i: s += "T " 
                        else: s += "F "
                    mqtt_client.publish(topic="WBot/Joystick/Buttons", payload=s.encode("ascii"), qos=1, retain=True)
                if self.last_xyz != xyz:
                    self.last_xyz = xyz
                    s = "%7.4f %7.4f %7.4f" % xyz
                    mqtt_client.publish(topic="WBot/Joystick/xyz", payload=s.encode("ascii"), qos=1, retain=True)
                if last_ruv != ruv:
                    self.last_ruv = ruv
                    s = "%7.4f %7.4f %7.4f" % ruv
                    mqtt_client.publish(topic="WBot/Joystick/ruv", payload=s.encode("ascii"), qos=1, retain=True)
            self.bg_count += 1
            # if self.bg_count % 100 == 0: print("Background Loop: %d." % self.bg_count)
            if self.quit: 
              print("Quitting the joystick thread.")
              return
            time.sleep(0.015)
    
    def start_background(self):
        self.bgid = threading.Thread(target=self.background_joystick, name="background-joystick")
        self.bgid.daemon = True  # KLUGH -- Should not need this!  Bug in the shutdown code for this program.
        self.bgid.start()

    def stop_all(self):
        global joystick_quit
        self.quit = True
    
if __name__ == "__main__":
    enable_mqtt = True
    for a in sys.argv[1:]:
      if a == "nomqtt":
        print("MQTT disabled.")
        enable_mqtt = False

    if enable_mqtt:
      mqtt_client = mqtt.Client()
      mqtt_client.connect(broker_url, broker_port)
      mqtt_client.loop_start()
    else: 
      mqtt_client = None

    root = tk.Tk()
    root.title("Driver Station for Water Bot")
    root.geometry('300x900')
    ds = DriveStation(root, mqtt_client)
    ds.place(x=0, y=0, relwidth=1, relheight=1)
    ds.start_background()
    root.mainloop()
    ds.stop_all()
    if mqtt_client:
      mqtt_client.loop_stop()