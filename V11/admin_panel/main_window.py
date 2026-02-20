import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Callable

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QFrame, QButtonGroup, QLabel, QGraphicsDropShadowEffect,
    QSizePolicy, QMessageBox
)
from PyQt6.QtCore import (
    Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QPoint, pyqtSlot
)
from PyQt6.QtGui import QColor, QFontDatabase, QFont, QIcon
import qtawesome as qta

from config import BASE_DIR

# ایمپورت ویجت‌ها
from .dashboard_widget import DashboardWidget
from .categories_widget import CategoriesWidget
from .products_widget import ProductsWidget
from .orders_widget import OrdersWidget
from .settings_widget import SettingsWidget
from .users_widget import UsersWidget
from .tickets_widget import TicketsWidget

logger = logging.getLogger("MainWindow")

class MainWindow(QMainWindow):
    PAGE_MAP = {
        0: ("داشبورد", "fa5s.chart-pie"),
        1: ("محصولات", "fa5s.box-open"),
        2: ("دسته‌بندی‌ها", "fa5s.layer-group"),
        3: ("سفارشات", "fa5s.clipboard-list"),
        4: ("تیکت‌ها", "fa5s.ticket-alt"),
        5: ("کاربران", "fa5s.users"),
        6: ("تنظیمات", "fa5s.cog"),
    }

    def __init__(self, bot_application: Optional[object] = None, rubika_client: Optional[object] = None):
        super().__init__()
        self.bot_application = bot_application
        self.rubika_client = rubika_client
        self.base_path = Path(BASE_DIR) / "admin_panel"
        
        # تنظیمات پایه پنجره
        self.setWindowTitle("مدیریت هوشمند فروشگاه | Omnichannel Panel")
        self.resize(1300, 850)
        self.setMinimumSize(1100, 750)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowIcon(qta.icon("fa5s.store", color="#7f5af0"))

        self._load_font()
        self.is_sidebar_collapsed = False
        self.pages: Dict[int, QWidget] = {}
        
        # تعریف کلاس‌ها برای Lazy Loading
        self.page_factories = [
            lambda: DashboardWidget(),
            lambda: ProductsWidget(bot_app=self.bot_application),
            lambda: CategoriesWidget(),
            lambda: OrdersWidget(bot_app=self.bot_application, rubika_client=self.rubika_client),
            lambda: TicketsWidget(bot_app=self.bot_application, rubika_client=self.rubika_client),
            lambda: UsersWidget(),
            lambda: SettingsWidget(bot_app=self.bot_application, rubika_client=self.rubika_client)
        ]
        
        self.setup_ui()
        self.load_stylesheet()
        
        # تایمر بررسی وضعیت اتصال
        self.check_connection_timer = QTimer(self)
        self.check_connection_timer.timeout.connect(self._safe_check_connection)
        self.check_connection_timer.start(15000) # هر ۱۵ ثانیه

        self._toast = None

    def _load_font(self):
        # بررسی چند مسیر احتمالی برای فونت
        possible_paths = [
            Path(BASE_DIR) / "fonts" / "Vazirmatn.ttf",
            self.base_path / "fonts" / "Vazirmatn.ttf",
            Path(BASE_DIR) / "Vazirmatn.ttf"
        ]
        
        font_loaded = False
        for path in possible_paths:
            if path.exists():
                QFontDatabase.addApplicationFont(str(path))
                QApplication.setFont(QFont("Vazirmatn", 10))
                logger.info(f"Font loaded from: {path}")
                font_loaded = True
                break
        
        if not font_loaded:
            logger.warning("Vazirmatn font not found. Using system default.")

    def setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralwidget") 
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0) 
        main_layout.setSpacing(0)

        # ==================== ۱. سایدبار (Sidebar) ====================
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(260)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(-5, 0)
        self.sidebar.setGraphicsEffect(shadow)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(5)

        # --- هدر سایدبار ---
        header_box = QHBoxLayout()
        
        self.menu_btn = QPushButton()
        self.menu_btn.setIcon(qta.icon("fa5s.bars", color="#94a1b2"))
        self.menu_btn.setFixedSize(40, 40)
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.setObjectName("menu_btn")
        self.menu_btn.clicked.connect(self.toggle_sidebar)
        
        self.app_title = QLabel("پنل ادمین")
        self.app_title.setObjectName("app_title")
        
        header_box.addWidget(self.menu_btn)
        header_box.addWidget(self.app_title)
        header_box.addStretch()
        sidebar_layout.addLayout(header_box)

        # --- دکمه‌های ناوبری (بخش ترمیم شده) ---
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons = []

        for index, (text, icon) in self.PAGE_MAP.items():
            btn = QPushButton(f"  {text}")
            btn.setIcon(qta.icon(icon, color="#94a1b2"))
            btn.setIconSize(QSize(20, 20))
            btn.setCheckable(True)
            btn.setFixedHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("original_text", f"  {text}")
            btn.setProperty("icon_name", icon)
            
            self.nav_group.addButton(btn, index)
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # --- بخش وضعیت ربات‌ها (طراحی جدید) ---
        self.status_container = QFrame()
        self.status_container.setObjectName("status_container")
        self.status_container.setFixedHeight(140)
        
        status_main_layout = QVBoxLayout(self.status_container)
        status_main_layout.setContentsMargins(10, 10, 10, 10)
        status_main_layout.setSpacing(8)

        title_label = QLabel("وضعیت اتصال")
        title_label.setStyleSheet("color: #72757e; font-size: 11px; font-weight: bold;")
        status_main_layout.addWidget(title_label)

        # ردیف تلگرام
        tg_row = QHBoxLayout()
        tg_row.setSpacing(8)
        tg_icon = QLabel()
        tg_icon.setPixmap(qta.icon("fa5b.telegram", color="#fffffe").pixmap(20, 20))
        tg_name = QLabel("تلگرام")
        tg_name.setStyleSheet("color: #fffffe; font-size: 13px;")
        self.tg_indicator = QLabel()
        self.tg_indicator.setObjectName("status_indicator")
        self.tg_indicator.setToolTip("بررسی وضعیت...")
        
        tg_row.addWidget(tg_icon)
        tg_row.addWidget(tg_name)
        tg_row.addStretch()
        tg_row.addWidget(self.tg_indicator)
        status_main_layout.addLayout(tg_row)

        # ردیف روبیکا
        rb_row = QHBoxLayout()
        rb_row.setSpacing(8)
        rb_icon = QLabel()
        rb_icon.setPixmap(qta.icon("fa5s.rocket", color="#fffffe").pixmap(20, 20))
        rb_name = QLabel("روبیکا")
        rb_name.setStyleSheet("color: #fffffe; font-size: 13px;")
        self.rb_indicator = QLabel()
        self.rb_indicator.setObjectName("status_indicator")
        self.rb_indicator.setToolTip("بررسی وضعیت...")
        
        rb_row.addWidget(rb_icon)
        rb_row.addWidget(rb_name)
        rb_row.addStretch()
        rb_row.addWidget(self.rb_indicator)
        status_main_layout.addLayout(rb_row)

        # خط جداکننده و دکمه ریستارت
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #2e2e38;")
        separator.setFixedHeight(1)
        status_main_layout.addWidget(separator)

        self.btn_restart_bots = QPushButton("🔄 ریستارت سرویس‌ها")
        self.btn_restart_bots.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restart_bots.setObjectName("secondary_btn")
        self.btn_restart_bots.clicked.connect(self._handle_restart_click)
        status_main_layout.addWidget(self.btn_restart_bots)

        sidebar_layout.addWidget(self.status_container)

        # ==================== ۲. محتوا (Content Area) ====================
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("content_area")
        
        content_margin = QWidget()
        content_layout = QHBoxLayout(content_margin)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.addWidget(self.content_area)

        self.nav_group.idClicked.connect(self.switch_page)

        # افزودن ویجت‌ها به لایه اصلی
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_margin)
        
        # بارگذاری صفحه اول
        self.switch_page(0)
        self.nav_buttons[0].setChecked(True)

        # بررسی رمز عبور پیش‌فرض
        QTimer.singleShot(2000, self._check_default_password)

    def _check_default_password(self):
        from db.database import SessionLocal
        from db import crud
        with SessionLocal() as db:
            if crud.get_setting(db, "panel_password", "admin") == "admin":
                QMessageBox.warning(self, "هشدار امنیتی", "شما هنوز از رمز عبور پیش‌فرض (admin) استفاده می‌کنید.\nلطفاً برای امنیت بیشتر در بخش تنظیمات آن را تغییر دهید.")

    def switch_page(self, page_id):
        """مدیریت جابجایی بین صفحات با Lazy Loading"""
        if page_id not in self.pages:
            self.show_loading_state(True)
            try:
                widget = self.page_factories[page_id]()
                self.pages[page_id] = widget
                self.content_area.addWidget(widget)
            except Exception as e:
                logger.error(f"Error creating page {page_id}: {e}")
                self.show_loading_state(False)
                return

        current_page = self.pages[page_id]
        
        # تغییر رنگ آیکون‌ها
        for btn in self.nav_buttons:
            idx = self.nav_group.id(btn)
            icon_name = btn.property("icon_name")
            if idx == page_id:
                btn.setIcon(qta.icon(icon_name, color="#ffffff"))
            else:
                btn.setIcon(qta.icon(icon_name, color="#94a1b2"))

        self.content_area.setCurrentWidget(current_page)
        
        if hasattr(current_page, "refresh_data"):
            res = current_page.refresh_data()
            if asyncio.iscoroutine(res):
                asyncio.create_task(res)
        
        QTimer.singleShot(100, lambda: self.show_loading_state(False))

    def show_loading_state(self, show: bool):
        if show:
            if not hasattr(self, '_loading_widget'):
                self._loading_widget = QLabel("⏳ در حال بارگذاری...")
                self._loading_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._loading_widget.setObjectName("loading_label")
                self.content_area.addWidget(self._loading_widget)
            self.content_area.setCurrentWidget(self._loading_widget)

    def toggle_sidebar(self):
        width = self.sidebar.width()
        collapsed = 70
        expanded = 260
        
        if width > 100:
            target = collapsed
            self.is_sidebar_collapsed = True
            self.app_title.hide()
            self.status_container.hide()
            for btn in self.nav_buttons:
                btn.setText("")
                btn.setToolTip(btn.property("original_text").strip())
        else:
            target = expanded
            self.is_sidebar_collapsed = False
            for btn in self.nav_buttons:
                btn.setText(btn.property("original_text"))
                btn.setToolTip("")
            self.app_title.show()
            self.status_container.show()

        self.anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.anim.setDuration(350)
        self.anim.setStartValue(width)
        self.anim.setEndValue(target)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuint)
        self.anim.start()
        self.sidebar.setMaximumWidth(target)

    def _safe_check_connection(self):
        """بررسی وضعیت و تغییر استایل نشانگرها"""
        # وضعیت تلگرام
        tg_status = "online" if self.bot_application else "offline"
        self.tg_indicator.setProperty("status", tg_status)
        self.tg_indicator.setStyleSheet("") # ریست استایل برای اعمال تغییرات
        self.tg_indicator.setToolTip("آنلاین" if self.bot_application else "آفلاین")
        
        # وضعیت روبیکا
        rb_status = "online" if self.rubika_client else "offline"
        self.rb_indicator.setProperty("status", rb_status)
        self.rb_indicator.setStyleSheet("")
        self.rb_indicator.setToolTip("آنلاین" if self.rubika_client else "آفلاین")

    def _handle_restart_click(self):
        self.show_toast("درخواست ریستارت ارسال شد...")
        QTimer.singleShot(1000, lambda: self.show_toast("سرویس‌ها در حال راه‌اندازی مجدد..."))

    def load_stylesheet(self):
        path = self.base_path / "themes" / "dark_theme.qss"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            logger.error(f"Stylesheet not found at: {path}")

    def show_toast(self, message: str, is_error: bool = False):
        if self._toast: self._toast.close()
        
        self._toast = QLabel(message, self)
        bg_color = "#ef476f" if is_error else "#7f5af0"
        self._toast.setStyleSheet(f"""
            background-color: {bg_color}; 
            color: white; 
            padding: 12px 25px; 
            border-radius: 8px; 
            font-weight: bold; 
            font-size: 13px;
        """)
        self._toast.adjustSize()
        
        x = self.width() - self._toast.width() - 30
        y = self.height() - self._toast.height() - 30
        self._toast.move(x, y)
        self._toast.show()
        
        QTimer.singleShot(3500, self._toast.close)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 'خروج', "آیا از خروج و توقف مدیریت مطمئن هستید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()