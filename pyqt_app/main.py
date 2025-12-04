from PyQt6.QtWidgets import QApplication
from pyqt_app.login_window import LoginWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec())
