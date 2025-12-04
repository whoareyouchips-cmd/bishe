from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QBrush, QLinearGradient, QColor
import pymysql

from scripts.log_query_service import DB
from pyqt_app.main_window import MainWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("手语识别系统 - 登录")
        self.resize(420, 320)

        # 设置渐变背景
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0.0, QColor("#74ebd5"))
        gradient.setColorAt(1.0, QColor("#ACB6E5"))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)

        # 半透明白色卡片
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.85);
                border-radius: 15px;
            }
        """)
        container.setFixedWidth(300)
        container.setFixedHeight(260)

        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)

        # 标题
        title = QLabel("手语识别系统")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:24px; font-weight:bold; color:#333;")
        layout.addWidget(title)

        # 用户名输入框
        self.username = QLineEdit()
        self.username.setPlaceholderText("用户名")
        self.username.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border-radius: 10px;
                border: 1px solid #ccc;
                background: white;
            }
            QLineEdit:focus {
                border: 1px solid #6C63FF;
            }
        """)
        layout.addWidget(self.username)

        # 密码框
        self.password = QLineEdit()
        self.password.setPlaceholderText("密码")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border-radius: 10px;
                border: 1px solid #ccc;
                background: white;
            }
            QLineEdit:focus {
                border: 1px solid #6C63FF;
            }
        """)
        layout.addWidget(self.password)

        # 登录按钮
        login_btn = QPushButton("登录")
        login_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 12px;
                background-color: #6C63FF;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #574bff;
            }
            QPushButton:pressed {
                background-color: #453aff;
            }
        """)
        login_btn.clicked.connect(self.do_login)
        layout.addWidget(login_btn)

        # 外部布局
        outer = QVBoxLayout(self)
        outer.addStretch()
        outer.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        outer.addStretch()

    # 登录逻辑不变
    def do_login(self):
        user = self.username.text().strip()
        pwd = self.password.text().strip()

        conn = pymysql.connect(**DB)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (user, pwd)
        )
        res = cursor.fetchone()
        conn.close()

        if not res:
            QMessageBox.warning(self, "错误", "用户名或密码错误！")
            return

        QMessageBox.information(self, "欢迎", f"欢迎你 {res['username']}！")

        self.hide()
        self.main = MainWindow(user_info=res)
        self.main.show()
