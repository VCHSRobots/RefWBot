# test_joystick.py -- Test getting joystick input.
# EPIC Robotz, dlb, Feb 2021

import paho.mqtt.client as mqtt
import sys
import xpwm

broker_url = "10.0.5.1"
broker_port = 1883

buttons = [False, False, False, False, False, False, False, False, False, False, False, False]
joy_xyz = [0.0, 0.0, 0.0]
joy_ruv = [0.0, 0.0, 0.0]
heartbeat = 0
heartbeat_age = 0
xpwm.board_init()

def on_connect(client, userdata, flags, rc):
    print("Connected to broker. Code: " + str(rc))

def on_disconnect(client, userdata, flags, rc):
    print("Disconnected from broker. Code: " + rc)
    sys.exit()

ncnt = 19
def on_message(client, userdata, msg):
    global ncnt
    ncnt += 1
    if ncnt == 20:
      print("Msgs Received (%d) [%s] = %s" % (ncnt, msg.topic, msg.payload.decode()))
      ncnt = 0
    if msg.topic == "WBot/Joystick/xyz":
        rot = float(msg.payload.decode().split()[0])
        rot = (rot + 1.0) / 2.0
        xpwm.set_servo(11, rot)
        speed = float(msg.payload.decode().split()[1])  # speed between -1 and 1
        if speed <= 0:
          xpwm.set_servo(15, 0.0)
        else:
          xpwm.set_servo(15, speed)


mqtt_client = mqtt.Client()
mqtt_client.connect(broker_url, broker_port)
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_message = on_message
mqtt_client.subscribe("WBot/Joystick/Buttons", qos=1)
mqtt_client.subscribe("WBot/Joystick/xyz", qos=1)
mqtt_client.subscribe("WBot/Joystick/ruv", qos=1)
#mqtt_client.subscribe("WBot/Heartbeat", qos=1)
xpwm.set_servo(15, 0.0)
mqtt_client.loop_forever()
