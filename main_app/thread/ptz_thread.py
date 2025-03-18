from PyQt5.QtCore import QThread, pyqtSignal
from main_app.controller.ptz_controller import PTZController
from main_app.model.device import Device
from main_app.service.preset_service import PresetService


class PTZThread(QThread):
    # Add a new signal for presets loaded
    presets_loaded = pyqtSignal(list)

    def __init__(self):
        self.__thread_running = False
        self.ptz_controller = PTZController()
        self.device = None
        self.is_changed = False
        self.code = "stop"
        self.preset_service = PresetService()
        self.movement_speed = 5  # Default speed (matches slider default)
        self.default_per_move = 0.5
        super().__init__()

    def on_device_selected(self, device: Device):
        print("device selected in ptz thread", device)
        self.is_changed = self.device != device
        print("is changed", self.is_changed)
        if self.is_changed:
            self.device = device
            # Fetch presets for the new device
            self.fetch_presets()

    # Modified method to fetch presets from JSON file
    def fetch_presets(self):
        if self.device:
            # Get presets from the preset service
            presets_data = self.preset_service.get_presets(self.device.id)

            # Convert to a format compatible with the existing UI
            presets = []
            for preset_data in presets_data:
                # Create a simple object with the necessary attributes
                class PresetObj:
                    pass

                preset = PresetObj()
                preset.token = preset_data["token"]
                preset.Name = preset_data["Name"]
                preset.position = preset_data.get("position", {})

                presets.append(preset)

            # Emit the presets
            self.presets_loaded.emit(presets)
            return presets
        return []

    # Modified method to go to a preset
    def goto_preset(self, preset_token):
        if self.device:
            # Get the preset data
            presets_data = self.preset_service.get_presets(self.device.id)
            for preset_data in presets_data:
                if preset_data["token"] == preset_token:
                    # If position data is available, use it
                    position = preset_data.get("position")
                    if position and hasattr(self.ptz_controller, 'absolute_move'):
                        # Extract position values with defaults
                        pan = position.get("pan", 0.0)
                        tilt = position.get("tilt", 0.0)
                        zoom = position.get("zoom", 0.0)

                        # Convert slider value (1-7) to a speed value (0.1-1.0)
                        speed = min(1.0, max(0.1, self.movement_speed / 5.0))

                        # Move to the position using current speed setting
                        self.ptz_controller.absolute_move(
                            pan, tilt, zoom, speed)
                        return True

                    # Fallback to camera's preset if position data is not available
                    elif hasattr(self.ptz_controller, 'goto_preset'):
                        # Convert slider value (1-7) to a speed value (0.1-1.0)
                        speed = min(1.0, max(0.1, self.movement_speed / 5.0))
                        self.ptz_controller.goto_preset(preset_token, speed)
                        return True
        return False

    # Modified method to save a preset
    def save_preset(self, preset_name):
        if self.device:
            # Get current position if possible
            position = None
            if hasattr(self.ptz_controller, 'get_status'):
                status = self.ptz_controller.get_status()
                if status and hasattr(status, 'Position'):
                    position = {
                        "pan": status.Position.PanTilt.x,
                        "tilt": status.Position.PanTilt.y,
                        "zoom": status.Position.Zoom.x
                    }

            # Save the preset
            preset_token = self.preset_service.save_preset(
                self.device.id, preset_name, position
            )

            # Also save to camera if supported
            if hasattr(self.ptz_controller, 'save_preset'):
                try:
                    self.ptz_controller.save_preset(preset_name)
                except Exception as e:
                    print(f"Warning: Could not save preset to camera: {e}")

            return preset_token
        return None

    # Modified method to delete a preset
    def delete_preset(self, preset_token):
        if self.device:
            # Delete from JSON file
            success = self.preset_service.delete_preset(
                self.device.id, preset_token)

            # Also delete from camera if supported
            if hasattr(self.ptz_controller, 'remove_preset'):
                try:
                    self.ptz_controller.remove_preset(preset_token)
                except Exception as e:
                    print(f"Warning: Could not delete preset from camera: {e}")

            return success
        return False

    # Add method to update a preset name
    def update_preset_name(self, preset_token, new_name):
        if self.device:
            return self.preset_service.update_preset(
                self.device.id, preset_token, preset_name=new_name
            )
        return False

    def move_up(self):
        self.code = "up"

    def move_down(self):
        self.code = "down"

    def move_left(self):
        self.code = "left"

    def move_right(self):
        self.code = "right"

    def zoom_in(self):
        self.code = "zoom_in"

    def zoom_out(self):
        self.code = "zoom_out"

    def stop(self):
        self.code = "stop"
        self.ptz_controller.stop()

    def set_movement_speed(self, speed):
        """Set the movement speed (1 to 10)"""
        self.movement_speed = speed

    def run(self):
        self.__thread_running = True
        while self.__thread_running:
            if self.is_changed:
                self.ptz_controller.setup_device(self.device)
                self.is_changed = False

            # Calculate speed-adjusted movement values
            # Convert slider value (1-7) to a movement multiplier
            # Lower values for more precise/slower movement, higher for faster
            speed_factor = self.movement_speed / 5.0  # This gives a range of 0.1 to 1.0

            if self.code == "up":
                self.ptz_controller.continuous_move(
                    0, self.default_per_move * speed_factor, 0)
            elif self.code == "down":
                self.ptz_controller.continuous_move(
                    0, -self.default_per_move * speed_factor, 0)
            elif self.code == "left":
                self.ptz_controller.continuous_move(
                    -self.default_per_move * speed_factor, 0, 0)
            elif self.code == "right":
                self.ptz_controller.continuous_move(
                    self.default_per_move * speed_factor, 0, 0)
            elif self.code == "zoom_in":
                self.ptz_controller.continuous_move(
                    0, 0, self.default_per_move * speed_factor)
            elif self.code == "zoom_out":
                self.ptz_controller.continuous_move(
                    0, 0, -self.default_per_move * speed_factor)

            self.msleep(10)
