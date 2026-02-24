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
    QTableWidgetItem, QHeaderView, QMessageBox, QCheckBox, QDialog, QGridLayout, QInputDialog, QAbstractSpinBox
)
from PyQt6.QtGui import QColor, QPixmap, QPainter, QFont, QPen, QBrush, QIcon
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QTime, QEasingCurve, pyqtProperty, QRect, QSize
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
WARNING_COLOR = "#f39c12"
DANGER_COLOR = "#ef4565"
TEXT_MAIN = "#fffffe"
TEXT_SUB = "#94a1b2"
BORDER_COLOR = "#2e2e38"

# ==============================================================================
# ویجت‌های کمکی
# ==============================================================================
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
        self.setObjectName("SettingCard")
        self.setStyleSheet(f"""
            QFrame#SettingCard {{ background-color: rgba(36, 38, 41, 0.6); border-radius: 15px; border: 1px solid {BORDER_COLOR}; }}
            QLabel {{ color: {TEXT_MAIN}; border: none; background: transparent; }}
            QLineEdit, QTextEdit, QComboBox, QTimeEdit, QSpinBox {{
                background-color: rgba(22, 22, 26, 0.5); color: {TEXT_MAIN}; border: 1px solid {BORDER_COLOR};
                border-radius: 10px; padding: 10px;
            }}
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        lbl = QLabel(title)
        lbl.setStyleSheet(f"color: {ACCENT_COLOR}; font-weight: 900; font-size: 16px;")
        self.layout.addWidget(lbl)

        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background: rgba(255, 255, 255, 0.05); max-height: 1px;")
        self.layout.addWidget(line)

    def add_widget(self, w): self.layout.addWidget(w)
    def add_layout(self, l): self.layout.addLayout(l)

# ==============================================================================
# Settings Widget (Enterprise Version)
# ==============================================================================
class SettingsWidget(QWidget):
    def __init__(self, bot_app=None, rubika_client=None):
        super().__init__()
        self.bot_app = bot_app
        self.rubika_client = rubika_client
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()
        self._data_loaded = False

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar Navigation ---
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(240)
        self.nav_list.setObjectName("SettingsNav")
        self.nav_list.setStyleSheet(f"""
            QListWidget#SettingsNav {{ background: rgba(22, 22, 26, 0.4); border-left: 1px solid rgba(255, 255, 255, 0.05); padding: 10px; outline: none; }}
            QListWidget#SettingsNav::item {{ height: 55px; color: {TEXT_SUB}; padding-right: 20px; border-radius: 12px; margin-bottom: 5px; }}
            QListWidget#SettingsNav::item:selected {{ color: white; background: {ACCENT_COLOR}; font-weight: bold; }}
            QListWidget#SettingsNav::item:hover:!selected {{ background: rgba(255, 255, 255, 0.05); }}
        """)

        nav_items = [
            ("⚙️ تنظیمات اصلی", 0),
            ("💬 محتوای متنی (Template)", 1),
            ("💳 مالی و درگاه", 2),
            ("🎨 شخصی‌سازی (Branding)", 3),
            ("🔔 اطلاع‌رسانی", 4),
            ("🛠 ابزارها و بک‌آپ", 5)
        ]

        for t, i in nav_items:
            item = QListWidgetItem(t)
            self.nav_list.addItem(item)

        self.nav_list.currentRowChanged.connect(self.change_page)
        main_layout.addWidget(self.nav_list)

        # --- Content Stack ---
        self.pages_stack = QStackedWidget()
        self.pages_stack.addWidget(self._ui_core_settings())
        self.pages_stack.addWidget(self._ui_template_settings())
        self.pages_stack.addWidget(self._ui_payment_settings())
        self.pages_stack.addWidget(self._ui_branding_settings())
        self.pages_stack.addWidget(self._ui_notification_settings())
        self.pages_stack.addWidget(self._ui_tools_settings())

        main_layout.addWidget(self.pages_stack)
        self.nav_list.setCurrentRow(0)

    def change_page(self, index):
        self.pages_stack.setCurrentIndex(index)

    def _ui_core_settings(self):
        page = QScrollArea(); page.setWidgetResizable(True); page.setStyleSheet("background: transparent; border: none;")
        container = QWidget(); layout = QVBoxLayout(container); layout.setSpacing(20); layout.setContentsMargins(30, 30, 30, 30)

        # Telegram Core
        card_tg = SettingCard("پیکربندی ربات تلگرام")
        self.inp_tg_token = QLineEdit(); self.inp_tg_token.setPlaceholderText("Telegram Bot Token (600000000:AA...)")
        self.inp_tg_token.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        card_tg.add_widget(QLabel("توکن ربات:"))
        card_tg.add_widget(self.inp_tg_token)
        layout.addWidget(card_tg)

        # Rubika Core
        card_rb = SettingCard("پیکربندی ربات روبیکا")
        self.inp_rb_token = QLineEdit(); self.inp_rb_token.setPlaceholderText("Rubika Bot Token")
        card_rb.add_widget(QLabel("توکن ربات:"))
        card_rb.add_widget(self.inp_rb_token)
        layout.addWidget(card_rb)

        # Admins
        card_adm = SettingCard("مدیریت مدیران (Admins)")
        self.inp_admin_ids = QTextEdit(); self.inp_admin_ids.setPlaceholderText("آیدی‌های عددی ادمین‌ها را با کاما جدا کنید\nمثال: 1234567, 9876543")
        self.inp_admin_ids.setMaximumHeight(80)
        card_adm.add_widget(QLabel("لیست ادمین‌ها:"))
        card_adm.add_widget(self.inp_admin_ids)
        layout.addWidget(card_adm)

        btn_save = QPushButton("💾 ذخیره و راه‌اندازی مجدد سرویس‌ها")
        btn_save.setStyleSheet(f"background: {SUCCESS_COLOR}; color: white; padding: 15px; font-weight: 900; border-radius: 12px;")
        btn_save.clicked.connect(self.save_core_settings)
        layout.addWidget(btn_save)
        layout.addStretch()

        page.setWidget(container)
        return page

    def _ui_template_settings(self):
        page = QScrollArea(); page.setWidgetResizable(True); page.setStyleSheet("background: transparent; border: none;")
        container = QWidget(); layout = QVBoxLayout(container); layout.setSpacing(20); layout.setContentsMargins(30, 30, 30, 30)

        # Welcome Template
        card_welcome = SettingCard("پیام خوش‌آمدگویی (/start)")
        self.tmpl_welcome = QTextEdit()
        self.tmpl_welcome.setPlaceholderText("متغیرهای مجاز: {user_name}, {shop_name}")
        card_welcome.add_widget(self.tmpl_welcome)
        layout.addWidget(card_welcome)

        # Order Confirmation
        card_order = SettingCard("متن تایید ثبت سفارش")
        self.tmpl_order = QTextEdit()
        self.tmpl_order.setPlaceholderText("متغیرهای مجاز: {order_id}, {total_amount}")
        card_order.add_widget(self.tmpl_order)
        layout.addWidget(card_order)

        # Support Page
        card_support = SettingCard("متن صفحه پشتیبانی")
        self.tmpl_support = QTextEdit()
        card_support.add_widget(self.tmpl_support)
        layout.addWidget(card_support)

        btn_save = QPushButton("💾 بروزرسانی متون ربات")
        btn_save.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; padding: 15px; font-weight: bold; border-radius: 12px;")
        btn_save.clicked.connect(self.save_templates)
        layout.addWidget(btn_save)
        layout.addStretch()

        page.setWidget(container)
        return page

    def _ui_payment_settings(self):
        page = QScrollArea(); page.setWidgetResizable(True); page.setStyleSheet("background: transparent; border: none;")
        container = QWidget(); layout = QVBoxLayout(container); layout.setSpacing(20); layout.setContentsMargins(30, 30, 30, 30)

        # ZarinPal
        card_zp = SettingCard("تنظیمات درگاه زرین‌پال")
        self.inp_zp_merchant = QLineEdit(); self.inp_zp_merchant.setPlaceholderText("Merchant ID (36 digits)")
        self.inp_zp_callback = QLineEdit(); self.inp_zp_callback.setPlaceholderText("Callback URL")
        card_zp.add_widget(QLabel("کد درگاه (Merchant ID):"))
        card_zp.add_widget(self.inp_zp_merchant)
        card_zp.add_widget(QLabel("آدرس بازگشت (Callback):"))
        card_zp.add_widget(self.inp_zp_callback)
        layout.addWidget(card_zp)

        # Payment Methods
        card_methods = SettingCard("روش‌های پرداخت فعال")
        self.chk_pay_online = ToggleSwitch(); self.chk_pay_online.setText("پرداخت آنلاین (زرین‌پال)")
        self.chk_pay_card = ToggleSwitch(); self.chk_pay_card.setText("کارت به کارت (ارسال فیش)")
        
        row1 = QHBoxLayout(); row1.addWidget(QLabel("درگاه آنلاین:")); row1.addStretch(); row1.addWidget(self.chk_pay_online)
        row2 = QHBoxLayout(); row2.addWidget(QLabel("کارت به کارت:")); row2.addStretch(); row2.addWidget(self.chk_pay_card)
        
        card_methods.add_layout(row1); card_methods.add_layout(row2)
        layout.addWidget(card_methods)

        # Currency
        card_curr = SettingCard("واحد پولی")
        self.cmb_currency = QComboBox(); self.cmb_currency.addItems(["تومان", "ریال"])
        card_curr.add_widget(self.cmb_currency)
        layout.addWidget(card_curr)

        btn_save = QPushButton("💾 ذخیره تنظیمات مالی")
        btn_save.setStyleSheet(f"background: {SUCCESS_COLOR}; color: white; padding: 15px; font-weight: bold; border-radius: 12px;")
        btn_save.clicked.connect(self.save_payment_settings)
        layout.addWidget(btn_save)
        layout.addStretch()

        page.setWidget(container)
        return page

    def _ui_branding_settings(self):
        page = QScrollArea(); page.setWidgetResizable(True); page.setStyleSheet("background: transparent; border: none;")
        container = QWidget(); layout = QVBoxLayout(container); layout.setSpacing(20); layout.setContentsMargins(30, 30, 30, 30)

        # Identity
        card_id = SettingCard("هویت برند")
        self.inp_shop_name = QLineEdit()
        self.inp_shop_logo = QLineEdit(); self.inp_shop_logo.setReadOnly(True)
        btn_logo = QPushButton("انتخاب لوگو"); btn_logo.clicked.connect(self.select_logo)

        card_id.add_widget(QLabel("نام فروشگاه:"))
        card_id.add_widget(self.inp_shop_name)
        card_id.add_widget(QLabel("لوگوی فروشگاه:"))
        h_logo = QHBoxLayout(); h_logo.addWidget(self.inp_shop_logo); h_logo.addWidget(btn_logo)
        card_id.add_layout(h_logo)
        layout.addWidget(card_id)

        # Theme
        card_theme = SettingCard("رنگ سازمانی (Accent Color)")
        self.btn_pick_color = QPushButton("انتخاب رنگ"); self.btn_pick_color.clicked.connect(self.pick_accent_color)
        self.lbl_color_preview = QLabel(); self.lbl_color_preview.setFixedSize(50, 30); self.lbl_color_preview.setStyleSheet("border-radius: 5px;")
        h_col = QHBoxLayout(); h_col.addWidget(self.btn_pick_color); h_col.addWidget(self.lbl_color_preview); h_col.addStretch()
        card_theme.add_layout(h_col)
        layout.addWidget(card_theme)

        btn_save = QPushButton("💾 اعمال تغییرات ظاهری")
        btn_save.setStyleSheet(f"background: {INFO_COLOR}; color: white; padding: 15px; font-weight: bold; border-radius: 12px;")
        btn_save.clicked.connect(self.save_branding)
        layout.addWidget(btn_save)
        layout.addStretch()

        page.setWidget(container)
        return page

    def _ui_notification_settings(self):
        page = QScrollArea(); page.setWidgetResizable(True); page.setStyleSheet("background: transparent; border: none;")
        container = QWidget(); layout = QVBoxLayout(container); layout.setSpacing(20); layout.setContentsMargins(30, 30, 30, 30)

        card_notif = SettingCard("تنظیمات اطلاع‌رسانی مدیریت")
        self.chk_notif_order = ToggleSwitch(); self.chk_notif_order.setText("سفارش جدید")
        self.chk_notif_stock = ToggleSwitch(); self.chk_notif_stock.setText("اتمام موجودی کالا")
        self.chk_notif_ticket = ToggleSwitch(); self.chk_notif_ticket.setText("تیکت پشتیبانی جدید")
        
        card_notif.add_widget(self.chk_notif_order)
        card_notif.add_widget(self.chk_notif_stock)
        card_notif.add_widget(self.chk_notif_ticket)
        layout.addWidget(card_notif)

        card_dest = SettingCard("مقصد نوتیفیکیشن‌ها")
        self.chk_dest_desktop = QCheckBox("نوتیفیکیشن دسکتاپ (Windows/Mac)"); self.chk_dest_desktop.setChecked(True)
        self.chk_dest_bot = QCheckBox("ارسال به ربات (برای ادمین‌ها)")
        card_dest.add_widget(self.chk_dest_desktop); card_dest.add_widget(self.chk_dest_bot)
        layout.addWidget(card_dest)

        btn_save = QPushButton("💾 ذخیره تنظیمات")
        btn_save.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; padding: 12px; border-radius: 10px;")
        btn_save.clicked.connect(self.save_notification_settings)
        layout.addWidget(btn_save)
        layout.addStretch()

        page.setWidget(container)
        return page

    def _ui_tools_settings(self):
        # این متد قبلاTools بود، فقط استایلش را هماهنگ میکنیم
        page = QScrollArea(); page.setWidgetResizable(True); page.setStyleSheet("background: transparent; border: none;")
        container = QWidget(); layout = QVBoxLayout(container); layout.setSpacing(20); layout.setContentsMargins(30, 30, 30, 30)

        card_bk = SettingCard("مدیریت بک‌آپ و فایل‌ها")
        btn_bk = QPushButton("📦 ایجاد نسخه پشتیبان آنی"); btn_bk.clicked.connect(self.create_manual_backup)
        btn_bk.setStyleSheet(f"background: {INFO_COLOR}; color: white; padding: 10px;")
        card_bk.add_widget(btn_bk)
        layout.addWidget(card_bk)
        
        card_log = SettingCard("Audit Logs (تاریخچه تغییرات پنل)")
        self.audit_table = QTableWidget(0, 4)
        self.audit_table.setHorizontalHeaderLabels(["زمان", "ادمین", "عملیات", "توضیح"])
        self.audit_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.audit_table.setFixedHeight(300)
        card_log.add_widget(self.audit_table)
        layout.addWidget(card_log)

        layout.addStretch()
        page.setWidget(container)
        return page

    # ==================== Logic ====================

    def showEvent(self, event):
        super().showEvent(event)
        if not self._data_loaded:
            QTimer.singleShot(200, self.refresh_data)
            self._data_loaded = True

    @asyncSlot()
    async def refresh_data(self):
        loop = asyncio.get_running_loop()
        try:
            data = await loop.run_in_executor(None, self._fetch_all_settings)
            
            # Core
            self.inp_tg_token.setText(data.get("tg_bot_token", ""))
            self.inp_rb_token.setText(data.get("rb_bot_token", ""))
            self.inp_admin_ids.setPlainText(data.get("admin_ids", ""))

            # Templates
            self.tmpl_welcome.setPlainText(data.get("tmpl_welcome", ""))
            self.tmpl_order.setPlainText(data.get("tmpl_order", ""))
            self.tmpl_support.setPlainText(data.get("tmpl_support", ""))

            # Payment
            self.inp_zp_merchant.setText(data.get("zp_merchant", ""))
            self.inp_zp_callback.setText(data.get("zp_callback", ""))
            self.chk_pay_online.setChecked(data.get("pay_online_active", "true") == "true")
            self.chk_pay_card.setChecked(data.get("pay_card_active", "true") == "true")
            self.cmb_currency.setCurrentText(data.get("currency", "تومان"))

            # Branding
            self.inp_shop_name.setText(data.get("shop_name", "فروشگاه من"))
            self.inp_shop_logo.setText(data.get("shop_logo", ""))
            accent = data.get("accent_color", ACCENT_COLOR)
            self.lbl_color_preview.setStyleSheet(f"background: {accent}; border: 1px solid white;")

            # Notifications
            self.chk_notif_order.setChecked(data.get("notif_order", "true") == "true")
            self.chk_notif_stock.setChecked(data.get("notif_stock", "true") == "true")
            self.chk_notif_ticket.setChecked(data.get("notif_ticket", "true") == "true")
            self.chk_dest_bot.setChecked(data.get("notif_dest_bot", "false") == "true")

            # Audit Logs
            await self.load_audit_logs()

        except Exception as e: logger.error(f"Settings refresh error: {e}")

    def _fetch_all_settings(self):
        with next(get_db()) as db:
            keys = [
                "tg_bot_token", "rb_bot_token", "admin_ids",
                "tmpl_welcome", "tmpl_order", "tmpl_support",
                "zp_merchant", "zp_callback", "pay_online_active", "pay_card_active", "currency",
                "shop_name", "shop_logo", "accent_color",
                "notif_order", "notif_stock", "notif_ticket", "notif_dest_bot"
            ]
            return {k: crud.get_setting(db, k, "") for k in keys}

    def _save_all_settings(self, data):
        with next(get_db()) as db:
            for k, v in data.items(): crud.set_setting(db, k, str(v))
            # ثبت در لاگ سیستم
            crud.record_audit_log(db, "update_settings", description="تنظیمات سیستم بروزرسانی شد.")

    @asyncSlot()
    async def save_core_settings(self):
        data = {
            "tg_bot_token": self.inp_tg_token.text(),
            "rb_bot_token": self.inp_rb_token.text(),
            "admin_ids": self.inp_admin_ids.toPlainText()
        }
        await asyncio.get_running_loop().run_in_executor(None, lambda: self._save_all_settings(data))
        self.window().show_toast("تنظیمات اصلی ذخیره شد. برای اعمال تغییرات توکن، سرویس‌ها را ریستارت کنید.")

    @asyncSlot()
    async def save_templates(self):
        data = {
            "tmpl_welcome": self.tmpl_welcome.toPlainText(),
            "tmpl_order": self.tmpl_order.toPlainText(),
            "tmpl_support": self.tmpl_support.toPlainText()
        }
        await asyncio.get_running_loop().run_in_executor(None, lambda: self._save_all_settings(data))
        self.window().show_toast("قالب‌های متنی بروزرسانی شدند.")

    @asyncSlot()
    async def save_payment_settings(self):
        data = {
            "zp_merchant": self.inp_zp_merchant.text(),
            "zp_callback": self.inp_zp_callback.text(),
            "pay_online_active": "true" if self.chk_pay_online.isChecked() else "false",
            "pay_card_active": "true" if self.chk_pay_card.isChecked() else "false",
            "currency": self.cmb_currency.currentText()
        }
        await asyncio.get_running_loop().run_in_executor(None, lambda: self._save_all_settings(data))
        self.window().show_toast("تنظیمات مالی ذخیره شد.")

    @asyncSlot()
    async def save_branding(self):
        data = {
            "shop_name": self.inp_shop_name.text(),
            "shop_logo": self.inp_shop_logo.text()
        }
        await asyncio.get_running_loop().run_in_executor(None, lambda: self._save_all_settings(data))
        self.window().show_toast("برندینگ بروزرسانی شد. (نیاز به باز و بسته کردن پنل)")

    @asyncSlot()
    async def save_notification_settings(self):
        data = {
            "notif_order": "true" if self.chk_notif_order.isChecked() else "false",
            "notif_stock": "true" if self.chk_notif_stock.isChecked() else "false",
            "notif_ticket": "true" if self.chk_notif_ticket.isChecked() else "false",
            "notif_dest_bot": "true" if self.chk_dest_bot.isChecked() else "false"
        }
        await asyncio.get_running_loop().run_in_executor(None, lambda: self._save_all_settings(data))
        self.window().show_toast("تنظیمات اطلاع‌رسانی ذخیره شد.")

    def select_logo(self):
        f, _ = QFileDialog.getOpenFileName(self, "انتخاب لوگو", "", "Images (*.png *.jpg *.ico)")
        if f: self.inp_shop_logo.setText(f)

    def pick_accent_color(self):
        from PyQt6.QtWidgets import QColorDialog
        col = QColorDialog.getColor()
        if col.isValid():
            hex_col = col.name()
            self.lbl_color_preview.setStyleSheet(f"background: {hex_col}; border: 1px solid white;")
            with next(get_db()) as db: crud.set_setting(db, "accent_color", hex_col)

    async def load_audit_logs(self):
        loop = asyncio.get_running_loop()
        def fetch():
            with next(get_db()) as db:
                from db.models import AuditLog
                return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(50).all()
        
        logs = await loop.run_in_executor(None, fetch)
        self.audit_table.setRowCount(0)
        for i, l in enumerate(logs):
            self.audit_table.insertRow(i)
            self.audit_table.setItem(i, 0, QTableWidgetItem(l.created_at.strftime("%Y/%m/%d %H:%M")))
            self.audit_table.setItem(i, 1, QTableWidgetItem(str(l.admin_id)))
            self.audit_table.setItem(i, 2, QTableWidgetItem(str(l.action)))
            self.audit_table.setItem(i, 3, QTableWidgetItem(str(l.description)))

    def create_manual_backup(self):
        from db.database import create_backup
        res = create_backup()
        if res: self.window().show_toast(f"بک‌آپ ایجاد شد: {os.path.basename(res)}")
