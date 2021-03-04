# mqttinterface.py -- Interface to MQTT for the Water Bot
# EPIC Robotsz, dlb, Mar 2021

import paho.mqtt.client as mqtt
import time

#defaults for the water bot
default_broker_url = "10.0.5.1"
default_broker_port = 1883

class MqttInterface():

    def __init__(self, broker_url=default_broker_url, broker_port=default_broker_port):
        self._broker_url = broker_url
        self._broker_port = broker_port
        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.connect_async(self._broker_url, self._broker_port, keepalive=20)
        self._client.loop_start()
        self._last_connect_tme = 0
        self._last_rx_time = 0
        self._last_tx_time = 0
        self._rx_msg_count = 0
        self._tx_msg_count = 0
        self._connect_count = 0
        self._err_count = 0

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connect_count += 1
            self._last_connect_tme = time.monotonic()
        else: self._err_count += 1

    def _on_message(self, client, userdata, message):
        self._last_rx_time = time.monotonic()
        self._rx_msg_count += 1

    def is_connected(self):
        ''' Returns true if the MQTT client is connected. '''
        return self._client.is_connected()

    def time_since_last_rx(self):
        ''' Returns the number of seconds since the last message
            was received, or -1 if no messages have been received. '''
        if self._rx_msg_count == 0: return -1
        return time.monotonic() - self._last_rx_time

    def get_counts(self):
        ''' returns a dict of counts: {rx:, tx:, err:, cc:} where
        rx is the number of messages received, tx the number of messages
        sent, err is the number of errors encounterd, and cc is the
        number of connections and reconnections logged. '''
        d = {"rx": self._rx_msg_count, "tx": self._tx_msg_count, 
            "err": self._err_count, "cc": self._connect_count }
        return d

    def publish(self, topic, data):
        ''' sends data to the broker. Input is the topic (string), and
        the data (string).  If the client is not connected, the data
        is not sent, and False is returned.  Otherwise True is returned
        weither or not the data was actually delivered.'''
        if not self.is_connected(): return False
        self._client.publish(topic=topic, payload=data.encode("ascii"), qos=1, retain=True)
        self._tx_msg_count += 1
        self._last_tx_time = time.monotonic()
        return True

    def close(self):
        ''' Causes the connection to shut down.  Do not use
        this object after calling close(). '''
        self._client.loop_stop()


    



    

