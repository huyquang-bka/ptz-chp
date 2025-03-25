# ptz_controller.py

from onvif import ONVIFCamera
import time
import zeep
from main_app.model.device import Device
from PyQt5.QtCore import QObject
from threading import Thread


class PTZController(QObject):

    def __init__(self):
        super().__init__()

    def setup_device(self, device: Device):
        try:
            username, password, host = device.get_ptz_info()
            port = 80
            print("ptz info", username, password, host)
            self.cam = ONVIFCamera(host, port, username,
                                   password, wsdl_dir="wsdl")
            self.media = self.cam.create_media_service()
            self.ptz = self.cam.create_ptz_service()
            self.profile = self.media.GetProfiles()[0]
            self.host = host
            self.username = username
            self.password = password
            print("ptz controller is ready")

        except Exception as e:
            print(f"ZEEP Fault: {e}")

    def get_status(self):
        try:
            return self.ptz.GetStatus({'ProfileToken': self.profile.token})
        except Exception as e:
            print(f"Error getting status: {e}")
            return None

    def continuous_move(self, pan=0.0, tilt=0.0, zoom=0.0, duration=1):
        try:
            request = self.ptz.create_type('ContinuousMove')
            request.ProfileToken = self.profile.token
            request.Velocity = {
                'PanTilt': {'x': pan, 'y': tilt},
                'Zoom': {'x': zoom}
            }
            self.ptz.ContinuousMove(request)
            time.sleep(duration)
            self.stop()
        except Exception as e:
            print(f"Error in continuous move: {e}")

    def absolute_move(self, pan=0.0, tilt=0.0, zoom=0.0, speed=0.5):
        try:
            request = self.ptz.create_type('AbsoluteMove')
            request.ProfileToken = self.profile.token
            request.Position = {
                'PanTilt': {'x': pan, 'y': tilt},
                'Zoom': {'x': zoom}
            }
            request.Speed = {
                'PanTilt': {'x': speed, 'y': speed},
                'Zoom': {'x': speed}
            }
            self.ptz.AbsoluteMove(request)
        except Exception as e:
            print(f"Error in absolute move: {e}")

    def relative_move(self, pan=0.0, tilt=0.0, zoom=0.0):
        try:
            request = self.ptz.create_type('RelativeMove')
            request.ProfileToken = self.profile.token
            request.Translation = {
                'PanTilt': {'x': pan, 'y': tilt},
                'Zoom': {'x': zoom}
            }
            self.ptz.RelativeMove(request)
        except Exception as e:
            print(f"Error in relative move: {e}")

    def stop(self, pan_tilt=True, zoom=True):
        try:
            request = self.ptz.create_type('Stop')
            request.ProfileToken = self.profile.token
            request.PanTilt = pan_tilt
            request.Zoom = zoom
            self.ptz.Stop(request)
        except Exception as e:
            print(f"Error stopping camera: {e}")

    def get_presets(self):
        try:
            return self.ptz.GetPresets({'ProfileToken': self.profile.token})
        except Exception as e:
            print(f"Error getting presets: {e}")
            return []

    def save_preset(self, preset_name):
        """Save current position as a preset with the given name"""
        try:
            request = self.ptz.create_type('SetPreset')
            request.ProfileToken = self.profile.token
            request.PresetName = preset_name
            response = self.ptz.SetPreset(request)
            print(
                f"Preset '{preset_name}' saved with token: {response.PresetToken}")
            return response.PresetToken
        except Exception as e:
            print(f"Error saving preset: {e}")
            return None

    def goto_preset(self, preset_token, speed=0.5):
        try:
            request = self.ptz.create_type('GotoPreset')
            request.ProfileToken = self.profile.token
            request.PresetToken = preset_token
            request.Speed = {
                'PanTilt': {'x': speed, 'y': speed},
                'Zoom': {'x': speed}
            }
            self.ptz.GotoPreset(request)
        except Exception as e:
            print(f"Error going to preset: {e}")

    def tour_presets(self, delay=2, speed=1):
        """Tour through all presets with specified delay and speed"""
        presets = self.get_presets()
        if not presets:
            print("No presets found")
            return

        print(f"Starting preset tour with {len(presets)} presets")
        for i, preset in enumerate(presets):
            preset_name = preset.Name if hasattr(
                preset, 'Name') else f"preset_{i}"
            print(f"Moving to preset {i+1}/{len(presets)}: {preset_name}")
            self.goto_preset(preset.token, speed)

            # Wait for camera to settle at the preset position
            time.sleep(delay)
