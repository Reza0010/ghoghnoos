import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
try:
    import pandas as pd
except ImportError:
    pd = None

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QMessageBox, QFileDialog, QGraphicsDropShadowEffect, QLineEdit,
    QComboBox, QDialog, QGridLayout, QSizePolicy, QApplication, QInputDialog
)
from PyQt6.QtGui import QColor, QFont, QTextDocument, QPageSize, QDrag, QCursor
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt6.QtCore import Qt, QTimer, QSize, QMimeData, pyqtSignal
from qasync import asyncSlot
import qtawesome as qta

from db.database import get_db
from db import crud
from config import BASE_DIR

logger = logging.getLogger(__name__)

# --- پالت رنگی ---
BG_COLOR = "#16161a"
PANEL_BG = "#242629"
CARD_BG = "#2a2c30"
ACCENT_COLOR = "#7f5af0"
SUCCESS_COLOR = "#2cb67d"
INFO_COLOR = "#3da9fc"
WARNING_COLOR = "#ff9f1c"
DANGER_COLOR = "#ef4565"
TEXT_MAIN = "#fffffe"
TEXT_SUB = "#94a1b2"

KANBAN_COLUMNS = [
    {"id": "pending_payment", "title": "در انتظار پرداخت", "icon": "fa5s.hourglass-half", "color": "#f72585"},
    {"id": "approved",        "title": "تایید شده",       "icon": "fa5s.check-circle",   "color": "#4cc9f0"},
    {"id": "shipped",         "title": "ارسال شده",       "icon": "fa5s.truck",          "color": "#4361ee"},
    {"id": "rejected",        "title": "لغو شده",         "icon": "fa5s.times-circle",   "color": "#ef4565"},
    {"id": "paid",            "title": "پرداخت شده",      "icon": "fa5s.money-bill-wave","color": "#2cb67d"}
]

# --- تابع کمکی برای نمایش زمان ---
def time_ago(dt):
    if not dt: return ""
    now = datetime.now()
    diff = now - dt
    secs = diff.total_seconds()
    if secs < 60: return "همین الان"
    elif secs < 3600: return f"{int(secs/60)} دقیقه پیش"
    elif secs < 86400: return f"{int(secs/3600)} ساعت پیش"
    else: return dt.strftime("%m/%d")

# ==============================================================================
# دیالوگ جزئیات سفارش (پیشرفته با دکمه‌های کپی و اقدام)
# ==============================================================================
class OrderDetailDialog(QDialog):
    def __init__(self, order_data, parent_widget):
        super().__init__(parent_widget)
        self.order_data = order_data
        self.parent_widget = parent_widget
        self.setWindowTitle(f"جزئیات سفارش #{order_data['id']}")
        self.setFixedSize(550, 650)
        self.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_MAIN}; border: 1px solid #333;")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- هدر ---
        header = QFrame()
        header.setStyleSheet(f"background-color: {PANEL_BG}; border-bottom: 1px solid #333;")
        header_layout = QHBoxLayout(header)
        title = QLabel(f"فاکتور سفارش #{self.order_data['id']}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 15px;")
        
        btn_print = QPushButton(" چاپ")
        btn_print.setIcon(qta.icon("fa5s.print", color="white"))
        btn_print.setStyleSheet(f"background: {INFO_COLOR}; color: white; border-radius: 5px; padding: 5px 10px;")
        btn_print.clicked.connect(lambda: self.parent_widget.print_invoice(self.order_data['id']))
        
        btn_close = QPushButton(qta.icon('fa5s.times', color=TEXT_SUB), "")
        btn_close.setFlat(True)
        btn_close.clicked.connect(self.close)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(btn_print)
        header_layout.addWidget(btn_close)
        layout.addWidget(header)

        # --- محتوا ---
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(10)

        # اطلاعات مشتری (با دکمه کپی)
        user_box = QFrame()
        user_box.setStyleSheet(f"background: {PANEL_BG}; border-radius: 10px; padding: 10px;")
        user_grid = QGridLayout(user_box)
        user_grid.setSpacing(10)
        
        # ردیف 1: نام
        user_grid.addWidget(self._info_label("مشتری:", "fa5s.user"), 0, 0)
        user_grid.addWidget(self._value_label(self.order_data.get('user_name')), 0, 1)
        
        # ردیف 2: تلفن (با دکمه کپی)
        user_grid.addWidget(self._info_label("تلفن:", "fa5s.phone"), 1, 0)
        phone_w = self._copyable_value(self.order_data.get('phone'))
        user_grid.addWidget(phone_w, 1, 1)

        # ردیف 3: آدرس (با دکمه کپی)
        user_grid.addWidget(self._info_label("آدرس:", "fa5s.map-marker-alt"), 2, 0)
        address_w = self._copyable_value(self.order_data.get('address'))
        user_grid.addWidget(address_w, 2, 1)
        
        # ردیف 4: کد رهگیری
        if self.order_data.get('tracking_code'):
            user_grid.addWidget(self._info_label("کد رهگیری:", "fa5s.truck"), 3, 0)
            track_w = self._copyable_value(self.order_data.get('tracking_code'))
            user_grid.addWidget(track_w, 3, 1)

        content_layout.addWidget(user_box)

        # لیست محصولات
        items_lbl = QLabel("محصولات")
        items_lbl.setStyleSheet(f"color: {TEXT_SUB}; font-weight: bold; margin-top: 10px;")
        content_layout.addWidget(items_lbl)

        list_frame = QFrame()
        list_frame.setStyleSheet(f"background: {BG_COLOR}; border-radius: 8px;")
        list_lay = QVBoxLayout(list_frame)
        
        total_price = 0
        for item in self.order_data.get('items', []):
            row = QHBoxLayout()
            name = QLabel(item['name'])
            name.setStyleSheet("font-size: 13px;")
            qty = QLabel(f"{item['qty']} عدد")
            qty.setStyleSheet(f"color: {TEXT_SUB}; font-size: 12px;")
            price = QLabel(f"{int(item['total']):,} ت")
            price.setStyleSheet(f"color: {SUCCESS_COLOR}; font-weight: bold;")
            
            row.addWidget(name)
            row.addStretch()
            row.addWidget(qty)
            row.addWidget(price)
            list_lay.addLayout(row)
            total_price += item['total']
            
        content_layout.addWidget(list_frame)
        content_layout.addStretch()

        # --- فوتر و اقدامات ---
        footer = QFrame()
        footer.setStyleSheet(f"background-color: {PANEL_BG}; border-top: 1px solid #333; padding: 10px;")
        footer_lay = QHBoxLayout(footer)
        
        total_val = QLabel(f"مبلغ کل: {int(self.order_data.get('total', 0)):,} تومان")
        total_val.setStyleSheet(f"font-size: 16px; font-weight: 900; color: {SUCCESS_COLOR};")
        footer_lay.addWidget(total_val)
        footer_lay.addStretch()

        # دکمه‌های تغییر وضعیت سریع
        current_status = self.order_data.get('status')
        if current_status == "pending_payment":
            footer_lay.addWidget(self._action_btn("تایید", SUCCESS_COLOR, lambda: self.do_action("approved")))
            footer_lay.addWidget(self._action_btn("رد", DANGER_COLOR, lambda: self.do_action("rejected")))
        elif current_status == "approved":
            footer_lay.addWidget(self._action_btn("ارسال شد", INFO_COLOR, lambda: self.do_action("shipped")))

        layout.addWidget(content)
        layout.addWidget(footer, alignment=Qt.AlignmentFlag.AlignBottom)

    def _action_btn(self, text, color, callback):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"background: {color}; color: white; border-radius: 8px; padding: 8px 15px; font-weight: bold;")
        btn.clicked.connect(callback)
        return btn

    def _info_label(self, text, icon_name):
        lbl = QLabel(f"  {text}")
        lbl.setPixmap(qta.icon(icon_name, color=ACCENT_COLOR).pixmap(16, 16))
        lbl.setStyleSheet(f"color: {TEXT_SUB}; font-size: 12px;")
        return lbl

    def _value_label(self, text):
        lbl = QLabel(str(text) if text else "-")
        lbl.setStyleSheet("color: white; font-size: 13px;")
        lbl.setWordWrap(True)
        return lbl

    def _copyable_value(self, text):
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0,0,0,0)
        lay.setSpacing(5)
        lbl = QLabel(str(text) if text else "-")
        lbl.setStyleSheet("color: white;")
        btn = QPushButton()
        btn.setFixedSize(20, 20)
        btn.setIcon(qta.icon("fa5s.copy", color=TEXT_SUB))
        btn.setStyleSheet("background: transparent; border: none;")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip("کپی")
        btn.clicked.connect(lambda: QApplication.clipboard().setText(str(text)))
        lay.addWidget(lbl)
        lay.addWidget(btn)
        lay.addStretch()
        return w

    def do_action(self, status):
        self.close()
        if status == "shipped":
            self.parent_widget.initiate_ship_process(self.order_data['id'])
        else:
            self.parent_widget.change_status_safe(self.order_data['id'], status)    
# ==============================================================================
# کارت سفارش (با Drag و زمان نسبی)
# ==============================================================================
class OrderCard(QFrame):
    def __init__(self, order_data: Dict[str, Any], parent_widget):
        super().__init__()
        self.data = order_data
        self.order_id = order_data['id']
        self.parent_widget = parent_widget
        self.setDragEnabled(True)

        self.setObjectName("kanban_card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(180)

        col_conf = next((c for c in KANBAN_COLUMNS if c["id"] == self.data['status']), {"color": TEXT_SUB})
        status_color = col_conf["color"]

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20); shadow.setColor(QColor(0, 0, 0, 60)); shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self.setStyleSheet(f"""
            QFrame#kanban_card {{
                background-color: {CARD_BG}; border-radius: 12px;
                border-left: 4px solid {status_color}; border-top: 1px solid #333;
                border-right: 1px solid #333; border-bottom: 1px solid #333;
            }}
            QFrame#kanban_card:hover {{ background-color: #34363a; }}
            QLabel {{ border: none; background: transparent; color: {TEXT_MAIN}; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # هدر
        top_row = QHBoxLayout()
        lbl_id = QLabel(f"#{self.order_id}")
        lbl_id.setStyleSheet("font-weight: bold; font-size: 12px; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px;")
        lbl_price = QLabel(f"{int(self.data['total_amount']):,} ت")
        lbl_price.setStyleSheet(f"font-weight: 900; font-size: 15px; color: {SUCCESS_COLOR};")
        top_row.addWidget(lbl_id)
        top_row.addStretch()
        top_row.addWidget(lbl_price)
        layout.addLayout(top_row)

        # کاربر
        user_row = QHBoxLayout()
        plat_icon = qta.icon('fa5b.telegram', color=INFO_COLOR) if self.data['platform'] == 'telegram' else qta.icon('mdi6.infinity', color=ACCENT_COLOR)
        ico = QLabel(); ico.setPixmap(plat_icon.pixmap(16, 16))
        lbl_user = QLabel(self.data['user_name'][:20])
        lbl_user.setStyleSheet("color: #d1d1d1; font-size: 13px;")
        user_row.addWidget(ico); user_row.addSpacing(5); user_row.addWidget(lbl_user); user_row.addStretch()
        layout.addLayout(user_row)

        # زمان نسبی و کد رهگیری
        info_row = QHBoxLayout()
        time_lbl = QLabel(time_ago(self.data['created_at']))
        time_lbl.setStyleSheet(f"color: {TEXT_SUB}; font-size: 11px;")
        info_row.addWidget(time_lbl)
        
        # اگر کد رهگیری دارد
        if self.data['status'] == 'shipped' and self.data.get('tracking_code'):
            track_lbl = QLabel(f"🚚 {self.data['tracking_code']}")
            track_lbl.setStyleSheet(f"color: {INFO_COLOR}; font-size: 11px; font-weight: bold;")
            info_row.addStretch()
            info_row.addWidget(track_lbl)
            
        layout.addLayout(info_row)

        # خط جداکننده
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #3a3a4e; margin-top: 2px;"); line.setFixedHeight(1)
        layout.addWidget(line)

        # دکمه‌ها
        actions_layout = QHBoxLayout(); actions_layout.setSpacing(8)
        
        if self.data['status'] == "pending_payment":
            self._add_action_btn(actions_layout, "تایید", SUCCESS_COLOR, lambda: self.parent_widget.change_status_safe(self.order_id, "approved"))
        elif self.data['status'] == "approved":
             self._add_action_btn(actions_layout, "ارسال", INFO_COLOR, lambda: self.parent_widget.initiate_ship_process(self.order_id))

        btn_detail = QPushButton("جزئیات")
        btn_detail.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_detail.setStyleSheet("background: transparent; color: white; border: 1px solid #4a4a5e; border-radius: 6px; padding: 4px 10px; font-size: 11px;")
        btn_detail.clicked.connect(lambda: self.parent_widget.show_order_details(self.order_id))
        actions_layout.addWidget(btn_detail)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)

    def _add_action_btn(self, layout, text, color, callback):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(28)
        btn.setStyleSheet(f"background: {color}; color: white; border-radius: 6px; padding: 4px 12px; font-weight: bold; font-size: 11px;")
        btn.clicked.connect(callback)
        layout.addWidget(btn)

    def setDragEnabled(self, enabled):
        self._drag_enabled = enabled

    def mouseMoveEvent(self, event):
        if self._drag_enabled and event.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(str(self.order_id))
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)
# ==============================================================================
# ستون کانبان
# ==============================================================================
class KanbanColumn(QFrame):
    order_dropped = pyqtSignal(int, str)

    def __init__(self, title, icon_name, color, status_id, parent=None):
        super().__init__(parent)
        self.status_id = status_id
        self.setAcceptDrops(True)
        
        self.setStyleSheet(f"QFrame {{ background-color: {PANEL_BG}; border-radius: 16px; border: 1px solid #2e2e38; }}")
        self.setFixedWidth(300)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 15, 12, 15)
        main_layout.setSpacing(10)

        # هدر
        header_layout = QHBoxLayout()
        ico = qta.icon(icon_name, color=color)
        lbl_ico = QLabel(); lbl_ico.setPixmap(ico.pixmap(20, 20))
        header_lbl = QLabel(title)
        header_lbl.setStyleSheet(f"color: white; font-weight: bold; font-size: 14px;")
        
        self.count_badge = QLabel("0")
        self.count_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_badge.setFixedSize(25, 25)
        self.count_badge.setStyleSheet(f"background-color: rgba(255,255,255,0.05); color: {color}; border-radius: 12px; font-weight: bold;")
        
        header_layout.addWidget(lbl_ico)
        header_layout.addWidget(header_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.count_badge)
        main_layout.addLayout(header_layout)

        # اسکرول
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_area.verticalScrollBar().setStyleSheet("QScrollBar:vertical { background: transparent; width: 8px; } QScrollBar::handle:vertical { background: #3a3a4e; border-radius: 4px; }")
        
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(0, 0, 0, 10)
        self.cards_layout.addStretch()

        self.scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll_area)
        
        self.empty_lbl = QLabel("سفارشی نیست")
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setStyleSheet(f"color: {TEXT_SUB}; font-size: 12px; padding: 20px;")
        self.cards_layout.insertWidget(0, self.empty_lbl)

    def add_card(self, card_widget):
        if self.cards_layout.count() == 2: self.empty_lbl.hide()
        self.cards_layout.insertWidget(0, card_widget)
        self.update_count()

    def clear_all(self):
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.empty_lbl.show()
        self.update_count()

    def update_count(self):
        count = self.cards_layout.count() - 1
        self.count_badge.setText(str(count))

    def dragEnterEvent(self, event):
        if event.mimeData().hasText(): event.acceptProposedAction()

    def dropEvent(self, event):
        order_id = int(event.mimeData().text())
        self.order_dropped.emit(order_id, self.status_id)

# ==============================================================================
# ویجت اصلی
# ==============================================================================
class OrdersWidget(QWidget):
    def __init__(self, bot_app=None, rubika_client=None):
        super().__init__()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.bot_app = bot_app
        self.rubika_client = rubika_client
        self.columns_map = {}
        self.all_orders_cache = []
        self.setup_ui()
        self._data_loaded = False

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # هدر
        header_layout = QHBoxLayout()
        title = QLabel("📦 مدیریت سفارشات"); title.setStyleSheet("font-size: 24px; font-weight: 900; color: white;")
        subtitle = QLabel("نمای کانبان"); subtitle.setStyleSheet(f"color: {TEXT_SUB}; font-size: 12px;")
        title_box = QVBoxLayout(); title_box.addWidget(title); title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        self.search_inp = QLineEdit()
        self.search_inp.setPlaceholderText("🔍 جستجو...")
        self.search_inp.setFixedWidth(200)
        self.search_inp.setStyleSheet(f"background: {PANEL_BG}; border: 1px solid #3a3a4e; border-radius: 8px; padding: 8px 12px; color: white;")
        self.search_inp.textChanged.connect(self.filter_cards)
        header_layout.addWidget(self.search_inp)

        self.btn_refresh = QPushButton()
        self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='white'))
        self.btn_refresh.setFixedSize(40, 40)
        self.btn_refresh.setStyleSheet(f"background-color: {PANEL_BG}; border-radius: 10px; border: 1px solid #3a3a4e;")
        self.btn_refresh.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.btn_refresh)

        btn_export = QPushButton(" خروجی اکسل"); btn_export.setIcon(qta.icon('fa5s.file-excel', color='white'))
        btn_export.setStyleSheet("background-color: #2cb67d; color: white; border: none; border-radius: 10px; padding: 10px 20px; font-weight: bold;")
        btn_export.clicked.connect(self.export_to_excel)
        header_layout.addWidget(btn_export)

        main_layout.addLayout(header_layout)

        # بورد
        scroll_container = QScrollArea()
        scroll_container.setWidgetResizable(True)
        scroll_container.setStyleSheet("background: transparent; border: none;")
        board_widget = QWidget()
        self.board_layout = QHBoxLayout(board_widget)
        self.board_layout.setSpacing(15)
        self.board_layout.setContentsMargins(0, 0, 0, 0)

        for col_conf in KANBAN_COLUMNS:
            col_widget = KanbanColumn(col_conf["title"], col_conf["icon"], col_conf["color"], col_conf["id"], self)
            col_widget.order_dropped.connect(self.handle_drop)
            self.columns_map[col_conf["id"]] = col_widget
            self.board_layout.addWidget(col_widget)

        self.board_layout.addStretch()
        scroll_container.setWidget(board_widget)
        main_layout.addWidget(scroll_container)

    def handle_drop(self, order_id, target_status):
        if target_status == "shipped": self.initiate_ship_process(order_id)
        else: self.change_status_safe(order_id, target_status)

    def initiate_ship_process(self, order_id):
        text, ok = QInputDialog.getText(self, 'ارسال سفارش', 'لطفا کد رهگیری پستی را وارد کنید:')
        if ok and text:
            asyncio.create_task(self.update_order_status(order_id, "shipped", tracking_code=text))
        elif ok:
            QMessageBox.warning(self, "هشدار", "کد رهگیری الزامی است.")

    @asyncSlot()
    async def refresh_data(self):
        self.btn_refresh.setEnabled(False)
        self.search_inp.clear()
        for col in self.columns_map.values(): col.clear_all()

        loop = asyncio.get_running_loop()
        try:
            def fetch():
                with next(get_db()) as db:
                    orders = crud.get_filtered_orders(db, status="all")
                    res = []
                    for o in orders:
                        user_name = o.user.full_name if o.user else "Unknown"
                        platform = o.user.platform if o.user else "telegram"
                        res.append({
                            "id": o.id, "user_id": o.user_id, "user_name": user_name,
                            "platform": platform, "total_amount": o.total_amount,
                            "status": o.status, "created_at": o.created_at,
                            "items_count": len(o.items) if o.items else 0,
                            "tracking_code": o.tracking_code or "",
                            "phone": o.phone_number,
                            "address": o.shipping_address,
                            "items": [{"name": i.product.name if i.product else "؟", "qty": i.quantity, "total": i.quantity * i.price_at_purchase} for i in o.items] if o.items else []
                        })
                    return res

            self.all_orders_cache = await loop.run_in_executor(None, fetch)
            for data in self.all_orders_cache:
                self._add_card_to_column(data)
        except Exception as e:
            logger.error(f"Refresh Error: {e}")
        finally:
            self.btn_refresh.setEnabled(True)

    def _add_card_to_column(self, data):
        status = data['status']
        if status in self.columns_map:
            self.columns_map[status].add_card(OrderCard(data, self))

    def filter_cards(self, text):
        text = text.lower().strip()
        for col in self.columns_map.values(): col.clear_all()
        for data in self.all_orders_cache:
            if text and text not in str(data['id']) and text not in data['user_name'].lower():
                continue
            self._add_card_to_column(data)

    def filter_by_order_id(self, order_id):
        """فیلتر کردن بر اساس یک سفارش خاص (استفاده توسط پالت جستجو)"""
        self.search_inp.setText(str(order_id))
        self.filter_cards(str(order_id))

    def change_status_safe(self, order_id, new_status):
        asyncio.create_task(self.update_order_status(order_id, new_status))

    async def update_order_status(self, order_id, new_status, tracking_code=None):
        loop = asyncio.get_running_loop()
        try:
            def db_op():
                with next(get_db()) as db:
                    order = db.query(crud.models.Order).get(order_id)
                    if order:
                        order.status = new_status
                        if tracking_code: order.tracking_code = tracking_code
                        db.commit()
                        return order
                    return None

            updated_order = await loop.run_in_executor(None, db_op)

            if updated_order and updated_order.user:
                user_platform = updated_order.user.platform
                user_id = updated_order.user_id

                status_texts = {
                    "approved": "سفارش شما تایید شد.",
                    "rejected": "سفارش شما لغو شد.",
                    "shipped": "سفارش شما ارسال شد."
                }
                msg_text = status_texts.get(new_status, f"وضعیت سفارش: {new_status}")
                full_msg = f"🔔 **وضعیت سفارش #{order_id}**\n\n{msg_text}"

                # ارسال به تلگرام
                if user_platform == "telegram" and self.bot_app:
                    try:
                        await self.bot_app.bot.send_message(chat_id=int(user_id), text=full_msg.replace("**", "<b>").replace("**", "</b>"), parse_mode="HTML")
                    except Exception as e:
                        logger.error(f"TG Notify Error: {e}")

                # ارسال به روبیکا
                elif user_platform == "rubika" and self.rubika_client:
                    try:
                        await self.rubika_client.api.send_message(chat_id=user_id, text=full_msg.replace("**", ""))
                    except Exception as e:
                        logger.error(f"RB Notify Error: {e}")

            await self.refresh_data()
            if hasattr(self.window(), 'show_toast'): self.window().show_toast("وضعیت سفارش تغییر کرد.")

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"{e}")
            
    @asyncSlot()
    async def show_order_details(self, order_id):
        order_data = next((o for o in self.all_orders_cache if o['id'] == order_id), None)
        if order_data:
            dialog = OrderDetailDialog(order_data, self)
            dialog.exec()        

    def print_invoice(self, order_id):
        try:
            with next(get_db()) as db:
                order = crud.get_order_by_id(db, order_id)
                if not order: return

                items = []
                for item in order.items:
                    items.append({
                        "name": item.product.name if item.product else "محصول حذف شده",
                        "qty": item.quantity,
                        "price": item.price_at_purchase,
                        "total": item.quantity * item.price_at_purchase
                    })

                user_info = {
                    "name": order.user.full_name if order.user else "ناشناس",
                    "phone": order.phone_number or "-",
                    "address": order.shipping_address or "-"
                }

                date_str = order.created_at.strftime("%Y/%m/%d - %H:%M")
                total = order.total_amount
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error: {e}")
            return

        html_content = self._generate_invoice_html(order_id, date_str, user_info, items, total)

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        preview = QPrintPreviewDialog(printer, self)
        preview.setWindowTitle(f"چاپ فاکتور سفارش #{order_id}")
        preview.setMinimumSize(1000, 800)

        def handle_paint(printer_obj):
            doc = QTextDocument()
            font_path = BASE_DIR / "fonts" / "Vazirmatn.ttf"
            if font_path.exists():
                 doc.setDefaultFont(QFont("Vazirmatn", 10))
            else:
                 doc.setDefaultFont(QFont("Tahoma", 10))
            doc.setHtml(html_content)
            doc.print(printer_obj)

        preview.paintRequested.connect(handle_paint)
        preview.exec()

    def _generate_invoice_html(self, order_id, date, user, items, total):
        rows = ""
        for idx, item in enumerate(items, 1):
            rows += f"""<tr><td style="text-align: center;">{idx}</td><td>{item['name']}</td><td style="text-align: center;">{item['qty']}</td><td style="text-align: right;">{int(item['price']):,}</td><td style="text-align: right;">{int(item['total']):,}</td></tr>"""

        return f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="fa">
        <head>
        <style>
        body {{ font-family: 'Vazirmatn', 'Tahoma', sans-serif; padding: 20px; direction: rtl; }}
        .header {{ text-align: center; border-bottom: 2px solid #ddd; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background-color: #f0f0f0; padding: 10px; border: 1px solid #ddd; text-align: center; font-weight: bold; }}
        td {{ padding: 10px; border: 1px solid #ddd; }}
        </style>
        </head>
        <body>
        <div class="header"><h1>فاکتور فروش</h1><p>تاریخ: {date}</p></div>
        <div style="margin-bottom: 20px;">
        <p><strong>خریدار:</strong> {user['name']}</p>
        <p><strong>تلفن:</strong> {user['phone']}</p>
        <p><strong>آدرس:</strong> {user['address']}</p>
        <p><strong>شماره سفارش:</strong> #{order_id}</p>
        </div>
        <table>
        <thead><tr><th width="5%">#</th><th>شرح کالا</th><th width="10%">تعداد</th><th width="20%">قیمت واحد</th><th width="20%">قیمت کل</th></tr></thead>
        <tbody>{rows}</tbody>
        </table>
        <h3 style="text-align: left; margin-top: 20px;">مبلغ قابل پرداخت: {int(total):,} تومان</h3>
        </body>
        </html>
        """

    @asyncSlot()
    async def export_to_excel(self):
        if pd is None:
            QMessageBox.warning(self, "خطا", "کتابخانه pandas نصب نیست.")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "ذخیره اکسل", "Orders.xlsx", "Excel (*.xlsx)")
        if not file_path: return

        loop = asyncio.get_running_loop()
        try:
            def save():
                data = self.all_orders_cache
                if not data: return False
                df = pd.DataFrame(data)
                if 'user_id' in df.columns: del df['user_id']
                df.to_excel(file_path, index=False)
                return True

            res = await loop.run_in_executor(None, save)
            if res:
                if hasattr(self.window(), 'show_toast'): self.window().show_toast("فایل اکسل ذخیره شد.")
            else:
                QMessageBox.warning(self, "توجه", "داده‌ای وجود ندارد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", str(e))

    @asyncSlot()
    async def show_order_details(self, order_id):
        try:
            with next(get_db()) as db:
                order = crud.get_order_by_id(db, order_id)
                if not order: return

                details = f"""
                📦 <b>جزئیات سفارش #{order.id}</b>
                
                👤 <b>مشتری:</b> {order.user.full_name if order.user else 'ناشناس'}
                📱 <b>تلفن:</b> {order.phone_number or '-'}
                📍 <b>آدرس:</b> {order.shipping_address or '-'}
                📮 <b>کد پستی:</b> {order.postal_code or '-'}
                
                💰 <b>مبلغ کل:</b> {int(order.total_amount):,} تومان
                🚚 <b>هزینه ارسال:</b> {int(order.shipping_cost):,} تومان
                🏷 <b>وضعیت:</b> {order.status}
                🕒 <b>تاریخ:</b> {order.created_at.strftime('%Y/%m/%d %H:%M')}
                """

                if order.tracking_code:
                    details += f"\n📦 <b>کد رهگیری:</b> <code>{order.tracking_code}</code>"

                details += "\n\n<b>--- محصولات ---</b>\n"
                for item in order.items:
                    details += f"\n🔸 {item.product.name if item.product else 'حذف شده'}\n   {item.quantity} × {int(item.price_at_purchase):,} = {int(item.quantity * item.price_at_purchase):,} ت"

                QMessageBox.information(self, f"جزئیات سفارش #{order_id}", details)
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"دریافت جزئیات با خطا مواجه شد: {str(e)}")