from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QTextBrowser
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QThread
from telegram.error import Forbidden
from telegram_shop_bot.db.database import get_db
from telegram_shop_bot.db import crud
from .async_worker import AsyncWorker

class OrdersWidget(QWidget):
    def __init__(self, bot_app):
        super().__init__()
        self.bot_app = bot_app
        self.current_order_id = None
        # Use separate threads for different async tasks to avoid conflicts
        self.photo_worker_thread = QThread()
        self.message_worker_thread = QThread()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setDirection(QHBoxLayout.Direction.RightToLeft)
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.addWidget(QLabel("سفارش‌های در انتظار تایید:"))
        self.orders_table = QTableWidget(columnCount=4)
        self.orders_table.setHorizontalHeaderLabels(["ID", "مشتری", "مبلغ", "تاریخ"])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.orders_table.selectionModel().selectionChanged.connect(self.display_order_details)
        table_layout.addWidget(self.orders_table)
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_widget.setFixedWidth(400)
        details_layout.addWidget(QLabel("جزئیات سفارش:"))
        self.details_browser = QTextBrowser()
        details_layout.addWidget(self.details_browser)
        details_layout.addWidget(QLabel("تصویر رسید:"))
        self.receipt_label = QLabel("یک سفارش را انتخاب کنید")
        self.receipt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.receipt_label.setMinimumHeight(200)
        details_layout.addWidget(self.receipt_label)
        btn_layout = QHBoxLayout()
        self.approve_btn = QPushButton("✅ تایید")
        self.reject_btn = QPushButton("❌ رد")
        btn_layout.addWidget(self.approve_btn)
        btn_layout.addWidget(self.reject_btn)
        details_layout.addLayout(btn_layout)
        main_layout.addWidget(table_widget)
        main_layout.addWidget(details_widget)
        self.approve_btn.clicked.connect(lambda: self.update_status("approved"))
        self.reject_btn.clicked.connect(lambda: self.update_status("rejected"))

    def refresh_data(self):
        self.load_orders()

    def load_orders(self):
        with next(get_db()) as db:
            orders = crud.get_orders_by_status(db, "pending_payment")
        self.orders_table.clearContents()
        self.orders_table.setRowCount(len(orders))
        for r, o in enumerate(orders):
            self.orders_table.setItem(r, 0, QTableWidgetItem(str(o.id)))
            self.orders_table.setItem(r, 1, QTableWidgetItem(o.user.full_name))
            self.orders_table.setItem(r, 2, QTableWidgetItem(f"{o.total_amount:,.0f}"))
            self.orders_table.setItem(r, 3, QTableWidgetItem(o.created_at.strftime("%Y-%m-%d %H:%M")))
            self.orders_table.item(r, 0).setData(Qt.ItemDataRole.UserRole, o.id)

    def display_order_details(self):
        items = self.orders_table.selectedItems()
        if not items: return
        self.current_order_id = items[0].data(Qt.ItemDataRole.UserRole)
        with next(get_db()) as db: order = crud.get_order(db, self.current_order_id)
        if not order: return

        details = f"<b>مشتری:</b> {order.user.full_name}<br><b>آدرس:</b> {order.shipping_address}<br><b>مبلغ:</b> {order.total_amount:,.0f} تومان<hr><b>محصولات:</b><br>" + "<br>".join([f"- {item.product.name} ({item.quantity} عدد)" for item in order.items])
        self.details_browser.setHtml(details)

        self.receipt_label.setText("در حال بارگیری...")
        if self.photo_worker_thread.isRunning(): self.photo_worker_thread.quit()

        self.worker = AsyncWorker(self.fetch_receipt_data, order.payment_receipt_photo_id)
        self.worker.moveToThread(self.photo_worker_thread)
        self.photo_worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_photo_load_finished)
        self.worker.error.connect(self.on_photo_load_error)
        self.worker.finished.connect(self.photo_worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.photo_worker_thread.finished.connect(self.photo_worker_thread.deleteLater)
        self.photo_worker_thread.start()

    async def fetch_receipt_data(self, file_id: str) -> bytes:
        file = await self.bot_app.bot.get_file(file_id)
        return bytes(await file.download_as_bytearray())

    def on_photo_load_finished(self, data: bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.receipt_label.setPixmap(pixmap.scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio))

    def on_photo_load_error(self, e: Exception):
        self.receipt_label.setText("خطا در بارگیری تصویر.")
        print(f"Error fetching photo: {e}")

    def update_status(self, status: str):
        if not self.current_order_id: return
        with next(get_db()) as db:
            order = crud.update_order_status(db, self.current_order_id, status)
        if order:
            QMessageBox.information(self, "موفق", f"وضعیت سفارش به '{status}' تغییر یافت.")

            # Run the async message sending in a background thread
            if self.message_worker_thread.isRunning(): self.message_worker_thread.quit()
            msg_worker = AsyncWorker(self._send_status_update_message, order.user_id, status)
            msg_worker.moveToThread(self.message_worker_thread)
            self.message_worker_thread.started.connect(msg_worker.run)
            msg_worker.finished.connect(self.message_worker_thread.quit)
            msg_worker.finished.connect(msg_worker.deleteLater)
            msg_worker.error.connect(self.on_message_send_error)
            self.message_worker_thread.finished.connect(self.message_worker_thread.deleteLater)
            self.message_worker_thread.start()

            self.refresh_data()
            self.details_browser.clear()
            self.receipt_label.clear()
            self.current_order_id = None

    async def _send_status_update_message(self, user_id: int, status: str):
        """Sends a message to the user with the new order status."""
        message_map = {
            "approved": "✅ سفارش شما تایید شد و به زودی برایتان ارسال خواهد شد.",
            "rejected": "❌ متاسفانه پرداخت شما رد شد. لطفا با پشتیبانی تماس بگیرید."
        }
        text = message_map.get(status, f"وضعیت سفارش شما به '{status}' تغییر کرد.")
        try:
            await self.bot_app.bot.send_message(chat_id=user_id, text=text)
            print(f"Successfully sent status update to user {user_id}")
        except Forbidden:
            print(f"Error: User {user_id} has blocked the bot. Could not send message.")
        except Exception as e:
            print(f"An unexpected error occurred while sending message to {user_id}: {e}")

    def on_message_send_error(self, e: Exception):
        """Handles errors from the message sending worker."""
        # We can show a non-blocking notification to the admin if needed
        print(f"Failed to send message: {e}")
        if isinstance(e, Forbidden):
             QMessageBox.warning(self, "خطا", "ارسال پیام ناموفق بود. کاربر ربات را مسدود کرده است.")
