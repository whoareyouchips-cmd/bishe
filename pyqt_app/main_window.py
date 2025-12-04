from PyQt6.QtWidgets import (
    QMainWindow, QListWidget, QStackedWidget, QLabel,
    QHBoxLayout, QWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class MainWindow(QMainWindow):
    def __init__(self, user_info):
        super().__init__()
        self.user = user_info
        self.setWindowTitle("手语识别系统 - 主界面")
        self.resize(980, 620)

        # ===============================
        # 左侧菜单栏（美化）
        # ===============================
        self.menu = QListWidget()
        self.menu.setFixedWidth(210)

        self.menu.setStyleSheet("""
            QListWidget {
                background: #2C2F33;
                border: none;
                padding-top: 10px;
            }
            QListWidget::item {
                color: #FFFFFF;
                padding: 12px;
                font-size: 16px;
                border-radius: 8px;
                margin: 4px 8px;
            }
            QListWidget::item:hover {
                background: #3E4248;
            }
            QListWidget::item:selected {
                background: #5865F2;
                color: white;
            }
        """)

        self.menu.itemClicked.connect(self.switch_page)

        # ===============================
        # 动态菜单（按角色不同显示）
        # ===============================

        role = self.user["role"]
        print("当前用户角色：", role)

        def add_menu(text):
            item = QListWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.menu.addItem(item)

        add_menu("📹 实时手语识别")
        add_menu("📝 我的识别记录")

        if role == "advanced":
            add_menu("📘 手语学习")

        if role == "admin":
            add_menu("👥 用户管理")
            add_menu("📚 手语词汇管理")
            add_menu("📊 识别日志管理")

        add_menu("🚪 退出登录")

        # ===============================
        # 右侧页面区域
        # ===============================
        self.pages = QStackedWidget()

        self.pages.addWidget(self._page("实时识别模块"))
        self.pages.addWidget(self._page("我的识别记录"))
        self.pages.addWidget(self._page("手语学习"))

        if role == "admin":
            self.pages.addWidget(self._page("用户管理模块"))
            self.pages.addWidget(self._page("手语词汇管理模块"))
            self.pages.addWidget(self._page("识别日志管理模块"))

        # ===============================
        # 主布局
        # ===============================
        layout = QHBoxLayout()
        layout.addWidget(self.menu)
        layout.addWidget(self.pages)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # 卡片式页面
    def _page(self, title):
        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #333;
        """)
        page = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        page.setLayout(layout)
        return page

    # 切换页面
    def switch_page(self, item):
        text = item.text()

        if "退出" in text:
            exit()

        self.pages.setCurrentIndex(self.menu.row(item))
