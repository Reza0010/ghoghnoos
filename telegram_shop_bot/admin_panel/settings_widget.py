from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QMessageBox
)
from telegram_shop_bot.db.database import get_db
from telegram_shop_bot.db import crud

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        form = QFormLayout()
        self.shop_name_input = QLineEdit()
        self.welcome_msg_input = QTextEdit()
        self.card_num_input = QLineEdit()
        form.addRow("نام فروشگاه:", self.shop_name_input)
        form.addRow("پیام خوش‌آمدگویی:", self.welcome_msg_input)
        form.addRow("شماره کارت:", self.card_num_input)
        self.save_btn = QPushButton("ذخیره تنظیمات")
        self.save_btn.clicked.connect(self.save_settings)
        main_layout.addLayout(form)
        main_layout.addWidget(self.save_btn)

    def refresh_data(self):
        with next(get_db()) as db:
            self.shop_name_input.setText(crud.get_setting(db, "shop_name", "فروشگاه شما"))
            self.welcome_msg_input.setPlainText(crud.get_setting(db, "welcome_message", "به فروشگاه ما خوش آمدید!"))
            self.card_num_input.setText(crud.get_setting(db, "card_number", ""))

    def save_settings(self):
        with next(get_db()) as db:
            crud.set_setting(db, "shop_name", self.shop_name_input.text())
            crud.set_setting(db, "welcome_message", self.welcome_msg_input.toPlainText())
            crud.set_setting(db, "card_number", self.card_num_input.text())
        QMessageBox.information(self, "موفق", "تنظیمات ذخیره شد!")
        self.refresh_data()
