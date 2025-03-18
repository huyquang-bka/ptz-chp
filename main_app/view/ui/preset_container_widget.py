from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QScrollArea
from main_app.view.ui.preset_button_widget import PresetButtonWidget


class PresetContainerWidget(QWidget):
    """Container widget for preset buttons"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.preset_widgets = {}  # Store references to preset widgets
        self.setup_ui()

    def setup_ui(self):
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create scroll area for presets
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded)

        # Create container widget for scroll area
        self.scroll_content = QWidget()

        # Create layout for presets
        self.preset_layout = QVBoxLayout(self.scroll_content)
        self.preset_layout.setContentsMargins(4, 4, 4, 4)
        self.preset_layout.setSpacing(4)
        self.preset_layout.setAlignment(QtCore.Qt.AlignTop)

        # Add "Add Preset" button
        self.add_preset_btn = QPushButton("+ Add Preset")
        self.add_preset_btn.setMinimumHeight(40)

        # Set up scroll area
        self.scroll_area.setWidget(self.scroll_content)

        # Add widgets to main layout
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(self.add_preset_btn)

    def add_preset(self, preset):
        """Add a preset button to the container"""
        preset_name = preset.Name if hasattr(
            preset, 'Name') else f"Preset {preset.token}"
        preset_widget = PresetButtonWidget(preset.token, preset_name)

        # Add to layout
        self.preset_layout.addWidget(preset_widget)

        # Store reference
        self.preset_widgets[preset.token] = preset_widget

        return preset_widget

    def clear_presets(self):
        """Clear all preset buttons"""
        # Remove all widgets from layout
        while self.preset_layout.count():
            item = self.preset_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Clear references
        self.preset_widgets = {}

    def get_add_preset_button(self):
        """Get the add preset button"""
        return self.add_preset_btn
