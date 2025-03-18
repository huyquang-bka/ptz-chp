import os
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox


def setup_language_icons(ui_form):
    """Set up language icons for the language combo box"""
    us_icon_path = os.path.join("resources", "assets", "icons", "us.png")
    vi_icon_path = os.path.join("resources", "assets", "icons", "vi.png")

    if os.path.exists(us_icon_path):
        ui_form.comboBox_language.setItemIcon(0, QtGui.QIcon(us_icon_path))

    if os.path.exists(vi_icon_path):
        ui_form.comboBox_language.setItemIcon(1, QtGui.QIcon(vi_icon_path))


def setup_logo_image(label, width=None, height=None):
    """Set up logo image for the given label"""
    logo_path = os.path.join("resources", "assets", "icons", "logo.png")
    if os.path.exists(logo_path):
        pixmap = QtGui.QPixmap(logo_path)
        if width is None:
            width = label.width()
        if height is None:
            height = label.height()

        label.setPixmap(pixmap.scaled(
            width,
            height,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation))
        label.setScaledContents(True)


def set_button_state(button, enabled, text=None, disabled_style=None, enabled_style=None):
    """Set the state of a button"""
    button.setEnabled(enabled)

    if not enabled:
        if disabled_style:
            button.setStyleSheet(disabled_style)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #7f8c8d;
                    color: white;
                    border-radius: 4px;
                    padding: 6px;
                }
            """)
    else:
        if enabled_style:
            button.setStyleSheet(enabled_style)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4a90e2;
                    color: white;
                    border-radius: 4px;
                    padding: 6px;
                }
                QPushButton:hover {
                    background-color: #3a80d2;
                }
                QPushButton:pressed {
                    background-color: #2a70c2;
                }
            """)

    if text:
        button.setText(text)


def show_message_box(title, message, icon=QMessageBox.Warning, parent=None):
    """Show a message box with the given title and message"""
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(icon)
    msg_box.exec_()
