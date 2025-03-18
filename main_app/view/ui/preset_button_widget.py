from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QFrame


class PresetButtonWidget(QWidget):
    """Custom widget for preset buttons with control functions"""

    # Define signals
    preset_clicked = QtCore.pyqtSignal(str)  # Emits preset token
    edit_clicked = QtCore.pyqtSignal(str, str)  # Emits preset token and name
    update_position_clicked = QtCore.pyqtSignal(
        str, str)  # Emits preset token and name
    delete_clicked = QtCore.pyqtSignal(str, str)  # Emits preset token and name

    def __init__(self, preset_token, preset_name, parent=None):
        super().__init__(parent)
        self.preset_token = preset_token
        self.preset_name = preset_name
        self.setup_ui()

    def setup_ui(self):
        # Create a container frame
        self.frame = QFrame(self)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)

        # Create layout
        self.layout = QHBoxLayout(self.frame)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)

        # Create the main preset button
        self.preset_btn = QPushButton(self.preset_name)
        self.preset_btn.setMinimumHeight(40)
        self.preset_btn.clicked.connect(self._on_preset_clicked)

        # Create edit button
        self.edit_btn = QPushButton("✏️")
        self.edit_btn.setMaximumWidth(40)
        self.edit_btn.setToolTip("Edit preset name")
        self.edit_btn.clicked.connect(self._on_edit_clicked)

        # Create update position button
        self.update_pos_btn = QPushButton("📍")
        self.update_pos_btn.setMaximumWidth(40)
        self.update_pos_btn.setToolTip("Update position for this preset")
        self.update_pos_btn.clicked.connect(self._on_update_position_clicked)

        # Create delete button
        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setMaximumWidth(40)
        self.delete_btn.setToolTip("Delete preset")
        self.delete_btn.clicked.connect(self._on_delete_clicked)

        # Add buttons to layout
        self.layout.addWidget(self.preset_btn, 1)
        self.layout.addWidget(self.edit_btn, 0)
        self.layout.addWidget(self.update_pos_btn, 0)
        self.layout.addWidget(self.delete_btn, 0)

        # Set main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.frame)
        self.setLayout(main_layout)

    def _on_preset_clicked(self):
        self.preset_clicked.emit(self.preset_token)

    def _on_edit_clicked(self):
        self.edit_clicked.emit(self.preset_token, self.preset_name)

    def _on_update_position_clicked(self):
        self.update_position_clicked.emit(self.preset_token, self.preset_name)

    def _on_delete_clicked(self):
        self.delete_clicked.emit(self.preset_token, self.preset_name)

    def update_name(self, new_name):
        """Update the preset button name"""
        self.preset_name = new_name
        self.preset_btn.setText(new_name)
