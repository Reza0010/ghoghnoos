import asyncio
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QFrame, QLabel, QGraphicsDropShadowEffect,
    QApplication, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QIcon
import qtawesome as qta

from db.database import get_db
from db import crud, models
from sqlalchemy import or_

logger = logging.getLogger("CommandPalette")

class CommandPalette(QDialog):
    """
    پالت دستورات هوشمند (Ctrl+K)
    برای جستجوی سریع بین تمام بخش‌های برنامه
    """
    item_selected = pyqtSignal(str, int) # Type (product/user/order), ID

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(650)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # کانتینر اصلی با افکت شیشه‌ای
        self.container = QFrame()
        self.container.setObjectName("PaletteContainer")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(5, 5, 5, 5)
        container_layout.setSpacing(0)

        # بخش ورودی جستجو
        search_row = QHBoxLayout()
        search_row.setContentsMargins(15, 15, 15, 15)

        search_icon = QLabel()
        search_icon.setPixmap(qta.icon("fa5s.search", color="#7f5af0").pixmap(20, 20))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجوی سریع محصول، کاربر یا سفارش...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 18px;
                color: white;
                padding: 5px;
            }
        """)
        self.search_input.textChanged.connect(self.start_search)

        search_row.addWidget(search_icon)
        search_row.addWidget(self.search_input)
        container_layout.addLayout(search_row)

        # خط جداکننده
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); max-height: 1px;")
        container_layout.addWidget(line)

        # لیست نتایج
        self.results_list = QListWidget()
        self.results_list.setObjectName("PaletteList")
        self.results_list.itemClicked.connect(self.on_item_clicked)
        container_layout.addWidget(self.results_list)

        # راهنما در پایین
        help_row = QHBoxLayout()
        help_row.setContentsMargins(15, 8, 15, 8)
        help_lbl = QLabel("<b>Enter</b> برای انتخاب  |  <b>↑↓</b> برای پیمایش  |  <b>Esc</b> برای خروج")
        help_lbl.setStyleSheet("color: #94a1b2; font-size: 11px;")
        help_row.addWidget(help_lbl)
        help_row.addStretch()
        container_layout.addWidget(help_lbl)

        layout.addWidget(self.container)

    def start_search(self, text):
        if len(text) < 2:
            self.results_list.clear()
            return

        # اجرای جستجو در ترد مجزا (ساده‌سازی شده)
        asyncio.create_task(self.perform_search(text))

    async def perform_search(self, text):
        loop = asyncio.get_running_loop()

        def db_search():
            with next(get_db()) as db:
                # 1. جستجوی محصولات
                prods = db.query(models.Product).filter(
                    or_(models.Product.name.ilike(f"%{text}%"), models.Product.brand.ilike(f"%{text}%"))
                ).limit(5).all()

                # 2. جستجوی کاربران
                users = db.query(models.User).filter(
                    or_(models.User.full_name.ilike(f"%{text}%"), models.User.username.ilike(f"%{text}%"))
                ).limit(5).all()

                # 3. جستجوی سفارشات (بر اساس ID)
                orders = []
                if text.isdigit():
                    orders = db.query(models.Order).filter(models.Order.id == int(text)).all()

                return prods, users, orders

        results = await loop.run_in_executor(None, db_search)
        self.update_results(results)

    def update_results(self, results):
        self.results_list.clear()
        prods, users, orders = results

        # محصولات
        for p in prods:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, ("product", p.id))

            widget = QWidget()
            lay = QHBoxLayout(widget)
            icon_lbl = QLabel()
            icon_lbl.setPixmap(qta.icon("fa5s.shopping-bag", color="#2cb67d").pixmap(24, 24))
            text_lbl = QLabel(f"<b>محصول:</b> {p.name}")
            price_lbl = QLabel(f"{int(p.price):,} ت")
            price_lbl.setStyleSheet("color: #7f5af0;")

            lay.addWidget(icon_lbl); lay.addWidget(text_lbl); lay.addStretch(); lay.addWidget(price_lbl)
            item.setSizeHint(widget.sizeHint())
            self.results_list.addItem(item)
            self.results_list.setItemWidget(item, widget)

        # کاربران
        for u in users:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, ("user", u.user_id))

            widget = QWidget()
            lay = QHBoxLayout(widget)
            icon_lbl = QLabel()
            icon_lbl.setPixmap(qta.icon("fa5s.user", color="#3da9fc").pixmap(24, 24))
            text_lbl = QLabel(f"<b>کاربر:</b> {u.full_name or u.username}")
            plat_lbl = QLabel(u.platform)
            plat_lbl.setStyleSheet("color: #94a1b2; font-size: 10px;")

            lay.addWidget(icon_lbl); lay.addWidget(text_lbl); lay.addStretch(); lay.addWidget(plat_lbl)
            item.setSizeHint(widget.sizeHint())
            self.results_list.addItem(item)
            self.results_list.setItemWidget(item, widget)

        # سفارشات
        for o in orders:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, ("order", o.id))

            widget = QWidget()
            lay = QHBoxLayout(widget)
            icon_lbl = QLabel()
            icon_lbl.setPixmap(qta.icon("fa5s.receipt", color="#f39c12").pixmap(24, 24))
            text_lbl = QLabel(f"<b>سفارش شماره:</b> {o.id}")
            status_lbl = QLabel(o.status)
            status_lbl.setStyleSheet("color: #ef4565;")

            lay.addWidget(icon_lbl); lay.addWidget(text_lbl); lay.addStretch(); lay.addWidget(status_lbl)
            item.setSizeHint(widget.sizeHint())
            self.results_list.addItem(item)
            self.results_list.setItemWidget(item, widget)

        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)

    def on_item_clicked(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.item_selected.emit(data[0], data[1])
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            curr = self.results_list.currentItem()
            if curr: self.on_item_clicked(curr)
        elif event.key() == Qt.Key.Key_Up:
            self.results_list.setCurrentRow(max(0, self.results_list.currentRow() - 1))
        elif event.key() == Qt.Key.Key_Down:
            self.results_list.setCurrentRow(min(self.results_list.count() - 1, self.results_list.currentRow() + 1))
        else:
            super().keyPressEvent(event)
