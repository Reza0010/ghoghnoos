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
from .command_palette import CommandPalette
from .dashboard_widget import DashboardWidget
from .categories_widget import CategoriesWidget
from .products_widget import ProductsWidget
from .orders_widget import OrdersWidget
from .settings_widget import SettingsWidget
from .users_widget import UsersWidget
from .tickets_widget import TicketsWidget

logger = logging.getLogger("MainWindow")

# پالت رنگی هماهنگ
BG_COLOR = "#16161a"
PANEL_BG = "#242629"
ACCENT_COLOR = "#7f5af0"
DANGER_COLOR = "#ef4565"
TEXT_MAIN = "#fffffe"
TEXT_SUB = "#94a1b2"
BORDER_COLOR = "#2e2e38"

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
        self._is_shutting_down = False
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
        self.setup_palette()
        
        # تایمر بررسی وضعیت اتصال
        self.check_connection_timer = QTimer(self)
        self.check_connection_timer.timeout.connect(self._safe_check_connection)
        self.check_connection_timer.start(15000) # هر ۱۵ ثانیه

        # تایمر اعلان‌های جدید
        self.notification_timer = QTimer(self)
        self.notification_timer.timeout.connect(self._check_new_notifications)
        self.notification_timer.start(30000) # هر ۳۰ ثانیه

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

    def setup_palette(self):
        self.palette = CommandPalette(self)
        self.palette.action_triggered.connect(self._on_palette_action)

    def _on_palette_action(self, category, data):
        if category == 'nav':
            self.switch_page(data)
            self.nav_group.button(data).setChecked(True)
        elif category == 'product':
            self.switch_page(1) # تب محصولات
            self.nav_group.button(1).setChecked(True)
            # در اینجا می‌توان مستقیماً دیالوگ ویرایش محصول را هم باز کرد
            if hasattr(self.pages.get(1), 'open_editor_dialog'):
                self.pages[1].open_editor_dialog(data)
        elif category == 'user':
            self.switch_page(5)
            self.nav_group.button(5).setChecked(True)
            # اسکرول یا فیلتر به کاربر خاص در تب کاربران (اختیاری)
        elif category == 'order':
            self.switch_page(3)
            self.nav_group.button(3).setChecked(True)
        elif category == 'action':
            if data == 'add_product':
                self.switch_page(1)
                self.nav_group.button(1).setChecked(True)
                if hasattr(self.pages.get(1), 'open_editor_dialog'):
                    self.pages[1].open_editor_dialog(None)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_K:
            self.palette.exec()
            return
        super().keyPressEvent(event)

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
        
        self.k_hint = QLabel("Ctrl+K")
        self.k_hint.setStyleSheet(f"color: {TEXT_SUB}; background: {BG_COLOR}; padding: 2px 5px; border-radius: 4px; font-size: 10px; font-family: Consolas;")

        header_box.addWidget(self.menu_btn)
        header_box.addWidget(self.app_title)
        header_box.addWidget(self.k_hint)
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
        
        QTimer.singleShot(250, lambda: self.show_loading_state(False))

    def show_loading_state(self, show: bool):
        if show:
            if not hasattr(self, '_loading_widget'):
                self._loading_widget = QFrame()
                self._loading_widget.setStyleSheet(f"background: {BG_COLOR};")
                lay = QVBoxLayout(self._loading_widget)

                # یک افکت شبیه‌ساز اسکلت
                skeleton = QFrame()
                skeleton.setFixedSize(600, 400)
                skeleton.setStyleSheet(f"background: {PANEL_BG}; border-radius: 15px; border: 1px solid {BORDER_COLOR};")

                self.loading_lbl = QLabel("🚀 در حال آماده‌سازی هوشمند داده‌ها...")
                self.loading_lbl.setStyleSheet(f"color: {ACCENT_COLOR}; font-weight: bold; font-size: 16px;")
                self.loading_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

                lay.addStretch()
                lay.addWidget(skeleton, 0, Qt.AlignmentFlag.AlignCenter)
                lay.addWidget(self.loading_lbl, 0, Qt.AlignmentFlag.AlignCenter)
                lay.addStretch()

                self.content_area.addWidget(self._loading_widget)
            self.content_area.setCurrentWidget(self._loading_widget)

    def toggle_sidebar(self):
        width = self.sidebar.width()
        collapsed = 80
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
        self.sidebar.setMinimumWidth(target)

    def _check_new_notifications(self):
        """بررسی برای سفارشات یا تیکت‌های جدید و نمایش نقطه اعلان"""
        asyncio.create_task(self._fetch_notification_stats())

    async def _fetch_notification_stats(self):
        from db.database import SessionLocal
        from db import crud, models

        loop = asyncio.get_running_loop()
        def fetch():
            with SessionLocal() as db:
                new_orders = db.query(models.Order).filter(models.Order.status == 'pending_payment').count()
                new_tickets = db.query(models.Ticket).filter(models.Ticket.status == 'open').count()
                return new_orders, new_tickets

        try:
            orders_count, tickets_count = await loop.run_in_executor(None, fetch)
            self._update_sidebar_badges(orders_count, tickets_count)
        except: pass

    def _update_sidebar_badges(self, orders, tickets):
        # ایندکس ۳ سفارشات، ۴ تیکت‌ها است طبق PAGE_MAP
        for btn in self.nav_buttons:
            idx = self.nav_group.id(btn)
            if idx == 3: # سفارشات
                self._apply_badge_style(btn, orders > 0)
            elif idx == 4: # تیکت‌ها
                self._apply_badge_style(btn, tickets > 0)

    def _apply_badge_style(self, btn, has_new):
        current_style = btn.styleSheet()
        if has_new:
            # اضافه کردن یک نقطه قرمز یا تغییر حاشیه
            btn.setStyleSheet(f"""
                QPushButton {{ border-left: 4px solid {DANGER_COLOR}; }}
            """)
        else:
            btn.setStyleSheet("") # بازگشت به استایل پیش‌فرض QSS

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
        if hasattr(self, 'app_manager'):
            self.show_toast("در حال بازآوری سرویس‌ها...")
            asyncio.create_task(self.app_manager.restart_services())
        else:
            self.show_toast("خطا: مدیر برنامه در دسترس نیست", is_error=True)

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
        if self._is_shutting_down:
            event.accept()
            return

        reply = QMessageBox.question(
            self, 'خروج', "آیا از خروج و توقف مدیریت مطمئن هستید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._is_shutting_down = True
            event.accept()
        else:
            event.ignore()