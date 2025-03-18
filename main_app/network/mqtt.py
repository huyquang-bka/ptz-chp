import paho.mqtt.client as mqtt
from PyQt5.QtCore import pyqtSignal, QThread
import time
from uuid import uuid4
import json
import base64


class MQTTClient(QThread):
    message_signal = pyqtSignal(dict)

    def __init__(self, broker, port, username=None, password=None):
        super().__init__()
        self.broker = broker
        self.port = port
        self.topic = "container"
        self.username = username
        self.password = password
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=str(
            uuid4()), clean_session=False, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_connect_fail = self.on_connect_fail
        self.client.on_disconnect = self.on_disconnect

    def login(self):
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.broker, self.port)

    def start(self):
        try:
            self.login()
            self.client.loop_start()
        except Exception as e:
            print("Failed to start MQTT client:", e)

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("Connected to MQTT Broker!")
            self.client.subscribe(self.topic)
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        # decode base64
        message = base64.b64decode(message).decode()
        message_json = json.loads(message)
        self.message_signal.emit(message_json)
        print("Received message: ", message_json)

    def on_connect_fail(self, client, userdata, rc):
        print(f"Failed to connect to MQTT Broker, reconnecting... ({rc})")
        time.sleep(1)
        try:
            self.login()
        except Exception as e:
            print("Reconnect failed:", e)

    def on_disconnect(self, *args):
        print("Unexpected disconnection. Reconnecting...")
        try:
            time.sleep(1)
            self.login()
        except Exception as e:
            print("Reconnect failed:", e)

    def publish(self, topic, message):
        try:
            result = self.client.publish(topic, message, retain=False)
            result.wait_for_publish()
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                return 1
            else:
                return 0
        except Exception as e:
            print("Failed to publish message:", e)
            return 0

    def publish_json(self, topic, data):
        message = json.dumps(data)
        return self.publish(topic, message)

    def run(self):
        self.start()

    def __del__(self):
        self.stop()
