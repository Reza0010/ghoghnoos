"""
FixBoard Miner Manager - Authentication Dialog (Non-Blocking)
Utilizes a background QThread (LoginWorker) to perform socket / SSH connection checks
to avoid freezing or hanging the PySide6 main GUI thread during connection attempts.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QSize, QThread, Signal, Slot
from PySide6.QtGui import QColor, QFont

from database.db_manager import DatabaseManager
from miners.cgminer_api import CGMinerAPI
from miners.whatsminer_api import WhatsMinerSecureAPI
from miners.ssh_api import SSHFallbackAPI
from miners.http_api import HTTPFallbackAPI

class LoginWorker(QThread):
    """
    Performs network authentication in a background worker thread to prevent any UI freezing.
    """
    success = Signal(str, str) # Emits (username, password)
    failed = Signal(str)       # Emits error message

    def __init__(self, ip: str, brand: str, username: str, password: str):
        super().__init__()
        self.ip = ip
        self.brand = brand
        self.username = username
        self.password = password

    def run(self):
        success = False
        err_msg = ""

        # Authenticate using appropriate mechanism
        if self.brand == "WhatsMiner":
            # For Whatsminer, try secure token api check or SSH fallback
            ws_api = WhatsMinerSecureAPI(self.ip, timeout=3.0)
            salt = ws_api.extract_salt()
            if salt:
                success = True
            else:
                # Try SSH handshake
                ssh = SSHFallbackAPI(self.ip, self.username, self.password, timeout=3.0)
                login_ok, _ = ssh.execute_command("echo 1")
                if login_ok:
                    success = True
                else:
                    err_msg = "خطا در برقراری ارتباط با پورت API 4433 یا SSH واتس‌ماینر."
        else:
            # Antminer: standard SSH verification or HTTP CGI Basic Auth verification
            ssh = SSHFallbackAPI(self.ip, self.username, self.password, timeout=3.0)
            login_ok, _ = ssh.execute_command("echo 1")
            if login_ok:
                success = True
            else:
                # Try HTTP CGI validation
                http_api = HTTPFallbackAPI(self.ip, self.username, self.password, timeout=3.0)
                http_ok, _ = http_api.send_request("/cgi-bin/get_status.cgi")
                if http_ok:
                    success = True
                else:
                    # Antminer CGMiner privilege check
                    cg_api = CGMinerAPI(self.ip, timeout=3.0)
                    if cg_api.get_summary() is not None:
                        success = True
                    else:
                        err_msg = "نام کاربری/رمز عبور اشتباه است یا پورت‌های ارتباطی دستگاه مسدود می‌باشند."

        if success:
            self.success.emit(self.username, self.password)
        else:
            self.failed.emit(err_msg)


class LoginDialog(QDialog):
    def __init__(self, miner_ip: str, parent=None):
        super().__init__(parent)
        self.ip = miner_ip
        self.db = DatabaseManager()
        self.authenticated = False
        self.worker = None

        self.setWindowTitle(f"ورود به پنل ماینر - {self.ip}")
        self.setFixedSize(QSize(360, 280))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        # Apply modern dark mode styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1F1F24;
                color: #FFFFFF;
                font-family: 'Segoe UI';
            }
            QLabel {
                color: #E2E2E5;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #2D2D35;
                border: 1px solid #444450;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 6px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #3498DB;
            }
            QComboBox {
                background-color: #2D2D35;
                border: 1px solid #444450;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 5px;
            }
            QPushButton {
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_lbl = QLabel(f"دستگاه هدف: {self.ip}")
        title_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #3498DB;")
        title_lbl.setAlignment(Qt.AlignRight)
        layout.addWidget(title_lbl)

        # Combo box for template credentials
        preset_layout = QHBoxLayout()
        preset_lbl = QLabel("قالب اطلاعات:")
        preset_lbl.setAlignment(Qt.AlignRight)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "انتخاب از قالب‌های آماده...",
            "root / root (آنت‌ماینر پیش‌فرض)",
            "admin / admin (پیش‌فرض)",
            "admin / @WhatsMiner (واتس‌ماینر پیش‌فرض)",
            "root / admin",
            "root / (بدون رمز)"
        ])
        self.preset_combo.currentIndexChanged.connect(self.apply_preset)
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addWidget(preset_lbl)
        layout.addLayout(preset_layout)

        # Username Input
        user_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        user_lbl = QLabel("نام کاربری:")
        user_lbl.setFixedWidth(70)
        user_lbl.setAlignment(Qt.AlignRight)
        user_layout.addWidget(self.user_input)
        user_layout.addWidget(user_lbl)
        layout.addLayout(user_layout)

        # Password Input
        pass_layout = QHBoxLayout()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("Password")
        pass_lbl = QLabel("رمز عبور:")
        pass_lbl.setFixedWidth(70)
        pass_lbl.setAlignment(Qt.AlignRight)
        pass_layout.addWidget(self.pass_input)
        pass_layout.addWidget(pass_lbl)
        layout.addLayout(pass_layout)

        # Load existing credentials from DB if present
        existing_user, existing_pass = self.db.get_miner_credentials(self.ip)
        if existing_user:
            self.user_input.setText(existing_user)
            self.pass_input.setText(existing_pass)

        # Button Layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_cancel = QPushButton("انصراف")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #3E3E4A;
                color: white;
            }
            QPushButton:hover {
                background-color: #4E4E5A;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_login = QPushButton("بررسی و ورود")
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
            }
            QPushButton:hover {
                background-color: #2ECC71;
            }
        """)
        self.btn_login.clicked.connect(self.verify_and_save_credentials)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_login)
        layout.addLayout(btn_layout)

    def apply_preset(self, index: int):
        """Autofills username/password fields based on index presets."""
        if index == 1:
            self.user_input.setText("root")
            self.pass_input.setText("root")
        elif index == 2:
            self.user_input.setText("admin")
            self.pass_input.setText("admin")
        elif index == 3:
            self.user_input.setText("admin")
            self.pass_input.setText("@WhatsMiner")
        elif index == 4:
            self.user_input.setText("root")
            self.pass_input.setText("admin")
        elif index == 5:
            self.user_input.setText("root")
            self.pass_input.setText("")

    def verify_and_save_credentials(self):
        """
        Starts a background LoginWorker thread to verify credentials.
        Keeps GUI completely responsive with animated state change.
        """
        username = self.user_input.text().strip()
        password = self.pass_input.text()

        # Retrieve brand
        miner_record = self.db.get_miner_by_ip(self.ip)
        brand = miner_record.get("brand", "Antminer") if miner_record else "Antminer"

        # Disable inputs and update button state
        self.btn_login.setEnabled(False)
        self.btn_login.setText("در حال بررسی اتصال...")
        self.user_input.setEnabled(False)
        self.pass_input.setEnabled(False)
        self.preset_combo.setEnabled(False)

        # Launch QThread background worker
        self.worker = LoginWorker(self.ip, brand, username, password)
        self.worker.success.connect(self.on_auth_success)
        self.worker.failed.connect(self.on_auth_failed)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    @Slot(str, str)
    def on_auth_success(self, username, password):
        """Callback from background thread indicating successful login verification."""
        self.db.update_miner_credentials(self.ip, username, password)
        self.db.log_action("AUTHENTICATE_MINER", self.ip, "SUCCESS", "Credentials verified successfully via non-blocking login")
        self.authenticated = True
        self.accept()

    @Slot(str)
    def on_auth_failed(self, err_msg):
        """Callback from background thread indicating failed login verification."""
        # Restore inputs
        self.btn_login.setEnabled(True)
        self.btn_login.setText("بررسی و ورود")
        self.user_input.setEnabled(True)
        self.pass_input.setEnabled(True)
        self.preset_combo.setEnabled(True)

        QMessageBox.critical(
            self, "خطای احراز هویت",
            err_msg or "اطلاعات وارد شده اشتباه است یا پورت‌های ارتباطی دستگاه مسدود می‌باشند."
        )
