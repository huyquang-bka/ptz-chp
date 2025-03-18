from main_app.controller.main_controller import MainController
import sys
from PyQt5.QtWidgets import QApplication
import signal

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    main_controller = MainController()
    sys.exit(app.exec_())
