import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
try:
    import pandas as pd
except ImportError:
    pd = None

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QMessageBox, QFileDialog, QGraphicsDropShadowEffect, QLineEdit,
    QComboBox, QDialog, QGridLayout, QSizePolicy, QApplication, QInputDialog,
    QCheckBox, QTabWidget, QTextBrowser
)
from PyQt6.QtGui import QColor, QFont, QTextDocument, QPageSize, QDrag, QCursor, QPixmap
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
        self.setFixedSize(800, 750) # Made it wider for preview
        self.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_MAIN};")
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

        # --- Tab Widget ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid #333; background: {BG_COLOR}; }}
            QTabBar::tab {{ background: {PANEL_BG}; color: {TEXT_SUB}; padding: 10px 20px; }}
            QTabBar::tab:selected {{ background: {ACCENT_COLOR}; color: white; }}
        """)

        # --- Tab 1: General Info ---
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

        self.tabs.addTab(content, "اطلاعات کلی")

        # --- Tab 2: Invoice Preview ---
        preview_tab = QWidget()
        p_lay = QVBoxLayout(preview_tab)
        self.txt_preview = QTextBrowser()
        self.txt_preview.setStyleSheet("background: white; color: black; border-radius: 8px;")
        p_lay.addWidget(self.txt_preview)
        self.tabs.addTab(preview_tab, "پیش‌نمایش فاکتور")

        # Load Preview
        self.update_invoice_preview()

        # --- Tab 3: Audit Trail ---
        audit_tab = QWidget()
        a_lay = QVBoxLayout(audit_tab)
        self.audit_list = QScrollArea()
        self.audit_list.setWidgetResizable(True)
        self.audit_container = QWidget()
        self.audit_vbox = QVBoxLayout(self.audit_container)
        self.audit_vbox.addStretch()
        self.audit_list.setWidget(self.audit_container)
        a_lay.addWidget(self.audit_list)
        self.tabs.addTab(audit_tab, "تاریخچه تغییرات")

        self.load_audit_trail()

        layout.addWidget(self.tabs)

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

    def update_invoice_preview(self):
        # Generate HTML
        date_str = self.order_data['created_at'].strftime("%Y/%m/%d")
        user_info = {
            "name": self.order_data['user_name'],
            "phone": self.order_data['phone'],
            "address": self.order_data['address']
        }
        html = self.parent_widget._generate_invoice_html(
            self.order_data['id'], date_str, user_info,
            self.order_data['items'], self.order_data['total_amount']
        )
        self.txt_preview.setHtml(html)

    def load_audit_trail(self):
        with next(get_db()) as db:
            from db.models import AuditLog
            logs = db.query(AuditLog).filter(
                AuditLog.target_type == 'order',
                AuditLog.target_id == str(self.order_data['id'])
            ).order_by(AuditLog.created_at.desc()).all()

            for log in logs:
                item = QFrame()
                item.setStyleSheet(f"background: {PANEL_BG}; border-radius: 8px; margin-bottom: 5px; border-right: 4px solid {ACCENT_COLOR};")
                l = QVBoxLayout(item)
                header = QHBoxLayout()
                action = QLabel(f"<b>{log.action}</b>")
                time = QLabel(log.created_at.strftime("%Y/%m/%d %H:%M"))
                time.setStyleSheet(f"color: {TEXT_SUB}; font-size: 10px;")
                header.addWidget(action); header.addStretch(); header.addWidget(time)
                desc = QLabel(log.description)
                desc.setStyleSheet(f"color: {TEXT_SUB}; font-size: 11px;")
                l.addLayout(header); l.addWidget(desc)
                self.audit_vbox.insertWidget(0, item)

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
    selectionChanged = pyqtSignal(int, bool)

    def __init__(self, order_data: Dict[str, Any], parent_widget):
        super().__init__()
        self.data = order_data
        self.order_id = order_data['id']
        self.parent_widget = parent_widget
        self.setDragEnabled(True)

        self.setObjectName("kanban_card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(220) # Increased height for thumbnails

        col_conf = next((c for c in KANBAN_COLUMNS if c["id"] == self.data['status']), {"color": TEXT_SUB})
        status_color = col_conf["color"]

        # Platform Contrast & Status Urgency
        bg_tint = "rgba(41, 128, 185, 0.05)" if self.data['platform'] == 'telegram' else "rgba(142, 68, 173, 0.05)"

        urgency_border = ""
        now = datetime.now()
        if self.data['status'] == "pending_payment" and (now - self.data['created_at']).total_seconds() > 86400:
            urgency_border = f"border: 2px solid {DANGER_COLOR};"

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20); shadow.setColor(QColor(0, 0, 0, 60)); shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self.setStyleSheet(f"""
            QFrame#kanban_card {{
                background-color: {CARD_BG}; border-radius: 12px;
                border-left: 5px solid {status_color};
                background: {bg_tint};
                {urgency_border}
            }}
            QFrame#kanban_card:hover {{ background-color: #34363a; }}
            QLabel {{ border: none; background: transparent; color: {TEXT_MAIN}; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # هدر
        top_row = QHBoxLayout()
        self.chk_select = QCheckBox()
        self.chk_select.setFixedSize(20, 20)
        self.chk_select.stateChanged.connect(lambda s: self.selectionChanged.emit(self.order_id, s == 2))
        top_row.addWidget(self.chk_select)

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

        # --- Product Thumbnails ---
        thumb_layout = QHBoxLayout()
        thumb_layout.setSpacing(4)
        for item in self.data.get('items', [])[:4]: # Show max 4 thumbs
            img_lbl = QLabel()
            img_lbl.setFixedSize(35, 35)
            img_lbl.setStyleSheet("background: #111; border-radius: 4px; border: 1px solid #333;")
            if item.get('image'):
                pix = QPixmap(str(BASE_DIR / item['image']))
                if not pix.isNull():
                    img_lbl.setPixmap(pix.scaled(35, 35, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
                else: img_lbl.setText("?")
            else: img_lbl.setText("?")
            img_lbl.setToolTip(item['name'])
            thumb_layout.addWidget(img_lbl)
        thumb_layout.addStretch()
        layout.addLayout(thumb_layout)

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
        self.color = color
        
        self.setStyleSheet(f"QFrame {{ background-color: {PANEL_BG}; border-radius: 16px; border: 1px solid #2e2e38; }}")
        self.setFixedWidth(300)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 15, 12, 15)
        main_layout.setSpacing(10)

        # هدر
        header_layout = QVBoxLayout()
        top_h = QHBoxLayout()
        ico = qta.icon(icon_name, color=color)
        lbl_ico = QLabel(); lbl_ico.setPixmap(ico.pixmap(20, 20))
        header_lbl = QLabel(title)
        header_lbl.setStyleSheet(f"color: white; font-weight: bold; font-size: 14px;")
        
        self.count_badge = QLabel("0")
        self.count_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_badge.setFixedSize(25, 25)
        self.count_badge.setStyleSheet(f"background-color: rgba(255,255,255,0.05); color: {color}; border-radius: 12px; font-weight: bold;")
        
        top_h.addWidget(lbl_ico)
        top_h.addWidget(header_lbl)
        top_h.addStretch()
        top_h.addWidget(self.count_badge)
        header_layout.addLayout(top_h)

        # Summary Badge (Total Amount)
        self.lbl_total_sum = QLabel("مجموع: 0 تومان")
        self.lbl_total_sum.setStyleSheet(f"color: {TEXT_SUB}; font-size: 11px;")
        header_layout.addWidget(self.lbl_total_sum)

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
        self.update_stats()

    def clear_all(self):
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.empty_lbl.show()
        self.update_stats()

    def update_stats(self):
        count = self.cards_layout.count() - 1
        self.count_badge.setText(str(count))

        total_sum = 0
        for i in range(self.cards_layout.count()):
            item = self.cards_layout.itemAt(i).widget()
            if isinstance(item, OrderCard):
                total_sum += item.data['total_amount']

        self.lbl_total_sum.setText(f"مجموع: {int(total_sum):,} تومان")

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
        self.selected_order_ids = set()

        # Auto refresh timer
        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.timeout.connect(self.refresh_data)

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
        self.search_inp.setPlaceholderText("🔍 جستجو نام یا محصول...")
        self.search_inp.setFixedWidth(200)
        self.search_inp.setStyleSheet(f"background: {PANEL_BG}; border: 1px solid #3a3a4e; border-radius: 8px; padding: 8px 12px; color: white;")
        self.search_inp.textChanged.connect(self.filter_cards)
        header_layout.addWidget(self.search_inp)

        # Auto Refresh Toggle
        self.btn_auto_refresh = QPushButton("بروزرسانی خودکار: خاموش")
        self.btn_auto_refresh.setCheckable(True)
        self.btn_auto_refresh.setStyleSheet(f"background: {PANEL_BG}; border: 1px solid #3a3a4e; border-radius: 8px; padding: 8px; color: {TEXT_SUB};")
        self.btn_auto_refresh.clicked.connect(self.toggle_auto_refresh)
        header_layout.addWidget(self.btn_auto_refresh)

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

        # --- Advanced Filter Panel ---
        self.filter_panel = QFrame()
        self.filter_panel.setStyleSheet(f"background: {PANEL_BG}; border-radius: 12px; border: 1px solid #2e2e38;")
        self.filter_panel.setFixedHeight(60)
        f_lay = QHBoxLayout(self.filter_panel)
        f_lay.setContentsMargins(15, 0, 15, 0)

        f_lay.addWidget(QLabel("پلتفرم:"))
        self.cmb_plat = QComboBox()
        self.cmb_plat.addItems(["همه", "تلگرام", "روبیکا"])
        self.cmb_plat.currentIndexChanged.connect(self.filter_cards)
        f_lay.addWidget(self.cmb_plat)

        f_lay.addWidget(QLabel("زمان:"))
        self.cmb_date = QComboBox()
        self.cmb_date.addItems(["همه زمان‌ها", "امروز", "دیروز", "هفته اخیر"])
        self.cmb_date.currentIndexChanged.connect(self.filter_cards)
        f_lay.addWidget(self.cmb_date)

        f_lay.addWidget(QLabel("مبلغ از:"))
        self.inp_min_price = QLineEdit()
        self.inp_min_price.setPlaceholderText("0")
        self.inp_min_price.setFixedWidth(80)
        self.inp_min_price.textChanged.connect(self.filter_cards)
        f_lay.addWidget(self.inp_min_price)

        f_lay.addStretch()

        btn_clear_filters = QPushButton("پاکسازی فیلترها")
        btn_clear_filters.setFlat(True)
        btn_clear_filters.setStyleSheet(f"color: {ACCENT_COLOR}; font-weight: bold;")
        btn_clear_filters.clicked.connect(self.clear_filters)
        f_lay.addWidget(btn_clear_filters)

        main_layout.addWidget(self.filter_panel)

        # --- Bulk Actions Toolbar ---
        self.bulk_toolbar = QFrame()
        self.bulk_toolbar.setStyleSheet(f"background: {ACCENT_COLOR}; border-radius: 12px;")
        self.bulk_toolbar.setFixedHeight(50)
        self.bulk_toolbar.setVisible(False)
        b_lay = QHBoxLayout(self.bulk_toolbar)

        self.lbl_bulk_info = QLabel("0 مورد انتخاب شده")
        self.lbl_bulk_info.setStyleSheet("color: white; font-weight: bold;")
        b_lay.addWidget(self.lbl_bulk_info)
        b_lay.addStretch()

        btn_bulk_approve = QPushButton("تایید همگانی")
        btn_bulk_approve.setStyleSheet("background: white; color: black; border-radius: 6px; padding: 4px 10px;")
        btn_bulk_approve.clicked.connect(lambda: self.bulk_change_status("approved"))
        b_lay.addWidget(btn_bulk_approve)

        btn_bulk_cancel = QPushButton("لغو انتخاب")
        btn_bulk_cancel.setFlat(True)
        btn_bulk_cancel.setStyleSheet("color: white;")
        btn_bulk_cancel.clicked.connect(self.clear_selection)
        b_lay.addWidget(btn_bulk_cancel)

        main_layout.addWidget(self.bulk_toolbar)

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

    def toggle_auto_refresh(self, checked):
        if checked:
            self.auto_refresh_timer.start(30000) # 30 seconds
            self.btn_auto_refresh.setText("بروزرسانی خودکار: روشن")
            self.btn_auto_refresh.setStyleSheet(f"background: {SUCCESS_COLOR}20; border: 1px solid {SUCCESS_COLOR}; border-radius: 8px; padding: 8px; color: {SUCCESS_COLOR};")
        else:
            self.auto_refresh_timer.stop()
            self.btn_auto_refresh.setText("بروزرسانی خودکار: خاموش")
            self.btn_auto_refresh.setStyleSheet(f"background: {PANEL_BG}; border: 1px solid #3a3a4e; border-radius: 8px; padding: 8px; color: {TEXT_SUB};")

    def clear_filters(self):
        self.search_inp.clear()
        self.cmb_plat.setCurrentIndex(0)
        self.cmb_date.setCurrentIndex(0)
        self.inp_min_price.clear()
        self.filter_cards()

    def clear_selection(self):
        self.selected_order_ids.clear()
        self.refresh_data() # To uncheck all boxes

    def on_order_selected(self, order_id, checked):
        if checked: self.selected_order_ids.add(order_id)
        else: self.selected_order_ids.discard(order_id)

        count = len(self.selected_order_ids)
        self.bulk_toolbar.setVisible(count > 0)
        self.lbl_bulk_info.setText(f"{count} مورد انتخاب شده")

    @asyncSlot()
    async def bulk_change_status(self, new_status):
        if not self.selected_order_ids: return
        if QMessageBox.question(self, "تایید گروهی", f"آیا از تغییر وضعیت {len(self.selected_order_ids)} سفارش مطمئن هستید؟") == QMessageBox.StandardButton.Yes:
            for oid in list(self.selected_order_ids):
                await self.update_order_status(oid, new_status)
            self.clear_selection()

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
                            "items": [{"name": i.product.name if i.product else "؟",
                                       "qty": i.quantity,
                                       "total": i.quantity * i.price_at_purchase,
                                       "image": i.product.image_path if i.product else None} for i in o.items] if o.items else []
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
            card = OrderCard(data, self)
            card.selectionChanged.connect(self.on_order_selected)
            self.columns_map[status].add_card(card)

    def filter_cards(self, *args):
        text = self.search_inp.text().lower().strip()
        plat = self.cmb_plat.currentText()
        date_f = self.cmb_date.currentIndex()
        min_p = 0
        try: min_p = int(self.inp_min_price.text() or "0")
        except: pass

        for col in self.columns_map.values(): col.clear_all()

        now = datetime.now()

        for data in self.all_orders_cache:
            # Search Filter
            product_names = " ".join([i['name'] for i in data.get('items', [])]).lower()
            if text and (text not in str(data['id']) and text not in data['user_name'].lower() and text not in product_names):
                continue

            # Platform Filter
            if plat != "همه" and data['platform'] != plat.lower().replace('تلگرام', 'telegram').replace('روبیکا', 'rubika'):
                continue

            # Date Filter
            if date_f == 1: # Today
                if data['created_at'].date() != now.date(): continue
            elif date_f == 2: # Yesterday
                if data['created_at'].date() != (now - timedelta(days=1)).date(): continue
            elif date_f == 3: # Last Week
                if data['created_at'] < (now - timedelta(days=7)): continue

            # Price Filter
            if data['total_amount'] < min_p:
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
