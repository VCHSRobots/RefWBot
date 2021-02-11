# test_joystick.py -- Test getting joystick input.
# dlb Feb 2021

import paho.mqtt.client as mqtt
import sys
import lib.xpwm as xpwm

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

def on_message(client, userdata, msg):
    print("Msg Received [%s] = %s" % (msg.topic, msg.payload.decode()))
    if msg.topic == "WBot/Joystick/xyz":
        rot = float(msg.payload.decode().split()[0])
        rot = (rot + 1.0) / 2.0
        xpwm.set_servo(11, rot)


mqtt_client = mqtt.Client()
mqtt_client.connect(broker_url, broker_port)
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_message = on_message
mqtt_client.subscribe("WBot/Joystick/Buttons", qos=1)
mqtt_client.subscribe("WBot/Joystick/xyz", qos=1)
mqtt_client.subscribe("WBot/Joystick/ruv", qos=1)
#mqtt_client.subscribe("WBot/Heartbeat", qos=1)
mqtt_client.loop_forever()
