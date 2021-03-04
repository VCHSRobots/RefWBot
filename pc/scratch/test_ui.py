# test_ui.py -- Test UI with Joystick and MQTT For first real control program...
# EPIC Robotz, dlb, Feb 2021

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkbox
import joystick as joystick
import threading
import time
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker. Code: " + rc)

broker_url = "10.0.5.1"
broker_port = 1883
mqtt_client = mqtt.Client()
mqtt_client.connect(broker_url, broker_port)
mqtt_client.loop_start()

if joystick.openGamepad(): joy_status = "Joystick Detected."

# -------------------------------------------------
# Background task...
bg_count = 0
bg_quit = False
last_btns = [ ]
last_xyz = [ ]
last_ruv = [ ]
def run_joystick_com():
    global bg_count, last_btns, last_xyz, last_ruv
    while True:
        btns = joystick.getGamepadButtons()
        xyz = joystick.getGamepadAxis()
        ruv = joystick.getGamepadRot()
        # send out joystick values to robot here...
        if last_btns != btns:
            last_btns = btns
            s = ""
            for i in btns:
                if i: s += "T " 
                else: s += "F "
            mqtt_client.publish(topic="WBot/Joystick/Buttons", payload=s.encode("ascii"), qos=1, retain=True)
        if last_xyz != xyz:
            last_xyz = xyz
            s = "%7.4f %7.4f %7.4f" % xyz
            mqtt_client.publish(topic="WBot/Joystick/xyz", payload=s.encode("ascii"), qos=1, retain=True)
        if last_ruv != ruv:
            last_ruv = ruv
            s = "%7.4f %7.4f %7.4f" % ruv
            mqtt_client.publish(topic="WBot/Joystick/ruv", payload=s.encode("ascii"), qos=1, retain=True)
        bg_count += 1
        time.sleep(0.015)
        if bg_quit: return

def start_background_tasks():
    bg = threading.Thread(target=run_joystick_com, name="background-joystick")
    bg.start()

joy_status = "No Joystick Detected."
joy_buttons = "Buttons: F F F F F F F F F F F F"
joy_x = "X:  0.000"
joy_y = "Y:  0.000"
joy_z = "Z:  0.000"
joy_r = "X:  0.000"
joy_u = "Y:  0.000"
joy_v = "Z:  0.000"

if joystick.openGamepad(): joy_status = "Joystick Detected."

win1 = tk.Tk()
win1.title("Driver Station for WBot")
win1.geometry('1200x600')
frame_main = tk.Frame(win1)
frame_main.pack(side=tk.LEFT)
frame_joy = tk.Frame(win1)
frame_joy.pack(side=tk.RIGHT)
slider_x = ttk.Progressbar(frame_joy, orient=tk.VERTICAL, length=300, mode='determinate')
slider_x.pack(side=tk.LEFT, padx=5)
slider_y = ttk.Progressbar(frame_joy, orient=tk.VERTICAL, length=300, mode='determinate')
slider_y.pack(side=tk.LEFT, padx=5)
frame_status = tk.Frame(frame_main)
frame_status.pack()
lbl_status = tk.Label(frame_status, text=joy_status, font=("Arial Bold", 30))
lbl_status.pack()
frame_buttons = tk.Frame(frame_main)
frame_buttons.pack()
lbl_btns = tk.Label(frame_buttons, text=joy_buttons, font=("Arial Bold", 30), width=40)
lbl_btns.pack()
frame_cnt = tk.Frame(frame_main)
frame_cnt.pack()
lbl_cnt = tk.Label(frame_cnt, text="update: %d" % bg_count, font=("Arial Bold", 18))
lbl_cnt.pack()
frame_xyz = tk.Frame(frame_main)
frame_xyz.pack()
lbl_x = tk.Label(frame_xyz, text=joy_x, font=("Arial Bold", 24))
lbl_x.grid(column=0, row=0)
lbl_y = tk.Label(frame_xyz, text=joy_y, font=("Arial Bold", 24))
lbl_y.grid(column=1, row=0)
lbl_z = tk.Label(frame_xyz, text=joy_z, font=("Arial Bold", 24))
lbl_z.grid(column=2, row=0)
frame_ruv = tk.Frame(frame_main)
frame_ruv.pack()
lbl_r = tk.Label(frame_ruv, text=joy_r, font=("Arial Bold", 24))
lbl_r.grid(column=0, row=0)
lbl_u = tk.Label(frame_ruv, text=joy_u, font=("Arial Bold", 24))
lbl_u.grid(column=1, row=0)
lbl_v = tk.Label(frame_ruv, text=joy_v, font=("Arial Bold", 24))
lbl_v.grid(column=2, row=0)


def update_joy_sliders():
    x,y,z = joystick.getGamepadAxis()
    ix = (x + 1) * 50
    iy = (y + 1) * 50
    slider_x['value'] = ix
    slider_y['value'] = iy
    
def update_status():
    lbl_cnt.configure(text="update: %d" % bg_count)
    if not joystick.haveGamepad(): return
    btns = joystick.getGamepadButtons()
    xyz = joystick.getGamepadAxis()
    ruv = joystick.getGamepadRot()
    joy_buttons = "Buttons: "
    bcount = 0
    for b in btns:
        bcount += 1
        if bcount > 12: break
        if b: joy_buttons += " T"
        else: joy_buttons += " F"
    joy_x = "X: %6.3f" % xyz[0]
    joy_y = "Y: %6.3f" % xyz[1]
    joy_z = "Z: %6.3f" % xyz[2]
    joy_r = "R: %6.3f" % ruv[0]
    joy_u = "U: %6.3f" % ruv[1]
    joy_v = "V: %6.3f" % ruv[2]
    lbl_btns.configure(text=joy_buttons)
    lbl_x.configure(text=joy_x)
    lbl_y.configure(text=joy_y)
    lbl_z.configure(text=joy_z)
    lbl_r.configure(text=joy_r)
    lbl_u.configure(text=joy_u)
    lbl_v.configure(text=joy_v)
    update_joy_sliders()
    win1.after(100, update_status)

def show_msg():
    ans = tkbox.askquestion(title="Idiots -- question", message="Are you an idiot?")
    print(ans)
    ans = tkbox.askokcancel(title="Idiots -- okcancel", message="Are you an idiot?")
    print(ans)
    ans = tkbox.askretrycancel(title="Idiots -- retrycancel", message="Are you an idiot?")
    print(ans)
    ans = tkbox.askyesno(title="Idiots -- yesno", message="Are you an idiot?")
    print(ans)
    ans = tkbox.askyesnocancel(title="Idiots -- yesnotcancel", message="Are you an idiot?")
    print(ans)

frame_control = tk.Frame(frame_main)
frame_control.pack()
btn1 = tk.Button(frame_control, text="Update", command=update_status, font=("Arial Bold", 24), width=6, height=1)
btn1.grid(column=0, row=0, padx=20, pady=20)
btn2 = tk.Button(frame_control, text="Test", command=show_msg, font=("Arial Bold", 24), width=6, height=1)
btn2.grid(column=1, row=0, padx=20, pady=20)

start_background_tasks()
update_status()
win1.after(100, update_status)
win1.mainloop()

#shutdown the background.
bg_quit = True
mqtt_client.loop_stop()

