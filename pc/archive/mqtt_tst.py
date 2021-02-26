# A test of basic mqtt message subscribe
# EPIC Robotz, dlb, Feb 2021

import paho.mqtt.client as mqtt

broker_url = "192.168.3.25"
broker_port = 1883

def on_connect(client, userdata, flags, rc):
   print("Connected With Result Code %d" % rc)

def on_message(client, userdata, message):
   print("Message Recieved: " + message.payload.decode())

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_url, broker_port)

client.subscribe("test/msg", qos=1)

client.loop_forever()
