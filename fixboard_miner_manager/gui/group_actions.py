"""
FixBoard Miner Manager - Group Actions Panel
Provides bulk execution interface to perform reboot, pool configuration, config deployment,
and password updates on multiple selected miners concurrently in a non-blocking thread pool.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QTextEdit, QLineEdit,
                             QMessageBox, QFrame, QGridLayout, QGroupBox)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont

import threading
from concurrent.futures import ThreadPoolExecutor
from database.db_manager import DatabaseManager
from miners.cgminer_api import CGMinerAPI
from miners.whatsminer_api import WhatsMinerSecureAPI
from miners.ssh_api import SSHFallbackAPI

class GroupActionsWidget(QWidget):
    # Safe GUI Thread signal to update terminal logs
    log_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.selected_ips = []
        self.init_ui()

        # Connect signal to update UI safely
        self.log_signal.connect(self.log_to_terminal)

    def set_selected_miners(self, ips: list):
        """Receives list of selected miner IPs from the parent spreadsheet view."""
        self.selected_ips = ips
        self.lbl_count.setText(f"تعداد دستگاه‌های انتخاب شده: {len(self.selected_ips)}")
        if len(self.selected_ips) > 0:
            self.lbl_ips_list.setText(f"IPs: {', '.join(self.selected_ips)}")
        else:
            self.lbl_ips_list.setText("هیچ دستگاهی انتخاب نشده است. لطفاً از تب جدول ماینرها ابتدا دستگاه‌ها را علامت بزنید.")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 1. Header Info Box
        info_box = QFrame()
        info_box.setStyleSheet("background-color: #25252D; border: 1px solid #3E3E4A; border-radius: 8px;")
        info_layout = QVBoxLayout(info_box)

        self.lbl_count = QLabel("تعداد دستگاه‌های انتخاب شده: 0")
        self.lbl_count.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: bold;")
        self.lbl_count.setAlignment(Qt.AlignRight)
        info_layout.addWidget(self.lbl_count)

        self.lbl_ips_list = QLabel("هیچ دستگاهی انتخاب نشده است. لطفاً از تب جدول ماینرها ابتدا دستگاه‌ها را علامت بزنید.")
        self.lbl_ips_list.setWordWrap(True)
        self.lbl_ips_list.setStyleSheet("color: #8E9297; font-size: 11px;")
        self.lbl_ips_list.setAlignment(Qt.AlignRight)
        info_layout.addWidget(self.lbl_ips_list)

        layout.addWidget(info_box)

        # 2. Main control grid
        grid = QGridLayout()
        grid.setSpacing(15)

        # Bulk Reboot Card
        reboot_box = QGroupBox("ری‌بوت گروهی")
        reboot_box.setStyleSheet("QGroupBox { color: #FFFFFF; font-weight: bold; }")
        reboot_layout = QVBoxLayout(reboot_box)
        btn_bulk_reboot = QPushButton("ری‌بوت همزمان (Bulk Reboot)")
        btn_bulk_reboot.setStyleSheet("background-color: #C0392B; padding: 10px; font-weight: bold; color: white;")
        btn_bulk_reboot.clicked.connect(self.bulk_reboot)
        reboot_layout.addWidget(btn_bulk_reboot)
        grid.addWidget(reboot_box, 0, 0)

        # Bulk Pool Card
        pool_box = QGroupBox("تنظیم استخر گروهی")
        pool_box.setStyleSheet("QGroupBox { color: #FFFFFF; font-weight: bold; }")
        pool_layout = QVBoxLayout(pool_box)

        self.txt_bulk_pool = QLineEdit()
        self.txt_bulk_pool.setPlaceholderText("stratum+tcp://btc.global.luxor.tech:700")
        self.txt_bulk_worker = QLineEdit()
        self.txt_bulk_worker.setPlaceholderText("worker.name")
        self.txt_bulk_pass = QLineEdit()
        self.txt_bulk_pass.setPlaceholderText("password")

        btn_bulk_pool = QPushButton("ثبت استخر (Set Pools)")
        btn_bulk_pool.setStyleSheet("background-color: #27AE60; padding: 10px; font-weight: bold; color: white;")
        btn_bulk_pool.clicked.connect(self.bulk_set_pools)

        pool_layout.addWidget(self.txt_bulk_pool)
        pool_layout.addWidget(self.txt_bulk_worker)
        pool_layout.addWidget(self.txt_bulk_pass)
        pool_layout.addWidget(btn_bulk_pool)
        grid.addWidget(pool_box, 0, 1)

        # Bulk Password Card
        pass_box = QGroupBox("تغییر کلمه عبور گروهی")
        pass_box.setStyleSheet("QGroupBox { color: #FFFFFF; font-weight: bold; }")
        pass_layout = QVBoxLayout(pass_box)
        self.txt_bulk_username = QLineEdit()
        self.txt_bulk_username.setPlaceholderText("نام کاربری جدید (یا root)")
        self.txt_bulk_password = QLineEdit()
        self.txt_bulk_password.setPlaceholderText("رمز عبور جدید")

        btn_bulk_password = QPushButton("تغییر کلمه عبور (Change Password)")
        btn_bulk_password.setStyleSheet("background-color: #2980B9; padding: 10px; font-weight: bold; color: white;")
        btn_bulk_password.clicked.connect(self.bulk_change_password)

        pass_layout.addWidget(self.txt_bulk_username)
        pass_layout.addWidget(self.txt_bulk_password)
        pass_layout.addWidget(btn_bulk_password)
        grid.addWidget(pass_box, 1, 0)

        # Configuration deployer
        config_box = QGroupBox("ارسال فایل تنظیمات گروهی")
        config_box.setStyleSheet("QGroupBox { color: #FFFFFF; font-weight: bold; }")
        config_layout = QVBoxLayout(config_box)

        self.txt_bulk_config = QTextEdit()
        self.txt_bulk_config.setPlaceholderText("متن کامل cgminer.conf را در اینجا الصاق کنید تا به تمام ماینرها ارسال شود...")
        self.txt_bulk_config.setFixedHeight(90)
        self.txt_bulk_config.setStyleSheet("background-color: #0E0E12; color: #D0D0D5;")

        btn_bulk_config = QPushButton("ارسال و اعمال تنظیمات (Deploy Config)")
        btn_bulk_config.setStyleSheet("background-color: #D35400; padding: 10px; font-weight: bold; color: white;")
        btn_bulk_config.clicked.connect(self.bulk_deploy_config)

        config_layout.addWidget(self.txt_bulk_config)
        config_layout.addWidget(btn_bulk_config)
        grid.addWidget(config_box, 1, 1)

        layout.addLayout(grid)

        # 3. Terminal Execution Logs Box
        layout.addWidget(QLabel("گزارش اجرای عملیات گروهی:"))
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("background-color: #0E0E12; color: #39FF14; font-family: 'Consolas'; border-radius: 6px;")
        layout.addWidget(self.terminal)

    def log_to_terminal(self, msg: str):
        """Executed on the MAIN GUI thread safely."""
        self.terminal.append(f">> {msg}")

    def check_selection(self) -> bool:
        if not self.selected_ips:
            QMessageBox.warning(self, "خطا", "هیچ دستگاهی انتخاب نشده است. لطفاً از جدول ماینرها، دستگاه‌های مورد نظر را تیک بزنید.")
            return False
        return True

    def bulk_reboot(self):
        if not self.check_selection():
            return

        self.terminal.clear()
        self.log_signal.emit(f"شروع ری‌بوت همزمان برای {len(self.selected_ips)} دستگاه...")

        def task(ip):
            miner = self.db.get_miner_by_ip(ip)
            brand = miner.get("brand", "Antminer")
            username, password = self.db.get_miner_credentials(ip)

            ok = False
            if brand == "WhatsMiner":
                ws = WhatsMinerSecureAPI(ip)
                ok = ws.reboot(password)
            else:
                cg = CGMinerAPI(ip)
                ok = cg.reboot()
                if not ok:
                    ssh = SSHFallbackAPI(ip, username, password)
                    ok = ssh.reboot()

            if ok:
                self.log_signal.emit(f"[موفقیت] دستگاه {ip} ری‌بوت شد.")
                self.db.log_action("BULK_REBOOT", ip, "SUCCESS", "Bulk reboot successful")
            else:
                self.log_signal.emit(f"[خطا] ارسال دستور ری‌بوت به {ip} شکست خورد.")
                self.db.log_action("BULK_REBOOT", ip, "FAILED", "Bulk reboot failed")

        threading.Thread(target=self._run_concurrently, args=(task,)).start()

    def bulk_set_pools(self):
        if not self.check_selection():
            return

        url = self.txt_bulk_pool.text().strip()
        worker = self.txt_bulk_worker.text().strip()
        passwd = self.txt_bulk_pass.text().strip()

        if not url or not worker:
            QMessageBox.warning(self, "خطا", "لطفاً آدرس استخر و نام کارگر را وارد کنید.")
            return

        self.terminal.clear()
        self.log_signal.emit(f"شروع ثبت استخر گروهی ({url}) بر روی {len(self.selected_ips)} دستگاه...")

        def task(ip):
            miner = self.db.get_miner_by_ip(ip)
            brand = miner.get("brand", "Antminer")
            username, password = self.db.get_miner_credentials(ip)

            ok = False
            if brand == "WhatsMiner":
                ws = WhatsMinerSecureAPI(ip)
                pools = [{"url": url, "worker": worker, "passwd": passwd}]
                ok = ws.set_pools(pools, password)
            else:
                cg = CGMinerAPI(ip)
                ok = cg.add_pool(url, worker, passwd)

            if ok:
                self.log_signal.emit(f"[موفقیت] استخر بر روی {ip} ثبت شد.")
                self.db.log_action("BULK_POOL", ip, "SUCCESS", f"Pool set to {url}")
            else:
                self.log_signal.emit(f"[خطا] تنظیم استخر بر روی {ip} با خطا مواجه شد.")
                self.db.log_action("BULK_POOL", ip, "FAILED", f"Pool set to {url} failed")

        threading.Thread(target=self._run_concurrently, args=(task,)).start()

    def bulk_change_password(self):
        if not self.check_selection():
            return

        new_user = self.txt_bulk_username.text().strip()
        new_pass = self.txt_bulk_password.text().strip()

        if not new_pass:
            QMessageBox.warning(self, "خطا", "رمز عبور جدید نمی‌تواند خالی باشد.")
            return

        user_to_set = new_user if new_user else "root"
        self.terminal.clear()
        self.log_signal.emit(f"تغییر اطلاعات ورود همزمان برای {len(self.selected_ips)} دستگاه...")

        def task(ip):
            miner = self.db.get_miner_by_ip(ip)
            username, password = self.db.get_miner_credentials(ip)

            ssh = SSHFallbackAPI(ip, username, password)
            # Standard Linux command to change system user password
            cmd = f"echo -e '{new_pass}\\n{new_pass}' | passwd {user_to_set}"
            success, out = ssh.execute_command(cmd)

            if success:
                # Save credentials to local SQLite as well
                self.db.update_miner_credentials(ip, user_to_set, new_pass)
                self.log_signal.emit(f"[موفقیت] رمز عبور {ip} برای کاربر '{user_to_set}' با موفقیت تغییر کرد.")
                self.db.log_action("BULK_PASSWORD", ip, "SUCCESS", "Bulk change password success")
            else:
                self.log_signal.emit(f"[خطا] تغییر رمز عبور در {ip} شکست خورد. ارتباط برقرار نشد.")
                self.db.log_action("BULK_PASSWORD", ip, "FAILED", "Bulk change password failed")

        threading.Thread(target=self._run_concurrently, args=(task,)).start()

    def bulk_deploy_config(self):
        if not self.check_selection():
            return

        content = self.txt_bulk_config.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "خطا", "محتوای پیکربندی را الصاق کنید.")
            return

        self.terminal.clear()
        self.log_signal.emit(f"شروع ارسال فایل پیکربندی به {len(self.selected_ips)} دستگاه...")

        def task(ip):
            miner = self.db.get_miner_by_ip(ip)
            username, password = self.db.get_miner_credentials(ip)

            ssh = SSHFallbackAPI(ip, username, password)
            dest_path = "/config/cgminer.conf"
            success, _ = ssh.execute_command(f"echo '{content}' > {dest_path}")

            if success:
                self.log_signal.emit(f"[موفقیت] پیکربندی بر روی {ip} ذخیره شد.")
                self.db.log_action("BULK_DEPLOY", ip, "SUCCESS", "Bulk config deploy successful")
            else:
                self.log_signal.emit(f"[خطا] ارسال فایل تنظیمات به {ip} ناموفق بود.")
                self.db.log_action("BULK_DEPLOY", ip, "FAILED", "Bulk config deploy failed")

        threading.Thread(target=self._run_concurrently, args=(task,)).start()

    def _run_concurrently(self, task_function):
        """Helper to run tasks across selected IPs concurrently inside ThreadPoolExecutor."""
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(task_function, self.selected_ips)
        self.log_signal.emit("عملیات گروهی به پایان رسید.")
