import time
from PyQt5.QtCore import QThread, pyqtSignal
from main_app.model.device import Device
import cv2
from queue import Queue
from ..model.main_config import mainConfig
from ..network.mqtt import MQTTClient
import uuid
from ..network.custom_http import CustomHTTPRequest
from ..model.api_route import ApiRoute


class EventThread(QThread):
    sig_capturing = pyqtSignal(bool)

    def __init__(self, parent=None, event_capture_queue: Queue = None):
        self.__thread_running = False
        super().__init__(parent)
        self.__device = None
        self.event_capture_queue = event_capture_queue
        self.api_route = ApiRoute()
        self.http_client = CustomHTTPRequest(
            base_url=self.api_route.base_url,
            additional_route=self.api_route.additional_route,
            refresh_token_endpoint=self.api_route.login_route
        )
        self.init_mqtt_client()

    def init_mqtt_client(self):
        self.mqtt_client = MQTTClient(
            mainConfig.mqtt_broker,
            mainConfig.mqtt_port,
            mainConfig.mqtt_username,
            mainConfig.mqtt_password
        )
        self.mqtt_client.start()
        print("MQTT client started")

    def on_device_selected(self, device: Device):
        self.__device = device
        print("Event thread device selected", self.__device.checkPointId)

    def run(self):
        self.__thread_running = True
        print("Event thread started")
        while self.__thread_running:
            if self.event_capture_queue.empty():
                self.msleep(100)
                continue
            frame = self.event_capture_queue.get()
            # self.sig_capturing.emit(True)
            try:
                # Save image and get the path from server
                image_path = self.save_image_to_server(frame)

                # Prepare MQTT message
                message = {
                    "checkPointId": self.__device.checkPointId,
                    "imagePaths": [image_path]
                }
                print("MQTT message", message)
                # Publish to MQTT
                self.mqtt_client.publish_json(
                    "Event/ptz",
                    message
                )

            except Exception as e:
                print(f"Error processing event: {e}")
                # Still save locally as backup
            # self.sig_capturing.emit(False)

    def save_image_to_server(self, frame):
        """
        Save image to server and get the path
        Returns: str - The image path from server
        """
        try:
            # Convert frame to jpg bytes
            _, img_encoded = cv2.imencode('.jpg', frame)
            fn = str(uuid.uuid4())
            files = {
                'file': (fn + '.jpg', img_encoded.tobytes(), 'image/jpeg')
            }

            # Make POST request to save image
            response = self.http_client.post(
                endpoint=self.api_route.save_image_route,
                data=None,
                headers=None,
                file=files,
                timeout=10
            )

            if response.status_code == 200:
                # Return the image path from response
                return response.text.strip()
            else:
                raise Exception(
                    f"Failed to save image: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"Error saving image to server: {e}")
            raise

    def stop(self):
        self.__thread_running = False
        if hasattr(self, 'mqtt_client'):
            self.mqtt_client.stop()
