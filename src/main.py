import sys
import asyncio
from asyncqt import QEventLoop
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QLabel, QStackedWidget, QListWidget
)
from PyQt6.QtCore import Qt
from telegram_service import TelegramService

class LoginWidget(QWidget):
    def __init__(self, telegram_service, main_window, parent=None):
        super().__init__(parent)
        self.telegram_service = telegram_service
        self.main_window = main_window

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone Number (e.g., +1234567890)")
        layout.addWidget(self.phone_input)

        self.send_code_button = QPushButton("Send Code")
        self.send_code_button.clicked.connect(lambda: asyncio.create_task(self.send_code()))
        layout.addWidget(self.send_code_button)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Verification Code")
        layout.addWidget(self.code_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("2FA Password (if any)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(lambda: asyncio.create_task(self.login()))
        layout.addWidget(self.login_button)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

    async def send_code(self):
        phone_number = self.phone_input.text()
        if not phone_number:
            self.status_label.setText("Please enter a phone number.")
            return

        self.status_label.setText("Sending code...")
        success, message = await self.telegram_service.send_code(phone_number)
        self.status_label.setText(message)

    async def login(self):
        code = self.code_input.text()
        password = self.password_input.text()

        if not code:
            self.status_label.setText("Please enter the verification code.")
            return

        self.status_label.setText("Logging in...")
        success, message = await self.telegram_service.login(code, password or None)
        self.status_label.setText(message)

        if success:
            self.main_window.show_main_app()


class ChannelListWidget(QWidget):
    def __init__(self, telegram_service, parent=None):
        super().__init__(parent)
        self.telegram_service = telegram_service
        self.layout = QVBoxLayout(self)

        self.channel_list = QListWidget()
        self.layout.addWidget(self.channel_list)

    async def populate_channels(self):
        self.channel_list.clear()
        self.channel_list.addItem("Loading channels...")
        try:
            dialogs = await self.telegram_service.get_dialogs()
            self.channel_list.clear()
            for dialog in dialogs:
                if dialog.is_channel:
                    self.channel_list.addItem(dialog.name)
        except Exception as e:
            self.channel_list.clear()
            self.channel_list.addItem(f"Error loading channels: {e}")


class MainWindow(QMainWindow):
    def __init__(self, telegram_service):
        super().__init__()
        self.telegram_service = telegram_service
        self.setWindowTitle("Telegram Store Channel Manager")
        self.setGeometry(100, 100, 400, 600)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.login_widget = LoginWidget(self.telegram_service, self)
        self.main_app_widget = ChannelListWidget(self.telegram_service)

        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.main_app_widget)

        self.stacked_widget.setCurrentWidget(self.login_widget)

    def show_main_app(self):
        self.stacked_widget.setCurrentWidget(self.main_app_widget)
        asyncio.create_task(self.main_app_widget.populate_channels())


async def main():
    telegram_service = TelegramService()
    await telegram_service.connect()

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow(telegram_service)
    window.show()

    try:
        with loop:
            loop.run_forever()
    finally:
        if telegram_service.is_connected():
            loop.run_until_complete(telegram_service.disconnect())

if __name__ == "__main__":
    asyncio.run(main())
