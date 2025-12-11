import sys
import asyncio
import configparser
from asyncqt import QEventLoop
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QLabel, QStackedWidget, QListWidget,
    QGroupBox, QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt
from telegram_service import TelegramService, CONFIG_FILE

class LoginWidget(QWidget):
    def __init__(self, telegram_service, main_window, parent=None):
        super().__init__(parent)
        self.telegram_service = telegram_service
        self.main_window = main_window

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Login Group
        login_group = QGroupBox("Login")
        login_layout = QFormLayout()

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone Number (e.g., +1234567890)")
        login_layout.addRow("Phone:", self.phone_input)

        self.send_code_button = QPushButton("Send Code")
        self.send_code_button.clicked.connect(lambda: asyncio.create_task(self.send_code()))
        login_layout.addWidget(self.send_code_button)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Verification Code")
        login_layout.addRow("Code:", self.code_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("2FA Password (if any)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        login_layout.addRow("Password:", self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(lambda: asyncio.create_task(self.login()))
        login_layout.addWidget(self.login_button)

        login_group.setLayout(login_layout)
        layout.addWidget(login_group)

        # Proxy Group
        proxy_group = QGroupBox("Proxy Settings")
        self.proxy_layout = QFormLayout()

        self.proxy_type = QComboBox()
        self.proxy_type.addItems(["SOCKS5", "HTTP", "MTProto"])
        self.proxy_type.currentTextChanged.connect(self.toggle_proxy_fields)
        self.proxy_layout.addRow("Type:", self.proxy_type)

        self.proxy_server = QLineEdit()
        self.proxy_layout.addRow("Server:", self.proxy_server)

        self.proxy_port = QLineEdit()
        self.proxy_layout.addRow("Port:", self.proxy_port)

        self.proxy_secret = QLineEdit()
        self.proxy_layout.addRow("Secret:", self.proxy_secret)

        self.proxy_username = QLineEdit()
        self.proxy_layout.addRow("Username:", self.proxy_username)

        self.proxy_password = QLineEdit()
        self.proxy_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.proxy_layout.addRow("Password:", self.proxy_password)

        self.save_proxy_button = QPushButton("Save Proxy")
        self.save_proxy_button.clicked.connect(self.save_proxy)
        self.proxy_layout.addWidget(self.save_proxy_button)

        proxy_group.setLayout(self.proxy_layout)
        layout.addWidget(proxy_group)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.load_proxy_settings()
        self.toggle_proxy_fields(self.proxy_type.currentText())

    def toggle_proxy_fields(self, proxy_type):
        is_mtproto = proxy_type == "MTProto"
        self.proxy_secret.setVisible(is_mtproto)
        self.proxy_layout.labelForField(self.proxy_secret).setVisible(is_mtproto)

        self.proxy_username.setVisible(not is_mtproto)
        self.proxy_layout.labelForField(self.proxy_username).setVisible(not is_mtproto)
        self.proxy_password.setVisible(not is_mtproto)
        self.proxy_layout.labelForField(self.proxy_password).setVisible(not is_mtproto)

    def load_proxy_settings(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        if 'proxy' in config:
            self.proxy_type.setCurrentText(config['proxy'].get('type', 'SOCKS5'))
            self.proxy_server.setText(config['proxy'].get('server', ''))
            self.proxy_port.setText(config['proxy'].get('port', ''))
            self.proxy_secret.setText(config['proxy'].get('secret', ''))
            self.proxy_username.setText(config['proxy'].get('username', ''))
            self.proxy_password.setText(config['proxy'].get('password', ''))

    def save_proxy(self):
        proxy_type = self.proxy_type.currentText()
        server = self.proxy_server.text()
        port = self.proxy_port.text()
        secret = self.proxy_secret.text()
        username = self.proxy_username.text()
        password = self.proxy_password.text()

        self.telegram_service.save_proxy_settings(proxy_type, server, port, username, password, secret)
        self.status_label.setText("Proxy settings saved. Please restart the application to apply.")

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
    try:
        telegram_service = TelegramService()
    except Exception as e:
        print(f"Error during initialization: {e}")
        return

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
