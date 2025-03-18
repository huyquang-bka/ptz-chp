from PyQt5.QtWidgets import QMessageBox


def show_message_box(title: str, message: str = None):
    QMessageBox.warning(None, title, message)


def show_message_box_error(title: str, message: str = None):
    QMessageBox.critical(None, title, message)


def show_message_box_success(title: str, message: str = None):
    QMessageBox.information(None, title, message)
