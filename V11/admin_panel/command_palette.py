import asyncio
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QLabel, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QKeyEvent
import qtawesome as qta

from db.database import SessionLocal
from db import crud, models

logger = logging.getLogger("CommandPalette")

# پالت رنگی هماهنگ با تم اصلی
BG_COLOR = "#16161a"
PANEL_BG = "#242629"
ACCENT_COLOR = "#7f5af0"
TEXT_MAIN = "#fffffe"
TEXT_SUB = "#94a1b2"
BORDER_COLOR = "#2e2e38"

class PaletteItem(QListWidgetItem):
    def __init__(self, title, subtitle, icon, category, data=None):
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.category = category # 'nav', 'product', 'user', 'order'
        self.data = data # ID or other relevant info

        self.setIcon(qta.icon(icon, color=ACCENT_COLOR if category != 'nav' else TEXT_SUB))
        self.setText(f"{title}\n{subtitle}")

class CommandPalette(QDialog):
    action_triggered = pyqtSignal(str, object) # category, data

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedWidth(600)
        self.setFixedHeight(450)

        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.container = QFrame()
        self.container.setObjectName("PaletteContainer")
        self.container.setStyleSheet(f"""
            QFrame#PaletteContainer {{
                background-color: {PANEL_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 12px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30); shadow.setColor(QColor(0, 0, 0, 150)); shadow.setOffset(0, 10)
        self.container.setGraphicsEffect(shadow)

        c_layout = QVBoxLayout(self.container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(0)

        # بخش ورودی
        h_input = QHBoxLayout()
        h_input.setContentsMargins(15, 15, 15, 15)

        self.search_icon = QLabel()
        self.search_icon.setPixmap(qta.icon("fa5s.search", color=ACCENT_COLOR).pixmap(20, 20))

        self.input = QLineEdit()
        self.input.setPlaceholderText("جستجو در محصولات، کاربران، سفارشات یا منوها...")
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {TEXT_MAIN};
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }}
        """)
        self.input.textChanged.connect(self.on_search)

        h_input.addWidget(self.search_icon)
        h_input.addWidget(self.input)
        c_layout.addLayout(h_input)

        line = QFrame(); line.setFixedHeight(1); line.setStyleSheet(f"background: {BORDER_COLOR};")
        c_layout.addWidget(line)

        # لیست نتایج
        self.list = QListWidget()
        self.list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
                color: {TEXT_MAIN};
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 2px;
            }}
            QListWidget::item:selected {{
                background-color: {ACCENT_COLOR}30;
                color: {TEXT_MAIN};
            }}
        """)
        self.list.itemDoubleClicked.connect(self.trigger_selection)
        c_layout.addWidget(self.list)

        # فوتر
        footer = QFrame()
        footer.setFixedHeight(35)
        footer.setStyleSheet(f"background: {BG_COLOR}; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;")
        f_layout = QHBoxLayout(footer)

        hint = QLabel("↑↓ جابجایی | Enter انتخاب | Esc لغو")
        hint.setStyleSheet(f"color: {TEXT_SUB}; font-size: 10px;")
        f_layout.addWidget(hint); f_layout.addStretch()

        c_layout.addWidget(footer)
        layout.addWidget(self.container)

    def setup_shortcuts(self):
        # جهت هدایت کیبورد به لیست
        self.input.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.input and event.type() == event.Type.KeyPress:
            key_event = QKeyEvent(event)
            if key_event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                self.list.keyPressEvent(key_event)
                return True
            if key_event.key() == Qt.Key.Key_Enter or key_event.key() == Qt.Key.Key_Return:
                self.trigger_selection(self.list.currentItem())
                return True
            if key_event.key() == Qt.Key.Key_Escape:
                self.reject()
                return True
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        super().showEvent(event)
        self.input.clear()
        self.input.setFocus()
        self.load_default_items()

    def load_default_items(self):
        self.list.clear()
        # آیتم‌های ناوبری پیش‌فرض
        navs = [
            ("محصول جدید", "➕ افزودن کالا به انبار", "fa5s.plus-circle", 101),
            ("داشبورد", "مشاهده وضعیت کلی فروشگاه", "fa5s.chart-pie", 0),
            ("محصولات", "مدیریت و لیست کالاها", "fa5s.box-open", 1),
            ("سفارشات", "بررسی خریدهای جدید", "fa5s.clipboard-list", 3),
            ("تیکت‌ها", "پاسخ به پیام‌های مشتریان", "fa5s.ticket-alt", 4),
            ("کاربران", "مدیریت مشتریان و CRM", "fa5s.users", 5),
            ("تنظیمات", "پیکربندی ربات و سیستم", "fa5s.cog", 6),
        ]
        for title, sub, icon, idx in navs:
            self.list.addItem(PaletteItem(title, sub, icon, 'nav', idx))
        self.list.setCurrentRow(0)

    def on_search(self, text):
        text = text.strip().lower()
        if not text:
            self.load_default_items()
            return

        self.list.clear()
        asyncio.create_task(self.perform_db_search(text))

    async def perform_db_search(self, query):
        loop = asyncio.get_running_loop()
        def db_search():
            results = []
            with SessionLocal() as db:
                # جستجوی محصولات
                prods = crud.advanced_search_products(db, query=query, limit=5)
                for p in prods:
                    results.append(PaletteItem(p.name, f"محصول - {int(p.price):,} تومان", "fa5s.tag", "product", p.id))

                # جستجوی کاربران
                users = db.query(models.User).filter(
                    (models.User.full_name.ilike(f"%{query}%")) |
                    (models.User.user_id.ilike(f"%{query}%"))
                ).limit(5).all()
                for u in users:
                    results.append(PaletteItem(u.full_name or "کاربر ناشناس", f"مشتری - ID: {u.user_id}", "fa5s.user", "user", u.user_id))

                # جستجوی سفارشات (ID)
                if query.isdigit():
                    order = crud.get_order_by_id(db, int(query))
                    if order:
                        results.append(PaletteItem(f"سفارش #{order.id}", f"وضعیت: {order.status}", "fa5s.shopping-cart", "order", order.id))
            return results

        items = await loop.run_in_executor(None, db_search)
        for item in items:
            self.list.addItem(item)

        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def trigger_selection(self, item):
        if not item: return
        # مدیریت عملیات ویژه
        if item.category == 'nav' and item.data == 101:
             self.action_triggered.emit('action', 'add_product')
        else:
             self.action_triggered.emit(item.category, item.data)
        self.accept()
