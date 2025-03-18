from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QPushButton, QInputDialog, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QFrame
from main_app.view.ui.main_window import Ui_MainWindow
from main_app.model.language_manager import LanguageManager
from main_app.service.device_service import DeviceService
from main_app.model.device import Device
from typing import Dict, Any, List
from main_app.thread.capture_thread import CaptureThread
from main_app.thread.ptz_thread import PTZThread
from queue import Queue
from main_app.view.ui.preset_container_widget import PresetContainerWidget


class MainWindow(QMainWindow):
    sig_device_changed = QtCore.pyqtSignal(Device)

    def __init__(self, user_data: Dict[str, Any]):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Store user data
        self.user_data = user_data

        # Get language manager instance
        self.language_manager = LanguageManager()

        # Connect language manager signal to update UI
        self.language_manager.language_changed.connect(self.update_ui_texts)

        # Initialize device service
        self.device_service = DeviceService()

        # Connect device service signals
        self.device_service.devices_loaded.connect(self.on_devices_loaded)
        self.device_service.devices_loading_failed.connect(
            self.on_devices_loading_failed)

        # Connect UI signals
        self.ui.comboBox_camera.currentIndexChanged.connect(
            self.on_device_selected)

        # Setup preset container
        self.setup_preset_container()

        # Initialize UI with current language
        self.update_ui_texts()

        # init thread
        self.init_thread()
        self.init_signals()

        # Store preset buttons
        self.preset_buttons = {}

        # Connect speed slider to update movement speed
        self.ui.qslider_ptz_speed.valueChanged.connect(self.on_speed_changed)

        # Initialize the PTZ thread with the default speed value
        self.ptz_thread.set_movement_speed(self.ui.qslider_ptz_speed.value())

    def setup_preset_container(self):
        """Set up the preset container"""
        # Create preset container widget
        self.preset_container = PresetContainerWidget()

        # Add to the UI
        self.ui.groupBox.setLayout(QVBoxLayout())
        self.ui.groupBox.layout().addWidget(self.preset_container)

    def init_thread(self):
        # queue
        self.capture_queue = Queue()
        # thread
        self.capture_thread = CaptureThread(capture_queue=self.capture_queue)
        self.ptz_thread = PTZThread()
        # start thread
        self.capture_thread.start()
        self.ptz_thread.start()

    def init_signals(self):
        self.sig_device_changed.connect(self.capture_thread.on_device_selected)
        self.sig_device_changed.connect(self.ptz_thread.on_device_selected)
        # Connect the presets_loaded signal
        self.ptz_thread.presets_loaded.connect(self.on_presets_loaded)
        self.connect_buttons()

    def connect_buttons(self):
        # start moving
        self.ui.btn_up.pressed.connect(self.ptz_thread.move_up)
        self.ui.btn_down.pressed.connect(self.ptz_thread.move_down)
        self.ui.btn_left.pressed.connect(self.ptz_thread.move_left)
        self.ui.btn_right.pressed.connect(self.ptz_thread.move_right)
        self.ui.btn_zoom_in.pressed.connect(self.ptz_thread.zoom_in)
        self.ui.btn_zoom_out.pressed.connect(self.ptz_thread.zoom_out)
        # stop moving
        self.ui.btn_up.released.connect(self.ptz_thread.stop)
        self.ui.btn_down.released.connect(self.ptz_thread.stop)
        self.ui.btn_left.released.connect(self.ptz_thread.stop)
        self.ui.btn_right.released.connect(self.ptz_thread.stop)
        self.ui.btn_zoom_in.released.connect(self.ptz_thread.stop)
        self.ui.btn_zoom_out.released.connect(self.ptz_thread.stop)
        # Add reload button to refresh presets
        self.ui.btn_reload.clicked.connect(self.ptz_thread.fetch_presets)
        self.preset_container.add_preset_btn.clicked.connect(
            self.on_add_preset_clicked)

    def on_presets_loaded(self, presets):
        """Handle presets loaded event"""
        # Clear existing preset buttons
        self.preset_container.clear_presets()

        # Create buttons for each preset
        for preset in presets:
            preset_widget = self.preset_container.add_preset(preset)

            # Connect signals
            preset_widget.preset_clicked.connect(self.ptz_thread.goto_preset)
            preset_widget.edit_clicked.connect(self.on_edit_preset_clicked)
            preset_widget.update_position_clicked.connect(
                self.on_update_preset_position_clicked)
            preset_widget.delete_clicked.connect(self.on_delete_preset_clicked)

    def on_add_preset_clicked(self):
        """Handle add preset button click"""
        # Show dialog to get preset name
        preset_name, ok = QInputDialog.getText(
            self, "Add Preset", "Enter preset name:", text="")

        if ok and preset_name:
            # Save the preset
            success = self.ptz_thread.save_preset(preset_name)
            if success:
                # Refresh presets
                self.ptz_thread.fetch_presets()
            else:
                # Show error message
                QMessageBox.warning(
                    self, "Add Preset",
                    "Failed to save preset."
                )

    def on_edit_preset_clicked(self, token, current_name):
        """Handle edit preset button click"""
        # Show dialog to edit preset name
        new_name, ok = QInputDialog.getText(
            self, "Edit Preset", "Enter new preset name:", text=current_name)

        if ok and new_name and new_name != current_name:
            # Update the preset name in the JSON file
            success = self.ptz_thread.update_preset_name(token, new_name)

            if success:
                # Update the button text
                if token in self.preset_container.preset_widgets:
                    self.preset_container.preset_widgets[token].update_name(
                        new_name)

                # Show success message
                QMessageBox.information(
                    self, "Edit Preset",
                    f"Preset name updated to '{new_name}'."
                )
            else:
                # Show error message
                QMessageBox.warning(
                    self, "Edit Preset",
                    "Failed to update preset name."
                )

    def on_delete_preset_clicked(self, token, name):
        """Handle delete preset button click"""
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Delete Preset",
            f"Are you sure you want to delete preset '{name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Delete the preset
            success = self.ptz_thread.delete_preset(token)
            if success:
                # Refresh presets
                self.ptz_thread.fetch_presets()
            else:
                # If deletion is not supported, show a message
                QMessageBox.information(
                    self, "Delete Preset",
                    "Deleting presets may not be supported by this camera. "
                    "Please check your camera documentation."
                )

    def on_update_preset_position_clicked(self, token, name):
        """Handle update preset position button click"""
        # Confirm update
        reply = QMessageBox.question(
            self, "Update Preset Position",
            f"Are you sure you want to update the position for preset '{name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Get current position from PTZ controller
            current_position = None
            if hasattr(self.ptz_thread.ptz_controller, 'get_status'):
                status = self.ptz_thread.ptz_controller.get_status()
                if status and hasattr(status, 'Position'):
                    current_position = {
                        "pan": status.Position.PanTilt.x,
                        "tilt": status.Position.PanTilt.y,
                        "zoom": status.Position.Zoom.x
                    }

                    # Update the preset position in the JSON file
                    if self.ptz_thread.device:
                        success = self.ptz_thread.preset_service.update_preset(
                            self.ptz_thread.device.id, token, position=current_position
                        )

                        if success:
                            QMessageBox.information(
                                self, "Update Preset Position",
                                f"Position for preset '{name}' has been updated."
                            )
                        else:
                            QMessageBox.warning(
                                self, "Update Preset Position",
                                "Failed to update preset position."
                            )
                else:
                    QMessageBox.warning(
                        self, "Update Preset Position",
                        "Could not get current camera position."
                    )
            else:
                QMessageBox.warning(
                    self, "Update Preset Position",
                    "This camera does not support position updates."
                )

    def update_ui_texts(self):
        """Update all UI texts based on current language"""
        lm = self.language_manager

        # Update window title
        self.setWindowTitle(lm.get_text("main_window_title"))

        # Update preset group title
        self.ui.groupBox.setTitle(lm.get_text("presets"))

    def load_devices(self):
        """Load devices from the API"""
        # Show loading indicator
        self.ui.comboBox_camera.clear()
        self.ui.comboBox_camera.addItem(
            self.language_manager.get_text("loading_devices"))
        self.ui.comboBox_camera.setEnabled(False)

        # Fetch devices in background thread
        self.device_service.fetch_devices()

    def on_devices_loaded(self, devices: List[Device]):
        """Handle devices loaded event

        Args:
            devices (List[Device]): The list of loaded devices
        """
        # Clear dropdown
        self.ui.comboBox_camera.clear()

        if not devices:
            # No devices found
            self.ui.comboBox_camera.addItem(
                self.language_manager.get_text("no_devices_found"))
            self.ui.comboBox_camera.setEnabled(False)
        else:
            # Add devices to dropdown
            self.ui.comboBox_camera.addItem(
                self.language_manager.get_text("select_device"), None)

            for device in devices:
                # Add device name with device ID as user data
                self.ui.comboBox_camera.addItem(device.name, device.id)

            # Enable dropdown
            self.ui.comboBox_camera.setEnabled(True)

    def on_devices_loading_failed(self, error_message: str):
        """Handle devices loading failed event

        Args:
            error_message (str): The error message
        """
        # Show error message
        QMessageBox.critical(
            self,
            self.language_manager.get_text("error"),
            self.language_manager.get_text(
                "failed_to_load_devices") + ": " + error_message
        )

        # Clear dropdown and add error message
        self.ui.comboBox_camera.clear()
        self.ui.comboBox_camera.addItem(
            self.language_manager.get_text("failed_to_load_devices"))
        self.ui.comboBox_camera.setEnabled(False)

    def on_device_selected(self, index: int):
        """Handle device selection

        Args:
            index (int): The index of the selected device
        """
        if index <= 0:
            # No device selected or placeholder selected
            return

        # Get selected device ID
        device_id = self.ui.comboBox_camera.itemData(index)

        # Get device by ID
        device = self.device_service.get_device_by_id(device_id)

        if device:
            # Show device details
            print(f"Selected device: {device.name} (ID: {device.id})")
            self.sig_device_changed.emit(device)
            # Here you would typically load the device stream or perform other actions

    def on_reload_clicked(self):
        """Handle reload button click"""
        self.load_devices()

    def show_main_window(self):
        """Show the main window and load devices"""
        self.show()

        # Load devices after showing the window
        QtCore.QTimer.singleShot(100, self.load_devices)

    def paintEvent(self, event):
        """Paint event"""
        if not self.capture_queue.empty():
            frame = self.capture_queue.get()
            qt_image = QtGui.QImage(frame, frame.shape[1], frame.shape[0],
                                    frame.shape[1] * 3, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(
                qt_image).scaled(self.ui.qlabel_camera_view.size(), QtCore.Qt.KeepAspectRatio)
            self.ui.qlabel_camera_view.setPixmap(pixmap)
        self.update()

    def on_speed_changed(self, value):
        """Handle speed slider value change"""
        # Update speed in PTZ thread
        self.ptz_thread.set_movement_speed(value)
