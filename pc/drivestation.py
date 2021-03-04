# drivestation.py -- Drive Station Program for Reference Water Bot
# Epic Robotz, dlb, Mar 2021

import sys
import tkinter as tk
import tkinter.font as tkFont
import mqttinterface as mi 
import gameclockwidget
import joystickwidget
import joystick
import threading
import time

title = "EPIC ROBOTZ"
teamname = "Reference Bot"

if joystick.openGamepad(): joy_status = "Joystick Detected."

class DriveStation(tk.Frame):

    def __init__(self, parent, enable_mqtt=True):
        tk.Frame.__init__(self, parent)
        if enable_mqtt: self.mqtt = mi.MqttInterface()
        else: self.mqtt = None
        self.titlefont = tkFont.Font(family="Copperplate Gothic Bold", size=24)
        self.namefont = tkFont.Font(family="Copperplate Gothic Light", size=20)
        self.titlelabel = tk.Label(self, text=title, anchor="center", font=self.titlefont)
        self.namelabel = tk.Label(self, text=teamname, anchor="center", font=self.namefont)
        self.gameclock = gameclockwidget.GameClockWidget(self)
        self.joystick = joystickwidget.JoystickWidget(self)

        #self.titlelabel.pack(side="top", fill="x", padx=4, pady=4)
        #self.namelabel.pack(side="top", padx=4, pady=4)
        #self.gameclock.pack(side="top", padx=4, pady=4)
        #self.joystick.pack(side="top", padx=4, pady=4)
        
        y = 5
        self.titlelabel.place(x=0, y=y, width=300, height=30)
        y += 30
        self.namelabel.place(x=0, y=y, width=300, height=30)
        y += 40
        w, h = self.gameclock.get_size()
        self.gameclock.place(x=25, y=y, width=w, height=h)
        y += h + 10
        w, h = self.joystick.get_size()
        self.joystick.place(x=25, y=y, width=w, height=h)
        y += h + 10
        self.quitbackgroundtasks = False
        self.bg_count = 0
        self.last_btns = []
        self.last_xyz = []
        self.last_ruv = []
      
    def background_joystick(self):
        while True:
            btns = joystick.getGamepadButtons()
            xyz = joystick.getGamepadAxis()
            ruv = joystick.getGamepadRot()
            self.joystick.set_axis(*xyz)
            self.joystick.set_ruv(*ruv)
            self.joystick.set_buttons(*btns)
            #self.joystick.set_mode("invalid")
            if self.mqtt:
                # send out joystick values to robot here...
                if self.last_btns != btns:
                    self.last_btns = btns
                    s = ""
                    for i in btns:
                        if i: s += "T " 
                        else: s += "F "
                    self.mqtt.publish("WBot/Joystick/Buttons", s)
                if self.last_xyz != xyz:
                    self.last_xyz = xyz
                    s = "%7.4f %7.4f %7.4f" % tuple(xyz)
                    self.mqtt.publish("WBot/Joystick/xyz", s)
                if self.last_ruv != ruv:
                    self.last_ruv = ruv
                    s = "%7.4f %7.4f %7.4f" % tuple(ruv)
                    self.mqtt.publish("WBot/Joystick/ruv", s)
            self.bg_count += 1
            # if self.bg_count % 100 == 0: print("Background Loop: %d." % self.bg_count)
            if self.quitbackgroundtasks: 
              print("Quitting the joystick thread.")
              return
            time.sleep(0.015)
    
    def start_background(self):
        self.bgid = threading.Thread(target=self.background_joystick, name="background-joystick")
        self.bgid.daemon = True  # KLUGH -- Should not need this!  Bug in the shutdown code for this program.
        self.bgid.start()

    def stop_all(self):
        self.quitbackgroundtasks = True
        if self.mqtt: 
            if self.mqtt.is_connected(): self.mqtt.close()

if __name__ == "__main__":
    enable_mqtt = True
    for a in sys.argv[1:]:
      if a == "nomqtt":
        print("MQTT disabled.")
        enable_mqtt = False

    root = tk.Tk()
    root.title("Driver Station for Water Bot")
    root.geometry('300x900')
    ds = DriveStation(root, enable_mqtt=enable_mqtt)
    ds.place(x=0, y=0, relwidth=1, relheight=1)
    ds.start_background()
    root.mainloop()
    ds.stop_all()
