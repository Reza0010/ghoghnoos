import asyncio
import shutil
import logging
import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QProgressBar, QListWidget, QListWidgetItem,
    QStackedWidget, QFrame, QScrollArea, QTimeEdit, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QCheckBox, QDialog, QGridLayout, QInputDialog, QAbstractSpinBox,
    QSpinBox
)
from PyQt6.QtGui import QColor, QPixmap, QPainter, QFont, QPen, QBrush
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QTime, QEasingCurve, pyqtProperty, QRect, QSize
from qasync import asyncSlot
import qtawesome as qta

from db.database import get_db
from db import crud, models
from config import BASE_DIR

logger = logging.getLogger(__name__)

# --- پالت رنگی ---
BG_COLOR = "#16161a"
PANEL_BG = "#242629"
CARD_BG = "#2a2c30"
ACCENT_COLOR = "#7f5af0"
SUCCESS_COLOR = "#2cb67d"
INFO_COLOR = "#3da9fc"
WARNING_COLOR = "#f39c12"
DANGER_COLOR = "#ef4565"
TEXT_MAIN = "#fffffe"
TEXT_SUB = "#94a1b2"
BORDER_COLOR = "#2e2e38"

# ==============================================================================
# ویجت‌های کمکی (Validated Inputs)
# ==============================================================================
class CardNumberInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.setMaxLength(19)
        self.textChanged.connect(self.format_text)
        self.setStyleSheet(f"""
            QLineEdit {{ background: {BG_COLOR}; border: 1px solid {BORDER_COLOR};
                border-radius: 8px; padding: 10px; color: {TEXT_MAIN}; font-size: 14px; font-weight: bold; }}
            QLineEdit:focus {{ border: 1px solid {ACCENT_COLOR}; }}
            QLineEdit[valid="false"] {{ border: 2px solid {DANGER_COLOR}; background: #2a1a1a; }}
        """)

    def format_text(self, text):
        clean = re.sub(r'[^\d]', '', text)
        formatted = ""
        for i, char in enumerate(clean):
            if i > 0 and i % 4 == 0: formatted += "-"
            formatted += char
            if i >= 15: break
        
        if text != formatted:
            self.blockSignals(True)
            self.setText(formatted)
            self.setCursorPosition(len(formatted))
            self.blockSignals(False)
        
        self.setProperty("valid", "true" if len(clean) == 16 else "false")
        self.style().unpolish(self); self.style().polish(self)

class FormattedPriceInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.textChanged.connect(self.format_text)
        self.setStyleSheet(f"""
            QLineEdit {{ background: {BG_COLOR}; border: 1px solid {BORDER_COLOR};
                border-radius: 8px; padding: 10px; color: {SUCCESS_COLOR}; font-weight: bold; font-size: 14px; }}
        """)

    def format_text(self, text):
        if not text: return
        clean = re.sub(r'[^\d]', '', text)
        if not clean: return
        formatted = f"{int(clean):,}"
        if text != formatted:
            self.blockSignals(True)
            self.setText(formatted)
            self.setCursorPosition(len(formatted))
            self.blockSignals(False)

class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(50, 26)
        self._circle_position = 3
        self.animation = QPropertyAnimation(self, b"circle_position", self)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.setDuration(300)
        self.stateChanged.connect(self.start_transition)

    @pyqtProperty(int)
    def circle_position(self): return self._circle_position
    @circle_position.setter
    def circle_position(self, pos): self._circle_position = pos; self.update()

    def start_transition(self, state):
        self.animation.stop()
        self.animation.setEndValue(self.width() - 23 if state else 3)
        self.animation.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(SUCCESS_COLOR if self.isChecked() else "#4a4a62")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, self.width(), self.height(), 13, 13)
        p.setBrush(QBrush(QColor("#ffffff")))
        p.drawEllipse(self._circle_position, 3, 20, 20)
        p.end()

class SettingCard(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{ background-color: {PANEL_BG}; border-radius: 12px; border: 1px solid {BORDER_COLOR}; }}
            QLabel {{ color: {TEXT_MAIN}; border: none; background: transparent; }}
            QLineEdit, QTextEdit, QComboBox, QTimeEdit, QSpinBox {{
                background-color: {BG_COLOR}; color: {TEXT_MAIN}; border: 1px solid {BORDER_COLOR};
                border-radius: 8px; padding: 8px;
            }}
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        lbl = QLabel(title)
        lbl.setStyleSheet(f"color: {ACCENT_COLOR}; font-weight: bold; font-size: 15px;")
        self.layout.addWidget(lbl)
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background: {BORDER_COLOR}; max-height: 1px;")
        self.layout.addWidget(line)

    def add_widget(self, w): self.layout.addWidget(w)
    def add_layout(self, l): self.layout.addLayout(l)

# --- اعتبارسنجی ---
def validate_support_ids(ids): return all(isinstance(i, str) and len(i) > 2 for i in ids)
def validate_bank_cards(cards):
    for c in cards:
        if not re.match(r"\d{16,19}", c.get("number", "")): return False
        if not c.get("owner", "").strip(): return False
    return True
def validate_phone_numbers(phones): return all(re.match(r"09\d{9}", p) or re.match(r"\+989\d{9}", p) for p in phones)

class SettingsWidget(QWidget):
    TELEGRAM_TEMPLATES = {
        "پیش‌فرض": "سلام {user_name} عزیز 👋\nبه فروشگاه {shop_name} خوش آمدید.",
        "رسمی": "با سلام،\nکاربر گرامی {user_name}، ورود شما به {shop_name} را گرامی می‌داریم.",
        "فروش ویژه": "🔥 {user_name} جان!\nفروش ویژه امروز فقط برای شماست!",
        "سفارشی": ""
    }
    RUBIKA_TEMPLATES = {
        "پیش‌فرض": "سلام {user_name} عزیز\nبه {shop_name} خوش اومدی 😊",
        "رسمی": "با سلام\nکاربر گرامی {user_name}، خوش آمدید.",
        "سفارشی": ""
    }

    def __init__(self, bot_app=None, rubika_client=None):
        super().__init__()
        self.bot_app = bot_app
        self.rubika_client = rubika_client
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._broadcast_image_path = None
        self.setup_ui()
        self._data_loaded = False

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- نوار ناوبری ---
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(220)
        self.nav_list.setStyleSheet(f"""
            QListWidget {{ background: {BG_COLOR}; border-left: 1px solid {BORDER_COLOR}; padding-top: 20px; outline: none; }}
            QListWidget::item {{ height: 50px; color: {TEXT_SUB}; padding-right: 15px; border-right: 3px solid transparent; }}
            QListWidget::item:selected {{ color: {TEXT_MAIN}; background: {PANEL_BG}; border-right: 3px solid {ACCENT_COLOR}; font-weight: bold; }}
        """)

        nav_items = [
            (" تنظیمات پایه", "fa5s.network-wired"),
            (" کدهای تخفیف", "fa5s.ticket-alt"),
            (" مدیریت پروکسی", "fa5s.shield-alt"),
            (" پاسخگوی خودکار", "fa5s.robot"),
            (" ربات تلگرام", "fa5b.telegram"),
            (" ربات روبیکا", "fa5s.infinity"),
            (" مالی و ارسال", "fa5s.credit-card"),
            (" ابزارها", "fa5s.tools"),
            (" گزارشات", "fa5s.file-alt")
        ]

        for t, i in nav_items:
            item = QListWidgetItem(t)
            item.setIcon(qta.icon(i, color=ACCENT_COLOR))
            self.nav_list.addItem(item)

        self.nav_list.currentRowChanged.connect(self.change_page)
        main_layout.addWidget(self.nav_list)

        # --- صفحات محتوا ---
        self.pages_stack = QStackedWidget()
        self.pages_stack.addWidget(self._ui_core_page())
        self.pages_stack.addWidget(self._ui_coupons_page())
        self.pages_stack.addWidget(self._ui_proxy_page())
        self.pages_stack.addWidget(self._ui_auto_reply_page())
        self.pages_stack.addWidget(self._ui_telegram_page())
        self.pages_stack.addWidget(self._ui_rubika_page())
        self.pages_stack.addWidget(self._ui_payment_page())
        self.pages_stack.addWidget(self._ui_tools_page())
        self.pages_stack.addWidget(self._ui_logs_page())

        main_layout.addWidget(self.pages_stack)
        self.nav_list.setCurrentRow(0)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._data_loaded:
            QTimer.singleShot(200, self.refresh_data)
            self._data_loaded = True

    def change_page(self, index):
        self.pages_stack.setCurrentIndex(index)
        
    # ==================== UI Pages ====================

    def _ui_core_page(self):
        page = QWidget()
        layout = QVBoxLayout(page); layout.setContentsMargins(30, 30, 30, 30)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget(); v_box = QVBoxLayout(container); v_box.setSpacing(25)

        # کارت توکن‌ها
        card_tokens = SettingCard("توکن‌های اتصال (Bot Tokens)")
        self.tg_token_inp = QLineEdit(); self.tg_token_inp.setPlaceholderText("Telegram Bot Token")
        self.rb_token_inp = QLineEdit(); self.rb_token_inp.setPlaceholderText("Rubika Bot Token")
        card_tokens.add_layout(self._form_row("توکن تلگرام:", self.tg_token_inp))
        card_tokens.add_layout(self._form_row("توکن روبیکا:", self.rb_token_inp))
        v_box.addWidget(card_tokens)

        # کارت شبکه و پراکسی
        card_network = SettingCard("تنظیمات شبکه و پراکسی")
        self.proxy_url_inp = QLineEdit(); self.proxy_url_inp.setPlaceholderText("http://username:password@ip:port")
        self.proxy_enabled = ToggleSwitch()
        card_network.add_layout(self._form_row("استفاده از پراکسی:", self.proxy_enabled))
        card_network.add_layout(self._form_row("آدرس پراکسی:", self.proxy_url_inp))
        v_box.addWidget(card_network)

        # کارت دسترسی ادمین‌ها
        card_admins = SettingCard("مدیریت دسترسی ادمین‌ها")
        self.admin_ids_main = QTextEdit(); self.admin_ids_main.setPlaceholderText("آیدی‌های عددی را با کاما جدا کنید...")
        self.admin_ids_main.setMaximumHeight(80)
        card_admins.add_widget(QLabel("شناسه ادمین‌های مجاز (تلگرام):"))
        card_admins.add_widget(self.admin_ids_main)
        v_box.addWidget(card_admins)

        btn_save = QPushButton("💾 ذخیره تنظیمات پایه")
        btn_save.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; padding: 12px; border-radius: 10px; font-weight: bold;")
        btn_save.clicked.connect(self.save_settings)
        v_box.addWidget(btn_save)

        btn_restart = QPushButton("🔄 راه‌اندازی مجدد سرویس‌ها")
        btn_restart.setStyleSheet(f"background: {PANEL_BG}; border: 1px solid {WARNING_COLOR}; color: {WARNING_COLOR}; padding: 10px; border-radius: 10px;")
        btn_restart.clicked.connect(self.restart_all_services)
        v_box.addWidget(btn_restart)

        v_box.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        return page

    def _ui_coupons_page(self):
        page = QWidget()
        layout = QVBoxLayout(page); layout.setContentsMargins(30, 30, 30, 30)

        card = SettingCard("مدیریت کدهای تخفیف (Coupons)")
        self.coupon_table = QTableWidget(0, 6)
        self.coupon_table.setHorizontalHeaderLabels(["کد", "تخفیف", "ظرفیت", "استفاده شده", "تاریخ انقضا", "عملیات"])
        self.coupon_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.coupon_table.setStyleSheet(f"background: {BG_COLOR}; border-radius: 8px;")

        btn_add = QPushButton(" ➕ تعریف کد تخفیف جدید")
        btn_add.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; padding: 10px; border-radius: 8px;")
        btn_add.clicked.connect(self.show_add_coupon_dialog)

        card.add_widget(self.coupon_table)
        card.add_widget(btn_add)
        layout.addWidget(card)
        layout.addStretch()

        QTimer.singleShot(1000, self.load_coupons)
        return page

    def _ui_proxy_page(self):
        page = QWidget()
        layout = QVBoxLayout(page); layout.setContentsMargins(30, 30, 30, 30); layout.setSpacing(20)

        card = SettingCard("مدیریت پروکسی‌های پیشرفته (Hiddify / V2Ray / Standard)")

        self.proxy_table = QTableWidget(0, 6)
        self.proxy_table.setHorizontalHeaderLabels(["نام", "پروتکل", "آدرس:پورت", "وضعیت", "تأخیر", "عملیات"])
        self.proxy_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.proxy_table.setStyleSheet(f"background: {BG_COLOR}; border-radius: 8px;")

        h_btns = QHBoxLayout()
        btn_add = QPushButton(" ➕ افزودن دستی")
        btn_add.setStyleSheet(f"background: {BG_COLOR}; border: 1px solid {ACCENT_COLOR}; color: {ACCENT_COLOR}; padding: 10px; border-radius: 8px; font-weight: bold;")
        btn_add.clicked.connect(self.show_add_proxy_dialog)

        btn_import = QPushButton(" 🔗 وارد کردن لینک (V2Ray/Hiddify)")
        btn_import.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; padding: 10px; border-radius: 8px; font-weight: bold;")
        btn_import.clicked.connect(self.show_import_proxy_dialog)

        h_btns.addWidget(btn_add); h_btns.addWidget(btn_import)

        card.add_widget(self.proxy_table)
        card.add_layout(h_btns)
        layout.addWidget(card)

        hint = QLabel("💡 نکته: پروکسی فعال برای اتصال ربات تلگرام استفاده می‌شود. لینک‌های V2Ray برای اتصال مستقیم نیاز به هسته Xray دارند.")
        hint.setStyleSheet(f"color: {TEXT_SUB}; font-size: 11px;")
        layout.addWidget(hint)
        layout.addStretch()

        QTimer.singleShot(600, self.load_proxies)
        return page

    def _ui_telegram_page(self):
        page = QWidget()
        layout = QVBoxLayout(page); layout.setContentsMargins(20, 20, 20, 20)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget(); v_box = QVBoxLayout(container); v_box.setSpacing(20)

        # --- کارت هویت و برندینگ ---
        card1 = SettingCard("هویت و برندینگ فروشگاه")
        row_name = QHBoxLayout()
        self.tg_shop_name = QLineEdit(); self.tg_shop_name.setPlaceholderText("نام فروشگاه")
        self.tg_toggle_status = ToggleSwitch()
        row_name.addWidget(QLabel("نام فروشگاه:")); row_name.addWidget(self.tg_shop_name)
        row_name.addStretch()
        row_name.addWidget(QLabel("باز/بسته:")); row_name.addWidget(self.tg_toggle_status)
        card1.add_layout(row_name)

        h_branding = QHBoxLayout()
        self.lbl_logo_path = QLineEdit(); self.lbl_logo_path.setPlaceholderText("مسیر لوگو (برای فاکتورها)"); self.lbl_logo_path.setReadOnly(True)
        btn_logo = QPushButton("انتخاب لوگو"); btn_logo.setStyleSheet(f"background: {INFO_COLOR}; color: white; padding: 5px;")
        btn_logo.clicked.connect(self.select_branding_logo)
        h_branding.addWidget(self.lbl_logo_path); h_branding.addWidget(btn_logo)
        card1.add_layout(h_branding)

        self.bot_footer_text = QLineEdit(); self.bot_footer_text.setPlaceholderText("متن فوتر پیام‌های ربات (مثلاً لینک کانال یا کپی‌رایت)")
        card1.add_layout(self._form_row("متن فوتر:", self.bot_footer_text))

        self.tg_shop_address = QTextEdit(); self.tg_shop_address.setPlaceholderText("آدرس فیزیکی فروشگاه...")
        self.tg_shop_address.setMaximumHeight(60)
        card1.add_widget(QLabel("آدرس فروشگاه:"))
        card1.add_widget(self.tg_shop_address)
        v_box.addWidget(card1)

        # --- کارت ساعات کاری ---
        card_hours = SettingCard("تنظیمات ساعات کاری خودکار")
        self.op_hours_enabled = ToggleSwitch()
        self.op_hours_start = QTimeEdit(); self.op_hours_end = QTimeEdit()

        card_hours.add_layout(self._form_row("فعالسازی زمانبندی:", self.op_hours_enabled))
        h_times = QHBoxLayout()
        h_times.addWidget(QLabel("از ساعت:")); h_times.addWidget(self.op_hours_start)
        h_times.addSpacing(20)
        h_times.addWidget(QLabel("تا ساعت:")); h_times.addWidget(self.op_hours_end)
        h_times.addStretch()
        card_hours.add_layout(h_times)
        v_box.addWidget(card_hours)

        # --- کارت ارتباطات ---
        card2 = SettingCard("اطلاعات تماس و پشتیبانی")
        # لیست آیدی‌ها
        self.tg_support_ids_list = QListWidget()
        self.tg_support_ids_list.setFixedHeight(100)
        self.tg_support_ids_list.setStyleSheet(f"background: {BG_COLOR}; border-radius: 8px;")
        self.tg_phones_list = QListWidget()
        self.tg_phones_list.setFixedHeight(100)
        self.tg_phones_list.setStyleSheet(f"background: {BG_COLOR}; border-radius: 8px;")
        
        btn_add_id = QPushButton("افزودن آیدی"); btn_add_id.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; border-radius: 5px; padding: 5px;")
        btn_add_id.clicked.connect(self.add_tg_support_id)
        btn_del_id = QPushButton("حذف"); btn_del_id.setStyleSheet(f"background: transparent; color: {DANGER_COLOR}; border: 1px solid {DANGER_COLOR}; border-radius: 5px;")
        btn_del_id.clicked.connect(self.remove_tg_support_id)
        
        h_btns_id = QHBoxLayout()
        h_btns_id.addStretch(); h_btns_id.addWidget(btn_del_id); h_btns_id.addWidget(btn_add_id)

        card2.add_widget(QLabel("آیدی‌های پشتیبانی:"))
        card2.add_widget(self.tg_support_ids_list)
        card2.add_layout(h_btns_id)
        
        # تلفن‌ها
        btn_add_phone = QPushButton("افزودن تلفن"); btn_add_phone.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; border-radius: 5px; padding: 5px;")
        btn_add_phone.clicked.connect(self.add_tg_phone)
        btn_del_phone = QPushButton("حذف"); btn_del_phone.setStyleSheet(f"background: transparent; color: {DANGER_COLOR}; border: 1px solid {DANGER_COLOR}; border-radius: 5px;")
        btn_del_phone.clicked.connect(self.remove_tg_phone)
        h_btns_phone = QHBoxLayout()
        h_btns_phone.addStretch(); h_btns_phone.addWidget(btn_del_phone); h_btns_phone.addWidget(btn_add_phone)
        
        card2.add_widget(QLabel("تلفن‌های پشتیبانی:"))
        card2.add_widget(self.tg_phones_list)
        card2.add_layout(h_btns_phone)
        v_box.addWidget(card2)

        # --- کارت پیام خوش‌آمدگویی ---
        card3 = SettingCard("پیام خوش‌آمدگویی (/start)")
        h_prev = QHBoxLayout()
        
        # بخش ویرایش متن
        v_edit = QVBoxLayout()
        self.tg_template_combo = QComboBox()
        self.tg_template_combo.addItems(self.TELEGRAM_TEMPLATES.keys())
        self.tg_template_combo.currentIndexChanged.connect(self.apply_tg_template)
        self.tg_welcome_msg = QTextEdit()
        self.tg_welcome_msg.setPlaceholderText("متن پیام...")
        self.tg_welcome_msg.textChanged.connect(self.update_preview)
        v_edit.addWidget(QLabel("قالب آماده:"))
        v_edit.addWidget(self.tg_template_combo)
        v_edit.addWidget(QLabel("متن پیام:"))
        v_edit.addWidget(self.tg_welcome_msg)

        # بخش پیش‌نمایش
        prev_frame = QFrame()
        prev_frame.setFixedWidth(300)
        prev_frame.setStyleSheet(f"background: #0e0e10; border-radius: 20px; border: 2px solid #333;")
        p_lay = QVBoxLayout(prev_frame)
        p_lay.setContentsMargins(10, 10, 10, 10)
        
        mock_header = QLabel("Telegram")
        mock_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mock_header.setStyleSheet("color: white; font-weight: bold; background: #242424; border-radius: 10px; padding: 5px;")
        p_lay.addWidget(mock_header)
        
        self.preview_img = QLabel()
        self.preview_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_img.setFixedHeight(120)
        self.preview_img.setStyleSheet("background: #222; border-radius: 8px;")
        
        msg_bubble = QFrame()
        msg_bubble.setStyleSheet(f"background: #2b5278; border-radius: 10px; padding: 10px;")
        m_lay = QVBoxLayout(msg_bubble)
        self.preview_lbl = QLabel()
        self.preview_lbl.setWordWrap(True)
        self.preview_lbl.setStyleSheet("color: white; font-size: 13px;")
        m_lay.addWidget(self.preview_lbl)
        
        p_lay.addWidget(self.preview_img)
        p_lay.addWidget(msg_bubble)
        p_lay.addStretch()
        
        h_prev.addLayout(v_edit)
        h_prev.addWidget(prev_frame)
        card3.add_layout(h_prev)

        # انتخاب بنر
        h_bnr = QHBoxLayout()
        self.tg_welcome_img_path = QLineEdit(); self.tg_welcome_img_path.setReadOnly(True)
        btn_img = QPushButton("انتخاب بنر"); btn_img.setStyleSheet(f"background: {INFO_COLOR}; color: white; border-radius: 5px;")
        btn_img.clicked.connect(self.on_select_image)
        h_bnr.addWidget(self.tg_welcome_img_path)
        h_bnr.addWidget(btn_img)
        card3.add_layout(h_bnr)
        
        # دکمه آپدیت منو
        btn_cmd = QPushButton("  بروزرسانی منوی ربات")
        btn_cmd.setIcon(qta.icon('fa5s.robot', color=INFO_COLOR))
        btn_cmd.clicked.connect(self.update_bot_commands)
        btn_cmd.setStyleSheet(f"background: {BG_COLOR}; border: 1px dashed {INFO_COLOR}; color: {INFO_COLOR}; border-radius: 8px; padding: 8px;")
        card3.add_widget(btn_cmd)
        
        v_box.addWidget(card3)
        
        # دکمه ذخیره
        self.btn_save_gen = QPushButton("💾 ذخیره تمام تغییرات تلگرام")
        self.btn_save_gen.setStyleSheet(f"background: {SUCCESS_COLOR}; color: white; padding: 12px; border-radius: 8px; font-weight: bold;")
        self.btn_save_gen.clicked.connect(self.save_settings)
        v_box.addWidget(self.btn_save_gen)
        v_box.addStretch()
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        return page

    def _ui_rubika_page(self):
        page = QWidget()
        layout = QVBoxLayout(page); layout.setContentsMargins(20, 20, 20, 20)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget(); v_box = QVBoxLayout(container); v_box.setSpacing(20)

        # --- هویت روبیکا ---
        card1 = SettingCard("هویت ربات روبیکا")
        self.rb_shop_name = QLineEdit()
        self.rb_shop_name.setPlaceholderText("مثلاً: فروشگاه ما")
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("نام فروشگاه:"))
        row1.addWidget(self.rb_shop_name)
        card1.add_layout(row1)
        v_box.addWidget(card1)

        # --- آیدی‌ها و تلفن‌های پشتیبانی روبیکا ---
        card2 = SettingCard("آیدی‌ها و تلفن‌های پشتیبانی (روبیکا)")
        self.rb_support_ids_list = QListWidget()
        self.rb_support_ids_list.setStyleSheet(f"background: {BG_COLOR}; border-radius: 8px;")
        self.rb_phones_list = QListWidget()
        self.rb_phones_list.setStyleSheet(f"background: {BG_COLOR}; border-radius: 8px;")
        
        btn_add_rb = QPushButton("افزودن آیدی"); btn_add_rb.clicked.connect(self.add_rb_support_id)
        btn_del_rb = QPushButton("حذف آیدی"); btn_del_rb.clicked.connect(self.remove_rb_support_id)
        h_btns_rb = QHBoxLayout(); h_btns_rb.addWidget(btn_add_rb); h_btns_rb.addWidget(btn_del_rb)
        
        btn_add_rb_phone = QPushButton("افزودن تلفن"); btn_add_rb_phone.clicked.connect(self.add_rb_phone)
        btn_del_rb_phone = QPushButton("حذف تلفن"); btn_del_rb_phone.clicked.connect(self.remove_rb_phone)
        h_btns_rb_phone = QHBoxLayout(); h_btns_rb_phone.addWidget(btn_add_rb_phone); h_btns_rb_phone.addWidget(btn_del_rb_phone)
        
        card2.add_widget(QLabel("آیدی‌های پشتیبانی:"))
        card2.add_widget(self.rb_support_ids_list)
        card2.add_layout(h_btns_rb)
        card2.add_widget(QLabel("تلفن‌های پشتیبانی:"))
        card2.add_widget(self.rb_phones_list)
        card2.add_layout(h_btns_rb_phone)
        v_box.addWidget(card2)

        # --- پیام خوش‌آمدگویی ---
        card3 = SettingCard("پیام خوش‌آمدگویی")
        self.rb_template_combo = QComboBox()
        self.rb_template_combo.addItems(self.RUBIKA_TEMPLATES.keys())
        self.rb_template_combo.currentIndexChanged.connect(self.apply_rb_template)
        self.rb_welcome_msg = QTextEdit()
        self.rb_welcome_msg.setPlaceholderText("متن خوش‌آمدگویی...")
        v_edit = QVBoxLayout()
        v_edit.addWidget(QLabel("قالب آماده:"))
        v_edit.addWidget(self.rb_template_combo)
        v_edit.addWidget(QLabel("متن پیام:"))
        v_edit.addWidget(self.rb_welcome_msg)
        card3.add_layout(v_edit)
        v_box.addWidget(card3)

        # --- کیبورد اصلی ---
        card4 = SettingCard("منوی اصلی (Reply Keyboard)")
        self.rb_main_menu = QTableWidget(0, 1)
        self.rb_main_menu.setHorizontalHeaderLabels(["دکمه‌ها"])
        self.rb_main_menu.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rb_main_menu.setStyleSheet(f"background: {BG_COLOR}; border-radius: 8px;")
        btn_add_btn = QPushButton("افزودن دکمه")
        btn_add_btn.clicked.connect(self.add_rb_button)
        btn_del_btn = QPushButton("حذف دکمه")
        btn_del_btn.clicked.connect(self.remove_rb_button)
        h_btns_kb = QHBoxLayout(); h_btns_kb.addWidget(btn_add_btn); h_btns_kb.addWidget(btn_del_btn)
        card4.add_widget(self.rb_main_menu)
        card4.add_layout(h_btns_kb)
        v_box.addWidget(card4)

        btn_save_rb = QPushButton("ذخیره تنظیمات روبیکا")
        btn_save_rb.clicked.connect(self.save_rubika_settings)
        btn_save_rb.setStyleSheet(f"background: #8e44ad; color: white; padding: 12px; border-radius: 8px; font-weight: bold;")
        v_box.addWidget(btn_save_rb)
        v_box.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        return page

    def _ui_auto_reply_page(self):
        page = QWidget()
        layout = QVBoxLayout(page); layout.setContentsMargins(30, 30, 30, 30)

        card = SettingCard("پاسخگوی خودکار کلمات کلیدی")
        self.auto_reply_table = QTableWidget(0, 4)
        self.auto_reply_table.setHorizontalHeaderLabels(["کلمه کلیدی", "پاسخ", "نوع تطبیق", "عملیات"])
        self.auto_reply_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.auto_reply_table.setStyleSheet(f"background: {BG_COLOR}; border-radius: 8px;")

        btn_add = QPushButton(" ➕ افزودن قانون جدید")
        btn_add.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; padding: 10px; border-radius: 8px;")
        btn_add.clicked.connect(self.show_add_auto_reply_dialog)

        card.add_widget(self.auto_reply_table)
        card.add_widget(btn_add)
        layout.addWidget(card)
        layout.addStretch()

        QTimer.singleShot(800, self.load_auto_replies)
        return page

    def _ui_payment_page(self):
        page = QWidget()
        layout = QVBoxLayout(page); layout.setContentsMargins(30, 30, 30, 30)

        # بخش وفادارسازی
        card_loyalty = SettingCard("سیستم وفادارسازی مشتریان (Loyalty)")
        self.loyalty_percent = QSpinBox()
        self.loyalty_percent.setRange(0, 100); self.loyalty_percent.setSuffix(" %")
        self.loyalty_percent.setStyleSheet(f"background: {BG_COLOR}; color: white; padding: 8px;")
        card_loyalty.add_layout(self._form_row("درصد هدیه از هر خرید:", self.loyalty_percent))
        layout.addWidget(card_loyalty)

        card1 = SettingCard("حساب‌های بانکی")
        self.card_table = QTableWidget(0, 3)
        self.card_table.setHorizontalHeaderLabels(["شماره کارت", "صاحب حساب", "عملیات"])
        self.card_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.card_table.setStyleSheet(f"background: {BG_COLOR}; border-radius: 8px;")
        btn_add_card = QPushButton("افزودن کارت جدید")
        btn_add_card.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; border-radius: 5px;")
        btn_add_card.clicked.connect(self.add_card_row)
        card1.add_widget(self.card_table)
        card1.add_widget(btn_add_card)
        layout.addWidget(card1)

        card2 = SettingCard("تنظیمات ارسال")
        self.shipping_cost = FormattedPriceInput()
        self.free_limit = FormattedPriceInput()
        card2.add_layout(self._form_row("هزینه ارسال:", self.shipping_cost))
        card2.add_layout(self._form_row("سقف ارسال رایگان:", self.free_limit))
        layout.addWidget(card2)

        card3 = SettingCard("درگاه پرداخت آنلاین (زرین‌پال)")
        self.zarinpal_enabled = ToggleSwitch()
        self.zarinpal_merchant = QLineEdit()
        self.zarinpal_merchant.setPlaceholderText("Merchant ID")
        card3.add_layout(self._form_row("فعال‌سازی درگاه:", self.zarinpal_enabled))
        card3.add_layout(self._form_row("کد مرچنت:", self.zarinpal_merchant))
        layout.addWidget(card3)
        
        btn = QPushButton("ذخیره تنظیمات مالی")
        btn.setStyleSheet(f"background: {SUCCESS_COLOR}; color: white; padding: 12px; border-radius: 8px;")
        btn.clicked.connect(self.save_settings)
        layout.addWidget(btn); layout.addStretch()
        return page

    def _ui_tools_page(self):
        page = QWidget()
        layout = QVBoxLayout(page); layout.setContentsMargins(30, 30, 30, 30)

        # --- بک‌آپ ---
        card_bk = SettingCard("مدیریت بک‌آپ (Backups)")
        self.bk_table = QTableWidget(0, 3)
        self.bk_table.setHorizontalHeaderLabels(["نام فایل", "تاریخ", "حجم"])
        self.bk_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.bk_table.setStyleSheet(f"background: {BG_COLOR}; border-radius: 8px;")
        h_bk = QHBoxLayout()
        b1 = QPushButton("ایجاد بک‌آپ"); b1.setStyleSheet(f"background: {INFO_COLOR}; color: white;")
        b1.clicked.connect(self.create_manual_backup)
        b2 = QPushButton("بازگردانی"); b2.setStyleSheet(f"background: {DANGER_COLOR}; color: white;")
        b2.clicked.connect(self.restore_backup)
        b3 = QPushButton("ارسال به تلگرام"); b3.setStyleSheet(f"background: {ACCENT_COLOR}; color: white;")
        b3.clicked.connect(self.send_backup_to_telegram)
        h_bk.addWidget(b1); h_bk.addWidget(b2); h_bk.addWidget(b3)
        
        # بک‌آپ خودکار
        h_auto = QHBoxLayout()
        self.auto_bk_toggle = ToggleSwitch()  # تعریف متغیر که باعث خطا می‌شد
        self.auto_bk_time = QTimeEdit()
        h_auto.addWidget(QLabel("بک‌آپ خودکار روزانه:"))
        h_auto.addWidget(self.auto_bk_toggle)
        h_auto.addSpacing(20)
        h_auto.addWidget(QLabel("زمان:"))
        h_auto.addWidget(self.auto_bk_time)
        h_auto.addStretch()
        
        card_bk.add_widget(self.bk_table)
        card_pass = SettingCard("امنیت پنل")
        self.panel_pass = QLineEdit()
        self.panel_pass.setPlaceholderText("رمز عبور جدید...")
        self.panel_pass.setEchoMode(QLineEdit.EchoMode.Password)
        card_pass.add_layout(self._form_row("رمز عبور پنل:", self.panel_pass))
        layout.addWidget(card_pass)

        # --- پیام همگانی ---
        card_bc = SettingCard("ارسال پیام همگانی (Broadcast)")
        self.bc_text = QTextEdit(); self.bc_text.setMaximumHeight(80)
        h_bc_img = QHBoxLayout()
        self.lbl_bc_img = QLabel("عکس: بدون عکس")
        btn_bc_img = QPushButton("انتخاب عکس")
        btn_bc_img.setStyleSheet(f"background: {PANEL_BG}; border: 1px solid {BORDER_COLOR};")
        btn_bc_img.clicked.connect(self.select_broadcast_image)
        h_bc_img.addWidget(self.lbl_bc_img); h_bc_img.addWidget(btn_bc_img)
        
        self.bc_progress = QProgressBar(); self.bc_progress.hide()
        btn_bc = QPushButton("ارسال به همه کاربران")
        btn_bc.setStyleSheet(f"background: {DANGER_COLOR}; color: white; padding: 10px; border-radius: 8px;")
        btn_bc.clicked.connect(self.on_start_broadcast)
        
        card_bc.add_widget(self.bc_text)
        card_bc.add_layout(h_bc_img)
        card_bc.add_widget(self.bc_progress)
        card_bc.add_widget(btn_bc)
        layout.addWidget(card_bc)

        card_admin = SettingCard("مدیریت و نقش‌های ادمین")
        self.admin_ids_input = QLineEdit()
        self.admin_ids_input.setPlaceholderText("آیدی‌های ادمین (با کاما جدا کنید)")
        card_admin.add_layout(self._form_row("کل ادمین‌ها:", self.admin_ids_input))

        grid_roles = QGridLayout()
        self.role_sales = QLineEdit(); self.role_sales.setPlaceholderText("آیدی‌های بخش فروش...")
        self.role_support = QLineEdit(); self.role_support.setPlaceholderText("آیدی‌های بخش پشتیبانی...")
        self.role_system = QLineEdit(); self.role_system.setPlaceholderText("آیدی‌های فنی/سیستمی...")

        grid_roles.addWidget(QLabel("اعلان فروش:"), 0, 0); grid_roles.addWidget(self.role_sales, 0, 1)
        grid_roles.addWidget(QLabel("اعلان تیکت:"), 1, 0); grid_roles.addWidget(self.role_support, 1, 1)
        grid_roles.addWidget(QLabel("اعلان انبار:"), 2, 0); grid_roles.addWidget(self.role_system, 2, 1)
        card_admin.add_layout(grid_roles)
        layout.addWidget(card_admin)
        
        QTimer.singleShot(500, self.load_backups_list)
        return page

    def _ui_logs_page(self):
        page = QWidget()
        layout = QVBoxLayout(page); layout.setContentsMargins(30, 30, 30, 30)
        card = SettingCard("لاگ‌های سیستم")
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet(f"background: #0f1015; color: #ccc; font-family: Consolas; border-radius: 8px; padding: 10px;")
        h_btn = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["همه", "ERROR", "WARNING", "INFO"])
        self.filter_combo.currentTextChanged.connect(self.read_app_logs)
        btn_ref = QPushButton("بروزرسانی"); btn_ref.clicked.connect(self.read_app_logs)
        h_btn.addWidget(QLabel("فیلتر:")); h_btn.addWidget(self.filter_combo)
        h_btn.addStretch(); h_btn.addWidget(btn_ref)
        card.add_widget(self.log_viewer)
        card.add_layout(h_btn)
        layout.addWidget(card)
        return page

    # --- Helper Layout ---
    def _form_row(self, label_text, widget):
        h = QHBoxLayout()
        h.addWidget(QLabel(label_text))
        h.addWidget(widget)
        return h

    # --- Logic Methods ---
    
    def add_tg_support_id(self):
        text, ok = QInputDialog.getText(self, "افزودن آیدی", "آیدی تلگرام (مثال: @admin):")
        if ok and text.strip(): QListWidgetItem(text.strip(), self.tg_support_ids_list)

    def remove_tg_support_id(self):
        if self.tg_support_ids_list.currentItem(): self.tg_support_ids_list.takeItem(self.tg_support_ids_list.currentRow())

    def add_tg_phone(self):
        text, ok = QInputDialog.getText(self, "افزودن تلفن", "شماره تلفن:")
        if ok and text.strip():
            if validate_phone_numbers([text.strip()]): QListWidgetItem(text.strip(), self.tg_phones_list)
            else: QMessageBox.warning(self, "خطا", "فرمت شماره صحیح نیست.")

    def remove_tg_phone(self):
        if self.tg_phones_list.currentItem(): self.tg_phones_list.takeItem(self.tg_phones_list.currentRow())

    # Rubika Logic
    def add_rb_support_id(self):
        text, ok = QInputDialog.getText(self, "افزودن آیدی", "آیدی روبیکا:")
        if ok and text.strip(): QListWidgetItem(text.strip(), self.rb_support_ids_list)

    def remove_rb_support_id(self):
        if self.rb_support_ids_list.currentItem(): self.rb_support_ids_list.takeItem(self.rb_support_ids_list.currentRow())

    def add_rb_phone(self):
        text, ok = QInputDialog.getText(self, "افزودن تلفن", "شماره تلفن:")
        if ok and text.strip():
            if validate_phone_numbers([text.strip()]): QListWidgetItem(text.strip(), self.rb_phones_list)
            else: QMessageBox.warning(self, "خطا", "فرمت شماره صحیح نیست.")

    def remove_rb_phone(self):
        if self.rb_phones_list.currentItem(): self.rb_phones_list.takeItem(self.rb_phones_list.currentRow())
        
    def add_card_row(self):
        r = self.card_table.rowCount()
        self.card_table.insertRow(r)
        self.card_table.setCellWidget(r, 0, CardNumberInput())
        self.card_table.setCellWidget(r, 1, QLineEdit())
        del_btn = QPushButton("حذف"); del_btn.setStyleSheet(f"background: {DANGER_COLOR}; color: white;")
        del_btn.clicked.connect(lambda: self.card_table.removeRow(r))
        self.card_table.setCellWidget(r, 2, del_btn)

    def add_rb_button(self):
        text, ok = QInputDialog.getText(self, "افزودن دکمه", "متن دکمه:")
        if ok and text.strip():
            row = self.rb_main_menu.rowCount()
            self.rb_main_menu.insertRow(row)
            self.rb_main_menu.setItem(row, 0, QTableWidgetItem(text.strip()))

    def remove_rb_button(self):
        if self.rb_main_menu.currentRow() >= 0: self.rb_main_menu.removeRow(self.rb_main_menu.currentRow())

    def update_preview(self):
        text = self.tg_welcome_msg.toPlainText()
        shop = self.tg_shop_name.text() or "فروشگاه"
        self.preview_lbl.setText(text.replace("{shop_name}", shop).replace("{user_name}", "کاربر"))

    def apply_tg_template(self):
        t = self.tg_template_combo.currentText()
        if t in self.TELEGRAM_TEMPLATES: self.tg_welcome_msg.setPlainText(self.TELEGRAM_TEMPLATES[t])

    def apply_rb_template(self):
        t = self.rb_template_combo.currentText()
        if t in self.RUBIKA_TEMPLATES: self.rb_welcome_msg.setPlainText(self.RUBIKA_TEMPLATES[t])

    def on_select_image(self):
        f, _ = QFileDialog.getOpenFileName(self, "تصویر", "", "Images (*.jpg *.png *.jpeg)")
        if f: self.tg_welcome_img_path.setText(f)

    def select_branding_logo(self):
        f, _ = QFileDialog.getOpenFileName(self, "انتخاب لوگوی برند", "", "Images (*.jpg *.png *.jpeg)")
        if f: self.lbl_logo_path.setText(f)
        
    def select_broadcast_image(self):
        f, _ = QFileDialog.getOpenFileName(self, "عکس پیام همگانی", "", "Images (*.jpg *.png)")
        if f:
            self._broadcast_image_path = f
            self.lbl_bc_img.setText(f"عکس: {os.path.basename(f)}")

    def read_app_logs(self):
        path = BASE_DIR / "logs" / "app.log"
        if not path.exists(): return
        try:
            with open(path, "r", encoding="utf-8") as f: lines = f.readlines()[-150:]
            html = ""
            filter_key = self.filter_combo.currentText()
            for line in lines:
                if filter_key != "همه" and filter_key not in line: continue
                col = DANGER_COLOR if "ERROR" in line else (WARNING_COLOR if "WARNING" in line else SUCCESS_COLOR)
                html += f"<div style='color:{col}; font-size: 12px;'>{line.strip()}</div>"
            self.log_viewer.setHtml(html)
        except: pass

    def load_coupons(self):
        try:
            with next(get_db()) as db:
                items = crud.get_all_coupons(db)
            self.coupon_table.setRowCount(0)
            for i, item in enumerate(items):
                self.coupon_table.insertRow(i)
                self.coupon_table.setItem(i, 0, QTableWidgetItem(item.code))
                val = f"{item.percent}%" if item.percent > 0 else f"{int(item.amount):,} ت"
                self.coupon_table.setItem(i, 1, QTableWidgetItem(val))
                self.coupon_table.setItem(i, 2, QTableWidgetItem(str(item.usage_limit)))
                self.coupon_table.setItem(i, 3, QTableWidgetItem(str(item.used_count)))
                exp = item.expiry_date.strftime("%Y/%m/%d") if item.expiry_date else "بدون انقضا"
                self.coupon_table.setItem(i, 4, QTableWidgetItem(exp))

                btn_del = QPushButton(); btn_del.setIcon(qta.icon('fa5s.trash-alt', color=DANGER_COLOR))
                btn_del.clicked.connect(lambda _, cid=item.id: self.delete_coupon_ui(cid))
                self.coupon_table.setCellWidget(i, 5, btn_del)
        except: pass

    def show_add_coupon_dialog(self):
        dlg = QDialog(self); dlg.setWindowTitle("تعریف کد تخفیف"); dlg.setFixedWidth(400)
        l = QVBoxLayout(dlg); l.setSpacing(10)

        code = QLineEdit(); code.setPlaceholderText("کد (مثلا: OFF20)")
        percent = QSpinBox(); percent.setRange(0, 100); percent.setSuffix(" %")
        amount = FormattedPriceInput(placeholder="مبلغ ثابت (اگر درصد صفر باشد)")
        limit = QSpinBox(); limit.setRange(1, 10000); limit.setValue(100)
        min_p = FormattedPriceInput(placeholder="حداقل مبلغ خرید")
        expiry = QLineEdit(); expiry.setPlaceholderText("تاریخ انقضا (YYYY-MM-DD)")

        for w in [code, expiry]: w.setStyleSheet(f"background: {BG_COLOR}; color: white; padding: 8px;")

        l.addWidget(QLabel("کد تخفیف (انگلیسی):")); l.addWidget(code)
        l.addWidget(QLabel("درصد تخفیف:")); l.addWidget(percent)
        l.addWidget(QLabel("یا مبلغ ثابت تخفیف (تومان):")); l.addWidget(amount)
        l.addWidget(QLabel("ظرفیت استفاده (تعداد):")); l.addWidget(limit)
        l.addWidget(QLabel("حداقل خرید (تومان):")); l.addWidget(min_p)
        l.addWidget(QLabel("تاریخ انقضا (اختیاری):")); l.addWidget(expiry)

        b = QPushButton("ذخیره کد تخفیف"); b.setStyleSheet(f"background: {SUCCESS_COLOR}; color: white; padding: 10px;")
        l.addWidget(b)

        def save():
            if not code.text(): return
            try:
                exp_date = datetime.strptime(expiry.text(), "%Y-%m-%d") if expiry.text() else None
                data = {
                    "code": code.text().strip().upper(),
                    "percent": percent.value(),
                    "amount": amount.value(),
                    "usage_limit": limit.value(),
                    "min_purchase": min_p.value(),
                    "expiry_date": exp_date
                }
                with next(get_db()) as db: crud.create_coupon(db, data)
                dlg.accept(); self.load_coupons()
            except Exception as e: QMessageBox.warning(dlg, "خطا", "فرمت تاریخ صحیح نیست (YYYY-MM-DD)")

        b.clicked.connect(save); dlg.exec()

    def delete_coupon_ui(self, cid):
        if QMessageBox.question(self, "حذف", "این کد تخفیف حذف شود؟") == QMessageBox.StandardButton.Yes:
            with next(get_db()) as db: crud.delete_coupon(db, cid)
            self.load_coupons()

    def load_proxies(self):
        try:
            with next(get_db()) as db:
                proxies = crud.get_all_proxies(db)

            self.proxy_table.setRowCount(0)
            for i, p in enumerate(proxies):
                self.proxy_table.insertRow(i)
                self.proxy_table.setItem(i, 0, QTableWidgetItem(p.name))
                self.proxy_table.setItem(i, 1, QTableWidgetItem(p.protocol.upper()))
                self.proxy_table.setItem(i, 2, QTableWidgetItem(f"{p.host}:{p.port}"))

                # وضعیت (فعال/غیرفعال)
                status_btn = QPushButton("فعال شود" if not p.is_active else "✅ فعال")
                status_btn.setEnabled(not p.is_active)
                status_btn.setStyleSheet(f"background: {SUCCESS_COLOR if p.is_active else PANEL_BG}; color: white; border-radius: 4px;")
                status_btn.clicked.connect(lambda _, pid=p.id: self.activate_proxy(pid))
                self.proxy_table.setCellWidget(i, 3, status_btn)

                # تأخیر
                lat_text = f"{p.latency}ms" if p.latency else "--"
                self.proxy_table.setItem(i, 4, QTableWidgetItem(lat_text))

                # عملیات
                actions = QWidget(); h = QHBoxLayout(actions); h.setContentsMargins(0,0,0,0)
                b_test = QPushButton(); b_test.setIcon(qta.icon('fa5s.vial', color=INFO_COLOR))
                b_test.setToolTip("تست اتصال"); b_test.clicked.connect(lambda _, pid=p.id: self.test_proxy_connection(pid))
                b_del = QPushButton(); b_del.setIcon(qta.icon('fa5s.trash-alt', color=DANGER_COLOR))
                b_del.setToolTip("حذف"); b_del.clicked.connect(lambda _, pid=p.id: self.delete_proxy_ui(pid))
                h.addWidget(b_test); h.addWidget(b_del)
                self.proxy_table.setCellWidget(i, 5, actions)
        except: pass

    def show_add_proxy_dialog(self):
        dlg = QDialog(self); dlg.setWindowTitle("افزودن پروکسی"); dlg.setFixedWidth(400)
        l = QVBoxLayout(dlg)

        name = QLineEdit(); name.setPlaceholderText("نام (مثلا: هیدیفای اصلی)")
        proto = QComboBox(); proto.addItems(["http", "socks5"])
        host = QLineEdit(); host.setPlaceholderText("آدرس (IP یا Domain)")
        port = QSpinBox(); port.setRange(1, 65535); port.setValue(2080)
        user = QLineEdit(); user.setPlaceholderText("نام کاربری (اختیاری)")
        passw = QLineEdit(); passw.setPlaceholderText("رمز عبور (اختیاری)"); passw.setEchoMode(QLineEdit.EchoMode.Password)

        for w in [name, host, user, passw]: w.setStyleSheet(f"background: {BG_COLOR}; color: white; padding: 8px; border-radius: 5px;")

        l.addWidget(QLabel("نام:")); l.addWidget(name)
        l.addWidget(QLabel("پروتکل:")); l.addWidget(proto)
        l.addWidget(QLabel("آدرس:")); l.addWidget(host)
        l.addWidget(QLabel("پورت:")); l.addWidget(port)
        l.addWidget(QLabel("نام کاربری:")); l.addWidget(user)
        l.addWidget(QLabel("رمز عبور:")); l.addWidget(passw)

        b = QPushButton("ذخیره"); b.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; padding: 10px;")
        l.addWidget(b)

        def save():
            if not host.text() or not name.text(): return
            data = {
                "name": name.text(), "protocol": proto.currentText(),
                "host": host.text(), "port": port.value(),
                "username": user.text() or None, "password": passw.text() or None
            }
            with next(get_db()) as db: crud.add_proxy(db, data)
            dlg.accept(); self.load_proxies()

        b.clicked.connect(save); dlg.exec()

    def show_import_proxy_dialog(self):
        text, ok = QInputDialog.getMultiLineText(self, "وارد کردن لینک", "لینک V2Ray را وارد کنید:")
        if ok and text.strip():
            from bot.proxy_utils import parse_v2ray_link
            data = parse_v2ray_link(text.strip())
            if data:
                with next(get_db()) as db: crud.add_proxy(db, data)
                self.load_proxies()
                self.window().show_toast("لینک با موفقیت وارد شد.")
            else:
                QMessageBox.warning(self, "خطا", "فرمت لینک صحیح نیست.")

    def activate_proxy(self, pid):
        with next(get_db()) as db:
            p = db.query(models.Proxy).get(pid)
            if not p: return

            # چک کردن وجود هسته Xray برای لینک‌های v2ray
            if p.config_type == "link" or p.protocol in ["vless", "vmess", "ss", "trojan"]:
                if not hasattr(self.window(), 'app_manager') or not self.window().app_manager.xray_manager.is_available():
                    QMessageBox.warning(self, "هسته Xray یافت نشد",
                        "برای استفاده از لینک‌های مستقیم V2ray/Hiddify، باید فایل xray.exe را در پوشه tools/xray قرار دهید.\n"
                        "در غیر این صورت ربات قادر به اتصال نخواهد بود.")

            crud.set_active_proxy(db, pid)

        self.load_proxies()
        self.window().show_toast("پروکسی فعال شد. برای اعمال نهایی، سرویس‌ها را ریستارت کنید.")

    def delete_proxy_ui(self, pid):
        if QMessageBox.question(self, "حذف", "آیا این پروکسی حذف شود؟") == QMessageBox.StandardButton.Yes:
            with next(get_db()) as db: crud.delete_proxy(db, pid)
            self.load_proxies()

    @asyncSlot()
    async def test_proxy_connection(self, pid):
        self.window().show_toast("در حال بررسی وضعیت اتصال...")

        with next(get_db()) as db:
            p = db.query(models.Proxy).get(pid)
            if not p: return

        # برای لینک‌های V2Ray (تست مستقیم TCP)
        if p.config_type == "link" or p.protocol in ["vless", "vmess", "ss", "trojan"]:
            from bot.proxy_utils import tcp_ping
            # استفاده از تایم اوت بیشتر در UI
            latency = await tcp_ping(p.host, p.port, timeout=10.0)
            if latency is not None:
                with next(get_db()) as db: crud.update_proxy_latency(db, pid, latency)
                self.load_proxies()
                self.window().show_toast(f"✅ سرور در دسترس است! تأخیر: {latency}ms")
            else:
                self.window().show_toast("❌ خطا: سرور پاسخگو نیست یا IP مسدود است (Timeout)", is_error=True)
            return

        # برای پروکسی‌های استاندارد (SOCKS5/HTTP)
        import time
        import httpx
        proxy_url = f"{p.protocol}://"
        if p.username and p.password: proxy_url += f"{p.username}:{p.password}@"
        proxy_url += f"{p.host}:{p.port}"

        start = time.time()
        try:
            # تست واقعی اتصال به تلگرام از طریق پروکسی
            async with httpx.AsyncClient(proxies=proxy_url, timeout=15) as client:
                resp = await client.get("https://api.telegram.org", follow_redirects=True)
                if resp.status_code in [200, 404]: # 404 هم یعنی به سرور تلگرام رسیده
                    latency = int((time.time() - start) * 1000)
                    with next(get_db()) as db: crud.update_proxy_latency(db, pid, latency)
                    self.load_proxies()
                    self.window().show_toast(f"✅ اتصال موفق! تأخیر: {latency}ms")
                else:
                    self.window().show_toast(f"⚠️ پاسخ غیرمنتظره از سرور: {resp.status_code}", is_error=True)
        except httpx.ConnectError:
            self.window().show_toast("❌ خطا: امکان اتصال به پروکسی وجود ندارد.", is_error=True)
        except httpx.TimeoutException:
            self.window().show_toast("❌ خطا: زمان پاسخگویی پروکسی بیش از حد طولانی شد.", is_error=True)
        except Exception as e:
            self.window().show_toast(f"❌ خطا در اتصال: {str(e)}", is_error=True)

    def load_auto_replies(self):
        try:
            with next(get_db()) as db:
                items = crud.get_all_auto_responses(db)
            self.auto_reply_table.setRowCount(0)
            for i, item in enumerate(items):
                self.auto_reply_table.insertRow(i)
                self.auto_reply_table.setItem(i, 0, QTableWidgetItem(item.keyword))
                self.auto_reply_table.setItem(i, 1, QTableWidgetItem(item.response_text[:50] + "..."))
                self.auto_reply_table.setItem(i, 2, QTableWidgetItem("دقیق" if item.match_type == "exact" else "محتوایی"))

                btn_del = QPushButton(); btn_del.setIcon(qta.icon('fa5s.trash-alt', color=DANGER_COLOR))
                btn_del.clicked.connect(lambda _, rid=item.id: self.delete_auto_reply(rid))
                self.auto_reply_table.setCellWidget(i, 3, btn_del)
        except: pass

    def show_add_auto_reply_dialog(self):
        dlg = QDialog(self); dlg.setWindowTitle("قانون پاسخ خودکار"); dlg.setFixedWidth(450)
        l = QVBoxLayout(dlg)

        kw = QLineEdit(); kw.setPlaceholderText("کلمه کلیدی (مثلا: آدرس)")
        resp = QTextEdit(); resp.setPlaceholderText("متن پاسخ...")
        m_type = QComboBox(); m_type.addItems(["دقیق (Exact)", "محتوایی (Contains)"])

        for w in [kw, resp]: w.setStyleSheet(f"background: {BG_COLOR}; color: white; padding: 8px; border-radius: 5px;")

        l.addWidget(QLabel("کلمه کلیدی:")); l.addWidget(kw)
        l.addWidget(QLabel("نوع تطبیق:")); l.addWidget(m_type)
        l.addWidget(QLabel("متن پاسخ:")); l.addWidget(resp)

        b = QPushButton("ذخیره"); b.setStyleSheet(f"background: {SUCCESS_COLOR}; color: white; padding: 10px;")
        l.addWidget(b)

        def save():
            if not kw.text() or not resp.toPlainText(): return
            match = "exact" if "Exact" in m_type.currentText() else "contains"
            with next(get_db()) as db: crud.set_auto_response(db, kw.text(), resp.toPlainText(), match)
            dlg.accept(); self.load_auto_replies()

        b.clicked.connect(save); dlg.exec()

    def delete_auto_reply(self, rid):
        if QMessageBox.question(self, "حذف", "این قانون حذف شود؟") == QMessageBox.StandardButton.Yes:
            with next(get_db()) as db: crud.delete_auto_response(db, rid)
            self.load_auto_replies()

    @asyncSlot()
    async def refresh_data(self, *args, **kwargs):
        try:
            if not self.window() or not self.isVisible() or getattr(self.window(), '_is_shutting_down', False):
                return
        except (RuntimeError, AttributeError): return

        loop = asyncio.get_running_loop()
        try:
            data = await loop.run_in_executor(None, self._fetch_all_settings)
            # تلگرام و برندینگ
            try:
                self.tg_shop_name.setText(data["tg_shop_name"])
            except RuntimeError: return
            self.tg_toggle_status.setChecked(data["tg_is_open"] == "true")
            self.tg_shop_address.setPlainText(data["tg_shop_address"])
            self.tg_welcome_msg.setPlainText(data["tg_welcome_message"])
            self.tg_welcome_img_path.setText(data["tg_welcome_image"])
            self.lbl_logo_path.setText(data.get("branding_logo", ""))
            self.bot_footer_text.setText(data.get("bot_footer_text", ""))

            # ساعات کاری
            self.op_hours_enabled.setChecked(data.get("op_hours_enabled") == "true")
            self.op_hours_start.setTime(QTime.fromString(data.get("op_hours_start", "08:00"), "HH:mm"))
            self.op_hours_end.setTime(QTime.fromString(data.get("op_hours_end", "22:00"), "HH:mm"))
            
            tg_support_ids = json.loads(data.get("tg_support_ids", "[]"))
            self.tg_support_ids_list.clear()
            for sid in tg_support_ids: self.tg_support_ids_list.addItem(sid)
            tg_phones = json.loads(data.get("tg_phones", "[]"))
            self.tg_phones_list.clear()
            for p in tg_phones: self.tg_phones_list.addItem(p)

            # روبیکا
            self.rb_shop_name.setText(data.get("rb_shop_name", data["tg_shop_name"]))
            rb_support_ids = json.loads(data.get("rb_support_ids", "[]"))
            self.rb_support_ids_list.clear()
            for sid in rb_support_ids: self.rb_support_ids_list.addItem(sid)
            rb_phones = json.loads(data.get("rb_phones", "[]"))
            self.rb_phones_list.clear()
            for p in rb_phones: self.rb_phones_list.addItem(p)
            self.rb_welcome_msg.setPlainText(data.get("rb_welcome_message", ""))
            
            # منوی روبیکا
            rb_menu = json.loads(data.get("rb_main_menu", "[]"))
            self.rb_main_menu.setRowCount(0)
            for btn in rb_menu:
                row = self.rb_main_menu.rowCount()
                self.rb_main_menu.insertRow(row)
                self.rb_main_menu.setItem(row, 0, QTableWidgetItem(btn))

            # مالی
            cards = json.loads(data.get("bank_cards", "[]"))
            self.card_table.setRowCount(0)
            for card in cards:
                self.add_card_row()
                row = self.card_table.rowCount() - 1
                self.card_table.cellWidget(row, 0).setText(card.get("number", ""))
                self.card_table.cellWidget(row, 1).setText(card.get("owner", ""))

            self.shipping_cost.setText(data["shipping_cost"])
            self.free_limit.setText(data["free_shipping_limit"])

            self.zarinpal_enabled.setChecked(data.get("zarinpal_enabled", "false") == "true")
            self.zarinpal_merchant.setText(data.get("zarinpal_merchant", ""))
            self.loyalty_percent.setValue(int(data.get("loyalty_percent", "1")))

            self.panel_pass.setText(data.get("panel_password", "admin"))
            self.admin_ids_input.setText(data.get("admin_user_ids", ""))

            # فیلدهای جدید
            self.tg_token_inp.setText(data.get("telegram_bot_token", ""))
            self.rb_token_inp.setText(data.get("rubika_bot_token", ""))
            self.proxy_url_inp.setText(data.get("proxy_url", ""))
            self.proxy_enabled.setChecked(data.get("proxy_enabled", "false") == "true")
            self.admin_ids_main.setText(data.get("admin_user_ids", ""))

            roles = json.loads(data.get("admin_notification_roles", "{}"))
            self.role_sales.setText(",".join(map(str, roles.get("sales", []))))
            self.role_support.setText(",".join(map(str, roles.get("support", []))))
            self.role_system.setText(",".join(map(str, roles.get("system", []))))

            # بک‌آپ
            self.auto_bk_toggle.setChecked(data["auto_backup_enabled"] == "true")
            try: self.auto_bk_time.setTime(QTime.fromString(data["auto_backup_time"], "HH:mm"))
            except: pass
            
            self.read_app_logs()
        except Exception as e:
            logger.error(e)

    def _fetch_all_settings(self):
        with next(get_db()) as db:
            DEFAULT_SETTINGS = {
                "tg_shop_name": "فروشگاه من", "tg_is_open": "true", "tg_welcome_message": "",
                "tg_welcome_image": "", "tg_support_ids": "[]", "tg_phones": "[]",
                "rb_shop_name": "فروشگاه من", "rb_welcome_message": "", "rb_support_ids": "[]",
                "rb_phones": "[]", "rb_main_menu": "[]", "bank_cards": "[]",
                "shipping_cost": "0", "free_shipping_limit": "0",
                "auto_backup_enabled": "false", "auto_backup_time": "00:00",
                "tg_shop_address": "",
                "zarinpal_enabled": "false", "zarinpal_merchant": "",
                "panel_password": "admin",
                "admin_user_ids": "",
                "branding_logo": "", "bot_footer_text": "",
                "op_hours_enabled": "false", "op_hours_start": "08:00", "op_hours_end": "22:00",
                "admin_notification_roles": "{}",
                "telegram_bot_token": "", "rubika_bot_token": "",
                "proxy_url": "", "proxy_enabled": "false"
            }
            return {k: crud.get_setting(db, k, v) for k, v in DEFAULT_SETTINGS.items()}

    @asyncSlot()
    async def save_settings(self, *args, **kwargs):
        try:
            if not self.window() or not self.isVisible() or getattr(self.window(), '_is_shutting_down', False):
                return
        except (RuntimeError, AttributeError): return

        # نقش‌های ادمین
        roles = {
            "sales": [x.strip() for x in self.role_sales.text().split(',') if x.strip().isdigit()],
            "support": [x.strip() for x in self.role_support.text().split(',') if x.strip().isdigit()],
            "system": [x.strip() for x in self.role_system.text().split(',') if x.strip().isdigit()]
        }

        data = {
            "tg_shop_name": self.tg_shop_name.text(),
            "tg_is_open": "true" if self.tg_toggle_status.isChecked() else "false",
            "tg_shop_address": self.tg_shop_address.toPlainText(),
            "tg_welcome_message": self.tg_welcome_msg.toPlainText(),
            "tg_welcome_image": self.tg_welcome_img_path.text(),
            "branding_logo": self.lbl_logo_path.text(),
            "bot_footer_text": self.bot_footer_text.text(),
            "op_hours_enabled": "true" if self.op_hours_enabled.isChecked() else "false",
            "op_hours_start": self.op_hours_start.time().toString("HH:mm"),
            "op_hours_end": self.op_hours_end.time().toString("HH:mm"),
            "admin_notification_roles": json.dumps(roles),
            "tg_support_ids": json.dumps([self.tg_support_ids_list.item(i).text() for i in range(self.tg_support_ids_list.count())]),
            "tg_phones": json.dumps([self.tg_phones_list.item(i).text() for i in range(self.tg_phones_list.count())]),
            "bank_cards": json.dumps([{"number": self.card_table.cellWidget(r, 0).text(), "owner": self.card_table.cellWidget(r, 1).text()} for r in range(self.card_table.rowCount())]),
            "shipping_cost": self.shipping_cost.text().replace(",", ""),
            "free_shipping_limit": self.free_limit.text().replace(",", ""),
            "auto_backup_enabled": "true" if self.auto_bk_toggle.isChecked() else "false",
            "auto_backup_time": self.auto_bk_time.time().toString("HH:mm"),
            "zarinpal_enabled": "true" if self.zarinpal_enabled.isChecked() else "false",
            "zarinpal_merchant": self.zarinpal_merchant.text().strip(),
            "loyalty_percent": str(self.loyalty_percent.value()),
            "panel_password": self.panel_pass.text().strip() or "admin",
            "admin_user_ids": self.admin_ids_main.toPlainText().strip() or self.admin_ids_input.text().strip(),
            "telegram_bot_token": self.tg_token_inp.text().strip(),
            "rubika_bot_token": self.rb_token_inp.text().strip(),
            "proxy_url": self.proxy_url_inp.text().strip(),
            "proxy_enabled": "true" if self.proxy_enabled.isChecked() else "false"
        }
        # کپی تصاویر برندینگ و بنر
        for key in ["tg_welcome_image", "branding_logo"]:
            img = data[key]
            if img and not img.startswith("media/"):
                suffix = Path(img).suffix
                dest = BASE_DIR / "media" / f"{key}{suffix}"
                try:
                    shutil.copy(img, dest)
                    data[key] = f"media/{dest.name}"
                except: pass
            
        await asyncio.get_running_loop().run_in_executor(None, lambda: self._save_db(data))
        self.window().show_toast("تنظیمات با موفقیت ذخیره شد.")

    @asyncSlot()
    async def save_rubika_settings(self, *args, **kwargs):
        data = {
            "rb_shop_name": self.rb_shop_name.text(),
            "rb_welcome_message": self.rb_welcome_msg.toPlainText(),
            "rb_support_ids": json.dumps([self.rb_support_ids_list.item(i).text() for i in range(self.rb_support_ids_list.count())]),
            "rb_phones": json.dumps([self.rb_phones_list.item(i).text() for i in range(self.rb_phones_list.count())]),
            "rb_main_menu": json.dumps([self.rb_main_menu.item(i, 0).text() for i in range(self.rb_main_menu.rowCount())])
        }
        await asyncio.get_running_loop().run_in_executor(None, lambda: self._save_db(data))
        self.window().show_toast("تنظیمات روبیکا ذخیره شد.")

    def _save_db(self, data):
        with next(get_db()) as db:
            for k, v in data.items(): crud.set_setting(db, k, v)

    @asyncSlot()
    async def restart_all_services(self, *args, **kwargs):
        if getattr(self, '_restarting', False): return

        if not hasattr(self.window(), 'app_manager'):
            return QMessageBox.warning(self, "خطا", "مدیریت برنامه در دسترس نیست.")

        if QMessageBox.question(self, "تایید", "سرویس‌های ربات با تنظیمات جدید ریستارت شوند؟\n(ممکن است برای اعمال کامل توکن جدید نیاز به بستن و باز کردن برنامه باشد)") == QMessageBox.StandardButton.Yes:
            try:
                self._restarting = True
                await self.window().app_manager.restart_services()
            finally:
                self._restarting = False

    @asyncSlot()
    async def update_bot_commands(self, *args, **kwargs):
        try:
            if not self.window() or not self.isVisible() or getattr(self.window(), '_is_shutting_down', False):
                return
        except (RuntimeError, AttributeError): return

        if not self.bot_app: return QMessageBox.warning(self, "خطا", "ربات تلگرام متصل نیست.")
        try:
            from telegram import BotCommand
            await self.bot_app.bot.set_my_commands([
                BotCommand("start", "🏠 خانه"), BotCommand("cart", "🛒 سبد خرید"),
                BotCommand("search", "🔍 جستجو"), BotCommand("support", "📞 پشتیبانی")
            ])
            self.window().show_toast("منوی ربات بروزرسانی شد.")
        except Exception as e: QMessageBox.warning(self, "خطا", str(e))

    # --- Tools Logic ---
    def create_manual_backup(self):
        try:
            n = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            dest = BASE_DIR / "db" / "backups"; dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(BASE_DIR / "db" / "shop_bot.db", dest / n)
            self.load_backups_list()
            self.window().show_toast("بک‌آپ ایجاد شد.")
        except Exception as e: QMessageBox.critical(self, "خطا", str(e))

    def load_backups_list(self):
        try:
            if not self.isVisible(): return
            self.bk_table.setRowCount(0)
        except RuntimeError:
            return

        d = BASE_DIR / "db" / "backups"
        if not d.exists(): return
        for i, f in enumerate(sorted(d.glob("*.db"), key=os.path.getmtime, reverse=True)):
            self.bk_table.insertRow(i)
            self.bk_table.setItem(i, 0, QTableWidgetItem(f.name))
            self.bk_table.setItem(i, 1, QTableWidgetItem(datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")))
            self.bk_table.setItem(i, 2, QTableWidgetItem(f"{f.stat().st_size/1024:.1f} KB"))

    def restore_backup(self):
        r = self.bk_table.currentRow()
        if r < 0: return
        f = self.bk_table.item(r, 0).text()
        if QMessageBox.question(self, "هشدار", f"بازگردانی {f}؟") == QMessageBox.StandardButton.Yes:
            try:
                shutil.copy2(BASE_DIR / "db" / "backups" / f, BASE_DIR / "db" / "shop_bot.db")
                os._exit(0)
            except Exception as e: QMessageBox.critical(self, "خطا", str(e))

    @asyncSlot()
    async def send_backup_to_telegram(self, *args, **kwargs):
        with next(get_db()) as db:
            admin_ids = crud.get_admin_ids(db)
        if not self.bot_app or not admin_ids: return self.window().show_toast("ربات تلگرام یا ادمین تنظیم نشده است.", is_error=True)
        d = BASE_DIR / "db" / "backups"
        if not d.exists(): return
        files = sorted(d.glob("*.db"), key=os.path.getmtime, reverse=True)
        if not files: return
        latest = files[0]
        self.window().show_toast("در حال ارسال به تلگرام...")
        try:
            with open(latest, 'rb') as doc:
                await self.bot_app.bot.send_document(chat_id=admin_ids[0], document=doc, caption=f"📦 Backup {datetime.now().strftime('%Y-%m-%d')}")
            self.window().show_toast("بک‌آپ در تلگرام ذخیره شد.")
        except Exception as e: self.window().show_toast(f"خطا: {e}", is_error=True)

    @asyncSlot()
    async def on_start_broadcast(self, *args, **kwargs):
        msg = self.bc_text.toPlainText().strip()
        if not msg and not self._broadcast_image_path:
            return QMessageBox.warning(self, "خطا", "متن یا عکس الزامی است.")
            
        self.bc_progress.show(); self.bc_progress.setValue(0)
        loop = asyncio.get_running_loop()
        users = await loop.run_in_executor(None, lambda: crud.get_all_users(next(get_db())))
        total = len(users); sent = 0
        
        for i, u in enumerate(users):
            try:
                if u.platform == 'telegram' and self.bot_app:
                    if self._broadcast_image_path:
                        with open(self._broadcast_image_path, 'rb') as photo:
                            await self.bot_app.bot.send_photo(chat_id=int(u.user_id), photo=photo, caption=msg)
                    else:
                        await self.bot_app.bot.send_message(chat_id=int(u.user_id), text=msg)
                    sent += 1
                elif u.platform == 'rubika' and self.rubika_client:
                    await self.rubika_client.api.send_message(chat_id=u.user_id, text=msg)
                    sent += 1
            except: pass
            self.bc_progress.setValue(int((i+1)/total * 100))
            if i % 5 == 0: await asyncio.sleep(0.1)
            
        self.bc_progress.hide()
        QMessageBox.information(self, "پایان", f"{sent} پیام ارسال شد.")