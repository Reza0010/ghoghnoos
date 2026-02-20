import asyncio
import shutil
import logging
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QSpinBox, QMessageBox, QDoubleSpinBox,
    QFileDialog, QCheckBox, QScrollArea, QFrame, QGridLayout, 
    QGraphicsDropShadowEffect, QSizePolicy, QButtonGroup, QAbstractSpinBox,
    QApplication, QMenu, QTableWidget, QTableWidgetItem, QHeaderView, 
    QInputDialog, QAbstractItemView, QTabWidget, QDialog
)
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QColor, QAction, QCursor, QFont, QDoubleValidator, QIcon, QMouseEvent
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QEvent, QPropertyAnimation, QRect
from qasync import asyncSlot
import qtawesome as qta

from db.database import get_db
from db import crud
from config import BASE_DIR, MEDIA_PRODUCTS_DIR

logger = logging.getLogger(__name__)

# --- تنظیمات تم ---
BG_COLOR = "#16161a"
PANEL_BG = "#242629"
CARD_BG = "#2a2c30"
ACCENT_COLOR = "#7f5af0"
SUCCESS_COLOR = "#2cb67d"
INFO_COLOR = "#3da9fc"
WARNING_COLOR = "#f39c12"
DANGER_COLOR = "#ef4565"
TEXT_MAIN = "#fffffe"
TEXT_SUB = "#94a1b2"
BORDER_COLOR = "#2e2e38"

# ==============================================================================
# Helper Widgets
# ==============================================================================
class FormattedPriceInput(QLineEdit):
    def __init__(self, parent=None, placeholder="0"):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setStyleSheet(f"""
            QLineEdit {{ background: {BG_COLOR}; border: 1px solid {BORDER_COLOR};
                border-radius: 8px; padding: 10px; color: {TEXT_MAIN};
                font-weight: bold; font-size: 14px; }}
            QLineEdit:focus {{ border: 1px solid {ACCENT_COLOR}; }}
        """)
        self.textChanged.connect(self.format_text)

    def format_text(self, text):
        if not text: return
        clean = text.replace(",", "")
        if not clean.isdigit(): return
        val = int(clean)
        formatted = f"{val:,}"
        if text != formatted:
            self.blockSignals(True)
            self.setText(formatted)
            self.setCursorPosition(len(formatted))
            self.blockSignals(False)

    def value(self) -> int: return int(self.text().replace(",", "") or 0)
    def setValue(self, val): self.setText(f"{int(val):,}")

class TagsInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("مثال: جدید, فروش ویژه")
        self.setStyleSheet(f"QLineEdit {{ background: {BG_COLOR}; border: 1px solid {BORDER_COLOR}; border-radius: 8px; padding: 10px; color: {TEXT_MAIN}; }}")
    def get_tags_list(self) -> List[str]: return [t.strip() for t in self.text().split(',') if t.strip()]
    def set_tags(self, tags_str: str): self.setText(tags_str if tags_str else "")

class MultiImageManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_paths = []
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.refresh_ui()

    def set_images(self, paths): self.image_paths = paths; self.refresh_ui()
    def get_images(self): return self.image_paths
    def add_images(self, paths):
        for p in paths:
            if p not in self.image_paths: self.image_paths.append(p)
        self.refresh_ui()
    def remove_image(self, path):
        if path in self.image_paths: self.image_paths.remove(path); self.refresh_ui()

    def refresh_ui(self):
        for i in reversed(range(self.layout.count())): 
            item = self.layout.itemAt(i)
            if item.widget(): item.widget().setParent(None)
        
        for path in self.image_paths:
            full_path = path
            if not os.path.isabs(path): full_path = str(BASE_DIR / path)
            if os.path.exists(full_path):
                container = QFrame()
                container.setFixedSize(100, 100)
                container.setStyleSheet(f"background: {BG_COLOR}; border-radius: 8px; border: 1px solid {BORDER_COLOR};")
                l = QVBoxLayout(container); l.setContentsMargins(5, 5, 5, 5)
                lbl_img = QLabel(); lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
                pix = QPixmap(full_path)
                lbl_img.setPixmap(pix.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                btn_del = QPushButton("×")
                btn_del.setFixedSize(20, 20)
                btn_del.setStyleSheet(f"background: {DANGER_COLOR}; color: white; border-radius: 10px; font-weight: bold; border: none;")
                btn_del.clicked.connect(lambda _, p=path: self.remove_image(p))
                overlay = QHBoxLayout(); overlay.addStretch(); overlay.addWidget(btn_del)
                l.addLayout(overlay); l.addWidget(lbl_img)
                self.layout.addWidget(container)

        btn_add = QPushButton("+")
        btn_add.setFixedSize(100, 100)
        btn_add.setStyleSheet(f"QPushButton {{ background: transparent; border: 2px dashed {BORDER_COLOR}; border-radius: 8px; color: {TEXT_SUB}; font-size: 30px; }} QPushButton:hover {{ border-color: {ACCENT_COLOR}; color: {ACCENT_COLOR}; }}")
        btn_add.clicked.connect(self.browse_files)
        self.layout.addWidget(btn_add)

    def browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "انتخاب تصاویر", "", "Images (*.jpg *.png *.jpeg *.webp)")
        if files: self.add_images(files)

class VariantManager(QTableWidget):
    def __init__(self):
        super().__init__(0, 4)
        self.setHorizontalHeaderLabels(["نام متغیر", "تفاوت قیمت", "موجودی", "عملیات"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(f"QTableWidget {{ background: {BG_COLOR}; border: 1px solid {BORDER_COLOR}; border-radius: 8px; color: {TEXT_MAIN}; gridline-color: #333; }} QHeaderView::section {{ background: {PANEL_BG}; color: {TEXT_SUB}; padding: 8px; border: none; font-weight: bold; }}")

    def add_row(self, name="", price_adj=0, stock=0):
        row = self.rowCount()
        self.insertRow(row)
        inp_name = QLineEdit(name); inp_name.setPlaceholderText("مثال: قرمز")
        inp_name.setStyleSheet(f"background: {BG_COLOR}; color: {TEXT_MAIN}; border: none; padding: 5px;")
        self.setCellWidget(row, 0, inp_name)
        inp_price = FormattedPriceInput(placeholder="0"); inp_price.setValue(price_adj)
        self.setCellWidget(row, 1, inp_price)
        inp_stock = QSpinBox(); inp_stock.setRange(0, 100000); inp_stock.setValue(stock)
        inp_stock.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        inp_stock.setStyleSheet(f"background: {BG_COLOR}; color: {TEXT_MAIN}; border: none; padding: 5px;")
        self.setCellWidget(row, 2, inp_stock)
        btn_del = QPushButton(); btn_del.setIcon(qta.icon('fa5s.trash-alt', color=DANGER_COLOR))
        btn_del.setStyleSheet("background: transparent; border: none;")
        btn_del.clicked.connect(lambda: self.removeRow(self.indexAt(btn_del.pos()).row()))
        self.setCellWidget(row, 3, btn_del)

    def get_data(self) -> List[dict]:
        variants = []
        for i in range(self.rowCount()):
            name_w = self.cellWidget(i, 0); price_w = self.cellWidget(i, 1); stock_w = self.cellWidget(i, 2)
            if name_w and name_w.text().strip():
                variants.append({"name": name_w.text().strip(), "price_adjustment": price_w.value(), "stock": stock_w.value()})
        return variants

# ==============================================================================
# Dialog: Editor
# ==============================================================================
class ProductEditorDialog(QDialog):
    product_saved = pyqtSignal()
    def __init__(self, parent=None, product_id=None):
        super().__init__(parent)
        self.product_id = product_id
        self.setWindowTitle("ویرایش محصول" if product_id else "افزودن محصول جدید")
        self.resize(900, 700)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(f"QDialog {{ background-color: {BG_COLOR}; }}")
        self.setup_ui()
        if product_id: asyncio.create_task(self.load_data(product_id))

    def setup_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(20, 20, 20, 20); layout.setSpacing(15)
        h_layout = QHBoxLayout()
        lbl_title = QLabel("✏️ ویرایش محصول" if self.product_id else "➕ محصول جدید")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        h_layout.addWidget(lbl_title); h_layout.addStretch()
        layout.addLayout(h_layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"QTabWidget::pane {{ border: 1px solid {BORDER_COLOR}; border-radius: 8px; background: {PANEL_BG}; top:-1px; }} QTabBar::tab {{ background: transparent; color: {TEXT_SUB}; padding: 10px 20px; font-weight: bold; margin-right: 5px; border-top-left-radius: 8px; border-top-right-radius: 8px; }} QTabBar::tab:selected {{ background: {PANEL_BG}; color: {ACCENT_COLOR}; border: 1px solid {BORDER_COLOR}; border-bottom: none; }}")
        
        # Main Tab
        tab_main = QWidget(); l_main = QVBoxLayout(tab_main); l_main.setContentsMargins(15, 20, 15, 20); l_main.setSpacing(15)
        l_main.addWidget(QLabel("تصاویر:", styleSheet=f"color:{TEXT_SUB}; font-weight:bold;"))
        self.img_manager = MultiImageManager()
        scroll_img = QScrollArea(); scroll_img.setWidget(self.img_manager); scroll_img.setWidgetResizable(True); scroll_img.setFixedHeight(130); scroll_img.setStyleSheet("background: transparent; border: none;")
        l_main.addWidget(scroll_img)
        grid = QGridLayout(); grid.setSpacing(10)
        self.inp_name = QLineEdit(); self.inp_name.setPlaceholderText("نام محصول")
        self.inp_cat = QComboBox(); self.inp_brand = QLineEdit(); self.inp_brand.setPlaceholderText("برند")
        self.inp_desc = QTextEdit(); self.inp_desc.setPlaceholderText("توضیحات...")
        for w in [self.inp_name, self.inp_cat, self.inp_brand]: w.setStyleSheet(f"background: {BG_COLOR}; color: {TEXT_MAIN}; border: 1px solid {BORDER_COLOR}; padding: 10px; border-radius: 8px;")
        self.inp_desc.setStyleSheet(f"background: {BG_COLOR}; color: {TEXT_MAIN}; border: 1px solid {BORDER_COLOR}; padding: 10px; border-radius: 8px;")
        grid.addWidget(QLabel("نام:"), 0, 0); grid.addWidget(self.inp_name, 0, 1)
        grid.addWidget(QLabel("دسته:"), 1, 0); grid.addWidget(self.inp_cat, 1, 1)
        grid.addWidget(QLabel("برند:"), 2, 0); grid.addWidget(self.inp_brand, 2, 1)
        l_main.addLayout(grid); l_main.addWidget(QLabel("توضیحات:")); l_main.addWidget(self.inp_desc)
        
        # Price Tab
        tab_price = QWidget(); l_price = QVBoxLayout(tab_price); l_price.setContentsMargins(20, 20, 20, 20); l_price.setSpacing(15)
        self.inp_price = FormattedPriceInput(placeholder="قیمت اصلی")
        self.inp_discount = FormattedPriceInput(placeholder="قیمت تخفیف (اختیاری)")
        self.inp_stock = QSpinBox(); self.inp_stock.setRange(0, 100000)
        self.inp_stock.setStyleSheet(f"background: {BG_COLOR}; color: {TEXT_MAIN}; border: 1px solid {BORDER_COLOR}; padding: 10px; border-radius: 8px;")
        self.chk_top = QCheckBox("پرفروش"); self.chk_top.setStyleSheet(f"color: {TEXT_MAIN}; font-weight: bold;")
        l_price.addWidget(QLabel("قیمت:")); l_price.addWidget(self.inp_price)
        l_price.addWidget(QLabel("تخفیف:")); l_price.addWidget(self.inp_discount)
        l_price.addWidget(QLabel("موجودی:")); l_price.addWidget(self.inp_stock)
        l_price.addWidget(self.chk_top); l_price.addStretch()

        # Vars Tab
        tab_vars = QWidget(); l_vars = QVBoxLayout(tab_vars); l_vars.setContentsMargins(15, 15, 15, 15)
        self.variant_mgr = VariantManager()
        btn_add_var = QPushButton(" افزودن"); btn_add_var.setIcon(qta.icon('fa5s.plus', color=SUCCESS_COLOR))
        btn_add_var.setStyleSheet(f"background: transparent; border: 1px dashed {SUCCESS_COLOR}; color: {SUCCESS_COLOR}; border-radius: 8px; padding: 8px; font-weight: bold;")
        btn_add_var.clicked.connect(lambda: self.variant_mgr.add_row())
        l_vars.addWidget(self.variant_mgr); l_vars.addWidget(btn_add_var)

        # SEO Tab
        tab_extra = QWidget(); l_extra = QVBoxLayout(tab_extra); l_extra.setContentsMargins(20, 20, 20, 20)
        self.inp_tags = TagsInput(); self.inp_rel = QLineEdit(); self.inp_rel.setPlaceholderText("ID محصولات مرتبط")
        self.inp_rel.setStyleSheet(f"background: {BG_COLOR}; color: {TEXT_MAIN}; border: 1px solid {BORDER_COLOR}; padding: 10px; border-radius: 8px;")
        l_extra.addWidget(QLabel("تگ‌ها:")); l_extra.addWidget(self.inp_tags)
        l_extra.addWidget(QLabel("مرتبط:")); l_extra.addWidget(self.inp_rel); l_extra.addStretch()

        self.tabs.addTab(tab_main, "اصلی"); self.tabs.addTab(tab_price, "قیمت"); self.tabs.addTab(tab_vars, "تنوع"); self.tabs.addTab(tab_extra, "سئو")
        layout.addWidget(self.tabs)

        btn_box = QHBoxLayout()
        btn_cancel = QPushButton("انصراف"); btn_cancel.setStyleSheet(f"background: {PANEL_BG}; color: {TEXT_MAIN}; padding: 10px 20px; border-radius: 8px; border: none;")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("ذخیره"); btn_save.setIcon(qta.icon('fa5s.save', color='white'))
        btn_save.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; padding: 10px 25px; border-radius: 8px; font-weight: bold; border: none;")
        btn_save.clicked.connect(self.save_product)
        btn_box.addStretch(); btn_box.addWidget(btn_cancel); btn_box.addWidget(btn_save)
        layout.addLayout(btn_box)
        self.load_categories()

    def load_categories(self):
        try:
            with next(get_db()) as db:
                cats = crud.get_all_categories(db)
                self.inp_cat.clear()
                for c in cats: self.inp_cat.addItem(c.name, c.id)
        except: pass

    async def load_data(self, pid):
        loop = asyncio.get_running_loop()
        def fetch():
            with next(get_db()) as db:
                p = crud.get_product(db, pid)
                if not p: return None
                images = [img.image_path for img in p.images] if hasattr(p, 'images') else ([p.image_path] if p.image_path else [])
                variants = [{"name": v.name, "price_adjustment": v.price_adjustment, "stock": v.stock} for v in p.variants]
                return {"obj": p, "images": images, "variants": variants}
        data = await loop.run_in_executor(None, fetch)
        if not data: return
        p = data["obj"]
        self.inp_name.setText(p.name); self.inp_price.setValue(float(p.price))
        self.inp_discount.setValue(float(p.discount_price or 0)); self.inp_stock.setValue(p.stock)
        self.inp_brand.setText(p.brand or ""); self.inp_desc.setPlainText(p.description or "")
        self.inp_tags.set_tags(p.tags or ""); self.inp_rel.setText(p.related_product_ids or "")
        self.chk_top.setChecked(p.is_top_seller)
        idx = self.inp_cat.findData(p.category_id)
        if idx >= 0: self.inp_cat.setCurrentIndex(idx)
        self.img_manager.set_images(data["images"])
        for v in data["variants"]: self.variant_mgr.add_row(v["name"], v["price_adjustment"], v["stock"])

    @asyncSlot()
    async def save_product(self):
        if not self.inp_name.text(): return QMessageBox.warning(self, "خطا", "نام الزامی است.")
        data = {
            "name": self.inp_name.text(), "category_id": self.inp_cat.currentData(),
            "price": self.inp_price.value(), "discount_price": self.inp_discount.value(),
            "stock": self.inp_stock.value(), "brand": self.inp_brand.text(),
            "description": self.inp_desc.toPlainText(), "tags": ",".join(self.inp_tags.get_tags_list()),
            "related_product_ids": self.inp_rel.text(), "is_top_seller": self.chk_top.isChecked()
        }
        raw_images = self.img_manager.get_images()
        final_images = []
        for img_path in raw_images:
            if str(MEDIA_PRODUCTS_DIR) not in os.path.abspath(img_path):
                ext = Path(img_path).suffix
                fname = f"prod_{datetime.now().strftime('%Y%m%d%H%M%S_%f')}{ext}"
                dest = MEDIA_PRODUCTS_DIR / fname
                try: shutil.copy(img_path, dest); final_images.append(f"media/products/{fname}")
                except: pass
            else:
                if os.path.isabs(img_path): final_images.append(os.path.relpath(img_path, BASE_DIR).replace("\\", "/"))
                else: final_images.append(img_path)
        
        variants = self.variant_mgr.get_data()
        loop = asyncio.get_running_loop()
        try:
            def db_op():
                with next(get_db()) as db:
                    if self.product_id:
                        if final_images: data["image_path"] = final_images[0]
                        crud.update_product_with_variants(db, self.product_id, data, variants)
                    else:
                        crud.create_product_with_variants(db, data, variants, image_paths=final_images)
            await loop.run_in_executor(None, db_op)
            self.product_saved.emit(); self.accept()
        except Exception as e: QMessageBox.critical(self, "خطا", str(e))

# ==============================================================================
# Card Widget (با Quick Edit)
# ==============================================================================
class ProductCard(QFrame):
    selectionChanged = pyqtSignal(int, bool)
    quickUpdateRequested = pyqtSignal(int, str, int) # ID, Field, Value

    def __init__(self, product, parent_widget):
        super().__init__()
        self.product = product
        self.p_widget = parent_widget
        self.setFixedSize(260, 450)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20); shadow.setColor(QColor(0,0,0,80)); shadow.setOffset(0,5)
        self.setGraphicsEffect(shadow)

        self.setStyleSheet(f"QFrame {{ background-color: {PANEL_BG}; border-radius: 14px; border: 1px solid {BORDER_COLOR}; }} QFrame:hover {{ border: 1px solid {ACCENT_COLOR}; }}")
        
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)

        # تصویر
        img_container = QWidget(); img_container.setFixedHeight(170)
        img_layout = QVBoxLayout(img_container); img_layout.setContentsMargins(0,0,0,0)
        self.img_lbl = QLabel(); self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.setStyleSheet(f"background-color: {BG_COLOR}; border-top-left-radius: 13px; border-top-right-radius: 13px;")
        
        img_path = None
        if hasattr(product, 'images') and product.images: img_path = product.images[0].image_path
        elif hasattr(product, 'image_path') and product.image_path: img_path = product.image_path
            
        if img_path:
            full_path = BASE_DIR / img_path
            if full_path.exists():
                pix = QPixmap(str(full_path))
                self.img_lbl.setPixmap(pix.scaled(260, 170, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
            else: self.img_lbl.setText("📷")
        else: self.img_lbl.setText("📷")
        
        # برچسب‌های وضعیت
        if product.stock == 0:
            self._add_badge("ناموجود", DANGER_COLOR, img_container)
        elif product.is_top_seller:
            self._add_badge("پرفروش", SUCCESS_COLOR, img_container, right=True)
        elif product.discount_price and product.discount_price > 0:
            self._add_badge("تخفیف‌دار", WARNING_COLOR, img_container, right=True)
        
        # چک‌باکس
        self.chk_select = QCheckBox(img_container)
        self.chk_select.move(10, 140); self.chk_select.setFixedSize(22, 22)
        self.chk_select.stateChanged.connect(self.on_checked)
        self.chk_select.setStyleSheet(f"QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 5px; border: 2px solid {ACCENT_COLOR}; background: rgba(0,0,0,0.5); }} QCheckBox::indicator:checked {{ background: {SUCCESS_COLOR}; }}")
        
        img_layout.addWidget(self.img_lbl)
        layout.addWidget(img_container)

        # اطلاعات
        content = QWidget(); c_layout = QVBoxLayout(content); c_layout.setContentsMargins(12, 10, 12, 10); c_layout.setSpacing(5)
        
        lbl_name = QLabel(product.name); lbl_name.setWordWrap(True); lbl_name.setFixedHeight(40)
        lbl_name.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {TEXT_MAIN};")
        
        cat_name = product.category.name if product.category else "بدون دسته"
        lbl_meta = QLabel(f"📂 {cat_name}"); lbl_meta.setStyleSheet(f"color: {TEXT_SUB}; font-size: 11px;")
        
        row_price = QHBoxLayout()
        if product.discount_price and product.discount_price > 0:
             lbl_price = QLabel(f"{int(product.discount_price):,} ت"); lbl_price.setStyleSheet(f"color: {WARNING_COLOR}; font-weight: bold; font-size: 14px;")
             lbl_old = QLabel(f"{int(product.price):,}"); lbl_old.setStyleSheet(f"color: {TEXT_SUB}; font-size: 10px; text-decoration: line-through;")
             row_price.addWidget(lbl_price); row_price.addWidget(lbl_old)
        else:
             lbl_price = QLabel(f"{int(product.price):,} تومان"); lbl_price.setStyleSheet(f"color: {SUCCESS_COLOR}; font-weight: bold; font-size: 14px;")
             row_price.addWidget(lbl_price)

        # موجودی با قابلیت دابل کلیک
        stock_color = DANGER_COLOR if product.stock < 5 else TEXT_SUB
        self.lbl_stock = QLabel(f"📦 موجودی: {product.stock}")
        self.lbl_stock.setStyleSheet(f"color: {stock_color}; font-size: 12px; font-weight: bold; padding: 2px;")
        self.lbl_stock.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_stock.setToolTip("دابل کلیک برای ویرایش سریع")
        self.lbl_stock.mouseDoubleClickEvent = lambda e: self._quick_edit_stock()
        
        row_price.addStretch(); row_price.addWidget(self.lbl_stock)
        
        c_layout.addWidget(lbl_name); c_layout.addWidget(lbl_meta); c_layout.addLayout(row_price)
        
        # دکمه‌های کپی لینک
        link_layout = QHBoxLayout(); link_layout.setSpacing(5)
        self.btn_tg = QPushButton(); self.btn_tg.setIcon(qta.icon('fa5b.telegram', color='white'))
        self.btn_tg.setFixedHeight(28); self.btn_tg.setToolTip("کپی لینک تلگرام")
        self.btn_tg.setStyleSheet(f"background: #2980b9; border-radius: 6px;")
        self.btn_tg.clicked.connect(self.copy_tg_link)
        
        self.btn_rb = QPushButton(); self.btn_rb.setIcon(qta.icon('fa5s.infinity', color='white'))
        self.btn_rb.setFixedHeight(28); self.btn_rb.setToolTip("کپی لینک روبیکا")
        self.btn_rb.setStyleSheet(f"background: #8e44ad; border-radius: 6px;")
        self.btn_rb.clicked.connect(self.copy_rb_link)
        
        link_layout.addWidget(self.btn_tg); link_layout.addWidget(self.btn_rb); link_layout.addStretch()
        c_layout.addLayout(link_layout)
        
        # دکمه‌های عملیاتی
        h_btn = QHBoxLayout(); h_btn.setSpacing(5)
        
        btn_del = QPushButton(); btn_del.setIcon(qta.icon('fa5s.trash', color=DANGER_COLOR))
        btn_del.setFixedSize(32, 32); btn_del.setStyleSheet(f"background: {BG_COLOR}; border-radius: 6px;")
        btn_del.clicked.connect(lambda: self.p_widget.delete_product_single(self.product.id))

        btn_dup = QPushButton(); btn_dup.setIcon(qta.icon('fa5s.copy', color=INFO_COLOR))
        btn_dup.setFixedSize(32, 32); btn_dup.setStyleSheet(f"background: {BG_COLOR}; border-radius: 6px;")
        btn_dup.setToolTip("تکثیر محصول")
        btn_dup.clicked.connect(lambda: self.p_widget.duplicate_product(self.product.id))

        btn_edit = QPushButton("ویرایش"); btn_edit.setIcon(qta.icon('fa5s.pen', color='white'))
        btn_edit.setStyleSheet(f"background: {ACCENT_COLOR}; border: none; border-radius: 6px; color: white; height: 32px; font-weight: bold;")
        btn_edit.clicked.connect(lambda: self.p_widget.open_editor_dialog(self.product.id))
        
        h_btn.addWidget(btn_del); h_btn.addWidget(btn_dup); h_btn.addWidget(btn_edit, 1)
        c_layout.addLayout(h_btn)
        
        layout.addWidget(content)

    def _add_badge(self, text, color, parent, right=False):
        lbl = QLabel(text, parent)
        lbl.setStyleSheet(f"background: {color}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 10px;")
        lbl.adjustSize()
        x = parent.width() - lbl.width() - 10 if right else 10
        lbl.move(x, 10)

    def _quick_edit_stock(self):
        val, ok = QInputDialog.getInt(self, "ویرایش سریع موجودی", f"موجی جدید برای {self.product.name}:", value=self.product.stock, min=0)
        if ok:
            self.quickUpdateRequested.emit(self.product.id, "stock", val)
            # آپدیت ظاهری موقت تا رفرش بعدی
            self.lbl_stock.setText(f"📦 موجودی: {val}")
            self.product.stock = val # آپدیت مدل داخلی

    def on_checked(self, state):
        self.selectionChanged.emit(self.product.id, state == 2)

    def copy_tg_link(self):
        bot = self.p_widget.bot_username or "Bot"
        QApplication.clipboard().setText(f"https://t.me/{bot}?start=p_{self.product.id}")
        self.p_widget.window().show_toast("لینک تلگرام کپی شد")

    def copy_rb_link(self):
        rb = self.p_widget.rubika_username or "Bot"
        QApplication.clipboard().setText(f"https://rubika.ir/{rb}?start=p_{self.product.id}")
        self.p_widget.window().show_toast("لینک روبیکا کپی شد")

# ==============================================================================
# Main Widget
# ==============================================================================
class ProductsWidget(QWidget):
    def __init__(self, bot_app=None):
        super().__init__()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.bot_app = bot_app
        self.selected_ids = set()
        self.bot_username = "MyBot"
        self.rubika_username = "MyShopBot"
        self.setup_ui()
        self._data_loaded = False

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # هدر
        top_row = QHBoxLayout()
        lbl_title = QLabel("مدیریت محصولات"); lbl_title.setStyleSheet("font-size: 24px; font-weight: 900; color: white;")
        
        self.bulk_toolbar = QFrame(); self.bulk_toolbar.setVisible(False)
        self.bulk_toolbar.setStyleSheet(f"background: {PANEL_BG}; border-radius: 8px; border: 1px solid {DANGER_COLOR};")
        h_bulk = QHBoxLayout(self.bulk_toolbar); h_bulk.setContentsMargins(10, 5, 10, 5)
        self.lbl_sel_count = QLabel("0 انتخاب شده"); self.lbl_sel_count.setStyleSheet("color: white; font-weight: bold;")
        btn_bulk_del = QPushButton("حذف گروهی"); btn_bulk_del.setIcon(qta.icon('fa5s.trash', color=DANGER_COLOR))
        btn_bulk_del.setStyleSheet(f"background: transparent; border: 1px solid {DANGER_COLOR}; color: {DANGER_COLOR}; border-radius: 6px; padding: 5px;")
        btn_bulk_del.clicked.connect(self.delete_bulk_slot)
        h_bulk.addWidget(self.lbl_sel_count); h_bulk.addWidget(btn_bulk_del); h_bulk.addStretch()
        
        top_row.addWidget(lbl_title); top_row.addWidget(self.bulk_toolbar); top_row.addStretch()
        
        btn_import = QPushButton("ورودی اکسل"); btn_import.setIcon(qta.icon('fa5s.file-import', color='white')); btn_import.setStyleSheet(f"background: {INFO_COLOR}; color: white; border-radius: 6px; padding: 8px;")
        btn_import.clicked.connect(self.import_data_slot)
        btn_export = QPushButton("خروجی اکسل"); btn_export.setIcon(qta.icon('fa5s.file-excel', color='white')); btn_export.setStyleSheet(f"background: {SUCCESS_COLOR}; color: white; border-radius: 6px; padding: 8px;")
        btn_export.clicked.connect(self.export_data_slot)
        top_row.addWidget(btn_import); top_row.addWidget(btn_export)
        layout.addLayout(top_row)

        # جستجو و مرتب‌سازی
        search_box = QFrame(); search_box.setStyleSheet(f"background: {PANEL_BG}; border-radius: 12px; padding: 10px;")
        s_layout = QHBoxLayout(search_box)
        self.inp_search = QLineEdit(); self.inp_search.setPlaceholderText("🔍 جستجو...")
        self.inp_search.setStyleSheet(f"background: {BG_COLOR}; border: 1px solid {BORDER_COLOR}; padding: 10px; border-radius: 8px; color: white;")
        self.inp_search.returnPressed.connect(self.refresh_data_slot)
        
        self.cmb_cat_filter = QComboBox(); self.cmb_cat_filter.addItem("همه دسته‌ها", None)
        self.cmb_cat_filter.setStyleSheet(f"background: {BG_COLOR}; color: white; padding: 8px; border-radius: 8px;")
        
        # مرتب‌سازی (Sorting)
        self.cmb_sort = QComboBox()
        self.cmb_sort.addItems(["جدیدترین", "گران‌ترین", "ارزان‌ترین", "بیشترین موجودی", "کمترین موجودی"])
        self.cmb_sort.setStyleSheet(f"background: {BG_COLOR}; color: white; padding: 8px; border-radius: 8px;")
        self.cmb_sort.currentIndexChanged.connect(self.refresh_data_slot)
        
        btn_search = QPushButton("جستجو"); btn_search.setIcon(qta.icon('fa5s.search', color='white')); btn_search.clicked.connect(self.refresh_data_slot)
        btn_search.setStyleSheet(f"background: {ACCENT_COLOR}; color: white; border-radius: 8px; padding: 10px;")
        
        btn_add = QPushButton(" محصول جدید"); btn_add.setIcon(qta.icon('fa5s.plus', color='white'))
        btn_add.clicked.connect(lambda: self.open_editor_dialog(None))
        btn_add.setStyleSheet(f"background: {SUCCESS_COLOR}; color: white; border-radius: 8px; padding: 10px; font-weight: bold;")
        
        s_layout.addWidget(self.inp_search, 2); s_layout.addWidget(self.cmb_cat_filter, 1); s_layout.addWidget(self.cmb_sort, 1)
        s_layout.addWidget(btn_search); s_layout.addWidget(btn_add)
        layout.addWidget(search_box)

        # گرید
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("background: transparent; border: none;")
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll)
        
        # حالت خالی
        self.empty_state = QLabel()
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state.setText("📦 محصولی یافت نشد\nبرای شروع دکمه 'محصول جدید' را بزنید.")
        self.empty_state.setStyleSheet(f"color: {TEXT_SUB}; font-size: 14px; margin-top: 50px;")
        self.empty_state.setWordWrap(True)
        layout.addWidget(self.empty_state)
        self.empty_state.hide()
        
    def showEvent(self, event):
        super().showEvent(event)
        if not self._data_loaded:
            QTimer.singleShot(200, lambda: asyncio.create_task(self.refresh_data()))
            self._data_loaded = True 
            
    def open_editor_dialog(self, pid):
        dialog = ProductEditorDialog(self, pid)
        dialog.product_saved.connect(self.refresh_data_slot)
        dialog.exec()

    @asyncSlot()
    async def refresh_data_slot(self):
        try:
            await self.refresh_data()
        except RuntimeError:
            pass

    async def refresh_data(self):
        try:
            if not self.isVisible() or (hasattr(self.window(), '_is_shutting_down') and self.window()._is_shutting_down):
                return
            for i in reversed(range(self.grid_layout.count())):
                if self.grid_layout.itemAt(i).widget(): self.grid_layout.itemAt(i).widget().setParent(None)
        except RuntimeError:
            return
        self.selected_ids.clear(); self.update_bulk_toolbar()
        
        loop = asyncio.get_running_loop()
        try:
            def fetch():
                with next(get_db()) as db:
                    cats = crud.get_all_categories(db)
                    prods = crud.advanced_search_products(db, query=self.inp_search.text(), category_id=self.cmb_cat_filter.currentData())
                    
                    # اعمال مرتب‌سازی
                    sort_idx = self.cmb_sort.currentIndex()
                    if sort_idx == 1: prods.sort(key=lambda x: x.price, reverse=True) # گرانترین
                    elif sort_idx == 2: prods.sort(key=lambda x: x.price) # ارزانترین
                    elif sort_idx == 3: prods.sort(key=lambda x: x.stock, reverse=True) # بیشترین موجودی
                    elif sort_idx == 4: prods.sort(key=lambda x: x.stock) # کمترین موجودی
                    # 0 = جدیدترین (پیش‌فرض)
                    
                    return cats, prods
                    
            cats, prods = await loop.run_in_executor(None, fetch)
            
            current_cat = self.cmb_cat_filter.currentData()
            self.cmb_cat_filter.clear(); self.cmb_cat_filter.addItem("همه دسته‌ها", None)
            for c in cats: self.cmb_cat_filter.addItem(c.name, c.id)
            if current_cat:
                idx = self.cmb_cat_filter.findData(current_cat)
                if idx >= 0: self.cmb_cat_filter.setCurrentIndex(idx)
            
            if not prods:
                self.empty_state.show(); self.grid_container.hide()
            else:
                self.empty_state.hide(); self.grid_container.show()
                cols = max(1, self.grid_container.width() // 280)
                for i, p in enumerate(prods):
                    card = ProductCard(p, self)
                    card.selectionChanged.connect(self.on_card_selection)
                    card.quickUpdateRequested.connect(self.handle_quick_update)
                    self.grid_layout.addWidget(card, i // cols, i % cols)
                    
        except Exception as e: 
            logger.error(f"Refresh error: {e}")

    def handle_quick_update(self, pid, field, value):
        """آپدیت سریع بدون باز کردن دیالوگ"""
        asyncio.create_task(self._quick_update_db(pid, field, value))

    async def _quick_update_db(self, pid, field, value):
        loop = asyncio.get_running_loop()
        try:
            def update():
                with next(get_db()) as db:
                    p = crud.get_product(db, pid)
                    if p:
                        setattr(p, field, value)
                        db.commit()
            await loop.run_in_executor(None, update)
            self.window().show_toast("آپدیت شد.")
        except Exception as e:
            self.window().show_toast("خطا در آپدیت!", is_error=True)

    def on_card_selection(self, pid, selected):
        if selected: self.selected_ids.add(pid)
        else: self.selected_ids.discard(pid)
        self.update_bulk_toolbar()

    def update_bulk_toolbar(self):
        count = len(self.selected_ids)
        self.bulk_toolbar.setVisible(count > 0)
        self.lbl_sel_count.setText(f"{count} انتخاب شده")

    @asyncSlot()
    async def delete_product_single(self, pid):
        try:
            if QMessageBox.question(self, "حذف", "آیا مطمئن هستید؟") == QMessageBox.StandardButton.Yes:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, lambda: crud.delete_product(next(get_db()), pid))
                await self.refresh_data()
        except RuntimeError:
            pass

    @asyncSlot()
    async def duplicate_product(self, pid):
        try:
            if not self.isVisible(): return
        except RuntimeError: return
        loop = asyncio.get_running_loop()
        try:
            def db_op():
                with next(get_db()) as db:
                    p = crud.get_product(db, pid)
                    if not p: return
                    data = {c.name: getattr(p, c.name) for c in p.__table__.columns if c.name not in ['id', 'created_at', 'updated_at']}
                    data['name'] += " (کپی)"
                    data['stock'] = 0
                    vars = [{"name": v.name, "price_adjustment": v.price_adjustment, "stock": 0} for v in p.variants]
                    imgs = [img.image_path for img in p.images] if hasattr(p, 'images') else ([p.image_path] if p.image_path else [])
                    crud.create_product_with_variants(db, data, vars, image_paths=imgs)
            await loop.run_in_executor(None, db_op)
            self.window().show_toast("محصول تکثیر شد.")
            await self.refresh_data()
        except Exception as e:
            logger.error(e)

    @asyncSlot()
    async def delete_bulk_slot(self):
        try:
            if QMessageBox.question(self, "حذف گروهی", f"حذف {len(self.selected_ids)} محصول؟") == QMessageBox.StandardButton.Yes:
                ids = list(self.selected_ids)
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, lambda: crud.bulk_delete_products(next(get_db()), ids))
                await self.refresh_data()
        except RuntimeError:
            pass

    # Import/Export Logic (خلاصه شده)
    def export_data_slot(self):
        path, _ = QFileDialog.getSaveFileName(self, "ذخیره اکسل", "products.xlsx", "Excel (*.xlsx)")
        if path: asyncio.create_task(self._perform_export(path))

    async def _perform_export(self, path):
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, lambda: pd.DataFrame([{"ID": p.id, "Name": p.name} for p in crud.get_all_products_raw(next(get_db()))]).to_excel(path, index=False))
            self.window().show_toast("اکسل ذخیره شد.")
        except: pass

    def import_data_slot(self):
        path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل", "", "Excel (*.xlsx)")
        if path: asyncio.create_task(self._perform_import(path))

    async def _perform_import(self, path):
        try:
            loop = asyncio.get_running_loop()
            s, f = await loop.run_in_executor(None, lambda: self._do_import_logic(path))
            QMessageBox.information(self, "پایان", f"موفق: {s}\nناموفق: {f}")
            await self.refresh_data()
        except: pass

    def _do_import_logic(self, path):
        df = pd.read_excel(path).fillna("")
        s, f = 0, 0
        with next(get_db()) as db:
            for _, row in df.iterrows():
                try:
                    crud.create_product_with_variants(db, {"name": str(row.get("Name", "New")), "price": 0, "stock": 0}, [])
                    s += 1
                except: f += 1
        return s, f