import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QFrame, QButtonGroup
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from .products_widget import ProductsWidget
from .orders_widget import OrdersWidget
from .dashboard_widget import DashboardWidget
from .settings_widget import SettingsWidget
from .categories_widget import CategoriesWidget

class MainWindow(QMainWindow):
    def __init__(self, bot_app):
        super().__init__()
        self.bot_app = bot_app
        self.base_path = os.path.dirname(__file__)
        self.light_theme = os.path.join(self.base_path, 'themes', 'light_theme.qss')
        self.dark_theme = os.path.join(self.base_path, 'themes', 'dark_theme.qss')
        self.setWindowTitle("پنل مدیریت فروشگاه")
        self.setGeometry(100, 100, 1280, 720)
        self.setup_ui()
        self.load_stylesheet(self.dark_theme)

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)

        self.nav_group = QButtonGroup()
        self.nav_group.setExclusive(True)
        style = self.style()
        self.dashboard_btn = self.create_nav_button("داشبورد", style.standardIcon(style.StandardPixmap.SP_ComputerIcon))
        self.products_btn = self.create_nav_button("محصولات", style.standardIcon(style.StandardPixmap.SP_FileDialogDetailedView))
        self.categories_btn = self.create_nav_button("دسته‌بندی‌ها", style.standardIcon(style.StandardPixmap.SP_DirIcon))
        self.orders_btn = self.create_nav_button("سفارش‌ها", style.standardIcon(style.StandardPixmap.SP_FileIcon))
        self.settings_btn = self.create_nav_button("تنظیمات", style.standardIcon(style.StandardPixmap.SP_FileDialogListView))

        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addWidget(self.products_btn)
        sidebar_layout.addWidget(self.categories_btn)
        sidebar_layout.addWidget(self.orders_btn)
        sidebar_layout.addWidget(self.settings_btn)
        sidebar_layout.addStretch()

        self.theme_btn = QPushButton("تغییر تم")
        self.theme_btn.setIcon(style.standardIcon(style.StandardPixmap.SP_DesktopIcon))
        self.theme_btn.setCheckable(True)
        self.theme_btn.toggled.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.theme_btn)

        self.content = QStackedWidget()
        self.dashboard_page = DashboardWidget()
        self.products_page = ProductsWidget()
        self.categories_page = CategoriesWidget()
        self.orders_page = OrdersWidget(bot_app=self.bot_app)
        self.settings_page = SettingsWidget()
        self.content.addWidget(self.dashboard_page)
        self.content.addWidget(self.products_page)
        self.content.addWidget(self.categories_page)
        self.content.addWidget(self.orders_page)
        self.content.addWidget(self.settings_page)

        self.dashboard_btn.clicked.connect(lambda: self.switch_page(self.dashboard_page))
        self.products_btn.clicked.connect(lambda: self.switch_page(self.products_page))
        self.categories_btn.clicked.connect(lambda: self.switch_page(self.categories_page))
        self.orders_btn.clicked.connect(lambda: self.switch_page(self.orders_page))
        self.settings_btn.clicked.connect(lambda: self.switch_page(self.settings_page))

        main_layout.addWidget(self.content)
        main_layout.addWidget(sidebar)

        self.dashboard_btn.setChecked(True)
        self.switch_page(self.dashboard_page)

    def create_nav_button(self, text, icon):
        btn = QPushButton(text)
        btn.setIcon(icon)
        btn.setIconSize(QSize(24, 24))
        btn.setCheckable(True)
        self.nav_group.addButton(btn)
        return btn

    def switch_page(self, widget):
        self.content.setCurrentWidget(widget)
        if hasattr(widget, 'refresh_data'):
            widget.refresh_data()

    def load_stylesheet(self, path):
        try:
            with open(path, "r") as f: self.setStyleSheet(f.read())
        except FileNotFoundError: print(f"Stylesheet not found: {path}")

    def toggle_theme(self, checked):
        if checked: self.load_stylesheet(self.light_theme); self.theme_btn.setText("تم روشن")
        else: self.load_stylesheet(self.dark_theme); self.theme_btn.setText("تم تیره")
