from typing import List, Optional
from PyQt5.QtCore import QSettings, QObject, pyqtSignal, QThread, QTimer
from main_app.model.device import Device
from main_app.model.api_route import ApiRoute
from main_app.network.custom_http import CustomHTTPRequest
from main_app.model.main_config import mainConfig


class DeviceWorker(QThread):
    """Worker thread for fetching devices"""

    # Signals
    finished = pyqtSignal(bool, str, list)  # success, error_message, devices

    def __init__(self, timeout=1000):
        super().__init__()
        self.api_route = ApiRoute()
        self.http_client = CustomHTTPRequest(
            self.api_route.base_url,
            self.api_route.additional_route
        )
        self.timeout = timeout
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.handle_timeout)
        self.is_timed_out = False

    def run(self):
        """Run the worker thread"""
        self.is_timed_out = False
        self.timer.start(self.timeout)

        try:
            # Get access token from settings
            settings = QSettings("PTZ-CHP", "UserData")
            access_token = settings.value("access_token", "")
            if not access_token:
                self.timer.stop()
                self.finished.emit(False, "No access token available", [])
                return

            # Set authorization header
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            # Make the request to get devices
            response = self.http_client.get(
                self.api_route.device_route,
                headers=headers,
                timeout=self.timeout
            )
            # Stop the timer
            self.timer.stop()

            # Check if timed out
            if self.is_timed_out:
                return

            # Check response status
            if response.status_code == 200:
                # Parse response data
                response_data = response.json()["data"]

                # Emit signal with devices
                devices = []
                for device_json in response_data.get("data", []):
                    device = Device()
                    device.from_json(device_json)
                    if device.deviceFunctionId != mainConfig.ptz_id_function:
                        continue
                    devices.append(device)
                self.finished.emit(True, "", devices)
            else:
                # Handle failed request
                error_message = f"Failed to fetch devices: {response.status_code}"

                # Try to get more specific error message from response
                try:
                    error_data = response.json()
                    if "error_description" in error_data:
                        error_message = error_data["error_description"]
                    elif "message" in error_data:
                        error_message = error_data["message"]
                except:
                    # If we can't parse the error, use the default message
                    pass

                self.finished.emit(False, error_message, [])

        except Exception as e:
            # Stop the timer
            self.timer.stop()

            # Check if timed out
            if self.is_timed_out:
                return

            self.finished.emit(False, str(e), [])

    def handle_timeout(self):
        """Handle timeout"""
        self.is_timed_out = True
        self.finished.emit(False, "Request timed out after 5 seconds", [])
        self.terminate()


class DeviceService(QObject):
    """Service class for device-related operations"""

    # Signal emitted when devices are loaded
    devices_loaded = pyqtSignal(list)

    # Signal emitted when device loading fails
    devices_loading_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Store devices
        self.devices: List[Device] = []

        # Worker thread
        self.worker = None

    def fetch_devices(self):
        """Fetch devices from the API in a background thread"""
        # Create and start worker thread
        self.worker = DeviceWorker()
        self.worker.finished.connect(self.on_fetch_completed)
        self.worker.start()

    def on_fetch_completed(self, success: bool, error_message: str, devices: List[Device]):
        """Handle fetch completion

        Args:
            success (bool): Whether the fetch was successful
            error_message (str): Error message if not successful
            devices (List[Device]): List of devices if successful
        """
        if success:
            # Store devices
            self.devices = devices
            # Emit signal with devices
            self.devices_loaded.emit(self.devices)
        else:
            # Emit signal with error message
            self.devices_loading_failed.emit(error_message)

    def get_devices(self) -> List[Device]:
        """Get the list of devices

        Returns:
            List[Device]: List of devices
        """
        return self.devices

    def get_device_by_id(self, device_id: int) -> Optional[Device]:
        """Get a device by its ID

        Args:
            device_id (int): The ID of the device to find

        Returns:
            Optional[Device]: The device if found, None otherwise
        """
        for device in self.devices:
            if device.id == device_id:
                return device
        return None

    def get_device_names(self) -> List[str]:
        """Get a list of device names for dropdown

        Returns:
            List[str]: List of device names
        """
        return [device.name for device in self.devices]
