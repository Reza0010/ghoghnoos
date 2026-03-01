import asyncio
import csv
import logging
import os
import webbrowser
from datetime import datetime, timedelta
from typing import Optional, List, Any, Set

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QLineEdit, QMessageBox,
    QGraphicsDropShadowEffect, QTextEdit, QDialog, QLayout, QStyle, QSizePolicy,
    QComboBox, QApplication, QCheckBox, QInputDialog, QFileDialog, QMenu, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget
)
from PyQt6.QtGui import QColor, QFont, QCursor, QPainter, QAction, QLinearGradient, QBrush, QPen, QPixmap
from PyQt6.QtCore import Qt, QSize, QTimer, QRect, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from qasync import asyncSlot
import qtawesome as qta
from db.database import SessionLocal
from db import crud, models

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
# Helper: Flow Layout
# ==============================================================================
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None: self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item: item = self.takeAt(0)

    def addItem(self, item): self.itemList.append(item)
    def count(self): return len(self.itemList)
    def itemAt(self, index): return self.itemList[index] if 0 <= index < len(self.itemList) else None
    def takeAt(self, index):
        if 0 <= index < len(self.itemList): return self.itemList.pop(index)
        return None

    def expandingDirections(self): return Qt.Orientation(0)
    def hasHeightForWidth(self): return True
    def heightForWidth(self, width): return self.doLayout(QRect(0, 0, width, 0), True)
    def setGeometry(self, rect): super(FlowLayout, self).setGeometry(rect); self.doLayout(rect, False)
    def sizeHint(self): return self.minimumSize()
    def minimumSize(self):
        size = QSize()
        for item in self.itemList: size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def doLayout(self, rect, testOnly):
        x, y = rect.x(), rect.y()
        lineHeight = 0
        spaceX = self.spacing()
        spaceY = self.spacing()

        for item in self.itemList:
            wid = item.widget()
            if wid.isHidden(): continue

            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly: item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y()

# ==============================================================================
# Dialog: جزئیات کاربر (بهینه شده با تاریخچه)
# ==============================================================================
class UserDetailsDialog(QDialog):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user = user_data
        self.setWindowTitle(f"پروفایل کاربر")
        self.setFixedSize(600, 800)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(f"QDialog {{ background-color: {BG_COLOR}; color: {TEXT_MAIN}; }}")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # هدر
        header = QFrame()
        header.setStyleSheet(f"background: {PANEL_BG}; border-bottom: 1px solid {BORDER_COLOR};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 20, 20, 20)

        avatar = QLabel()
        avatar.setFixedSize(60, 60)
        avatar.setStyleSheet(f"background: {ACCENT_COLOR}30; border-radius: 30px;")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setPixmap(qta.icon("fa5s.user", color=ACCENT_COLOR).pixmap(30, 30))

        info = QVBoxLayout()
        name = QLabel(self.user.full_name or "کاربر ناشناس")
        name.setStyleSheet("font-size: 18px; font-weight: bold;")
        uid = QLabel(f"ID: {self.user.user_id}")
        uid.setStyleSheet(f"color: {TEXT_SUB};")
        info.addWidget(name); info.addWidget(uid)

        h_layout.addWidget(avatar); h_layout.addLayout(info); h_layout.addStretch()
        layout.addWidget(header)

        # تب‌بندی
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; background: transparent; }}
            QTabBar::tab {{ background: {BG_COLOR}; color: {TEXT_SUB}; padding: 12px 25px; border-top-left-radius: 8px; border-top-right-radius: 8px; }}
            QTabBar::tab:selected {{ background: {PANEL_BG}; color: {ACCENT_COLOR}; font-weight: bold; border-bottom: 2px solid {ACCENT_COLOR}; }}
        """)

        # --- تب اطلاعات ---
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        info_layout.setContentsMargins(20, 20, 20, 20)

        stats_row = QHBoxLayout()
        spent = int(getattr(self.user, 'total_spent', 0) or 0)
        orders = int(getattr(self.user, 'order_count', 0) or 0)
        stats_row.addWidget(self._stat_box(f"{spent:,}", "کل خرید (تومان)"))
        stats_row.addWidget(self._stat_box(str(orders), "تعداد سفارش"))
        info_layout.addLayout(stats_row)

        # Tags Management
        info_layout.addWidget(QLabel("برچسب‌ها (سگمنتیشن):"))
        self.inp_tags = QLineEdit()
        self.inp_tags.setPlaceholderText("مثلاً: VIP, همکار (جدا شده با کاما)")
        self.inp_tags.setText(getattr(self.user, 'tags', "") or "")
        info_layout.addWidget(self.inp_tags)

        last_seen = getattr(self.user, 'last_seen', None)
        ls_text = last_seen.strftime("%Y/%m/%d %H:%M") if last_seen else "نامشخص"
        lbl_ls = QLabel(f"🕒 آخرین بازدید: {ls_text}")
        lbl_ls.setStyleSheet(f"color: {TEXT_SUB}; margin: 5px 0;")
        info_layout.addWidget(lbl_ls)

        info_layout.addWidget(QLabel("یادداشت خصوصی ادمین:"))
        self.txt_note = QTextEdit()
        self.txt_note.setPlainText(getattr(self.user, 'private_note', "") or "")
        self.txt_note.setStyleSheet(f"background: {PANEL_BG}; border: 1px solid {BORDER_COLOR}; border-radius: 8px; padding: 8px;")
        info_layout.addWidget(self.txt_note)

        btn_save = QPushButton("💾 ذخیره تغییرات نهایی")
        btn_save.setStyleSheet(f"background: {SUCCESS_COLOR}; color: white; padding: 12px; border-radius: 8px; font-weight: bold;")
        btn_save.clicked.connect(self.save_note)
        info_layout.addWidget(btn_save)
        info_layout.addStretch()

        tabs.addTab(info_tab, "اطلاعات کلی")

        # --- تب تاریخچه (Timeline) ---
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        self.timeline_container = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_container)
        self.timeline_layout.addStretch()
        scroll.setWidget(self.timeline_container)

        history_layout.addWidget(scroll)
        tabs.addTab(history_tab, "خط زمانی فعالیت‌ها")

        layout.addWidget(tabs)

        # دکمه بستن
        btn_close = QPushButton("بستن")
        btn_close.setStyleSheet(f"background: {BORDER_COLOR}; color: white; padding: 10px; margin: 10px; border-radius: 5px;")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

        QTimer.singleShot(100, self.load_history)

    def load_history(self):
        """بارگذاری زمانی تعاملات کاربر"""
        with SessionLocal() as db:
            # ۱. دریافت سفارشات
            orders = db.query(models.Order).filter(models.Order.user_id == str(self.user.user_id)).order_by(models.Order.created_at.desc()).all()
            for o in orders:
                self.add_timeline_item(
                    f"ثبت سفارش #{o.id}",
                    o.created_at.strftime("%Y/%m/%d %H:%M"),
                    f"مبلغ: {int(o.total_amount):,} تومان | وضعیت: {o.status}",
                    "fa5s.shopping-cart",
                    SUCCESS_COLOR if o.status in ['paid', 'approved', 'shipped'] else WARNING_COLOR
                )

            # ۲. دریافت لاگ‌های سیستمی
            logs = db.query(models.AuditLog).filter(
                models.AuditLog.target_id == str(self.user.user_id),
                models.AuditLog.target_type == "user"
            ).all()
            for l in logs:
                self.add_timeline_item(
                    l.action,
                    l.created_at.strftime("%Y/%m/%d %H:%M"),
                    l.description,
                    "fa5s.history",
                    INFO_COLOR
                )

    def add_timeline_item(self, title, time, desc, icon, color):
        item = QFrame()
        item.setStyleSheet(f"background: rgba(255,255,255,0.02); border-radius: 12px; margin-bottom: 10px;")
        lay = QVBoxLayout(item)

        header = QHBoxLayout()
        # Graphical Dot
        dot = QLabel(); dot.setFixedSize(12, 12); dot.setStyleSheet(f"background: {color}; border-radius: 6px; border: 2px solid white;")

        ico = QLabel()
        ico.setPixmap(qta.icon(icon, color=color).pixmap(18, 18))
        ti = QLabel(title); ti.setStyleSheet("font-weight: 900; color: white; font-size: 13px;")
        tm = QLabel(time); tm.setStyleSheet(f"color: {TEXT_SUB}; font-size: 10px;")

        header.addWidget(dot); header.addWidget(ico); header.addWidget(ti); header.addStretch(); header.addWidget(tm)

        content = QHBoxLayout()
        content.addSpacing(25)
        de = QLabel(desc); de.setStyleSheet(f"color: {TEXT_SUB}; font-size: 11px;")
        de.setWordWrap(True)
        content.addWidget(de)

        lay.addLayout(header)
        lay.addLayout(content)
        self.timeline_layout.insertWidget(0, item)

    def _stat_box(self, val, txt):
        f = QFrame()
        f.setStyleSheet(f"background: {BG_COLOR}; border-radius: 8px;")
        l = QVBoxLayout(f)
        v = QLabel(val); v.setAlignment(Qt.AlignmentFlag.AlignCenter); v.setStyleSheet("font-weight: bold; font-size: 16px;")
        t = QLabel(txt); t.setAlignment(Qt.AlignmentFlag.AlignCenter); t.setStyleSheet(f"color: {TEXT_SUB}; font-size: 11px;")
        l.addWidget(v); l.addWidget(t)
        return f

    def save_note(self):
        asyncio.create_task(self._save_db_note(self.txt_note.toPlainText(), self.inp_tags.text()))
        self.accept()

    async def _save_db_note(self, txt, tags):
        with SessionLocal() as db:
            u = db.query(models.User).filter(models.User.user_id == str(self.user.user_id)).first()
            if u:
                u.private_note = txt
                u.tags = tags
                db.commit()

# ==============================================================================
# Component: User Card
# ==============================================================================
class AvatarGenerator:
    COLORS = ["#7f5af0", "#2cb67d", "#3da9fc", "#ef4565", "#f39c12", "#72757e"]

    @staticmethod
    def get_initials(name):
        if not name: return "?"
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return name[0].upper()

    @staticmethod
    def generate_pixmap(name, size=40):
        initials = AvatarGenerator.get_initials(name)
        # انتخاب رنگ بر اساس نام برای ثبات
        color_idx = sum(ord(c) for c in initials) % len(AvatarGenerator.COLORS)
        color = QColor(AvatarGenerator.COLORS[color_idx])

        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw Circle
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size, size)

        # Draw Text
        painter.setPen(QColor("white"))
        font = QFont("Vazirmatn", int(size * 0.4), QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, initials)
        painter.end()
        return pixmap

class UserCard(QFrame):
    selectionChanged = pyqtSignal(str, bool)

    def __init__(self, user_data, parent_widget, delay=0):
        super().__init__()
        self.user = user_data
        self.parent_widget = parent_widget
        self.user_id = getattr(user_data, 'user_id', None)
        self.platform = getattr(user_data, 'platform', 'telegram')

        self.setFixedSize(300, 240)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # محاسبه سطح
        total_spent = getattr(user_data, 'total_spent', 0) or 0
        if total_spent > 10_000_000: self.badge = {"col": "#f1c40f", "icon": "fa5s.crown", "txt": "VIP"}
        elif total_spent > 3_000_000: self.badge = {"col": "#bdc3c7", "icon": "fa5s.star", "txt": "Pro"}
        elif getattr(user_data, 'order_count', 0) > 0: self.badge = {"col": SUCCESS_COLOR, "icon": "fa5s.user", "txt": "Active"}
        else: self.badge = {"col": TEXT_SUB, "icon": "fa5s.user-tag", "txt": "New"}

        self._apply_styles()
        self._setup_ui()

        # Entrance Animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(400)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        QTimer.singleShot(delay, self.anim.start)

    def _apply_styles(self):
        is_banned = getattr(self.user, 'is_banned', False)
        border = DANGER_COLOR if is_banned else BORDER_COLOR
        self.setStyleSheet(f"""
            QFrame {{ background-color: {PANEL_BG}; border-radius: 14px; border: 1px solid {border}; }}
            QFrame:hover {{ border: 1px solid {ACCENT_COLOR}; }}
            QLabel {{ background: transparent; color: {TEXT_MAIN}; border: none; }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20); shadow.setColor(QColor(0,0,0,60)); shadow.setOffset(0,5)
        self.setGraphicsEffect(shadow)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # --- Header ---
        h_top = QHBoxLayout()
        self.chk_select = QCheckBox()
        self.chk_select.setFixedSize(22, 22)
        self.chk_select.setStyleSheet(f"QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 5px; border: 2px solid {ACCENT_COLOR}; }} QCheckBox::indicator:checked {{ background: {SUCCESS_COLOR}; }}")
        self.chk_select.stateChanged.connect(self._on_select)

        ico = QLabel()
        ico.setFixedSize(40, 40)
        name_val = getattr(self.user, 'full_name', "") or getattr(self.user, 'username', "User")
        ico.setPixmap(AvatarGenerator.generate_pixmap(name_val))

        v_info = QVBoxLayout()
        name = getattr(self.user, 'full_name', "Unknown") or "User"
        if len(name) > 18: name = name[:16] + "..."
        lbl_name = QLabel(name); lbl_name.setStyleSheet("font-weight: bold; font-size: 14px;")
        lbl_id = QLabel(f"ID: ...{str(self.user_id)[-8:]}"); lbl_id.setStyleSheet(f"color: {TEXT_SUB}; font-size: 11px;")
        v_info.addWidget(lbl_name); v_info.addWidget(lbl_id)

        p_icon = "fa5b.telegram-plane" if self.platform == 'telegram' else "mdi6.infinity"
        p_col = INFO_COLOR if self.platform == 'telegram' else "#8e44ad"
        lbl_plat = QLabel()
        lbl_plat.setPixmap(qta.icon(p_icon, color=p_col).pixmap(22, 22))

        h_top.addWidget(self.chk_select)
        h_top.addWidget(ico)

        v_badge = QVBoxLayout()
        v_badge.setSpacing(2)
        lbl_badge = QLabel(self.badge['txt'])
        lbl_badge.setStyleSheet(f"color: {self.badge['col']}; font-size: 9px; font-weight: bold; background: {self.badge['col']}15; padding: 2px 6px; border-radius: 4px;")
        v_badge.addWidget(lbl_badge)
        v_badge.addLayout(v_info)

        h_top.addLayout(v_badge)
        h_top.addStretch()
        h_top.addWidget(lbl_plat)
        layout.addLayout(h_top)

        # --- Last Seen ---
        last_seen = getattr(self.user, 'last_seen', None)
        ls_text = "آخرین بازدید: "
        if last_seen:
            diff = datetime.now() - last_seen
            if diff.days == 0: ls_text += "امروز"
            elif diff.days == 1: ls_text += "دیروز"
            else: ls_text += last_seen.strftime("%Y/%m/%d")
        else: ls_text += "نامشخص"
        lbl_ls = QLabel(ls_text)
        lbl_ls.setStyleSheet(f"color: {TEXT_SUB}; font-size: 10px;")
        layout.addWidget(lbl_ls)

        # --- Stats ---
        h_stats = QHBoxLayout()
        spent = int(getattr(self.user, 'total_spent', 0) or 0)
        orders = int(getattr(self.user, 'order_count', 0) or 0)
        h_stats.addWidget(self._stat_box(f"{orders}", "سفارش"))
        h_stats.addWidget(self._stat_box(f"{spent:,}", "خرید"))
        layout.addLayout(h_stats)

        # --- Last Message Snippet ---
        last_msg = getattr(self.user, 'last_interaction_text', "") or ""
        if last_msg:
            snippet = last_msg[:45] + "..." if len(last_msg) > 45 else last_msg
            lbl_msg = QLabel(f"💬 {snippet}")
            lbl_msg.setStyleSheet(f"color: {TEXT_SUB}; font-size: 11px; font-style: italic; background: rgba(0,0,0,0.1); padding: 5px; border-radius: 5px;")
            layout.addWidget(lbl_msg)

        # --- Actions ---
        h_btns = QHBoxLayout()
        h_btns.setSpacing(8)

        btn_note = self._action_btn("fa5s.sticky-note", WARNING_COLOR if getattr(self.user, 'private_note') else PANEL_BG, self.open_note)
        btn_chat = self._action_btn("fa5s.comment", INFO_COLOR, self.open_chat)

        is_banned = getattr(self.user, 'is_banned', False)
        btn_ban = self._action_btn("fa5s.ban" if not is_banned else "fa5s.check", DANGER_COLOR if not is_banned else SUCCESS_COLOR, self.toggle_ban)

        h_btns.addStretch()
        h_btns.addWidget(btn_note); h_btns.addWidget(btn_chat); h_btns.addWidget(btn_ban)
        layout.addLayout(h_btns)

        # Context Menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def _stat_box(self, val, txt):
        f = QFrame(); f.setStyleSheet(f"background: {BG_COLOR}; border-radius: 6px;")
        l = QVBoxLayout(f); l.setContentsMargins(8, 4, 8, 4); l.setSpacing(0)
        v = QLabel(val); v.setAlignment(Qt.AlignmentFlag.AlignCenter); v.setStyleSheet("font-weight: bold; color: white;")
        t = QLabel(txt); t.setAlignment(Qt.AlignmentFlag.AlignCenter); t.setStyleSheet(f"color: {TEXT_SUB}; font-size: 10px;")
        l.addWidget(v); l.addWidget(t)
        return f

    def _action_btn(self, icon, color, callback):
        b = QPushButton()
        b.setFixedSize(34, 34)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setStyleSheet(f"background: {color}; border-radius: 8px; border: none;")
        b.setIcon(qta.icon(icon, color="white"))
        b.clicked.connect(callback)
        return b

    # --- Logic ---
    def mouseDoubleClickEvent(self, event):
        self.show_details()

    def show_details(self):
        dlg = UserDetailsDialog(self.user, self)
        dlg.exec()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"QMenu {{ background: {PANEL_BG}; color: white; border: 1px solid {BORDER_COLOR}; }} QMenu::item:selected {{ background: {ACCENT_COLOR}; }}")

        act_detail = QAction("جزئیات کامل", self)
        act_detail.triggered.connect(self.show_details)
        menu.addAction(act_detail)

        act_copy = QAction("کپی شناسه", self)
        act_copy.triggered.connect(lambda: QApplication.clipboard().setText(str(self.user_id)))
        menu.addAction(act_copy)

        menu.addSeparator()

        is_banned = getattr(self.user, 'is_banned', False)
        act_ban = QAction("رفع مسدودی" if is_banned else "مسدود کردن", self)
        act_ban.triggered.connect(self.toggle_ban)
        menu.addAction(act_ban)

        menu.exec(self.mapToGlobal(pos))

    def _on_select(self, state):
        self.selectionChanged.emit(str(self.user_id), state == 2)

    def open_chat(self):
        """ارسال پیام مستقیم از طریق ربات"""
        msg, ok = QInputDialog.getMultiLineText(self, "ارسال پیام مستقیم", f"متن پیام برای {self.user.full_name}:")
        if ok and msg:
            asyncio.create_task(self._async_send_direct_message(msg))

    async def _async_send_direct_message(self, text):
        try:
            if self.platform == 'telegram' and self.parent_widget.bot_app:
                await self.parent_widget.bot_app.bot.send_message(chat_id=self.user_id, text=text)
                self.parent_widget.window().show_toast("پیام تلگرام ارسال شد.")
            elif self.platform == 'rubika' and self.parent_widget.rubika_client:
                await self.parent_widget.rubika_client.send_message(chat_id=self.user_id, text=text)
                self.parent_widget.window().show_toast("پیام روبیکا ارسال شد.")
            else:
                self.parent_widget.window().show_toast("سرویس ربات متصل نیست!", is_error=True)
        except Exception as e:
            self.parent_widget.window().show_toast(f"خطا در ارسال: {str(e)}", is_error=True)

    def open_note(self):
        self.show_details()

    def toggle_ban(self):
        is_banned = getattr(self.user, 'is_banned', False)
        msg = "رفع مسدودی؟" if is_banned else "مسدود کردن؟"
        if QMessageBox.question(self, "تایید", msg) == QMessageBox.StandardButton.Yes:
            asyncio.create_task(self._db_op(lambda: self._db_ban(not is_banned)))

    async def _db_op(self, func):
        try:
            await asyncio.get_running_loop().run_in_executor(None, func)
            self.parent_widget.window().show_toast("عملیات با موفقیت انجام شد.")
            await self.parent_widget.refresh_data()
        except Exception as e: logger.error(e)

    def _db_ban(self, status):
        with SessionLocal() as db:
            u = db.query(models.User).filter(models.User.user_id == str(self.user_id)).first()
            if u:
                u.is_banned = status
                action = "ban_user" if status else "unban_user"
                crud.record_audit_log(db, action, target_type="user", target_id=u.user_id, description=f"کاربر {u.full_name} {'مسدود' if status else 'رفع مسدودیت'} شد.")
                db.commit()

# ==============================================================================
# Main Widget
# ==============================================================================
class UsersWidget(QWidget):
    def __init__(self, bot_app=None, rubika_client=None):
        super().__init__()
        self.bot_app = bot_app
        self.rubika_client = rubika_client
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._data_loaded = False
        self.selected_ids: Set[str] = set()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- Header ---
        h_top = QHBoxLayout()
        v_ti = QVBoxLayout()
        t = QLabel("👥 مدیریت مشتریان")
        t.setStyleSheet("font-size: 24px; font-weight: 900; color: white;")
        s = QLabel("CRM و مدیریت کاربران ربات")
        s.setStyleSheet(f"color: {TEXT_SUB}; font-size: 12px;")
        v_ti.addWidget(t); v_ti.addWidget(s)

        # Quick Filters
        h_quick = QHBoxLayout()
        btn_new = QPushButton("جدید امروز")
        btn_new.setStyleSheet(f"background: transparent; border: 1px solid {BORDER_COLOR}; color: {TEXT_SUB}; border-radius: 4px; padding: 4px;")
        btn_new.clicked.connect(lambda: self._quick_filter("new"))

        self.cmb_platform = QComboBox(); self.cmb_platform.addItems(["همه پلتفرم‌ها", "تلگرام", "روبیکا"])
        self.cmb_status = QComboBox(); self.cmb_status.addItems(["همه وضعیت‌ها", "فعال", "مسدود"])
        self.cmb_tags = QComboBox(); self.cmb_tags.addItems(["برچسب: همه"])
        self.cmb_platform.currentIndexChanged.connect(self._start_search)
        self.cmb_status.currentIndexChanged.connect(self._start_search)
        self.cmb_tags.currentIndexChanged.connect(self._start_search)

        self.inp_search = QLineEdit(); self.inp_search.setPlaceholderText("🔍 جستجو نام، آیدی یا مبلغ (>500000)")
        self.inp_search.setFixedWidth(300)
        self.inp_search.setStyleSheet(f"background: {PANEL_BG}; border: 1px solid {BORDER_COLOR}; border-radius: 8px; padding: 10px; color: white;")
        self.search_timer = QTimer(); self.search_timer.setSingleShot(True); self.search_timer.timeout.connect(self.refresh_data)
        self.inp_search.textChanged.connect(lambda: self.search_timer.start(400))

        btn_ref = QPushButton(); btn_ref.setIcon(qta.icon('fa5s.sync-alt', color='white'))
        btn_ref.setFixedSize(40, 40); btn_ref.setStyleSheet(f"background: {SUCCESS_COLOR}; border-radius: 8px;")
        btn_ref.clicked.connect(self.refresh_data)

        btn_exp = QPushButton(" خروجی اکسل"); btn_exp.setIcon(qta.icon('fa5s.file-csv', color='white'))
        btn_exp.setStyleSheet(f"background: {INFO_COLOR}; color: white; border-radius: 8px; padding: 8px;")
        btn_exp.clicked.connect(self.export_csv)

        h_top.addLayout(v_ti)
        h_quick.addWidget(btn_new)
        h_top.addLayout(h_quick)
        h_top.addWidget(QLabel("پلتفرم:")); h_top.addWidget(self.cmb_platform)
        h_top.addWidget(QLabel("وضعیت:")); h_top.addWidget(self.cmb_status)
        h_top.addWidget(self.cmb_tags)
        h_top.addWidget(self.inp_search)
        h_top.addWidget(btn_ref); h_top.addWidget(btn_exp)
        layout.addLayout(h_top)

        # --- Flow Area ---
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("background: transparent; border: none;")
        self.container = QWidget()
        self.flow_layout = FlowLayout(self.container, spacing=15)
        scroll.setWidget(self.container)
        layout.addWidget(scroll)

        # --- Bulk Toolbar ---
        self.bulk_toolbar = QFrame()
        self.bulk_toolbar.setVisible(False)
        self.bulk_toolbar.setStyleSheet(f"background: {PANEL_BG}; border-radius: 8px; border: 2px solid {DANGER_COLOR};")
        h_bulk = QHBoxLayout(self.bulk_toolbar); h_bulk.setContentsMargins(10, 5, 10, 5)
        self.lbl_sel = QLabel("0 انتخاب شده"); self.lbl_sel.setStyleSheet("color: white; font-weight: bold;")
        btn_bc = QPushButton("ارسال پیام گروهی"); btn_bc.setStyleSheet(f"background: {DANGER_COLOR}; color: white; border-radius: 6px; padding: 6px;")
        btn_bc.clicked.connect(self.broadcast)
        h_bulk.addWidget(self.lbl_sel); h_bulk.addWidget(btn_bc); h_bulk.addStretch()
        layout.addWidget(self.bulk_toolbar)

    def _quick_filter(self, f_type):
        if f_type == "new":
            # تنظیم فیلتر برای کاربران جدید (مثال)
            pass
        self.refresh_data()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._data_loaded:
            QTimer.singleShot(200, self.refresh_data)
            self._data_loaded = True

    def _start_search(self): self.search_timer.start(300)

    @asyncSlot()
    async def refresh_data(self):
        # --- Skeleton State ---
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for i in range(6):
            skel = QFrame()
            skel.setFixedSize(300, 240)
            skel.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PANEL_BG}, stop:0.5 {CARD_BG}, stop:1 {PANEL_BG}); border-radius: 14px;")
            self.flow_layout.addWidget(skel)

        self.selected_ids.clear(); self.update_bulk_ui()

        q = self.inp_search.text().lower().strip()
        p_f = self.cmb_platform.currentText()
        s_f = self.cmb_status.currentText()
        tag_f = self.cmb_tags.currentText().replace("برچسب: ", "")

        loop = asyncio.get_running_loop()
        try:
            data = await loop.run_in_executor(None, lambda: self._fetch_users(q, p_f, s_f, tag_f))
            users = data['users']

            # Update Tags List
            current_tag = self.cmb_tags.currentText()
            self.cmb_tags.blockSignals(True)
            self.cmb_tags.clear(); self.cmb_tags.addItem("برچسب: همه")
            for t in sorted(data['all_tags']): self.cmb_tags.addItem(f"برچسب: {t}")
            self.cmb_tags.setCurrentText(current_tag)
            self.cmb_tags.blockSignals(False)

            # Remove Skeletons
            while self.flow_layout.count():
                item = self.flow_layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()

            if not users:
                l = QLabel("هیچ کاربری یافت نشد."); l.setStyleSheet(f"color: {TEXT_SUB}; margin: 50px;"); l.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.flow_layout.addWidget(l)
            else:
                for i, u in enumerate(users):
                    card = UserCard(u, self, delay=i*30) # Cascading animation
                    card.selectionChanged.connect(self._on_card_select)
                    self.flow_layout.addWidget(card)
        except Exception as e: logger.error(e)

    def _fetch_users(self, q, p_f, s_f, tag_f):
        with SessionLocal() as db:
            all_users = crud.get_all_users(db)
            res = []
            all_tags = set()
            for u in all_users:
                # Extract Tags
                u_tags = [t.strip() for t in (u.tags or "").split(',') if t.strip()]
                for t in u_tags: all_tags.add(t)

                # Filters
                if p_f != "همه پلتفرم‌ها" and u.platform != p_f.lower(): continue
                if s_f == "فعال" and u.is_banned: continue
                if s_f == "مسدود" and not u.is_banned: continue
                if tag_f != "همه" and tag_f not in u_tags: continue

                # Search
                match = True
                if q:
                    if ">" in q:
                        try:
                            amt = int(q.replace(">", ""))
                            spent = sum(o.total_amount for o in u.orders if o.status in ['paid', 'shipped', 'approved'])
                            if spent <= amt: match = False
                        except: pass
                    elif "<" in q:
                         try:
                            amt = int(q.replace("<", ""))
                            spent = sum(o.total_amount for o in u.orders if o.status in ['paid', 'shipped', 'approved'])
                            if spent >= amt: match = False
                         except: pass
                    else:
                        if q not in (u.full_name or "").lower() and q not in str(u.user_id): match = False

                if match:
                    spent = sum(o.total_amount for o in u.orders if o.status in ['paid', 'shipped', 'approved'])
                    obj = type('U', (), {
                        "user_id": u.user_id, "full_name": u.full_name, "platform": u.platform,
                        "is_banned": u.is_banned, "private_note": u.private_note,
                        "tags": u.tags, "last_interaction_text": u.last_interaction_text,
                        "order_count": len(u.orders), "total_spent": spent, "last_seen": u.last_seen
                    })
                    res.append(obj)

            res.sort(key=lambda x: x.total_spent, reverse=True)
            return {"users": res, "all_tags": list(all_tags)}

    def show_user_details_by_id(self, user_id):
        """نمایش جزئیات یک کاربر خاص (استفاده توسط Command Palette)"""
        with SessionLocal() as db:
            u = db.query(models.User).filter(models.User.user_id == str(user_id)).first()
            if u:
                spent = sum(o.total_amount for o in u.orders if o.status in ['paid', 'shipped', 'approved'])
                obj = type('U', (), {
                    "user_id": u.user_id, "full_name": u.full_name, "platform": u.platform,
                    "is_banned": u.is_banned, "private_note": u.private_note,
                    "order_count": len(u.orders), "total_spent": spent, "last_seen": u.last_seen
                })
                dlg = UserDetailsDialog(obj, self)
                dlg.exec()

    def _on_card_select(self, uid, selected):
        if selected: self.selected_ids.add(uid)
        else: self.selected_ids.discard(uid)
        self.update_bulk_ui()

    def update_bulk_ui(self):
        c = len(self.selected_ids)
        self.bulk_toolbar.setVisible(c > 0)
        self.lbl_sel.setText(f"{c} انتخاب شده")

    @asyncSlot()
    async def broadcast(self):
        """ارسال پیام همگانی هوشمند با پلتفرم هدف"""
        target_ids = list(self.selected_ids)
        if not target_ids:
            # اگر کسی انتخاب نشده، تمام کاربران فیلتر شده فعلی را انتخاب کن
            # این کار برای سادگی در اینجا پیاده نشده، اما ایده Targeted Broadcast است.
            pass

        msg, ok = QInputDialog.getMultiLineText(self, "پیام همگانی (هدفمند)", f"پیام برای {len(target_ids)} کاربر:")
        if ok and msg:
            self.window().show_toast("در حال ارسال پیام...")
            asyncio.create_task(self._async_broadcast(msg, target_ids))

    async def _async_broadcast(self, text, user_ids):
        success, fail = 0, 0
        with SessionLocal() as db:
            for uid in user_ids:
                user = db.query(models.User).filter_by(user_id=uid).first()
                if not user: continue

                try:
                    if user.platform == 'telegram' and self.bot_app:
                        await self.bot_app.bot.send_message(chat_id=uid, text=text)
                        success += 1
                    elif user.platform == 'rubika' and self.rubika_client:
                        await self.rubika_client.send_message(chat_id=uid, text=text)
                        success += 1
                    else: fail += 1
                except Exception as e:
                    logger.error(f"Broadcast error for {uid}: {e}")
                    fail += 1

                await asyncio.sleep(0.05) # جلوگیری از فلود

        self.window().show_toast(f"پایان ارسال. موفق: {success} | ناموفق: {fail}")

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "خروجی اکسل", "users.csv", "CSV (*.csv)")
        if path:
            asyncio.create_task(self._do_export(path))

    async def _do_export(self, path):
        """خروجی اکسل پیشرفته (Export Pro)"""
        try:
            q = self.inp_search.text().lower().strip()
            p_f = self.cmb_platform.currentText()
            s_f = self.cmb_status.currentText()
            tag_f = self.cmb_tags.currentText().replace("برچسب: ", "")

            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(None, lambda: self._fetch_users(q, p_f, s_f, tag_f))
            users = data['users']

            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                w.writerow(["شناسه", "نام کامل", "نام کاربری", "پلتفرم", "تلفن", "مجموع خرید", "تعداد سفارش", "برچسب‌ها", "وضعیت", "آخرین بازدید"])

                # دریافت اطلاعات کامل‌تر از دیتابیس برای اکسپورت
                with SessionLocal() as db:
                    for u_summary in users:
                        u = db.query(models.User).get(u_summary.user_id)
                        w.writerow([
                            u.user_id, u.full_name, u.username, u.platform, u.phone_number,
                            u_summary.total_spent, u_summary.order_count, u.tags,
                            "مسدود" if u.is_banned else "فعال", u.last_seen
                        ])

            self.window().show_toast("خروجی Pro با موفقیت ذخیره شد.")
        except Exception as e: logger.error(f"Export error: {e}")
