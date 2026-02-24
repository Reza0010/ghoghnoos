import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QLabel, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QKeyEvent
import qtawesome as qta
from db.database import get_db
from db import models
from sqlalchemy import or_

logger = logging.getLogger("CommandPalette")

class CommandPalette(QDialog):
    # سیگنال برای ناوبری: (نوع_آیتم، آیدی_آیتم)
    item_selected = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(600)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.container = QFrame()
        self.container.setObjectName("PaletteContainer")
        self.container.setStyleSheet("""
            QFrame#PaletteContainer {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 12px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 10)
        self.container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # بخش ورودی
        search_box = QHBoxLayout()
        search_box.setContentsMargins(15, 15, 15, 15)

        search_icon = QLabel()
        search_icon.setPixmap(qta.icon("fa5s.search", color="#8b949e").pixmap(20, 20))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجوی سریع محصولات، کاربران و سفارشات... (Esc برای خروج)")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #c9d1d9;
                font-size: 16px;
                padding: 5px;
            }
        """)
        self.search_input.textChanged.connect(self.perform_search)

        search_box.addWidget(search_icon)
        search_box.addWidget(self.search_input)
        container_layout.addLayout(search_box)

        # خط جداکننده
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #30363d;")
        line.setFixedHeight(1)
        container_layout.addWidget(line)

        # لیست نتایج
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: #8b949e;
                outline: none;
                padding: 5px;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
                margin: 2px 5px;
            }
            QListWidget::item:selected {
                background-color: #21262d;
                color: #58a6ff;
            }
        """)
        self.results_list.itemDoubleClicked.connect(self.handle_selection)
        container_layout.addWidget(self.results_list)

        # فوتر راهنما
        footer = QLabel(" ↵ انتخاب  |  ↑↓ پیمایش  |  Esc بستن")
        footer.setStyleSheet("color: #484f58; font-size: 11px; padding: 10px; background: #0d1117; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;")
        container_layout.addWidget(footer)

        layout.addWidget(self.container)

    def perform_search(self, text):
        self.results_list.clear()
        if len(text) < 2:
            return

        with next(get_db()) as db:
            # ۱. جستجوی محصولات
            products = db.query(models.Product).filter(
                or_(models.Product.name.ilike(f"%{text}%"), models.Product.tags.ilike(f"%{text}%"))
            ).limit(5).all()

            for p in products:
                self.add_result_item(f"📦 محصول: {p.name}", "product", str(p.id), "fa5s.box")

            # ۲. جستجوی کاربران
            users = db.query(models.User).filter(
                or_(models.User.full_name.ilike(f"%{text}%"), models.User.username.ilike(f"%{text}%"), models.User.user_id.ilike(f"%{text}%"))
            ).limit(5).all()

            for u in users:
                self.add_result_item(f"👤 کاربر: {u.full_name or u.user_id}", "user", u.user_id, "fa5s.user")

            # ۳. جستجوی سفارشات
            if text.isdigit():
                orders = db.query(models.Order).filter(models.Order.id == int(text)).all()
                for o in orders:
                    self.add_result_item(f"🧾 سفارش شماره #{o.id}", "order", str(o.id), "fa5s.receipt")

        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)

    def add_result_item(self, text, type_name, item_id, icon_name):
        item = QListWidgetItem(qta.icon(icon_name, color="#8b949e"), text)
        item.setData(Qt.ItemDataRole.UserRole, (type_name, item_id))
        self.results_list.addItem(item)

    def handle_selection(self, item):
        if not item: return
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.item_selected.emit(data[0], data[1])
            self.accept()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            self.handle_selection(self.results_list.currentItem())
        elif event.key() == Qt.Key.Key_Down:
            self.results_list.setCurrentRow(min(self.results_list.currentRow() + 1, self.results_list.count() - 1))
        elif event.key() == Qt.Key.Key_Up:
            self.results_list.setCurrentRow(max(self.results_list.currentRow() - 1, 0))
        else:
            super().keyPressEvent(event)
