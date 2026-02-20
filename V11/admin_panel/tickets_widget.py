import asyncio
import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QFrame, QSplitter,
    QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from qasync import asyncSlot
import qtawesome as qta

from db.database import get_db
from db import crud, models

logger = logging.getLogger("TicketsWidget")

class TicketsWidget(QWidget):
    def __init__(self, bot_app=None, rubika_client=None):
        super().__init__()
        self.bot_app = bot_app
        self.rubika_client = rubika_client
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()
        self._current_ticket_id = None
        self._data_loaded = False

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        title = QLabel("🎫 مرکز پشتیبانی و تیکت")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        header.addWidget(title)
        header.addStretch()

        self.status_filter = QComboBox()
        self.status_filter.addItems(["همه", "open", "pending", "closed"])
        self.status_filter.currentTextChanged.connect(self.refresh_tickets)
        self.status_filter.setStyleSheet("background: #242629; color: white; padding: 5px; border-radius: 5px;")
        header.addWidget(QLabel("وضعیت:"))
        header.addWidget(self.status_filter)

        self.btn_refresh = QPushButton()
        self.btn_refresh.setFixedSize(40, 40)
        self.btn_refresh.setIcon(qta.icon("fa5s.sync", color="white"))
        self.btn_refresh.setStyleSheet("background: #242629; border-radius: 10px;")
        self.btn_refresh.clicked.connect(self.refresh_tickets)
        header.addWidget(self.btn_refresh)
        layout.addLayout(header)

        # Splitter for list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Ticket list
        self.list_widget = QListWidget()
        self.list_widget.setFixedWidth(300)
        self.list_widget.setStyleSheet("background: #242629; color: white; border-radius: 10px; padding: 5px; font-size: 13px;")
        self.list_widget.itemClicked.connect(self.load_ticket_details)
        splitter.addWidget(self.list_widget)

        # Right side: Chat area
        chat_container = QFrame()
        chat_container.setStyleSheet("background: #16161a; border-radius: 10px;")
        chat_layout = QVBoxLayout(chat_container)

        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.chat_view.setStyleSheet("background: #1e1e24; border: 1px solid #333; font-size: 14px; padding: 10px; color: white;")
        chat_layout.addWidget(self.chat_view)

        reply_box = QHBoxLayout()
        self.reply_input = QTextEdit()
        self.reply_input.setPlaceholderText("پاسخ خود را اینجا بنویسید...")
        self.reply_input.setFixedHeight(80)
        self.reply_input.setStyleSheet("background: #242629; color: white; border: 1px solid #333; border-radius: 10px; padding: 8px;")
        reply_box.addWidget(self.reply_input)

        btn_send = QPushButton("ارسال")
        btn_send.setFixedSize(80, 80)
        btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_send.setStyleSheet("background: #7f5af0; color: white; font-weight: bold; border-radius: 10px;")
        btn_send.clicked.connect(self.send_reply)
        reply_box.addWidget(btn_send)
        chat_layout.addLayout(reply_box)

        btn_close = QPushButton("✅ بستن تیکت")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("background: #2cb67d; color: white; padding: 10px; font-weight: bold; border-radius: 8px;")
        btn_close.clicked.connect(self.handle_close_ticket)
        chat_layout.addWidget(btn_close)

        splitter.addWidget(chat_container)
        layout.addWidget(splitter)

    def showEvent(self, event):
        if not self._data_loaded:
            asyncio.create_task(self.refresh_tickets())
            self._data_loaded = True

    @asyncSlot()
    async def refresh_tickets(self):
        status = self.status_filter.currentText()
        if status == "همه": status = None

        loop = asyncio.get_running_loop()
        try:
            def fetch():
                with next(get_db()) as db:
                    return crud.get_all_tickets(db, status)

            tickets = await loop.run_in_executor(None, fetch)

            self.list_widget.clear()
            for t in tickets:
                user_name = t.user.full_name if t.user else "ناشناس"
                item = QListWidgetItem(f"#{t.id} - {t.subject}\n👤 {user_name}")
                item.setData(Qt.ItemDataRole.UserRole, t.id)
                # استایل بر اساس وضعیت
                if t.status == 'open':
                    item.setForeground(Qt.GlobalColor.yellow)
                elif t.status == 'pending':
                    item.setForeground(Qt.GlobalColor.green)
                elif t.status == 'closed':
                    item.setForeground(Qt.GlobalColor.gray)
                self.list_widget.addItem(item)
        except Exception as e:
            logger.error(f"Refresh tickets error: {e}")

    @asyncSlot()
    async def load_ticket_details(self, item):
        ticket_id = item.data(Qt.ItemDataRole.UserRole)
        self._current_ticket_id = ticket_id

        loop = asyncio.get_running_loop()
        try:
            def fetch():
                with next(get_db()) as db:
                    return crud.get_ticket_with_messages(db, ticket_id)

            ticket = await loop.run_in_executor(None, fetch)
            if not ticket: return

            html = f"<div style='background: #333; padding: 10px; border-radius: 5px;'>"
            html += f"<h2 style='color: white; margin: 0;'>{ticket.subject}</h2>"
            html += f"<p style='color: #aaa;'>کاربر: {ticket.user.full_name if ticket.user else '؟'} | وضعیت: {ticket.status}</p></div><br>"

            for m in ticket.messages:
                color = "#7f5af0" if m.is_admin else "#2cb67d"
                align = "left" if m.is_admin else "right"
                bg = "#242629" if m.is_admin else "#1e1e24"
                sender = "ادمین" if m.is_admin else "کاربر"
                time_str = m.created_at.strftime("%H:%M")
                html += f"<div style='text-align: {align};'><div style='display: inline-block; background: {bg}; padding: 10px; border-radius: 10px; margin: 5px; min-width: 100px; border: 1px solid #333;'>"
                html += f"<b style='color: {color};'>{sender}</b> <small style='color: #555;'>{time_str}</small><br>"
                html += f"<span style='color: #eee;'>{m.text}</span></div></div>"

            self.chat_view.setHtml(html)
            QTimer.singleShot(100, lambda: self.chat_view.verticalScrollBar().setValue(self.chat_view.verticalScrollBar().maximum()))
        except Exception as e:
            logger.error(f"Load ticket details error: {e}")

    @asyncSlot()
    async def send_reply(self):
        text = self.reply_input.toPlainText().strip()
        if not text or not self._current_ticket_id: return

        loop = asyncio.get_running_loop()
        try:
            def db_op():
                with next(get_db()) as db:
                    t = crud.get_ticket_with_messages(db, self._current_ticket_id)
                    if not t: raise ValueError("Ticket not found")
                    crud.add_ticket_message(db, t.id, "admin", text, is_admin=True)
                    return t.user_id, t.user.platform, t.id

            user_id, platform, t_id = await loop.run_in_executor(None, db_op)

            # ارسال پیام به کاربر
            msg = f"👨‍💻 **پاسخ پشتیبانی برای تیکت #{t_id}:**\n\n{text}"

            if platform == 'telegram' and self.bot_app:
                try:
                    await self.bot_app.bot.send_message(chat_id=int(user_id), text=msg, parse_mode='Markdown')
                except Exception as e: logger.error(f"TG send error: {e}")
            elif platform == 'rubika' and self.rubika_client:
                try:
                    await self.rubika_client.api.send_message(chat_id=user_id, text=msg)
                except Exception as e: logger.error(f"RB send error: {e}")

            self.reply_input.clear()
            await self.load_ticket_details(self.list_widget.currentItem())

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ارسال پاسخ: {e}")

    @asyncSlot()
    async def handle_close_ticket(self):
        if not self._current_ticket_id: return
        if QMessageBox.question(self, "بستن تیکت", "آیا از بستن این تیکت مطمئن هستید؟") == QMessageBox.StandardButton.Yes:
            loop = asyncio.get_running_loop()

            def db_op():
                with next(get_db()) as db:
                    return crud.close_ticket(db, self._current_ticket_id)

            await loop.run_in_executor(None, db_op)
            await self.refresh_tickets()
            self.chat_view.clear()
            self._current_ticket_id = None
