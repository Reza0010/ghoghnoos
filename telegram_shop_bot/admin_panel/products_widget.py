import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QSpinBox,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from telegram_shop_bot.db.database import get_db
from telegram_shop_bot.db import crud

class ProductsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_product_id = None
        self.current_page = 1
        self.page_size = 15
        self.total_pages = 1
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setDirection(QHBoxLayout.Direction.RightToLeft)
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_widget.setFixedWidth(350)
        self.name_input = QLineEdit()
        self.category_combo = QComboBox()
        self.brand_input = QLineEdit()
        self.desc_input = QTextEdit()
        self.price_input = QSpinBox(maximum=10**9)
        self.stock_input = QSpinBox(maximum=10000)
        form_layout.addWidget(QLabel("نام محصول:"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("دسته بندی:"))
        form_layout.addWidget(self.category_combo)
        form_layout.addWidget(QLabel("برند:"))
        form_layout.addWidget(self.brand_input)
        form_layout.addWidget(QLabel("توضیحات:"))
        form_layout.addWidget(self.desc_input)
        price_stock_layout = QHBoxLayout()
        price_layout = QVBoxLayout()
        price_layout.addWidget(QLabel("قیمت:"))
        price_layout.addWidget(self.price_input)
        stock_layout = QVBoxLayout()
        stock_layout.addWidget(QLabel("موجودی:"))
        stock_layout.addWidget(self.stock_input)
        price_stock_layout.addLayout(price_layout)
        price_stock_layout.addLayout(stock_layout)
        form_layout.addLayout(price_stock_layout)
        form_layout.addStretch()
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("ذخیره")
        self.new_btn = QPushButton("جدید")
        self.delete_btn = QPushButton("حذف")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.new_btn)
        btn_layout.addWidget(self.delete_btn)
        form_layout.addLayout(btn_layout)

        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        self.products_table = QTableWidget(columnCount=4)
        self.products_table.setHorizontalHeaderLabels(["نام", "دسته", "قیمت", "موجودی"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        pagination_layout = QHBoxLayout()
        self.prev_btn = QPushButton("«")
        self.page_label = QLabel("1 / 1")
        self.next_btn = QPushButton("»")
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addStretch()

        table_layout.addWidget(self.products_table)
        table_layout.addLayout(pagination_layout)
        main_layout.addWidget(table_widget)
        main_layout.addWidget(form_widget)

        self.save_btn.clicked.connect(self.save_product)
        self.new_btn.clicked.connect(self.clear_form)
        self.delete_btn.clicked.connect(self.delete_product)
        self.products_table.selectionModel().selectionChanged.connect(self.load_product_to_form)
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)

    def refresh_data(self):
        self.load_categories()
        self.load_products()

    def load_categories(self):
        self.category_combo.clear()
        with next(get_db()) as db:
            cats = crud.get_categories(db)
            for cat in cats: self.category_combo.addItem(cat.name, cat.id)

    def load_products(self):
        with next(get_db()) as db:
            count = crud.get_total_product_count(db)
            self.total_pages = math.ceil(count / self.page_size) if count > 0 else 1
            prods = crud.get_all_products_paginated(db, page=self.current_page, page_size=self.page_size)
        self.populate_table(prods)
        self.update_pagination_ui()

    def populate_table(self, prods):
        self.products_table.clearContents()
        self.products_table.setRowCount(len(prods))
        for r, p in enumerate(prods):
            self.products_table.setItem(r, 0, QTableWidgetItem(p.name))
            self.products_table.setItem(r, 1, QTableWidgetItem(p.category.name if p.category else "N/A"))
            self.products_table.setItem(r, 2, QTableWidgetItem(f"{p.price:,.0f}"))
            self.products_table.setItem(r, 3, QTableWidgetItem(str(p.stock)))
            self.products_table.item(r, 0).setData(Qt.ItemDataRole.UserRole, p.id)

    def update_pagination_ui(self):
        self.page_label.setText(f"{self.current_page} / {self.total_pages}")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)

    def next_page(self):
        if self.current_page < self.total_pages: self.current_page += 1; self.load_products()
    def prev_page(self):
        if self.current_page > 1: self.current_page -= 1; self.load_products()

    def load_product_to_form(self):
        items = self.products_table.selectedItems()
        if not items: return
        self.current_product_id = items[0].data(Qt.ItemDataRole.UserRole)
        with next(get_db()) as db: prod = crud.get_product(db, self.current_product_id)
        if prod:
            self.name_input.setText(prod.name)
            self.brand_input.setText(prod.brand)
            self.desc_input.setPlainText(prod.description)
            self.price_input.setValue(int(prod.price))
            self.stock_input.setValue(prod.stock)
            idx = self.category_combo.findData(prod.category_id)
            if idx >= 0: self.category_combo.setCurrentIndex(idx)

    def save_product(self):
        cat_id = self.category_combo.currentData()
        if not self.name_input.text() or cat_id is None:
            QMessageBox.warning(self, "خطا", "نام و دسته بندی الزامی است.")
            return
        data = {"name": self.name_input.text(), "category_id": cat_id, "brand": self.brand_input.text(), "description": self.desc_input.toPlainText(), "price": self.price_input.value(), "stock": self.stock_input.value()}
        with next(get_db()) as db:
            if self.current_product_id: crud.update_product(db, self.current_product_id, **data)
            else: crud.create_product(db, **data)
        QMessageBox.information(self, "موفق", "محصول ذخیره شد!")
        self.load_products()
        self.clear_form()

    def delete_product(self):
        if not self.current_product_id: return
        if QMessageBox.question(self, "تایید حذف", "آیا مطمئن هستید؟") == QMessageBox.StandardButton.Yes:
            with next(get_db()) as db: crud.delete_product(db, self.current_product_id)
            self.load_products()
            self.clear_form()

    def clear_form(self):
        self.current_product_id = None
        self.name_input.clear()
        self.brand_input.clear()
        self.desc_input.clear()
        self.price_input.setValue(0)
        self.stock_input.setValue(0)
        self.category_combo.setCurrentIndex(0)
        self.products_table.clearSelection()
