from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from telegram_shop_bot.db.database import get_db
from telegram_shop_bot.db import crud

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        stats_layout = QHBoxLayout()
        self.pending_orders_value = QLabel("0")
        self.total_products_value = QLabel("0")
        stats_layout.addWidget(self.create_stat_card("سفارشات جدید", self.pending_orders_value))
        stats_layout.addWidget(self.create_stat_card("تعداد محصولات", self.total_products_value))
        main_layout.addLayout(stats_layout)

    def create_stat_card(self, title: str, value_label: QLabel) -> QFrame:
        card = QFrame()
        layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card

    def refresh_data(self):
        with next(get_db()) as db:
            pending_count = len(crud.get_orders_by_status(db, "pending_payment"))
            product_count = crud.get_total_product_count(db)
        self.pending_orders_value.setText(str(pending_count))
        self.total_products_value.setText(str(product_count))
