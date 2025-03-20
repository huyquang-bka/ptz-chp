import time
from PyQt5.QtCore import QThread
from main_app.model.device import Device
import cv2
from queue import Queue


class EventThread(QThread):
    def __init__(self, parent=None, event_capture_queue: Queue = None):
        self.__thread_running = False
        super().__init__(parent)
        self.__device = None
        self.event_capture_queue = event_capture_queue

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
            cv2.imwrite(
                f"event_{self.__device.checkPointId}_{time.strftime('%Y%m%d_%H%M%S')}.jpg", frame)

    def stop(self):
        pass
