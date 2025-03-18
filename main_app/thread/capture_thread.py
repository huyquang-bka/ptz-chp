import time
from PyQt5.QtCore import QThread
from main_app.model.device import Device
import cv2
from queue import Queue


class CaptureThread(QThread):
    def __init__(self, parent=None, capture_queue: Queue = None):
        self.__thread_running = False
        super().__init__(parent)
        self.__device = None
        self.cap = None
        self.capture_queue = capture_queue

    def on_device_selected(self, device: Device):
        self.__device = device

    def init_capture(self):
        try:
            print("init_capture", self.__device.devicePath)
            self.cap = cv2.VideoCapture(self.__device.devicePath)
        except Exception as e:
            print("Error initializing capture", e)

    def run(self):
        self.__thread_running = True
        print("Capture thread started")
        self.init_capture()
        fps = 0
        old_time = time.time()
        while self.__thread_running:
            if self.cap is None:
                self.msleep(1000)
                self.init_capture()
                continue
            if time.time() - old_time > 1:
                print(f"FPS: {fps}")
                fps = 0
                old_time = time.time()
            ret, frame = self.cap.read()
            if not ret:
                print("Error capturing frame")
                time.sleep(1)
                self.init_capture()
                continue
            fps += 1
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if self.capture_queue.empty():
                self.capture_queue.put(rgb_image)
            self.msleep(10)

    def stop(self):
        pass
