import asyncio
import logging
from typing import List, Tuple, Optional, Dict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QTreeWidget, QTreeWidgetItem, QLineEdit, QLabel, QFrame, 
    QSplitter, QComboBox, QSizePolicy, QGraphicsDropShadowEffect,
    QMenu
)
from PyQt6.QtGui import QColor, QFont, QIcon, QAction
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSlot, QPoint
from qasync import asyncSlot
import qtawesome as qta

from db import crud
from db.database import get_db

logger = logging.getLogger("CategoriesWidget")

# --- پالت رنگی ---
BG_COLOR = "#16161a"
PANEL_BG = "#242629"
ACCENT_COLOR = "#7f5af0"
SUCCESS_COLOR = "#2cb67d"
WARNING_COLOR = "#f39c12"
DANGER_COLOR = "#ef4565"
TEXT_COLOR = "#fffffe"
HINT_COLOR = "#94a1b2"

class CategoriesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.selected_cat_id: Optional[int] = None
        self.all_categories_cache = [] 
        
        self.setup_ui()
        self._data_loaded = False

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(0)
        self.splitter.setStyleSheet(f"QSplitter::handle {{ background-color: transparent; }}")

        # ==================== بخش ۱: لیست درختی ====================
        tree_container = QFrame()
        tree_container.setObjectName("card")
        tree_container.setStyleSheet(f"QFrame#card {{ background-color: {PANEL_BG}; border-radius: 15px; border: 1px solid #2e2e38; }}")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20); shadow.setColor(QColor(0, 0, 0, 50)); shadow.setOffset(0, 4)
        tree_container.setGraphicsEffect(shadow)

        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(15, 15, 15, 15)
        tree_layout.setSpacing(15)
        
        # --- هدر لیست ---
        header_lay = QHBoxLayout()
        lbl_list = QLabel("🏗 مدیریت دسته‌بندی‌ها")
        lbl_list.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold; font-size: 16px;")
        
        # دکمه‌های کنترلی بالا
        btn_actions_lay = QHBoxLayout()
        btn_actions_lay.setSpacing(5)
        
        self.btn_new_root = QPushButton()
        self.btn_new_root.setToolTip("افزودن دسته اصلی")
        self.btn_new_root.setFixedSize(32, 32)
        self.btn_new_root.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_root.setIcon(qta.icon("fa5s.plus", color=TEXT_COLOR))
        self.btn_new_root.setStyleSheet(f"QPushButton {{ background: {ACCENT_COLOR}; border-radius: 6px; }} QPushButton:hover {{ background: #6246ea; }}")
        self.btn_new_root.clicked.connect(self.reset_form)
        
        self.btn_expand = QPushButton()
        self.btn_expand.setToolTip("باز کردن همه")
        self.btn_expand.setFixedSize(32, 32)
        self.btn_expand.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_expand.setIcon(qta.icon("fa5s.expand-alt", color=HINT_COLOR))
        self.btn_expand.setStyleSheet(f"QPushButton {{ background: transparent; border: 1px solid #3a3a4e; border-radius: 6px; }} QPushButton:hover {{ background: #3a3a4e; }}")
        # اتصال بعداً انجام می‌شود

        self.btn_collapse = QPushButton()
        self.btn_collapse.setToolTip("بستن همه")
        self.btn_collapse.setFixedSize(32, 32)
        self.btn_collapse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_collapse.setIcon(qta.icon("fa5s.compress-alt", color=HINT_COLOR))
        self.btn_collapse.setStyleSheet(f"QPushButton {{ background: transparent; border: 1px solid #3a3a4e; border-radius: 6px; }} QPushButton:hover {{ background: #3a3a4e; }}")
        # اتصال بعداً انجام می‌شود

        btn_actions_lay.addWidget(self.btn_expand)
        btn_actions_lay.addWidget(self.btn_collapse)
        btn_actions_lay.addWidget(self.btn_new_root)

        header_lay.addWidget(lbl_list)
        header_lay.addStretch()
        header_lay.addLayout(btn_actions_lay)
        tree_layout.addLayout(header_lay)

        # --- جستجو ---
        self.search_inp = QLineEdit()
        self.search_inp.setPlaceholderText("🔍 جستجو در دسته‌ها...")
        self.search_inp.textChanged.connect(self.filter_tree)
        self.search_inp.setStyleSheet(f"""
            QLineEdit {{ background: {BG_COLOR}; border: 1px solid #3a3a4e; padding: 10px; border-radius: 10px; color: {TEXT_COLOR}; }}
            QLineEdit:focus {{ border: 1px solid {ACCENT_COLOR}; }}
        """)
        tree_layout.addWidget(self.search_inp)

        # --- تعریف درخت (اینجا منتقل شد) ---
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(20)
        self.tree.setAnimated(True)
        self.tree.setVerticalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        self.tree.setStyleSheet(f"""
            QTreeWidget {{ background-color: transparent; border: none; color: {TEXT_COLOR}; font-size: 14px; outline: none; }}
            QTreeWidget::item {{ padding: 10px; border-radius: 8px; margin-bottom: 2px; }}
            QTreeWidget::item:hover {{ background-color: #2d2e32; }}
            QTreeWidget::item:selected {{ background-color: {ACCENT_COLOR}20; border: 1px solid {ACCENT_COLOR}; color: {TEXT_COLOR}; }}
        """)
        
        # --- اتصال سیگنال‌های دکمه‌ها (بعد از تعریف tree) ---
        self.btn_expand.clicked.connect(self.tree.expandAll)
        self.btn_collapse.clicked.connect(self.tree.collapseAll)
        
        tree_layout.addWidget(self.tree)

        # --- حالت خالی (Empty State) ---
        self.empty_state = QLabel()
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state.setText("📂 هنوز دسته‌بندی وجود ندارد\nبرای شروع دکمه بعلاوه را بزنید")
        self.empty_state.setStyleSheet(f"color: {HINT_COLOR}; font-size: 13px; padding: 50px;")
        self.empty_state.setWordWrap(True)
        tree_layout.addWidget(self.empty_state)
        self.empty_state.hide()

        # ==================== بخش ۲: فرم ====================
        self.form_panel = QFrame()
        self.form_panel.setObjectName("card")
        self.form_panel.setStyleSheet(f"QFrame#card {{ background-color: {PANEL_BG}; border-radius: 15px; border: 1px solid #2e2e38; }}")
        self.form_panel.setFixedWidth(350)
        
        shadow_form = QGraphicsDropShadowEffect()
        shadow_form.setBlurRadius(20); shadow_form.setColor(QColor(0, 0, 0, 50)); shadow_form.setOffset(0, 4)
        self.form_panel.setGraphicsEffect(shadow_form)
        
        form_layout = QVBoxLayout(self.form_panel)
        form_layout.setContentsMargins(25, 30, 25, 30)
        form_layout.setSpacing(20)

        form_header = QVBoxLayout()
        self.lbl_form_icon = QLabel()
        self.lbl_form_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_form_icon.setFixedSize(70, 70)
        self.lbl_form_icon.setStyleSheet(f"background: {ACCENT_COLOR}15; border-radius: 35px;")
        self.lbl_form_icon.setPixmap(qta.icon('fa5s.folder-plus', color=ACCENT_COLOR).pixmap(35, 35))
        
        self.lbl_form_title = QLabel("دسته جدید")
        self.lbl_form_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_form_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        
        form_header.addWidget(self.lbl_form_icon)
        form_header.addWidget(self.lbl_form_title)
        form_layout.addLayout(form_header)

        name_lbl = QLabel("نام دسته‌بندی")
        name_lbl.setStyleSheet(f"color: {HINT_COLOR}; font-size: 12px;")
        form_layout.addWidget(name_lbl)
        
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("مثلاً: لوازم جانبی موبایل")
        self.inp_name.setStyleSheet(f"QLineEdit {{ background: {BG_COLOR}; padding: 12px; border-radius: 10px; color: {TEXT_COLOR}; border: 1px solid #4a4a5e; }} QLineEdit:focus {{ border: 1px solid {ACCENT_COLOR}; }}")
        form_layout.addWidget(self.inp_name)

        parent_lbl = QLabel("انتخاب والد")
        parent_lbl.setStyleSheet(f"color: {HINT_COLOR}; font-size: 12px;")
        form_layout.addWidget(parent_lbl)
        
        self.cmb_parent = QComboBox()
        self.cmb_parent.setStyleSheet(f"""
            QComboBox {{ background: {BG_COLOR}; padding: 10px; border-radius: 10px; color: {TEXT_COLOR}; border: 1px solid #4a4a5e; }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QComboBox QAbstractItemView {{ background: {PANEL_BG}; selection-background-color: {ACCENT_COLOR}; color: {TEXT_COLOR}; border-radius: 5px; }}
        """)
        form_layout.addWidget(self.cmb_parent)

        form_layout.addStretch()

        # دکمه افزودن زیرمجموعه
        self.btn_add_child = QPushButton("➕ افزودن زیرمجموعه")
        self.btn_add_child.setObjectName("secondary_btn")
        self.btn_add_child.setFixedHeight(40)
        self.btn_add_child.clicked.connect(self.add_child_category)
        self.btn_add_child.setStyleSheet(f"""
             QPushButton {{
                background: transparent; color: {ACCENT_COLOR};
                border: 1px solid {ACCENT_COLOR}; border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: rgba(127, 90, 240, 0.1); }}
        """)
        self.btn_add_child.hide()
        form_layout.addWidget(self.btn_add_child)

        # دکمه ذخیره
        self.btn_save = QPushButton("💾 ذخیره")
        self.btn_save.setFixedHeight(45)
        self.btn_save.clicked.connect(self.save_category)
        self.btn_save.setStyleSheet(f"QPushButton {{ background: {SUCCESS_COLOR}; color: white; border-radius: 10px; font-weight: bold; }} QPushButton:hover {{ background: #25a06c; }}")
        form_layout.addWidget(self.btn_save)

        # دکمه حذف
        self.btn_delete = QPushButton("🗑 حذف")
        self.btn_delete.setFixedHeight(45)
        self.btn_delete.clicked.connect(self.delete_category)
        self.btn_delete.setStyleSheet(f"QPushButton {{ background: transparent; color: {DANGER_COLOR}; border: 1px solid {DANGER_COLOR}; border-radius: 10px; font-weight: bold; }} QPushButton:hover {{ background: {DANGER_COLOR}; color: white; }}")
        self.btn_delete.hide()
        form_layout.addWidget(self.btn_delete)

        self.splitter.addWidget(tree_container)
        self.splitter.addWidget(self.form_panel)
        self.splitter.setSizes([600, 400])
        
        main_layout.addWidget(self.splitter)

    # --- توابع ---

    def show_context_menu(self, position: QPoint):
        """منوی راست‌کلیک"""
        item = self.tree.itemAt(position)
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background-color: {PANEL_BG}; color: {TEXT_COLOR}; border: 1px solid #4a4a5e; border-radius: 8px; padding: 5px; }}
            QMenu::item {{ padding: 8px 25px; border-radius: 5px; }}
            QMenu::item:selected {{ background-color: {ACCENT_COLOR}; }}
        """)
        
        if item:
            edit_action = QAction(qta.icon("fa5s.edit", color=WARNING_COLOR), "ویرایش", self)
            edit_action.triggered.connect(lambda: self.on_item_clicked(item))
            
            add_child_action = QAction(qta.icon("fa5s.plus", color=SUCCESS_COLOR), "افزودن زیرمجموعه", self)
            add_child_action.triggered.connect(lambda: self.add_child_category_context(item))
            
            delete_action = QAction(qta.icon("fa5s.trash", color=DANGER_COLOR), "حذف", self)
            delete_action.triggered.connect(self.delete_category)
            
            menu.addAction(edit_action)
            menu.addAction(add_child_action)
            menu.addSeparator()
            menu.addAction(delete_action)
        else:
            new_root_action = QAction(qta.icon("fa5s.folder-plus", color=ACCENT_COLOR), "افزودن دسته اصلی", self)
            new_root_action.triggered.connect(self.reset_form)
            menu.addAction(new_root_action)
            
        menu.exec(self.tree.viewport().mapToGlobal(position))

    def add_child_category_context(self, parent_item):
        self.on_item_clicked(parent_item)
        self.add_child_category()

    def add_child_category(self):
        if not self.selected_cat_id: return
        parent_name = self.inp_name.text()
        self.selected_cat_id = None 
        self.lbl_form_title.setText(f"زیرمجموعه جدید برای '{parent_name}'")
        self.lbl_form_icon.setStyleSheet(f"background: {SUCCESS_COLOR}15; border-radius: 35px;")
        self.lbl_form_icon.setPixmap(qta.icon('fa5s.sitemap', color=SUCCESS_COLOR).pixmap(30, 30))
        self.inp_name.clear()
        self.inp_name.setFocus()
        self.btn_save.setText("💾 ذخیره زیرمجموعه")
        self.btn_save.setStyleSheet(f"QPushButton {{ background: {SUCCESS_COLOR}; color: white; border-radius: 10px; font-weight: bold; }} QPushButton:hover {{ background: #25a06c; }}")
        self.btn_delete.hide()
        self.btn_add_child.hide()

    def showEvent(self, event):
        if not self._data_loaded:
            QTimer.singleShot(100, self.refresh_data)
            self._data_loaded = True

    @asyncSlot()
    async def refresh_data(self):
        self.tree.clear()
        loop = asyncio.get_running_loop()
        try:
            def fetch():
                with next(get_db()) as db:
                    return crud.get_categories_with_counts(db)
            
            data = await loop.run_in_executor(None, fetch)
            self.all_categories_cache = data
            
            if not data:
                self.empty_state.show()
                self.tree.hide()
            else:
                self.empty_state.hide()
                self.tree.show()
            
            self._update_parent_combo()

            items_map = {}
            for cat, count in data:
                display_text = f"{cat.name} ({count})" if count > 0 else cat.name
                item = QTreeWidgetItem([display_text])
                item.setData(0, Qt.ItemDataRole.UserRole, cat.id)
                item.setData(0, Qt.ItemDataRole.UserRole + 1, cat.parent_id)
                
                icon_color = SUCCESS_COLOR if count > 0 else HINT_COLOR
                item.setIcon(0, qta.icon('fa5s.folder', color=icon_color))
                
                items_map[cat.id] = item

            for cat, _ in data:
                item = items_map[cat.id]
                if cat.parent_id and cat.parent_id in items_map:
                    items_map[cat.parent_id].addChild(item)
                    items_map[cat.parent_id].setExpanded(True)
                else:
                    self.tree.addTopLevelItem(item)

        except Exception as e:
            logger.error(f"Refresh Categories Error: {e}")

    def _update_parent_combo(self, exclude_id=None):
        self.cmb_parent.clear()
        self.cmb_parent.addItem("بدون والد (دسته اصلی)", None)
        for cat, _ in self.all_categories_cache:
            if exclude_id and cat.id == exclude_id:
                continue
            self.cmb_parent.addItem(cat.name, cat.id)

    def on_item_clicked(self, item):
        cid = item.data(0, Qt.ItemDataRole.UserRole)
        pid = item.data(0, Qt.ItemDataRole.UserRole + 1)
        clean_name = item.text(0).split(" (")[0]
        
        self.selected_cat_id = cid
        self.inp_name.setText(clean_name)
        self._update_parent_combo(exclude_id=cid)
        
        idx = self.cmb_parent.findData(pid)
        self.cmb_parent.setCurrentIndex(max(0, idx))

        self.lbl_form_title.setText("ویرایش دسته")
        self.lbl_form_icon.setStyleSheet(f"background: {WARNING_COLOR}15; border-radius: 35px;")
        self.lbl_form_icon.setPixmap(qta.icon('fa5s.edit', color=WARNING_COLOR).pixmap(30, 30))
        
        self.btn_save.setText("✏️ بروزرسانی")
        self.btn_save.setStyleSheet(f"QPushButton {{ background: {WARNING_COLOR}; color: white; border-radius: 10px; font-weight: bold; }} QPushButton:hover {{ background: #d68910; }}")
        
        self.btn_delete.show()
        self.btn_add_child.show()

    def reset_form(self):
        self.selected_cat_id = None
        self.tree.clearSelection()
        self.inp_name.clear()
        self._update_parent_combo()
        
        self.lbl_form_title.setText("دسته جدید")
        self.lbl_form_icon.setStyleSheet(f"background: {ACCENT_COLOR}15; border-radius: 35px;")
        self.lbl_form_icon.setPixmap(qta.icon('fa5s.folder-plus', color=ACCENT_COLOR).pixmap(30, 30))
        
        self.btn_save.setText("💾 ذخیره")
        self.btn_save.setStyleSheet(f"QPushButton {{ background: {SUCCESS_COLOR}; color: white; border-radius: 10px; font-weight: bold; }} QPushButton:hover {{ background: #25a06c; }}")
        
        self.btn_delete.hide()
        self.btn_add_child.hide()
        self.inp_name.setFocus()

    def filter_tree(self, text):
        def search(item):
            found = text.lower() in item.text(0).lower()
            item.setHidden(not found)
            for i in range(item.childCount()):
                if search(item.child(i)):
                    item.setHidden(False)
                    found = True
            return found

        for i in range(self.tree.topLevelItemCount()):
            search(self.tree.topLevelItem(i))

    @asyncSlot()
    async def save_category(self):
        name = self.inp_name.text().strip()
        if not name:
            return QMessageBox.warning(self, "خطا", "نام دسته‌بندی الزامی است.")

        pid = self.cmb_parent.currentData()
        loop = asyncio.get_running_loop()
        try:
            def db_op():
                with next(get_db()) as db:
                    if self.selected_cat_id:
                        return crud.update_category(db, self.selected_cat_id, name, pid)
                    else:
                        return crud.create_category(db, name, pid)
            
            await loop.run_in_executor(None, db_op)
            await self.refresh_data()
            self.reset_form()
            if hasattr(self.window(), 'show_toast'):
                self.window().show_toast("✅ عملیات با موفقیت انجام شد.")

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره‌سازی: {e}")

    @asyncSlot()
    async def delete_category(self):
        if not self.selected_cat_id: return
        
        msg = "آیا از حذف این دسته مطمئن هستید؟\n(کالاهای زیرمجموعه حذف نخواهند شد)"
        if QMessageBox.question(self, "تایید", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            try:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, lambda: crud.delete_category(next(get_db()), self.selected_cat_id))
                await self.refresh_data()
                self.reset_form()
                if hasattr(self.window(), 'show_toast'):
                    self.window().show_toast("🗑 دسته حذف شد.", is_error=True)
            except Exception as e:
                logger.error(f"Delete Error: {e}")