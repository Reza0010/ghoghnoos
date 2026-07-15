"""
FixBoard Miner Manager - Miner Details Dialog
A multi-tabbed control panel providing real-time data inspection for hash boards, fans,
system temperatures, and logs, alongside administrative operations (reboot, restart, edit pools).
"""

import os
from PySide6.QtWidgets import (QDialog, QTabWidget, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QGridLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QTextEdit, QLineEdit,
                             QPushButton, QMessageBox, QFileDialog, QGroupBox, QAbstractItemView)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QBrush

from database.db_manager import DatabaseManager
from miners.cgminer_api import CGMinerAPI
from miners.whatsminer_api import WhatsMinerSecureAPI
from miners.ssh_api import SSHFallbackAPI
from miners.http_api import HTTPFallbackAPI
from utils.helpers import format_hashrate, format_uptime

class MinerDetailsDialog(QDialog):
    def __init__(self, miner_ip: str, parent=None):
        super().__init__(parent)
        self.ip = miner_ip
        self.db = DatabaseManager()
        self.miner_record = self.db.get_miner_by_ip(self.ip)
        self.brand = self.miner_record.get("brand", "Antminer") if self.miner_record else "Antminer"
        self.username, self.password = self.db.get_miner_credentials(self.ip)

        # Low-level APIs
        self.cg_api = CGMinerAPI(self.ip)
        self.ws_api = WhatsMinerSecureAPI(self.ip)
        self.ssh_api = SSHFallbackAPI(self.ip, self.username, self.password)
        self.http_api = HTTPFallbackAPI(self.ip, self.username, self.password)

        self.setWindowTitle(f"جزئیات و کنترل پنل - {self.ip} ({self.brand})")
        self.setMinimumSize(QSize(800, 600))

        self.init_ui()

        # Real-time refresh timer (every 4 seconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_live_data)
        self.timer.start(4000)

        # Load initially
        self.refresh_live_data()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1A1A1F;
                color: #FFFFFF;
                font-family: 'Segoe UI';
            }
            QTabWidget::pane {
                border: 1px solid #2E2E35;
                background-color: #1F1F24;
                border-radius: 8px;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #2D2D35;
                color: #A0A5AD;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
                font-size: 11px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #1F1F24;
                color: #FFFFFF;
                border-bottom: 2px solid #3498DB;
            }
            QLabel {
                font-size: 12px;
            }
            QPushButton {
                background-color: #34495E;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2C3E50;
            }
            QTableWidget {
                background-color: #1F1F24;
                gridline-color: #2E2E35;
                border: 1px solid #2E2E35;
                color: #E2E2E5;
            }
            QHeaderView::section {
                background-color: #2D2D35;
                color: #A0A5AD;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Tab Widget
        self.tabs = QTabWidget()

        # 1. Overview Tab
        self.tab_overview = QWidget()
        self.setup_overview_tab()
        self.tabs.addTab(self.tab_overview, "مشخصات و وضعیت کلی")

        # 2. Hash Boards Tab
        self.tab_boards = QWidget()
        self.setup_boards_tab()
        self.tabs.addTab(self.tab_boards, "وضعیت هش‌بردها")

        # 3. Fans Tab
        self.tab_fans = QWidget()
        self.setup_fans_tab()
        self.tabs.addTab(self.tab_fans, "فن‌ها و دما")

        # 4. Logs Tab
        self.tab_logs = QWidget()
        self.setup_logs_tab()
        self.tabs.addTab(self.tab_logs, "لاگ‌های سیستم")

        # 5. Controls Tab
        self.tab_controls = QWidget()
        self.setup_controls_tab()
        self.tabs.addTab(self.tab_controls, "عملیات مدیریتی")

        layout.addWidget(self.tabs)

    def setup_overview_tab(self):
        layout = QVBoxLayout(self.tab_overview)
        layout.setContentsMargins(10, 10, 10, 10)

        # KPI Card Container
        grid = QGridLayout()
        grid.setSpacing(15)

        # Labels for live metrics (no mock data, updated dynamically)
        self.lbl_ip = QLabel(self.ip)
        self.lbl_mac = QLabel("در حال دریافت...")
        self.lbl_brand = QLabel(self.brand)
        self.lbl_model = QLabel("در حال دریافت...")
        self.lbl_fw = QLabel("در حال دریافت...")
        self.lbl_serial = QLabel("در حال دریافت...")
        self.lbl_uptime = QLabel("در حال دریافت...")
        self.lbl_hashrate = QLabel("در حال دریافت...")
        self.lbl_power = QLabel("در حال دریافت...")
        self.lbl_pool = QLabel("در حال دریافت...")
        self.lbl_worker = QLabel("در حال دریافت...")

        labels_info = [
            ("آدرس IP", self.lbl_ip),
            ("مک آدرس (MAC)", self.lbl_mac),
            ("برند دستگاه", self.lbl_brand),
            ("مدل دستگاه", self.lbl_model),
            ("نسخه فریمور (Firmware)", self.lbl_fw),
            ("شماره سریال (S/N)", self.lbl_serial),
            ("زمان کارکرد (Uptime)", self.lbl_uptime),
            ("هش‌ریت زنده", self.lbl_hashrate),
            ("توان مصرفی (Power)", self.lbl_power),
            ("استخر فعال (Pool)", self.lbl_pool),
            ("نام کارگر (Worker)", self.lbl_worker)
        ]

        for idx, (title, lbl) in enumerate(labels_info):
            row = idx // 2
            col = idx % 2

            box = QGroupBox()
            box.setStyleSheet("QGroupBox { background-color: #25252D; border: 1px solid #3E3E4A; border-radius: 8px; }")
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(10, 10, 10, 10)

            t_lbl = QLabel(title)
            t_lbl.setStyleSheet("color: #8E9297; font-weight: bold; font-size: 11px;")
            t_lbl.setAlignment(Qt.AlignRight)
            box_layout.addWidget(t_lbl)

            lbl.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: bold;")
            lbl.setAlignment(Qt.AlignRight)
            box_layout.addWidget(lbl)

            grid.addWidget(box, row, col)

        layout.addLayout(grid)
        layout.addStretch()

    def setup_boards_tab(self):
        layout = QVBoxLayout(self.tab_boards)
        layout.setContentsMargins(10, 10, 10, 10)

        self.boards_table = QTableWidget()
        self.boards_table.setColumnCount(8)
        self.boards_table.setHorizontalHeaderLabels([
            "شماره برد", "وضعیت کارکرد", "دما (°C)", "فرکانس (MHz)",
            "ولتاژ (V)", "تعداد ASIC", "چیپ‌های شناسایی شده", "وضعیت نهایی"
        ])

        self.boards_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.boards_table.setAlternatingRowColors(True)
        self.boards_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout.addWidget(self.boards_table)

    def setup_fans_tab(self):
        layout = QVBoxLayout(self.tab_fans)
        layout.setContentsMargins(10, 10, 10, 10)

        grid = QGridLayout()
        grid.setSpacing(15)

        # Fan speed labels
        self.lbl_fan1 = QLabel("در حال دریافت...")
        self.lbl_fan2 = QLabel("در حال دریافت...")
        self.lbl_fan3 = QLabel("در حال دریافت...")
        self.lbl_fan4 = QLabel("در حال دریافت...")
        self.lbl_fan_health = QLabel("در حال دریافت...")
        self.lbl_temp_chip = QLabel("در حال دریافت...")
        self.lbl_temp_env = QLabel("در حال دریافت...")

        fan_widgets = [
            ("سرعت فن ۱", self.lbl_fan1),
            ("سرعت فن ۲", self.lbl_fan2),
            ("سرعت فن ۳", self.lbl_fan3),
            ("سرعت فن ۴", self.lbl_fan4),
            ("وضعیت سلامت فن‌ها", self.lbl_fan_health),
            ("دمای چیپ‌ها", self.lbl_temp_chip),
            ("دمای محیطی", self.lbl_temp_env)
        ]

        for idx, (title, lbl) in enumerate(fan_widgets):
            row = idx // 2
            col = idx % 2

            box = QGroupBox()
            box.setStyleSheet("QGroupBox { background-color: #25252D; border: 1px solid #3E3E4A; border-radius: 8px; }")
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(10, 10, 10, 10)

            t_lbl = QLabel(title)
            t_lbl.setStyleSheet("color: #8E9297; font-weight: bold; font-size: 11px;")
            t_lbl.setAlignment(Qt.AlignRight)
            box_layout.addWidget(t_lbl)

            lbl.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: bold;")
            lbl.setAlignment(Qt.AlignRight)
            box_layout.addWidget(lbl)

            grid.addWidget(box, row, col)

        layout.addLayout(grid)
        layout.addStretch()

    def setup_logs_tab(self):
        layout = QVBoxLayout(self.tab_logs)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Control row
        top_bar = QHBoxLayout()

        self.log_search_input = QLineEdit()
        self.log_search_input.setPlaceholderText("جستجو در لاگ...")
        self.log_search_input.setStyleSheet("background-color: #2D2D35; border: 1px solid #444450; padding: 6px; color: white;")
        self.log_search_input.textChanged.connect(self.search_logs)
        top_bar.addWidget(self.log_search_input)

        btn_save = QPushButton("ذخیره لاگ در فایل")
        btn_save.clicked.connect(self.save_logs_to_file)
        top_bar.addWidget(btn_save)

        layout.addLayout(top_bar)

        # Text Area for logs
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        self.logs_display.setFont(QFont("Consolas", 10))
        self.logs_display.setStyleSheet("background-color: #0E0E12; color: #D0D0D5; border: 1px solid #2E2E35; border-radius: 6px;")
        layout.addWidget(self.logs_display)

    def setup_controls_tab(self):
        layout = QVBoxLayout(self.tab_controls)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Add generic operational panels
        ops_grid = QGridLayout()
        ops_grid.setSpacing(15)

        # 1. Restart Mining
        btn_restart = QPushButton("راه‌اندازی مجدد ماینینگ (Restart Mining)")
        btn_restart.setStyleSheet("background-color: #2980B9; min-height: 40px;")
        btn_restart.clicked.connect(self.action_restart_mining)
        ops_grid.addWidget(btn_restart, 0, 0)

        # 2. Reboot
        btn_reboot = QPushButton("راه‌اندازی مجدد دستگاه (Reboot)")
        btn_reboot.setStyleSheet("background-color: #C0392B; min-height: 40px;")
        btn_reboot.clicked.connect(self.action_reboot)
        ops_grid.addWidget(btn_reboot, 0, 1)

        # 3. Blink LED
        self.btn_blink = QPushButton("چشمک‌زن مکان‌یاب (Blink LED)")
        self.btn_blink.setStyleSheet("background-color: #8E44AD; min-height: 40px;")
        self.btn_blink.clicked.connect(self.action_toggle_led)
        self.is_led_blinking = False
        ops_grid.addWidget(self.btn_blink, 1, 0)

        # 4. Change Pools
        btn_pools = QPushButton("تنظیم مجدد استخرها (Change Pool)")
        btn_pools.setStyleSheet("background-color: #27AE60; min-height: 40px;")
        btn_pools.clicked.connect(self.action_change_pool)
        ops_grid.addWidget(btn_pools, 1, 1)

        # 5. Backup Config
        btn_backup = QPushButton("پشتیبان‌گیری تنظیمات (Backup Config)")
        btn_backup.setStyleSheet("background-color: #D35400; min-height: 40px;")
        btn_backup.clicked.connect(self.action_backup_config)
        ops_grid.addWidget(btn_backup, 2, 0)

        # 6. Restore Config
        btn_restore = QPushButton("بازیابی تنظیمات (Restore Config)")
        btn_restore.setStyleSheet("background-color: #7F8C8D; min-height: 40px;")
        btn_restore.clicked.connect(self.action_restore_config)
        ops_grid.addWidget(btn_restore, 2, 1)

        layout.addLayout(ops_grid)
        layout.addStretch()

    def refresh_live_data(self):
        """
        Gathers live parameters from the miner according to the brand.
        NO MOCKED DATA.
        """
        # Read from CGMiner API or Whatsminer API
        if self.brand == "WhatsMiner":
            self.refresh_whatsminer_data()
        else:
            self.refresh_antminer_data()

    def refresh_whatsminer_data(self):
        """Fetches real WhatsMiner parameters."""
        status = self.ws_api.get_miner_status()
        device_info = self.ws_api.get_device_info()

        # Overview Tab updates
        if device_info and device_info.get("code") == 0:
            msg = device_info.get("msg", {})
            self.lbl_mac.setText(msg.get("mac_addr", "دریافت نشد"))
            self.lbl_model.setText(msg.get("model_type", "دریافت نشد"))
            self.lbl_fw.setText(msg.get("firmware_ver", "دریافت نشد"))
            self.lbl_serial.setText(msg.get("sn", "دریافت نشد"))
        else:
            self.lbl_mac.setText("دریافت نشد")
            self.lbl_model.setText("دریافت نشد")
            self.lbl_fw.setText("دریافت نشد")
            self.lbl_serial.setText("دریافت نشد")

        if status and status.get("code") == 0:
            msg = status.get("msg", {})

            # Hashrate & Uptime
            raw_hr = msg.get("hash_rate", 0.0)
            self.lbl_hashrate.setText(f"{raw_hr:.2f} TH/s")

            raw_up = msg.get("uptime", 0)
            self.lbl_uptime.setText(format_uptime(raw_up))

            self.lbl_power.setText(f"{msg.get('power', 'دریافت نشد')} W")

            # Active Pools
            pools = msg.get("pools", [])
            if pools and isinstance(pools, list):
                active_pool = pools[0]
                self.lbl_pool.setText(active_pool.get("url", "دریافت نشد"))
                self.lbl_worker.setText(active_pool.get("worker", "دریافت نشد"))
            else:
                self.lbl_pool.setText("دریافت نشد")
                self.lbl_worker.setText("دریافت نشد")

            # Hashboards parsing
            boards = msg.get("hash_boards", [])
            self.boards_table.setRowCount(len(boards))
            for i, b in enumerate(boards):
                # Columns: Board Number, Status, Temp, Freq, Volt, ASIC Count, Chips, Final Status
                self.boards_table.setItem(i, 0, QTableWidgetItem(f"برد {b.get('id', i)}"))

                b_status = "فعال" if b.get("is_active", 0) == 1 else "غیرفعال"
                self.boards_table.setItem(i, 1, QTableWidgetItem(b_status))

                self.boards_table.setItem(i, 2, QTableWidgetItem(f"{b.get('temp', 'دریافت نشد')}"))
                self.boards_table.setItem(i, 3, QTableWidgetItem(f"{b.get('frequency', 'دریافت نشد')}"))
                self.boards_table.setItem(i, 4, QTableWidgetItem(f"{b.get('voltage', 'دریافت نشد')}"))
                self.boards_table.setItem(i, 5, QTableWidgetItem(f"{b.get('asic_count', 'دریافت نشد')}"))
                self.boards_table.setItem(i, 6, QTableWidgetItem(f"{b.get('detected_chips', 'دریافت نشد')}"))

                health = b.get("status", "Normal")
                h_item = QTableWidgetItem(health)
                if health == "Normal":
                    h_item.setForeground(QColor("#2ECC71"))
                else:
                    h_item.setForeground(QColor("#E74C3C"))
                self.boards_table.setItem(i, 7, h_item)

            # Fans parsing
            fans = msg.get("fans", [])
            self.lbl_fan1.setText(f"{fans[0]} RPM" if len(fans) > 0 else "دریافت نشد")
            self.lbl_fan2.setText(f"{fans[1]} RPM" if len(fans) > 1 else "دریافت نشد")
            self.lbl_fan3.setText(f"{fans[2]} RPM" if len(fans) > 2 else "دریافت نشد")
            self.lbl_fan4.setText(f"{fans[3]} RPM" if len(fans) > 3 else "دریافت نشد")
            self.lbl_fan_health.setText("سالم" if len(fans) >= 2 else "دریافت نشد")

            self.lbl_temp_chip.setText(f"{msg.get('avg_temp_chip', 'دریافت نشد')} °C")
            self.lbl_temp_env.setText(f"{msg.get('env_temp', 'دریافت نشد')} °C")

        else:
            # Fallback to display "دریافت نشد" if cannot connect to Port 4433
            self._set_offline_labels()

        # Load logs via SSH fallback
        logs_text = self.ssh_api.fetch_logs()
        self.logs_display.setText(logs_text)
        self.highlight_log_lines()

    def refresh_antminer_data(self):
        """Fetches real Antminer parameters using CGMiner standard API."""
        summary = self.cg_api.get_summary()
        version = self.cg_api.get_version()
        pools = self.cg_api.get_pools()
        stats = self.cg_api.get_stats()

        # Uptime & Hashrate
        if summary:
            data = summary.get("SUMMARY", [{}])[0]
            uptime_s = data.get("Elapsed", 0)
            self.lbl_uptime.setText(format_uptime(uptime_s))

            raw_hr = data.get("GHS 5s", data.get("MHS 5s", 0))
            self.lbl_hashrate.setText(format_hashrate(raw_hr, "GH" if "GHS 5s" in data else "MH"))

            self.lbl_power.setText(f"{data.get('Power', 'دریافت نشد')} W")
        else:
            self._set_offline_labels()
            return

        if version:
            v_data = version.get("VERSION", [{}])[0]
            self.lbl_mac.setText(v_data.get("MAC", v_data.get("Mac", "دریافت نشد")))
            self.lbl_model.setText(v_data.get("Platform", v_data.get("Type", "Antminer")))
            self.lbl_fw.setText(v_data.get("FileSystem", v_data.get("OS", "دریافت نشد")))
            self.lbl_serial.setText(v_data.get("Serial", "دریافت نشد"))

        if pools:
            pool_list = pools.get("POOLS", [])
            if pool_list:
                active_p = pool_list[0]
                self.lbl_pool.setText(active_p.get("URL", "دریافت نشد"))
                self.lbl_worker.setText(active_p.get("User", "دریافت نشد"))

        # Parse Hashboards & Fans from stats API
        if stats:
            # S9/S17/S19 stats response parsing
            stat_items = stats.get("STATS", [{}])
            if stat_items:
                s_item = stat_items[0]

                # Render common Antminer boards S19 (e.g. Chain[0, 1, 2])
                chains_count = 0
                boards_info = []
                for k, v in s_item.items():
                    if k.startswith("chain_rate") or k.startswith("chain_acs"):
                        chains_count += 1

                # Build boards table dynamically
                self.boards_table.setRowCount(3) # S9/S19 standard is 3 boards
                for i in range(3):
                    self.boards_table.setItem(i, 0, QTableWidgetItem(f"برد {i+1}"))

                    # Status
                    chain_acs = s_item.get(f"chain_acs{i}", s_item.get(f"chain_acs_status{i}", ""))
                    b_status = "فعال" if chain_acs else "غیرفعال"
                    self.boards_table.setItem(i, 1, QTableWidgetItem(b_status))

                    # Temp
                    temp_board = s_item.get(f"temp{i+1}", s_item.get(f"temp2_{i+1}", "دریافت نشد"))
                    self.boards_table.setItem(i, 2, QTableWidgetItem(f"{temp_board}"))

                    # Frequency
                    freq = s_item.get(f"frequency{i+1}", s_item.get(f"freq{i+1}", "دریافت نشد"))
                    self.boards_table.setItem(i, 3, QTableWidgetItem(f"{freq}"))

                    # Voltage
                    volt = s_item.get(f"voltage{i+1}", s_item.get(f"volt{i+1}", "دریافت نشد"))
                    self.boards_table.setItem(i, 4, QTableWidgetItem(f"{volt}"))

                    # ASIC Count
                    asics = s_item.get(f"chain_asic_num{i}", s_item.get(f"asic{i+1}", "دریافت نشد"))
                    self.boards_table.setItem(i, 5, QTableWidgetItem(f"{asics}"))

                    # Chips
                    chips = s_item.get(f"chain_detected_asic_num{i}", "دریافت نشد")
                    self.boards_table.setItem(i, 6, QTableWidgetItem(f"{chips}"))

                    # Final Status
                    status_str = "Normal" if chain_acs else "Fault"
                    s_widget = QTableWidgetItem(status_str)
                    s_widget.setForeground(QColor("#2ECC71" if chain_acs else "#E74C3C"))
                    self.boards_table.setItem(i, 7, s_widget)

                # Fans parsing from STATS
                self.lbl_fan1.setText(f"{s_item.get('fan1', s_item.get('fan_speed1', 'دریافت نشد'))} RPM")
                self.lbl_fan2.setText(f"{s_item.get('fan2', s_item.get('fan_speed2', 'دریافت نشد'))} RPM")
                self.lbl_fan3.setText(f"{s_item.get('fan3', s_item.get('fan_speed3', 'دریافت نشد'))} RPM")
                self.lbl_fan4.setText(f"{s_item.get('fan4', s_item.get('fan_speed4', 'دریافت نشد'))} RPM")
                self.lbl_fan_health.setText("سالم")

                self.lbl_temp_chip.setText(f"{s_item.get('temp3_1', 'دریافت نشد')} °C")
                self.lbl_temp_env.setText(f"{s_item.get('temp_env', 'دریافت نشد')} °C")

        # Load logs via SSH
        logs_text = self.ssh_api.fetch_logs()
        self.logs_display.setText(logs_text)
        self.highlight_log_lines()

    def _set_offline_labels(self):
        """Standardizes fallback view on disconnection."""
        self.lbl_mac.setText("دریافت نشد")
        self.lbl_model.setText("دریافت نشد")
        self.lbl_fw.setText("دریافت نشد")
        self.lbl_serial.setText("دریافت نشد")
        self.lbl_hashrate.setText("دریافت نشد")
        self.lbl_uptime.setText("دریافت نشد")
        self.lbl_power.setText("دریافت نشد")
        self.lbl_pool.setText("دریافت نشد")
        self.lbl_worker.setText("دریافت نشد")
        self.lbl_fan1.setText("دریافت نشد")
        self.lbl_fan2.setText("دریافت نشد")
        self.lbl_fan3.setText("دریافت نشد")
        self.lbl_fan4.setText("دریافت نشد")
        self.lbl_fan_health.setText("دریافت نشد")
        self.lbl_temp_chip.setText("دریافت نشد")
        self.lbl_temp_env.setText("دریافت نشد")
        self.boards_table.setRowCount(0)

    # Operations Tab Logic
    def action_restart_mining(self):
        confirm = QMessageBox.question(self, "راه‌اندازی مجدد ماینینگ", "آیا می‌خواهید فرآیند استخراج دستگاه را مجدداً راه‌اندازی کنید؟", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            ok = False
            if self.brand == "WhatsMiner":
                ok = self.ws_api.restart_mining(self.password)
            else:
                ok = self.cg_api.restart_mining()

            if ok:
                self.db.log_action("RESTART_MINING", self.ip, "SUCCESS", "Mining engine restarted via details UI")
                QMessageBox.information(self, "موفقیت", "دستور راه‌اندازی مجدد ماینینگ با موفقیت ارسال شد.")
            else:
                QMessageBox.critical(self, "خطا", "ارسال دستور با خطا مواجه شد.")

    def action_reboot(self):
        confirm = QMessageBox.question(self, "راه‌اندازی مجدد دستگاه", "آیا مطمئن هستید که می‌خواهید دستگاه را ری‌بوت (Reboot) کنید؟", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            ok = False
            if self.brand == "WhatsMiner":
                ok = self.ws_api.reboot(self.password)
            else:
                ok = self.cg_api.reboot()
                if not ok:
                    ok = self.ssh_api.reboot() or self.http_api.reboot()

            if ok:
                self.db.log_action("REBOOT_MINER", self.ip, "SUCCESS", "Miner reboot command triggered")
                QMessageBox.information(self, "موفقیت", "دستور ری‌بوت برای دستگاه ارسال شد و ماینر در حال راه‌اندازی مجدد است.")
                self.close()
            else:
                QMessageBox.critical(self, "خطا", "امکان برقراری ارتباط برای ارسال دستور ری‌بوت میسر نیست.")

    def action_toggle_led(self):
        self.is_led_blinking = not self.is_led_blinking
        ok = False
        if self.brand == "WhatsMiner":
            ok = self.ws_api.set_led_blink(self.is_led_blinking, self.password)
        else:
            # Antminer SSH fallback command for LED blink
            cmd = "echo 1 > /sys/class/leds/red/blink" if self.is_led_blinking else "echo 0 > /sys/class/leds/red/blink"
            ok, _ = self.ssh_api.execute_command(cmd)

        if ok:
            self.btn_blink.setText("خاموش کردن چشمک‌زن" if self.is_led_blinking else "چشمک‌زن مکان‌یاب (Blink LED)")
            self.btn_blink.setStyleSheet("background-color: #E67E22;" if self.is_led_blinking else "background-color: #8E44AD;")
            self.db.log_action("TOGGLE_LED", self.ip, "SUCCESS", f"LED blink state: {self.is_led_blinking}")
        else:
            QMessageBox.critical(self, "خطا", "ارسال دستور تغییر وضعیت LED ناموفق بود.")

    def action_change_pool(self):
        # Displays simple prompt dialog
        from PySide6.QtWidgets import QInputDialog
        url, ok = QInputDialog.getText(self, "تغییر استخر", "آدرس جدید استخر را وارد کنید:")
        if ok and url.strip():
            worker, ok2 = QInputDialog.getText(self, "تغییر کارگر", "نام کارگر (Worker):")
            if ok2 and worker.strip():
                passwd, ok3 = QInputDialog.getText(self, "تغییر رمز عبور استخر", "رمز عبور استخر:")
                if ok3:
                    success = False
                    if self.brand == "WhatsMiner":
                        pools_dict = [{"url": url.strip(), "worker": worker.strip(), "passwd": passwd.strip()}]
                        success = self.ws_api.set_pools(pools_dict, self.password)
                    else:
                        success = self.cg_api.add_pool(url.strip(), worker.strip(), passwd.strip())

                    if success:
                        self.db.log_action("CHANGE_POOLS", self.ip, "SUCCESS", f"Changed pool to {url}")
                        QMessageBox.information(self, "موفق", "آدرس استخر فعال با موفقیت بروزرسانی شد.")
                        self.refresh_live_data()
                    else:
                        QMessageBox.critical(self, "خطا", "بروزرسانی استخر ناموفق بود.")

    def action_backup_config(self):
        """Downloads standard configuration from the miner via SSH/HTTP."""
        save_path, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل پشتیبان تنظیمات", f"backup_{self.ip}.conf", "Config Files (*.conf *.json *.xml)")
        if save_path:
            # Download file using SSH fallback
            cmd = "cat /config/cgminer.conf 2>/dev/null || cat /etc/config/cgminer 2>/dev/null || cat /etc/cgminer.conf 2>/dev/null"
            success, config_contents = self.ssh_api.execute_command(cmd)
            if success and config_contents:
                try:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(config_contents)
                    self.db.log_action("BACKUP_CONFIG", self.ip, "SUCCESS", f"Config backup downloaded to {save_path}")
                    QMessageBox.information(self, "موفقیت", "فایل پشتیبان با موفقیت بر روی سیستم شما ذخیره شد.")
                except Exception as e:
                    QMessageBox.critical(self, "خطا", f"ذخیره فایل با خطا مواجه شد: {e}")
            else:
                QMessageBox.critical(self, "خطا", "امکان دریافت فایل پیکربندی از ماینر میسر نیست.")

    def action_restore_config(self):
        """Restores a selected configuration file into the miner via SSH."""
        open_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل پیکربندی برای بازیابی", "", "Config Files (*.conf *.json *.xml)")
        if open_path:
            try:
                with open(open_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Write to miner via SSH
                # S9/S19 standard config locations
                dest_path = "/config/cgminer.conf"
                success, _ = self.ssh_api.execute_command(f"echo '{content}' > {dest_path}")
                if success:
                    self.db.log_action("RESTORE_CONFIG", self.ip, "SUCCESS", "Config restored via backup file")
                    QMessageBox.information(self, "موفقیت", "تنظیمات با موفقیت بازیابی شد. لطفاً فرآیند استخراج یا ماینر را ری‌استارت کنید.")
                else:
                    QMessageBox.critical(self, "خطا", "انتقال فایل پیکربندی به ماینر ناموفق بود.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"بارگذاری فایل با خطا مواجه شد: {e}")

    # Logs Highlighting and Searching
    def highlight_log_lines(self):
        """Performs automatic color styling for warnings (yellow) and errors (red) inside log view."""
        # Clean current selection formats
        cursor = self.logs_display.textCursor()
        cursor.select(cursor.Document)
        cursor.setCharFormat(QTextCharFormat())

        # Color markers
        fmt_error = QTextCharFormat()
        fmt_error.setForeground(QBrush(QColor("#E74C3C")))
        fmt_error.setFontWeight(QFont.Bold)

        fmt_warn = QTextCharFormat()
        fmt_warn.setForeground(QBrush(QColor("#F1C40F")))

        document = self.logs_display.document()

        # Search and highlight line by line
        for text in ["error", "fail", "fault", "crit"]:
            cursor = self.logs_display.document().find(text)
            while not cursor.isNull():
                cursor.select(cursor.LineUnderCursor)
                cursor.mergeCharFormat(fmt_error)
                cursor = self.logs_display.document().find(text, cursor)

        for text in ["warn", "timeout", "retry"]:
            cursor = self.logs_display.document().find(text)
            while not cursor.isNull():
                cursor.select(cursor.LineUnderCursor)
                cursor.mergeCharFormat(fmt_warn)
                cursor = self.logs_display.document().find(text, cursor)

    def search_logs(self):
        """Highlights matching keywords matching log search box inputs."""
        keyword = self.log_search_input.text().strip()
        if not keyword:
            self.highlight_log_lines()
            return

        # Clear previous formats
        self.highlight_log_lines()

        fmt_search = QTextCharFormat()
        fmt_search.setBackground(QBrush(QColor("#3498DB")))
        fmt_search.setForeground(QBrush(QColor("#FFFFFF")))

        cursor = self.logs_display.document().find(keyword)
        while not cursor.isNull():
            cursor.mergeCharFormat(fmt_search)
            cursor = self.logs_display.document().find(keyword, cursor)

    def save_logs_to_file(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "ذخیره کامل لاگ‌ها", f"miner_log_{self.ip}.txt", "Text Files (*.txt *.log)")
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(self.logs_display.toPlainText())
                QMessageBox.information(self, "موفقیت", "لاگ‌ها با موفقیت ذخیره شدند.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"ذخیره فایل با خطا مواجه شد: {e}")

    def closeEvent(self, event):
        # Stop background refresh timers
        self.timer.stop()
        super().closeEvent(event)
