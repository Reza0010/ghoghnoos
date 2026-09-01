from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QInputDialog, QLineEdit,
    QDialog, QFormLayout, QComboBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from telegram_shop_bot.db import crud
from telegram_shop_bot.db.database import get_db
from telegram_shop_bot.db.models import Category

class CategoryDialog(QDialog):
    """A dialog for adding or editing a category."""
    def __init__(self, parent_widget=None, category: Category = None):
        super().__init__(parent_widget)
        self.setWindowTitle("ویرایش دسته‌بندی" if category else "افزودن دسته‌بندی")

        self.name_input = QLineEdit(category.name if category else "")
        self.parent_combo = QComboBox()

        with next(get_db()) as db:
            parents = crud.get_all_categories(db)
            self.parent_combo.addItem("None (والد اصلی)", None)
            for p in parents:
                # Prevent a category from being its own parent
                if category and p.id == category.id:
                    continue
                self.parent_combo.addItem(p.name, p.id)

        if category and category.parent_id:
            index = self.parent_combo.findData(category.parent_id)
            if index != -1:
                self.parent_combo.setCurrentIndex(index)
        elif not category:
             # Default to "None" for new categories
             self.parent_combo.setCurrentIndex(0)


        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow("نام دسته‌بندی:", self.name_input)
        layout.addRow("دسته‌بندی والد:", self.parent_combo)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "parent_id": self.parent_combo.currentData()
        }

class CategoriesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["نام دسته‌بندی", "ID"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("افزودن")
        edit_btn = QPushButton("ویرایش")
        delete_btn = QPushButton("حذف")

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.tree)

        add_btn.clicked.connect(self.add_category)
        edit_btn.clicked.connect(self.edit_category)
        delete_btn.clicked.connect(self.delete_category)

    def refresh_data(self):
        self.load_categories()

    def load_categories(self):
        self.tree.clear()
        with next(get_db()) as db:
            categories = crud.get_all_categories(db)

        category_items = {}
        # First pass: create all items
        for category in categories:
            item = QTreeWidgetItem([category.name, str(category.id)])
            item.setData(0, Qt.ItemDataRole.UserRole, category.id)
            category_items[category.id] = item

        # Second pass: build the tree structure
        for category in categories:
            if category.parent_id is not None and category.parent_id in category_items:
                parent_item = category_items[category.parent_id]
                parent_item.addChild(category_items[category.id])
            else:
                self.tree.addTopLevelItem(category_items[category.id])

        self.tree.expandAll()

    def add_category(self):
        dialog = CategoryDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data["name"]:
                with next(get_db()) as db:
                    crud.create_category(db, data["name"], data["parent_id"])
                self.load_categories()
            else:
                QMessageBox.warning(self, "خطا", "نام دسته‌بندی نمی‌تواند خالی باشد.")

    def edit_category(self):
        selected_item = self.tree.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "خطا", "لطفاً یک دسته‌بندی را برای ویرایش انتخاب کنید.")
            return

        category_id = selected_item.data(0, Qt.ItemDataRole.UserRole)
        with next(get_db()) as db:
            category = crud.get_category(db, category_id)

        if category:
            dialog = CategoryDialog(self, category)
            if dialog.exec():
                data = dialog.get_data()
                if data["name"]:
                    with next(get_db()) as db:
                        crud.update_category(db, category_id, data["name"], data["parent_id"])
                    self.load_categories()
                else:
                    QMessageBox.warning(self, "خطا", "نام دسته‌بندی نمی‌تواند خالی باشد.")

    def delete_category(self):
        selected_item = self.tree.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "خطا", "لطفاً یک دسته‌بندی را برای حذف انتخاب کنید.")
            return

        category_id = selected_item.data(0, Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "تایید حذف",
                                     f"آیا از حذف دسته‌بندی با ID {category_id} اطمینان دارید؟\n"
                                     "توجه: تمام محصولات و زیرشاخه‌های این دسته‌بندی نیز حذف خواهند شد.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            with next(get_db()) as db:
                success = crud.delete_category(db, category_id)
            if success:
                self.load_categories()
            else:
                QMessageBox.critical(self, "خطا", "حذف دسته‌بندی ناموفق بود.")
