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
    QGraphicsOpacityEffect
)
from PyQt6.QtGui import QColor, QPixmap, QPainter, QFont, QPen, QBrush, QIcon
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QTime, QEasingCurve, pyqtProperty, QRect, QSize
from qasync import asyncSlot
import qtawesome as qta

from db.database import get_db
from db import crud
from config import BASE_DIR
from bot import proxy_utils

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
class BotMonitorCard(QFrame):
    def __init__(self, name, icon, parent=None):
        super().__init__(parent)
        self.setObjectName("BotMonitorCard")
        self.setFixedWidth(320)
        self.setStyleSheet(f"""
            QFrame#BotMonitorCard {{ background: rgba(30, 30, 35, 0.8); border-radius: 20px; border: 1px solid {BORDER_COLOR}; }}
            QLabel {{ color: {TEXT_MAIN}; background: transparent; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        lbl_icon = QLabel(); lbl_icon.setPixmap(qta.icon(icon, color=ACCENT_COLOR).pixmap(40, 40))
        lbl_name = QLabel(name); lbl_name.setStyleSheet("font-weight: 900; font-size: 18px;")
        header.addWidget(lbl_icon); header.addWidget(lbl_name); header.addStretch()
        layout.addLayout(header)

        grid = QGridLayout()
        grid.setSpacing(10)

        self.lbl_status = QLabel("⚪ آفلاین")
        self.lbl_status.setStyleSheet(f"color: {TEXT_SUB}; font-weight: bold;")

        self.lbl_cpu = QLabel("CPU: 0%")
        self.lbl_ram = QLabel("RAM: 0 MB")
        self.lbl_uptime = QLabel("Uptime: --")

        style_sub = f"color: {TEXT_SUB}; font-size: 13px;"
        self.lbl_cpu.setStyleSheet(style_sub); self.lbl_ram.setStyleSheet(style_sub); self.lbl_uptime.setStyleSheet(style_sub)

        grid.addWidget(QLabel("وضعیت:"), 0, 0); grid.addWidget(self.lbl_status, 0, 1)
        grid.addWidget(QLabel("پردازش:"), 1, 0); grid.addWidget(self.lbl_cpu, 1, 1)
        grid.addWidget(QLabel("حافظه:"), 2, 0); grid.addWidget(self.lbl_ram, 2, 1)
        grid.addWidget(QLabel("پایداری:"), 3, 0); grid.addWidget(self.lbl_uptime, 3, 1)
        layout.addLayout(grid)

        self.btn_restart = QPushButton("🔄 ریستارت")
        self.btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restart.setStyleSheet(f"background: rgba(255,255,255,0.05); color: white; border-radius: 10px; padding: 10px; border: 1px solid {BORDER_COLOR};")
        layout.addWidget(self.btn_restart)

    def update_stats(self, data):
        if data.get("alive"):
            self.lbl_status.setText("🟢 آنلاین")
            self.lbl_status.setStyleSheet(f"color: {SUCCESS_COLOR}; font-weight: bold;")
            self.lbl_cpu.setText(f"CPU: {data['cpu']:.1f}%")
            self.lbl_ram.setText(f"RAM: {data['ram']:.1f} MB")
            self.lbl_uptime.setText(f"Uptime: {data['uptime']}")
        else:
            self.lbl_status.setText("🔴 آفلاین")
            self.lbl_status.setStyleSheet(f"color: {DANGER_COLOR}; font-weight: bold;")
            self.lbl_cpu.setText("CPU: 0%")
            self.lbl_ram.setText("RAM: 0 MB")
            self.lbl_uptime.setText("Uptime: --")

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
        if not self.isVisible():
            return
        p = QPainter()
        if not p.begin(self):
            return
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setBrush(QBrush(QColor(SUCCESS_COLOR if self.isChecked() else "#4a4a62")))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(0, 0, self.width(), self.height(), 13, 13)
            p.setBrush(QBrush(QColor("#ffffff")))
            p.drawEllipse(self._circle_position, 3, 20, 20)
        finally:
            p.end()

class SkeletonFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(255,255,255,0.05), stop:0.5 rgba(255,255,255,0.1), stop:1 rgba(255,255,255,0.05));
                border-radius: 15px;
            }}
        """)
        self.anim = QPropertyAnimation(self, b"pos") # Just a placeholder for style

class ProxyCard(QFrame):
    activate_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    test_requested = pyqtSignal(int)

    def __init__(self, proxy, parent=None):
        super().__init__(parent)
        self.proxy_id = proxy.id
        self.setObjectName("ProxyCard")
        self.setFixedSize(280, 180)

        status_color = SUCCESS_COLOR if proxy.is_active else BORDER_COLOR
        self.setStyleSheet(f"""
            QFrame#ProxyCard {{
                background: {PANEL_BG}; border-radius: 15px;
                border: 2px solid {status_color};
            }}
            QLabel {{ color: {TEXT_MAIN}; background: transparent; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header: Name & Flag
        header = QHBoxLayout()
        name_lbl = QLabel(proxy.name or "Unnamed")
        name_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")

        flag_lbl = QLabel()
        if proxy.country_code:
            # استفاده از ایموجی پرچم یا متن
            flag_lbl.setText(self._get_flag_emoji(proxy.country_code))

        header.addWidget(name_lbl)
        header.addStretch()
        header.addWidget(flag_lbl)
        layout.addLayout(header)

        # Protocol & Ping
        info = QHBoxLayout()
        type_lbl = QLabel(proxy.type.upper())
        type_lbl.setStyleSheet(f"color: {TEXT_SUB}; font-size: 11px; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px;")

        ping_val = proxy.last_ping or 0
        ping_text = f"⚡ {ping_val}ms" if ping_val > 0 else "⚡ --"
        if ping_val == -1: ping_text = "⚠️ Timeout"
        if ping_val == -2: ping_text = "❌ Error"

        ping_lbl = QLabel(ping_text)
        p_color = SUCCESS_COLOR if ping_val > 0 and ping_val < 300 else (WARNING_COLOR if ping_val > 0 else DANGER_COLOR)
        ping_lbl.setStyleSheet(f"color: {p_color}; font-weight: bold;")

        info.addWidget(type_lbl)
        info.addStretch()
        info.addWidget(ping_lbl)
        layout.addLayout(info)

        # Latency Sparkline (Simple Drawing)
        self.sparkline = QFrame()
        self.sparkline.setFixedHeight(40)
        self.sparkline.setStyleSheet("background: rgba(0,0,0,0.2); border-radius: 5px;")
        self.sparkline.paintEvent = lambda e: self._draw_sparkline(proxy.latency_history)
        layout.addWidget(self.sparkline)

        layout.addStretch()

        # Actions
        actions = QHBoxLayout()
        btn_act = QPushButton("فعال‌سازی" if not proxy.is_active else "فعال است")
        btn_act.setEnabled(not proxy.is_active)
        btn_act.setCursor(Qt.CursorShape.PointingHandCursor)
        act_style = f"background: {SUCCESS_COLOR}; color: white; border-radius: 8px; padding: 5px;" if not proxy.is_active else "background: #444; color: #888; border-radius: 8px;"
        btn_act.setStyleSheet(act_style)
        btn_act.clicked.connect(lambda: self.activate_requested.emit(self.proxy_id))

        btn_del = QPushButton(qta.icon("fa5s.trash-alt", color=DANGER_COLOR), "")
        btn_del.setFixedSize(30, 30)
        btn_del.setStyleSheet(f"background: rgba(255,255,255,0.05); border-radius: 8px;")
        btn_del.clicked.connect(lambda: self.delete_requested.emit(self.proxy_id))

        actions.addWidget(btn_act, 1)
        actions.addWidget(btn_del)
        layout.addLayout(actions)

    def _get_flag_emoji(self, country_code):
        if not country_code or len(country_code) != 2: return ""
        return "".join(chr(127397 + ord(c)) for c in country_code.upper())

    def _draw_sparkline(self, history_json):
        if not history_json: return
        try:
            history = json.loads(history_json)
            if not history: return

            p = QPainter(self.sparkline)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)

            w = self.sparkline.width()
            h = self.sparkline.height()

            points = []
            max_p = max([x for x in history if x > 0] or [1000])
            for i, val in enumerate(history):
                x = (i / (len(history)-1)) * (w-10) + 5 if len(history)>1 else w/2
                # اگر پینگ منفی بود (خطا)، در پایین نمودار نشان بده
                norm_val = val if val > 0 else max_p * 1.2
                y = h - (min(norm_val, max_p) / max_p) * (h-10) - 5
                points.append(QPoint(int(x), int(y)))

            pen = QPen(QColor(ACCENT_COLOR), 2)
            p.setPen(pen)
            for i in range(len(points)-1):
                p.drawLine(points[i], points[i+1])
            p.end()
        except: pass

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
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- Sidebar Navigation ---
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(240)
        sidebar_frame.setStyleSheet(f"background: rgba(22, 22, 26, 0.4); border-left: 1px solid rgba(255, 255, 255, 0.05);")
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(10, 15, 10, 15)
        sidebar_layout.setSpacing(10)

        # Settings Search
        self.search_settings = QLineEdit()
        self.search_settings.setPlaceholderText("🔍 جستجو تنظیمات...")
        self.search_settings.setStyleSheet(f"background: {BG_COLOR}; border: 1px solid {BORDER_COLOR}; border-radius: 8px; padding: 10px; color: white;")
        self.search_settings.textChanged.connect(self.filter_settings_ui)
        sidebar_layout.addWidget(self.search_settings)

        self.nav_list = QListWidget()
        self.nav_list.setObjectName("SettingsNav")
        self.nav_list.setStyleSheet(f"""
            QListWidget#SettingsNav {{ background: transparent; border: none; outline: none; }}
            QListWidget#SettingsNav::item {{ height: 55px; color: {TEXT_SUB}; padding-right: 20px; border-radius: 12px; margin-bottom: 5px; }}
            QListWidget#SettingsNav::item:selected {{ color: white; background: {ACCENT_COLOR}; font-weight: bold; }}
            QListWidget#SettingsNav::item:hover:!selected {{ background: rgba(255, 255, 255, 0.05); }}
        """)

        nav_items = [
            ("⚙️ تنظیمات اصلی", 0),
            ("⚡ وضعیت سرور و ربات", 1),
            ("🌐 مدیریت پروکسی", 2),
            ("💬 محتوای متنی (Template)", 3),
            ("🎟 کدهای تخفیف", 4),
            ("🤖 پاسخگوی خودکار", 5),
            ("💳 مالی و درگاه", 6),
            ("🎨 شخصی‌سازی (Branding)", 7),
            ("🔔 اطلاع‌رسانی", 8),
            ("🛠 ابزارها و بک‌آپ", 9)
        ]

        for t, i in nav_items:
            item = QListWidgetItem(t)
            self.nav_list.addItem(item)

        self.nav_list.currentRowChanged.connect(self.change_page)
        sidebar_layout.addWidget(self.nav_list)
        self.main_layout.addWidget(sidebar_frame)

        # --- Content Stack ---
        self.pages_stack = QStackedWidget()
        self._all_pages = [
            self._ui_core_settings(),
            self._ui_bot_monitoring(),
            self._ui_proxy_settings(),
            self._ui_template_settings(),
            self._ui_coupon_settings(),
            self._ui_autoreply_settings(),
            self._ui_payment_settings(),
            self._ui_branding_settings(),
            self._ui_notification_settings(),
            self._ui_tools_settings()
        ]
        for p in self._all_pages: self.pages_stack.addWidget(p)

        self.main_layout.addWidget(self.pages_stack)
        self.nav_list.setCurrentRow(0)

    def filter_settings_ui(self, text):
        """فیلتر کردن آیتم‌های منوی تنظیمات"""
        query = text.lower().strip()
        for i in range(self.nav_list.count()):
            item = self.nav_list.item(i)
            item.setHidden(query not in item.text().lower())

    def change_page(self, index):
        # مدیریت تایمر مانیتورینگ
        if hasattr(self, 'monitor_timer'):
            if index == 1: self.monitor_timer.start(3000)
            else: self.monitor_timer.stop()

        current_widget = self.pages_stack.widget(index)

        # انیمیشن تعویض تب (Fade In) - بهینه‌سازی شده برای جلوگیری از تداخل Painter
        eff = current_widget.graphicsEffect()
        if not isinstance(eff, QGraphicsOpacityEffect):
            eff = QGraphicsOpacityEffect(current_widget)
            current_widget.setGraphicsEffect(eff)

        if hasattr(self, 'fade_anim'):
            self.fade_anim.stop()

        self.fade_anim = QPropertyAnimation(eff, b"opacity")
        self.fade_anim.setDuration(400)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.fade_anim.finished.connect(lambda: current_widget.setGraphicsEffect(None))

        self.pages_stack.setCurrentIndex(index)
        self.fade_anim.start()

    def _ui_bot_monitoring(self):
        page = QWidget()
        layout = QVBoxLayout(page); layout.setContentsMargins(30, 30, 30, 30); layout.setSpacing(20)

        title = QLabel("🤖 مرکز پایش و کنترل ربات‌ها")
        title.setStyleSheet("font-size: 24px; font-weight: 900; color: white;")
        layout.addWidget(title)

        h_cards = QHBoxLayout()
        self.tg_monitor = BotMonitorCard("Telegram Bot", "fa5b.telegram")
        self.rb_monitor = BotMonitorCard("Rubika Bot", "fa5s.rocket")

        # اتصال دکمه‌های ریستارت
        self.tg_monitor.btn_restart.clicked.connect(self.restart_all_bots)
        self.rb_monitor.btn_restart.clicked.connect(self.restart_all_bots)

        h_cards.addWidget(self.tg_monitor)
        h_cards.addWidget(self.rb_monitor)
        h_cards.addStretch()
        layout.addLayout(h_cards)

        # Log Snippet Viewer
        card_log = SettingCard("📜 آخرین رویدادهای سیستم")
        self.log_snippet = QTextEdit()
        self.log_snippet.setReadOnly(True)
        self.log_snippet.setStyleSheet("background: #0d1117; color: #c9d1d9; font-family: 'Consolas'; font-size: 12px; border-radius: 10px; padding: 10px;")
        self.log_snippet.setFixedHeight(350)
        card_log.add_widget(self.log_snippet)
        layout.addWidget(card_log)

        # تایمر آپدیت مانیتورینگ
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self.update_monitoring_data)

        layout.addStretch()
        return page

    def _ui_proxy_settings(self):
        page = QWidget()
        layout = QVBoxLayout(page); layout.setContentsMargins(30, 30, 30, 30)

        header = QHBoxLayout()
        title = QLabel("🌐 مدیریت هوشمند اتصالات")
        title.setStyleSheet("font-size: 20px; font-weight: 900; color: white;")
        header.addWidget(title); header.addStretch()

        btn_add = QPushButton("➕ افزودن پروکسی")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; padding: 8px 15px; border-radius: 10px; font-weight: bold;")
        btn_add.clicked.connect(self.add_proxy_dialog)

        btn_test_all = QPushButton("⚡ تست پینگ")
        btn_test_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_test_all.setStyleSheet(f"background: rgba(255,255,255,0.05); color: white; padding: 8px 15px; border-radius: 10px; border: 1px solid {BORDER_COLOR};")
        btn_test_all.clicked.connect(self.test_all_proxies)

        header.addWidget(btn_test_all); header.addWidget(btn_add)
        layout.addLayout(header)

        # Scroll Area for Cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        self.proxy_container = QWidget()
        self.proxy_grid = QGridLayout(self.proxy_container)
        self.proxy_grid.setSpacing(15)
        self.proxy_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self.proxy_container)
        layout.addWidget(scroll)

        # بخش Xray Bridge
        bridge_card = SettingCard("وضعیت پل Xray (V2Ray Bridge)")
        self.lbl_bridge_status = QLabel("⚪ وضعیت: نامشخص")
        self.lbl_bridge_port = QLabel("🔌 پورت محلی: 2080 (SOCKS5)")
        bridge_card.add_widget(self.lbl_bridge_status)
        bridge_card.add_widget(self.lbl_bridge_port)
        layout.addWidget(bridge_card)

        layout.addStretch()
        return page

    def _ui_core_settings(self):
        page = QScrollArea(); page.setWidgetResizable(True); page.setStyleSheet("background: transparent; border: none;")
        container = QWidget(); layout = QVBoxLayout(container); layout.setSpacing(20); layout.setContentsMargins(30, 30, 30, 30)

        # Telegram Core
        card_tg = SettingCard("پیکربندی ربات تلگرام")
        self.inp_tg_token = QLineEdit(); self.inp_tg_token.setPlaceholderText("Telegram Bot Token (600000000:AA...)")
        self.inp_tg_token.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.inp_tg_token.setToolTip("توکنی که از BotFather@ دریافت کرده‌اید را اینجا وارد کنید.")

        card_tg.add_widget(QLabel("توکن ربات:"))
        card_tg.add_widget(self.inp_tg_token)
        layout.addWidget(card_tg)

        # Rubika Core
        card_rb = SettingCard("پیکربندی ربات روبیکا")
        self.inp_rb_token = QLineEdit(); self.inp_rb_token.setPlaceholderText("Rubika Bot Token")
        self.inp_rb_token.setToolTip("توکن اختصاصی ربات روبیکا (Auth) را اینجا قرار دهید.")

        card_rb.add_widget(QLabel("توکن ربات:"))
        card_rb.add_widget(self.inp_rb_token)
        layout.addWidget(card_rb)

        # Admins
        card_adm = SettingCard("مدیریت مدیران (Admins)")
        self.inp_admin_ids = QTextEdit(); self.inp_admin_ids.setPlaceholderText("آیدی‌های عددی ادمین‌ها را با کاما جدا کنید\nمثال: 1234567, 9876543")
        self.inp_admin_ids.setMaximumHeight(80)

        self.inp_admin_user = QLineEdit(); self.inp_admin_user.setPlaceholderText("نام کاربری پنل")
        self.inp_admin_pass = QLineEdit(); self.inp_admin_pass.setPlaceholderText("رمز عبور جدید پنل")
        self.inp_admin_pass.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)

        card_adm.add_widget(QLabel("لیست ادمین‌های ربات (Telegram IDs):"))
        card_adm.add_widget(self.inp_admin_ids)
        card_adm.add_widget(QLabel("نام کاربری پنل دسکتاپ:"))
        card_adm.add_widget(self.inp_admin_user)
        card_adm.add_widget(QLabel("رمز عبور پنل دسکتاپ:"))
        card_adm.add_widget(self.inp_admin_pass)
        layout.addWidget(card_adm)

        btn_save = QPushButton("💾 ذخیره و راه‌اندازی مجدد سرویس‌ها")
        btn_save.setStyleSheet(f"background: {SUCCESS_COLOR}; color: white; padding: 15px; font-weight: 900; border-radius: 12px;")
        btn_save.clicked.connect(self.save_core_settings)
        layout.addWidget(btn_save)
        layout.addStretch()

        page.setWidget(container)
        return page

    def _ui_coupon_settings(self):
        page = QWidget()
        layout = QVBoxLayout(page); layout.setContentsMargins(30, 30, 30, 30)

        card = SettingCard("مدیریت کدهای تخفیف")
        self.coupon_table = QTableWidget(0, 6)
        self.coupon_table.setHorizontalHeaderLabels(["کد", "درصد", "ظرفیت", "استفاده", "حداقل خرید", "وضعیت"])
        self.coupon_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        btn_add = QPushButton("➕ افزودن کد جدید")
        btn_add.setStyleSheet(f"background: {SUCCESS_COLOR}; color: white;")
        btn_add.clicked.connect(self.add_coupon_dialog)

        card.add_widget(self.coupon_table)
        card.add_widget(btn_add)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def _ui_autoreply_settings(self):
        page = QWidget()
        layout = QVBoxLayout(page); layout.setContentsMargins(30, 30, 30, 30)

        card = SettingCard("پاسخگوی خودکار هوشمند")
        self.autoreply_table = QTableWidget(0, 3)
        self.autoreply_table.setHorizontalHeaderLabels(["کلمه کلیدی", "پاسخ ربات", "عملیات"])
        self.autoreply_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        btn_add = QPushButton("➕ افزودن کلمه کلیدی")
        btn_add.setStyleSheet(f"background: {ACCENT_COLOR}; color: white;")
        btn_add.clicked.connect(self.add_autoreply_dialog)

        card.add_widget(self.autoreply_table)
        card.add_widget(btn_add)
        layout.addWidget(card)
        layout.addStretch()
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

        h_btns = QHBoxLayout()
        btn_reset = QPushButton("🔄 بازنشانی به قالب‌های پیش‌فرض")
        btn_reset.setStyleSheet(f"background: {PANEL_BG}; color: {TEXT_SUB}; padding: 12px; border-radius: 10px; border: 1px solid {BORDER_COLOR};")
        btn_reset.clicked.connect(self.reset_templates_to_default)

        btn_save = QPushButton("💾 بروزرسانی متون ربات")
        btn_save.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; padding: 15px; font-weight: bold; border-radius: 12px;")
        btn_save.clicked.connect(self.save_templates)

        h_btns.addWidget(btn_reset)
        h_btns.addWidget(btn_save, 1)
        layout.addLayout(h_btns)
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
        self.btn_pick_color = QPushButton("انتخاب رنگ")
        self.btn_pick_color.clicked.connect(self.pick_accent_color)
        self.lbl_color_preview = QLabel()
        self.lbl_color_preview.setFixedSize(50, 30)
        self.lbl_color_preview.setStyleSheet("border-radius: 5px; border: 1px solid white;")

        h_col = QHBoxLayout()
        h_col.addWidget(self.btn_pick_color)
        h_col.addWidget(self.lbl_color_preview)
        h_col.addStretch()
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
        page = QScrollArea(); page.setWidgetResizable(True); page.setStyleSheet("background: transparent; border: none;")
        container = QWidget(); layout = QVBoxLayout(container); layout.setSpacing(20); layout.setContentsMargins(30, 30, 30, 30)

        # System Doctor
        doctor_card = SettingCard("🩺 دکتر سیستم (System Doctor)")
        self.btn_run_doctor = QPushButton("🚀 شروع عیب‌یابی هوشمند")
        self.btn_run_doctor.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_run_doctor.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; padding: 12px; font-weight: bold; border-radius: 10px;")
        self.btn_run_doctor.clicked.connect(self.run_system_doctor)

        self.doctor_results = QLabel("در انتظار شروع عیب‌یابی...")
        self.doctor_results.setStyleSheet(f"color: {TEXT_SUB}; font-size: 13px; padding: 10px; background: rgba(0,0,0,0.1); border-radius: 8px;")
        self.doctor_results.setWordWrap(True)

        doctor_card.add_widget(self.btn_run_doctor)
        doctor_card.add_widget(self.doctor_results)
        layout.addWidget(doctor_card)

        # Export/Import Settings
        config_card = SettingCard("💾 مدیریت پیکربندی (Config)")
        h_cfg = QHBoxLayout()
        btn_exp = QPushButton("📥 خروجی کل تنظیمات (JSON)"); btn_exp.clicked.connect(self.export_settings)
        btn_imp = QPushButton("📤 بارگذاری تنظیمات"); btn_imp.clicked.connect(self.import_settings)
        h_cfg.addWidget(btn_exp); h_cfg.addWidget(btn_imp)
        config_card.add_layout(h_cfg)
        layout.addWidget(config_card)

        card_bk = SettingCard("📦 مدیریت بک‌آپ دیتابیس")
        btn_bk = QPushButton("ایجاد نسخه پشتیبان دیتابیس (Instant)"); btn_bk.clicked.connect(self.create_manual_backup)
        btn_bk.setStyleSheet(f"background: {INFO_COLOR}; color: white; padding: 10px; border-radius: 8px;")
        card_bk.add_widget(btn_bk)
        layout.addWidget(card_bk)

        card_log = SettingCard("📜 Audit Logs (تاریخچه تغییرات پنل)")
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

    def show_loading_state(self, show=True):
        """نمایش حالت در حال بارگذاری با استفاده از Skeleton"""
        if show:
            if not hasattr(self, '_skeleton'):
                self._skeleton = QWidget()
                lay = QVBoxLayout(self._skeleton)
                for _ in range(3):
                    lay.addWidget(SkeletonFrame())
                self.pages_stack.addWidget(self._skeleton)
            self.pages_stack.setCurrentWidget(self._skeleton)
        else:
            self.pages_stack.setCurrentIndex(self.nav_list.currentRow())

    @asyncSlot()
    async def refresh_data(self):
        self.show_loading_state(True)
        loop = asyncio.get_running_loop()
        try:
            data = await loop.run_in_executor(None, self._fetch_all_settings)
            
            # Core
            self.inp_tg_token.setText(data.get("tg_bot_token", ""))
            self.inp_rb_token.setText(data.get("rb_bot_token", ""))
            self.inp_admin_ids.setPlainText(data.get("admin_ids", ""))
            self.inp_admin_user.setText(data.get("admin_username", "admin"))
            self.inp_admin_pass.setText(data.get("admin_password", "1234"))

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

            # Coupons
            await self.load_coupons()

            # Auto Replies
            await self.load_auto_replies()

            # Proxies
            await self.load_proxies()

            # Audit Logs
            await self.load_audit_logs()

        except Exception as e: logger.error(f"Settings refresh error: {e}")
        finally:
            self.show_loading_state(False)

    async def load_proxies(self):
        loop = asyncio.get_running_loop()
        proxies = await loop.run_in_executor(None, lambda: crud.get_all_proxies(next(get_db())))

        # پاکسازی گرید
        while self.proxy_grid.count():
            item = self.proxy_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        cols = 3
        for i, p in enumerate(proxies):
            card = ProxyCard(p, self)
            card.activate_requested.connect(self.activate_proxy)
            card.delete_requested.connect(self.delete_proxy_entry)
            self.proxy_grid.addWidget(card, i // cols, i % cols)

    async def load_coupons(self):
        loop = asyncio.get_running_loop()
        coupons = await loop.run_in_executor(None, lambda: crud.get_all_coupons(next(get_db())))
        self.coupon_table.setRowCount(0)
        for i, c in enumerate(coupons):
            self.coupon_table.insertRow(i)
            self.coupon_table.setItem(i, 0, QTableWidgetItem(c.code))
            self.coupon_table.setItem(i, 1, QTableWidgetItem(f"{c.percent}%"))
            self.coupon_table.setItem(i, 2, QTableWidgetItem("نامحدود" if c.max_uses == 0 else str(c.max_uses)))
            self.coupon_table.setItem(i, 3, QTableWidgetItem(str(c.current_uses)))
            self.coupon_table.setItem(i, 4, QTableWidgetItem(f"{int(c.min_purchase):,}"))
            status = "فعال" if c.is_active else "غیرفعال"
            self.coupon_table.setItem(i, 5, QTableWidgetItem(status))

    async def load_auto_replies(self):
        loop = asyncio.get_running_loop()
        replies = await loop.run_in_executor(None, lambda: crud.get_all_auto_replies(next(get_db())))
        self.autoreply_table.setRowCount(0)
        for i, r in enumerate(replies):
            self.autoreply_table.insertRow(i)
            self.autoreply_table.setItem(i, 0, QTableWidgetItem(r.keyword))
            self.autoreply_table.setItem(i, 1, QTableWidgetItem(r.response[:50] + "..."))

            del_btn = QPushButton("حذف")
            del_btn.setStyleSheet(f"background: {DANGER_COLOR}; color: white;")
            del_btn.clicked.connect(lambda _, kid=r.id: self.delete_autoreply(kid))
            self.autoreply_table.setCellWidget(i, 2, del_btn)

    def add_coupon_dialog(self):
        code, ok1 = QInputDialog.getText(self, "کد تخفیف", "کد را وارد کنید (مثلا OFF20):")
        if not ok1 or not code: return

        percent, ok2 = QInputDialog.getInt(self, "درصد تخفیف", "درصد (۱ تا ۱۰۰):", 20, 1, 100)
        if not ok2: return

        min_p, ok3 = QInputDialog.getInt(self, "حداقل خرید", "مبلغ به تومان:", 0, 0, 1000000000)
        if not ok3: return

        data = {"code": code.upper().strip(), "percent": percent, "min_purchase": min_p}
        with next(get_db()) as db:
            crud.create_coupon(db, data)

        self.window().show_toast("کد تخفیف ایجاد شد.")
        asyncio.create_task(self.load_coupons())

    def add_autoreply_dialog(self):
        key, ok1 = QInputDialog.getText(self, "کلمه کلیدی", "مثلاً (آدرس یا ساعت کاری):")
        if not ok1 or not key: return

        resp, ok2 = QInputDialog.getMultiLineText(self, "پاسخ ربات", "متن کامل پاسخ:")
        if not ok2 or not resp: return

        with next(get_db()) as db:
            crud.set_auto_reply(db, key, resp)

        self.window().show_toast("پاسخ خودکار ثبت شد.")
        asyncio.create_task(self.load_auto_replies())

    def delete_autoreply(self, kid):
        if QMessageBox.question(self, "حذف", "آیا مطمئن هستید؟") == QMessageBox.StandardButton.Yes:
            with next(get_db()) as db:
                from db.models import AutoReply
                db.query(AutoReply).filter_by(id=kid).delete()
                db.commit()
            asyncio.create_task(self.load_auto_replies())

    def add_proxy_dialog(self):
        """دیالوگ افزودن پروکسی جدید با قابلیت تشخیص خودکار V2Ray"""
        link, ok = QInputDialog.getMultiLineText(self, "افزودن پروکسی", "لینک V2Ray یا آدرس SOCKS5/HTTP را وارد کنید:")
        if not ok or not link: return

        name, ok2 = QInputDialog.getText(self, "نام پروکسی", "یک نام برای این اتصال انتخاب کنید:")
        if not ok2: name = "Unnamed"

        p_type = "http"
        if link.startswith("socks5://"): p_type = "socks5"
        elif any(link.startswith(s) for s in ["vless://", "vmess://", "trojan://", "ss://"]):
            p_type = "v2ray"

        with next(get_db()) as db:
            crud.add_proxy(db, {"name": name, "url": link.strip(), "type": p_type})

        self.window().show_toast("پروکسی جدید اضافه شد.")
        asyncio.create_task(self.load_proxies())

    def restart_all_bots(self):
        """درخواست ریستارت از MainWindow"""
        win = self.window()
        if hasattr(win, 'btn_restart_bots'):
            win.btn_restart_bots.click()

    def update_monitoring_data(self):
        """دریافت و نمایش دیتای مانیتورینگ از ApplicationManager"""
        win = self.window()
        if hasattr(win, 'app_manager') and win.app_manager:
            stats = win.app_manager.get_bot_stats()
            self.tg_monitor.update_stats(stats["telegram"])
            self.rb_monitor.update_stats(stats["rubika"])

            # آپدیت وضعیت پل Xray
            if win.app_manager.xray and win.app_manager.xray.process:
                if win.app_manager.xray.process.poll() is None:
                    self.lbl_bridge_status.setText("🟢 وضعیت پل Xray: در حال اجرا")
                    self.lbl_bridge_status.setStyleSheet("color: #2cb67d; font-weight: bold;")
                else:
                    self.lbl_bridge_status.setText("🔴 وضعیت پل Xray: متوقف شده")
                    self.lbl_bridge_status.setStyleSheet("color: #ef4565; font-weight: bold;")
            else:
                self.lbl_bridge_status.setText("⚪ وضعیت پل Xray: غیرفعال")
                self.lbl_bridge_status.setStyleSheet("color: #94a1b2;")

            # آپدیت لاگ اسنیپت (۳۰ خط آخر)
            try:
                from config import LOG_DIR
                log_file = LOG_DIR / 'app.log'
                if log_file.exists():
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        self.log_snippet.setPlainText("".join(lines[-30:]))
                        self.log_snippet.moveCursor(self.log_snippet.textCursor().MoveOperation.End)
            except: pass

    @asyncSlot()
    async def activate_proxy(self, pid):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: crud.set_active_proxy(next(get_db()), pid))
        self.window().show_toast("پروکسی فعال شد. برای اعمال کامل نیاز به ریستارت سرویس‌ها است.")
        await self.load_proxies()

    @asyncSlot()
    async def delete_proxy_entry(self, pid):
        if QMessageBox.question(self, "حذف", "آیا این پروکسی حذف شود؟") == QMessageBox.StandardButton.Yes:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, lambda: crud.delete_proxy(next(get_db()), pid))
            await self.load_proxies()

    @asyncSlot()
    async def test_all_proxies(self):
        self.window().show_toast("در حال تست پینگ تمام پروکسی‌ها...")
        with next(get_db()) as db:
            proxies = crud.get_all_proxies(db)
            for p in proxies:
                # تست غیرمسدودساز در پس‌زمینه
                latency, country = await asyncio.get_running_loop().run_in_executor(
                    None, proxy_utils.test_proxy_connectivity, p.url, p.type
                )
                crud.update_proxy_health(db, p.id, latency)
                if country: p.country_code = country
            db.commit()
        await self.load_proxies()

    def _fetch_all_settings(self):
        with next(get_db()) as db:
            keys = [
                "tg_bot_token", "rb_bot_token", "admin_ids",
                "admin_username", "admin_password",
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
            "admin_ids": self.inp_admin_ids.toPlainText(),
            "admin_username": self.inp_admin_user.text(),
            "admin_password": self.inp_admin_pass.text()
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
    async def reset_templates_to_default(self):
        if QMessageBox.question(self, "تایید", "آیا تمام قالب‌ها به متن‌های پیش‌فرض بازنشانی شوند؟") == QMessageBox.StandardButton.Yes:
            from db.database import seed_default_settings
            # برای بازنشانی اجباری، ابتدا باید مقادیر قدیمی پاک شوند (اختیاری) یا seed_default_settings اصلاح شود
            # در اینجا مستقیماً مقادیر را در UI ست می‌کنیم
            defaults = {
                "tmpl_welcome": (
                    "💎 **به فروشگاه {shop_name} خوش آمدید** 👋\n\n"
                    "ما مفتخریم که بهترین محصولات را با تضمین کیفیت و قیمت به شما ارائه می‌دهیم. \n\n"
                    "✨ **مزایای خرید از ما:**\n"
                    "✅ ارسال سریع به سراسر کشور\n"
                    "✅ ضمانت بازگشت وجه\n"
                    "✅ پشتیبانی آنلاین\n\n"
                    "👇 برای شروع خرید، از منوی زیر استفاده کنید:"
                ),
                "tmpl_order": (
                    "✅ **سفارش شما با موفقیت ثبت شد!**\n\n"
                    "🆔 شماره سفارش: `#{order_id}`\n"
                    "💰 مبلغ نهایی: `{total_amount}` تومان\n\n"
                    "📦 سفارش شما در وضعیت 'در حال پردازش' قرار گرفت. \n"
                    "🚀 به محض ارسال کالا، کد رهگیری پستی برای شما ارسال خواهد شد.\n\n"
                    "ممنون از اعتماد و خرید شما! ❤️"
                ),
                "tmpl_support": (
                    "📞 **مرکز پشتیبانی و هماهنگی**\n\n"
                    "در صورت داشتن هرگونه سوال، پیگیری سفارش یا نیاز به مشاوره قبل از خرید، از طریق روش‌های زیر با ما در ارتباط باشید:\n\n"
                    "🆔 **آیدی پشتیبانی:** @Support_Admin\n"
                    "⏰ **ساعات پاسخگویی:** ۱۰ صبح الی ۲۲\n\n"
                    "🔹 لطفاً شماره سفارش خود را برای پیگیری سریع‌تر همراه داشته باشید."
                )
            }
            self.tmpl_welcome.setPlainText(defaults["tmpl_welcome"])
            self.tmpl_order.setPlainText(defaults["tmpl_order"])
            self.tmpl_support.setPlainText(defaults["tmpl_support"])
            self.window().show_toast("قالب‌ها در پنل جایگذاری شدند. برای ثبت نهایی روی 'ذخیره' کلیک کنید.")

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
        # استفاده از رنگ فعلی به عنوان پیش‌فرض
        current_style = self.lbl_color_preview.styleSheet()
        match = re.search(r'background:\s*(#[0-9a-fA-F]+)', current_style)
        initial = QColor(match.group(1)) if match else QColor(ACCENT_COLOR)

        col = QColorDialog.getColor(initial, self, "انتخاب رنگ سازمانی")
        if col.isValid():
            hex_col = col.name()
            self.lbl_color_preview.setStyleSheet(f"background: {hex_col}; border: 1px solid white;")
            with next(get_db()) as db:
                crud.set_setting(db, "accent_color", hex_col)
            self.window().show_toast("رنگ با موفقیت تغییر کرد. برای اعمال سراسری پنل را ریستارت کنید.")

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

    @asyncSlot()
    async def run_system_doctor(self):
        """اجرای ابزار عیب‌یابی هوشمند سیستم"""
        self.doctor_results.setText("⏳ در حال بررسی بخش‌های مختلف سیستم... لطفا صبور باشید.")
        self.btn_run_doctor.setEnabled(False)

        results = []

        # ۱. بررسی دیتابیس
        try:
            from sqlalchemy import text
            with next(get_db()) as db:
                db.execute(text("SELECT 1"))
                results.append("✅ اتصال به پایگاه داده: سالم و فعال")
        except Exception as e:
            results.append(f"❌ پایگاه داده: خطا در اتصال! ({str(e)})")

        # ۲. بررسی شبکه و اینترنت
        try:
            import socket
            socket.create_connection(("google.com", 80), timeout=3)
            results.append("✅ دسترسی به شبکه جهانی: برقرار")
        except:
            results.append("⚠️ شبکه: اینترنت مستقیم قطع است (ممکن است پروکسی نیاز باشد)")

        # ۳. بررسی توکن تلگرام (غیرمسدودساز)
        with next(get_db()) as db:
            tg_token = crud.get_setting(db, "tg_bot_token")
            if tg_token:
                try:
                    import httpx
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(f"https://api.telegram.org/bot{tg_token}/getMe", timeout=5)
                        if resp.status_code == 200: results.append("✅ توکن تلگرام: معتبر و آنلاین")
                        else: results.append(f"❌ توکن تلگرام: نامعتبر (کد {resp.status_code})")
                except:
                    results.append("⚠️ وضعیت تلگرام: عدم امکان بررسی (احتمالا به دلیل فیلترینگ)")
            else:
                results.append("⚪ تلگرام: توکن تنظیم نشده است.")

        self.doctor_results.setText("\n".join(results))
        self.btn_run_doctor.setEnabled(True)

    def export_settings(self):
        """خروجی گرفتن از تمام تنظیمات در قالب فایل JSON"""
        path, _ = QFileDialog.getSaveFileName(self, "ذخیره تنظیمات", "shop_config_backup.json", "JSON Files (*.json)")
        if not path: return

        try:
            with next(get_db()) as db:
                from db.models import Setting
                settings = db.query(Setting).all()
                data = {s.key: s.value for s in settings}

                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

            self.window().show_toast("تنظیمات با موفقیت صادر شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در صادرات: {e}")

    def import_settings(self):
        """وارد کردن تنظیمات از فایل JSON"""
        path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل تنظیمات", "", "JSON Files (*.json)")
        if not path: return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if QMessageBox.question(self, "تایید", f"آیا مطمئن هستید؟ {len(data)} مورد جایگزین خواهد شد.") == QMessageBox.StandardButton.Yes:
                with next(get_db()) as db:
                    for k, v in data.items():
                        crud.set_setting(db, k, v)
                self.window().show_toast("تنظیمات با موفقیت بازنشانی شد.")
                asyncio.create_task(self.refresh_data())
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"فایل نامعتبر است: {e}")

    def create_manual_backup(self):
        from db.database import create_backup
        res = create_backup()
        if res: self.window().show_toast(f"بک‌آپ ایجاد شد: {os.path.basename(res)}")
