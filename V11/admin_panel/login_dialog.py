import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtGui import QColor, QFont, QIcon
from PyQt6.QtCore import Qt
import qtawesome as qta

class LoginDialog(QDialog):
    def __init__(self, verify_callback):
        super().__init__()
        self.verify_callback = verify_callback
        self.setWindowTitle("ورود به پنل مدیریت")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("MainFrame")
        self.main_frame.setFixedSize(400, 300)
        self.main_frame.setStyleSheet("""
            QFrame#MainFrame {
                background-color: #16161a;
                border: 2px solid #7f5af0;
                border-radius: 20px;
            }
            QLabel { color: #fffffe; }
            QLineEdit {
                background-color: #242629;
                color: white;
                border: 1px solid #333;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #7f5af0; }
            QPushButton#LoginBtn {
                background-color: #7f5af0;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#LoginBtn:hover { background-color: #6246ea; }
            QPushButton#CloseBtn {
                background: transparent;
                color: #94a1b2;
                font-size: 18px;
            }
        """)

        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(30, 20, 30, 30)

        header = QHBoxLayout()
        header.addStretch()
        close_btn = QPushButton("×")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        header.addWidget(close_btn)
        layout.addLayout(header)

        icon_lbl = QLabel()
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setPixmap(qta.icon("fa5s.lock", color="#7f5af0").pixmap(60, 60))
        layout.addWidget(icon_lbl)

        title = QLabel("ورود به پنل هوشمند")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("رمز عبور را وارد کنید...")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.attempt_login)
        layout.addWidget(self.password_input)

        self.login_btn = QPushButton("ورود به سیستم")
        self.login_btn.setObjectName("LoginBtn")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.attempt_login)
        layout.addWidget(self.login_btn)

    def attempt_login(self):
        password = self.password_input.text()
        if self.verify_callback(password):
            self.accept()
        else:
            QMessageBox.critical(self, "خطا", "رمز عبور اشتباه است!")
            self.password_input.clear()
