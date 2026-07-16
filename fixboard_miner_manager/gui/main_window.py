"""
FixBoard Miner Manager - Main Orchestration Window (Automated Subnets)
Integrates the Scanner Engine, SQLite database, Dashboard, Miner spreadsheet table,
and Group Operations. Supports automatic subnet detection to scan all local IPs (including 192.168.8.x) simultaneously.
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QProgressBar, QTabWidget,
                             QMessageBox, QLabel, QFrame, QComboBox)
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QIcon, QFont

from database.db_manager import DatabaseManager
from network.scanner import NetworkScanner
from gui.dashboard import DashboardWidget
from gui.miner_table import MinerTableWidget
from gui.login_dialog import LoginDialog
from gui.miner_details_dialog import MinerDetailsDialog
from gui.group_actions import GroupActionsWidget
from utils.helpers import detect_local_subnets

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.scanner = None

        self.setWindowTitle("FixBoard Miner Manager - v1.0.0")
        self.resize(1100, 750)

        self.init_ui()

        # Periodic database monitoring timer to refresh the Dashboard charts/cards
        self.db_timer = QTimer(self)
        self.db_timer.timeout.connect(self.calculate_global_kpis)
        self.db_timer.start(5000)

        # Initial call
        self.calculate_global_kpis()

    def init_ui(self):
        # Base central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 1. Top Scan Toolbar
        scan_panel = QFrame()
        scan_panel.setStyleSheet("""
            QFrame {
                background-color: #212128;
                border: 1px solid #3E3E4A;
                border-radius: 8px;
            }
        """)
        scan_layout = QHBoxLayout(scan_panel)
        scan_layout.setContentsMargins(12, 10, 12, 10)
        scan_layout.setSpacing(10)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #121216;
                border: 1px solid #3E3E4A;
                border-radius: 6px;
                text-align: center;
                color: #FFFFFF;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
                border-radius: 5px;
            }
        """)
        scan_layout.addWidget(self.progress_bar, 2)

        # Scan Button
        self.btn_scan = QPushButton("اسکن هوشمند شبکه (Scan)")
        self.btn_scan.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                font-family: 'Segoe UI';
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)
        self.btn_scan.clicked.connect(self.toggle_scan)
        scan_layout.addWidget(self.btn_scan)

        # Combo Box for Automatic Subnets Detection
        self.subnet_combo = QComboBox()
        self.subnet_combo.setStyleSheet("""
            QComboBox {
                background-color: #121216;
                border: 1px solid #3E3E4A;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 6px;
                min-width: 180px;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
        """)

        # Populate detected subnets automatically on startup
        detected = detect_local_subnets()
        self.subnet_combo.addItem("اسکن تمام محدوده‌های شبکه (خودکار)")
        for subnet in detected:
            self.subnet_combo.addItem(f"محدوده فعال: {subnet}", subnet)

        self.subnet_combo.addItem("محدوده دستی (وارد کردن در کادر)")
        self.subnet_combo.currentIndexChanged.connect(self.on_subnet_selection_changed)
        scan_layout.addWidget(self.subnet_combo)

        # Input IP range (for manual overriding or displaying auto)
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("مثال: 192.168.1.1-254")

        # Combine all auto-detected subnets as the default text representation
        default_range = ", ".join(detected)
        self.ip_input.setText(default_range)
        self.ip_input.setStyleSheet("""
            QLineEdit {
                background-color: #121216;
                border: 1px solid #3E3E4A;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 6px 12px;
                font-size: 12px;
                font-family: 'Segoe UI';
            }
        """)
        scan_layout.addWidget(self.ip_input, 1)

        lbl_ip = QLabel("شبکه هدف:")
        lbl_ip.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 11px;")
        scan_layout.addWidget(lbl_ip)

        main_layout.addWidget(scan_panel)

        # 2. Main Tabbed interface
        self.tabs = QTabWidget()

        # Dashboard tab
        self.tab_dashboard = DashboardWidget()
        self.tabs.addTab(self.tab_dashboard, "پیشخوان / داشبورد")

        # Spreadsheet list tab
        self.tab_table = MinerTableWidget()
        self.tab_table.miner_double_clicked.connect(self.open_miner_login)
        self.tab_table.selection_changed.connect(self.on_table_selection_changed)
        self.tabs.addTab(self.tab_table, "جدول ماینرها")

        # Group operations tab
        self.tab_group = GroupActionsWidget()
        self.tabs.addTab(self.tab_group, "عملیات گروهی همزمان")

        main_layout.addWidget(self.tabs)

    def on_subnet_selection_changed(self, index: int):
        """Dropdown index selection handler."""
        if index == 0: # Auto all
            detected = detect_local_subnets()
            self.ip_input.setText(", ".join(detected))
            self.ip_input.setEnabled(False)
        elif index == self.subnet_combo.count() - 1: # Manual
            self.ip_input.setText("")
            self.ip_input.setEnabled(True)
            self.ip_input.setFocus()
        else: # Specific active interface subnet
            subnet_data = self.subnet_combo.currentData()
            if subnet_data:
                self.ip_input.setText(subnet_data)
                self.ip_input.setEnabled(False)

    def toggle_scan(self):
        """Starts or cancels network range scans."""
        if self.scanner and self.scanner.isRunning():
            self.scanner.stop()
            self.btn_scan.setText("اسکن هوشمند شبکه (Scan)")
            self.btn_scan.setStyleSheet("""
                QPushButton {
                    background-color: #2ECC71;
                    color: white;
                    font-weight: bold;
                    padding: 8px 20px;
                    border-radius: 6px;
                }
            """)
            self.progress_bar.setValue(0)
            return

        ip_range = self.ip_input.text().strip()
        if not ip_range:
            QMessageBox.warning(self, "خطا", "لطفاً محدوده IP برای اسکن را مشخص نمایید.")
            return

        # Save last scan range
        self.db.set_setting("last_ip_range", ip_range)

        # Reset Progress Bar
        self.progress_bar.setValue(0)
        self.btn_scan.setText("لغو اسکن")
        self.btn_scan.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 6px;
            }
        """)

        # Initialize background scan thread
        self.scanner = NetworkScanner(ip_range)
        self.scanner.signals.progress.connect(self.on_scan_progress)
        self.scanner.signals.miner_discovered.connect(self.on_miner_discovered)
        self.scanner.signals.finished.connect(self.on_scan_finished)
        self.scanner.start()

    @Slot(int, str)
    def on_scan_progress(self, percent: int, current_ip: str):
        self.progress_bar.setValue(percent)
        self.progress_bar.setFormat(f"در حال اسکن {current_ip} - {percent}%")

    @Slot(dict)
    def on_miner_discovered(self, miner: dict):
        # Instant table refresh
        self.tab_table.refresh_data()
        self.calculate_global_kpis()

    @Slot(list)
    def on_scan_finished(self, discovered_list: list):
        self.btn_scan.setText("اسکن هوشمند شبکه (Scan)")
        self.btn_scan.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 6px;
            }
        """)
        self.progress_bar.setValue(100)
        self.progress_bar.setFormat("اسکن با موفقیت به پایان رسید.")

        self.tab_table.refresh_data()
        self.calculate_global_kpis()

        QMessageBox.information(
            self, "اسکن به پایان رسید",
            f"عملیات اسکن با موفقیت خاتمه یافت. تعداد {len(discovered_list)} دستگاه ماینر فعال جدید شناسایی شد."
        )

    def on_table_selection_changed(self, selected_ips: list):
        """Synchronizes selected check-boxes with Group Operation Widget tab."""
        self.tab_group.set_selected_miners(selected_ips)

    def open_miner_login(self, ip: str):
        """Launches auth modal and detailed management console upon login validation."""
        login_dlg = LoginDialog(ip, self)
        if login_dlg.exec() == LoginDialog.Accepted and login_dlg.authenticated:
            # Successfully authenticated, launch live Details Widget
            details_dlg = MinerDetailsDialog(ip, self)
            details_dlg.exec()
            # Refresh spreadsheet data to display potential MAC updates
            self.tab_table.refresh_data()

    def calculate_global_kpis(self):
        """
        Gathers database states and polls active online devices to generate
        live overall statistics across the dashboard tabs.
        """
        all_miners = self.db.get_all_miners()
        total = len(all_miners)
        online = sum(1 for m in all_miners if m["is_online"] == 1)
        offline = total - online

        # Calculate dynamic variables
        total_hashrate = 0.0
        temp_sum = 0.0
        temp_count = 0
        errors = 0

        # Propagate to dashboard widgets
        self.tab_dashboard.update_stats(
            total=total,
            online=online,
            offline=offline,
            error=errors,
            avg_temp=0.0,
            total_hr_th=0.0,
            avg_fan_rpm=0.0
        )
