"""
FixBoard Miner Manager - Miner Spreadsheet Widget
Provides a spreadsheet-like grid with multi-selection checkboxes, search filtering,
right-click contextual menus, and double-click actions to connect/authenticate with miners.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLineEdit, QPushButton, QAbstractItemView,
                             QMenu, QHeaderView, QLabel, QMessageBox, QCheckBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QAction, QCursor

from database.db_manager import DatabaseManager

class MinerTableWidget(QWidget):
    # Signals for parent integration
    miner_double_clicked = Signal(str) # Emits miner IP
    selection_changed = Signal(list)     # Emits list of selected miner IPs

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Search Bar & Bulk controls layout
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو بر اساس IP، برند، مدل یا نام...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2D2D35;
                border: 1px solid #444450;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 6px 12px;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #3498DB;
            }
        """)
        self.search_input.textChanged.connect(self.filter_table)
        top_bar.addWidget(self.search_input)

        self.btn_delete_selected = QPushButton("حذف انتخاب شده‌ها")
        self.btn_delete_selected.setStyleSheet("""
            QPushButton {
                background-color: #C0392B;
                border-radius: 6px;
                color: white;
                padding: 6px 15px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E74C3C;
            }
        """)
        self.btn_delete_selected.clicked.connect(self.delete_selected_miners)
        top_bar.addWidget(self.btn_delete_selected)

        layout.addLayout(top_bar)

        # Table Widget Creation
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "انتخاب", "آدرس IP", "مک آدرس (MAC)", "نام دستگاه",
            "مدل", "برند", "وضعیت اتصال", "آخرین اسکن"
        ])

        # Table Styling
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1F1F24;
                alternate-background-color: #27272E;
                color: #E2E2E5;
                gridline-color: #2E2E35;
                border: 1px solid #2E2E35;
                border-radius: 8px;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #2980B9;
                color: white;
            }
            QHeaderView::section {
                background-color: #2D2D35;
                color: #A0A5AD;
                padding: 6px;
                border: 1px solid #1F1F24;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: bold;
            }
        """)

        # Adjust Column Sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Checkbox
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # IP
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # MAC
        header.setSectionResizeMode(3, QHeaderView.Stretch)          # Name
        header.setSectionResizeMode(4, QHeaderView.Stretch)          # Model
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Brand
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Status
        header.setSectionResizeMode(7, QHeaderView.Stretch)          # Last scan

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.cellDoubleClicked.connect(self.on_cell_double_click)
        self.table.itemChanged.connect(self.on_item_changed)

        layout.addWidget(self.table)

        # Load data initially
        self.refresh_data()

    def refresh_data(self):
        """Loads and updates miners directly from SQLite."""
        # Block signals temporarily to prevent event loops while building rows
        self.table.blockSignals(True)

        miners = self.db.get_all_miners()
        self.table.setRowCount(len(miners))

        for row_idx, miner in enumerate(miners):
            # 0. Checkbox selector
            chk_box = QCheckBox()
            chk_box.setProperty("ip", miner["ip"])
            chk_box.stateChanged.connect(self.emit_selection_changed)

            # Align checkbox center
            container = QWidget()
            chk_layout = QHBoxLayout(container)
            chk_layout.addWidget(chk_box)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row_idx, 0, container)

            # 1. IP
            ip_item = QTableWidgetItem(miner["ip"])
            ip_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, ip_item)

            # 2. MAC
            mac_item = QTableWidgetItem(miner["mac"] or "دریافت نشد")
            mac_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 2, mac_item)

            # 3. Name
            name_item = QTableWidgetItem(miner["name"] or "دریافت نشد")
            name_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 3, name_item)

            # 4. Model
            model_item = QTableWidgetItem(miner["model"] or "دریافت نشد")
            model_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 4, model_item)

            # 5. Brand
            brand_item = QTableWidgetItem(miner["brand"] or "دریافت نشد")
            brand_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 5, brand_item)

            # 6. Status
            is_online = miner["is_online"] == 1
            status_text = "آنلاین" if is_online else "آفلاین"
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignCenter)
            if is_online:
                status_item.setForeground(QColor("#2ECC71"))
            else:
                status_item.setForeground(QColor("#E74C3C"))
            self.table.setItem(row_idx, 6, status_item)

            # 7. Last Scan
            scan_item = QTableWidgetItem(miner["last_scan"])
            scan_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 7, scan_item)

        self.table.blockSignals(False)

    def on_cell_double_click(self, row, col):
        """Triggers parent window dialog opening when user double clicks a miner row."""
        ip_item = self.table.item(row, 1)
        if ip_item:
            self.miner_double_clicked.emit(ip_item.text())

    def on_item_changed(self, item):
        pass

    def get_selected_ips(self) -> list:
        """Helper to collect currently checked IP addresses."""
        selected_ips = []
        for row in range(self.table.rowCount()):
            container = self.table.cellWidget(row, 0)
            if container:
                chk = container.findChild(QCheckBox)
                if chk and chk.isChecked():
                    selected_ips.append(chk.property("ip"))
        return selected_ips

    def emit_selection_changed(self, state):
        """Emits list of checked miner IPs."""
        self.selection_changed.emit(self.get_selected_ips())

    def filter_table(self):
        """Performs real-time search filtering over all visible columns."""
        search_text = self.search_input.text().lower().strip()
        for row in range(self.table.rowCount()):
            row_visible = False
            for col in range(1, self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    row_visible = True
                    break
            self.table.setRowHidden(row, not row_visible)

    def show_context_menu(self, pos):
        """Displays contextual actions for selected row."""
        row = self.table.currentRow()
        if row < 0:
            return

        ip_item = self.table.item(row, 1)
        if not ip_item:
            return

        ip = ip_item.text()

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2D2D35;
                border: 1px solid #444450;
                color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QMenu::item:selected {
                background-color: #3498DB;
            }
        """)

        act_connect = QAction("ورود به پنل و مانیتورینگ", self)
        act_connect.triggered.connect(lambda: self.miner_double_clicked.emit(ip))
        menu.addAction(act_connect)

        menu.addSeparator()

        act_delete = QAction("حذف این دستگاه", self)
        act_delete.triggered.connect(lambda: self.delete_single_miner(ip))
        menu.addAction(act_delete)

        menu.exec_(QCursor.pos())

    def delete_single_miner(self, ip: str):
        """Deletes single miner record."""
        confirm = QMessageBox.question(
            self, "تایید حذف", f"آیا از حذف ماینر {ip} اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            if self.db.delete_miner(ip):
                self.db.log_action("DELETE_MINER", ip, "SUCCESS", "Miner record deleted by user")
                self.refresh_data()

    def delete_selected_miners(self):
        """Deletes all checked miners."""
        selected_ips = self.get_selected_ips()
        if not selected_ips:
            QMessageBox.warning(self, "خطا", "هیچ ماینری انتخاب نشده است.")
            return

        confirm = QMessageBox.question(
            self, "تایید حذف گروهی", f"آیا از حذف {len(selected_ips)} ماینر انتخاب شده اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            success_count = 0
            for ip in selected_ips:
                if self.db.delete_miner(ip):
                    self.db.log_action("DELETE_MINER", ip, "SUCCESS", "Bulk delete miner record")
                    success_count += 1
            self.refresh_data()
            QMessageBox.information(self, "موفق", f"تعداد {success_count} دستگاه با موفقیت حذف شدند.")
