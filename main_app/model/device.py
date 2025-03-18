from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass(init=False)
class Device:
    id: int
    name: str
    devicePath: str
    deviceFunctionId: int
    checkPointId: int

    def from_json(self, json_data: dict):
        for key, value in json_data.items():
            setattr(self, key, value)
        # self.devicePath = "rtsp://admin:Admin%401234@172.34.65.97/live1s1.sdp"
        # self.devicePath = "rtsp://admin:T4123456@192.168.1.233/Streaming/Channels/1"

    def get_ptz_info(self):
        """Extract username, password, and host from RTSP URL (devicePath)"""
        if not self.devicePath or not self.devicePath.startswith("rtsp://"):
            return None, None, None

        try:
            # Parse RTSP URL format: rtsp://username:password@host/path
            url_without_protocol = self.devicePath[7:]  # Remove 'rtsp://'
            auth_host_parts = url_without_protocol.split('@', 1)

            if len(auth_host_parts) != 2:
                return None, None, None

            auth_part, host_part = auth_host_parts
            username_password = auth_part.split(':', 1)

            if len(username_password) != 2:
                return None, None, None

            username, password = username_password

            # Extract host (remove path part)
            host = host_part.split('/', 1)[0]

            # Handle URL-encoded characters
            import urllib.parse
            username = urllib.parse.unquote(username)
            password = urllib.parse.unquote(password)

            return username, password, host
        except Exception:
            return None, None, None


class DeviceResponse:
    """Model class for device API response"""

    def __init__(self, response_data: Dict[str, Any]):
        self.current_page: int = response_data.get('currentPage', 1)
        self.page_size: int = response_data.get('pageSize', 0)
        self.total_rows: int = response_data.get('totalRows', 0)
        data = response_data.get('data', [])
        self.devices: List[Device] = [
            Device(device_data) for device_data in data]
