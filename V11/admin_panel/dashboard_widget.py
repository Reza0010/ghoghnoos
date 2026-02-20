import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QPushButton, QGraphicsDropShadowEffect,
    QScrollArea, QTabWidget, QSizePolicy, QProgressBar, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, pyqtProperty, QRect
from PyQt6.QtGui import QColor, QFont, QPainter, QLinearGradient, QBrush, QPen, QTextDocument
from PyQt6.QtPrintSupport import QPrinter
from qasync import asyncSlot
import qtawesome as qta

# Matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties

# ابزارهای اصلاح فارسی
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_RTL_SUPPORT = True
except ImportError:
    HAS_RTL_SUPPORT = False

from config import BASE_DIR
from db.database import get_db
from db import crud, models
from sqlalchemy import func, desc

logger = logging.getLogger("Dashboard")

# --- رنگ‌ها ---
COLOR_BG = "#16161a"
COLOR_CARD = "#242629"
COLOR_PURPLE = "#7f5af0"
COLOR_GREEN = "#2cb67d"
COLOR_BLUE = "#3da9fc"
COLOR_RED = "#ef4565"
COLOR_YELLOW = "#fffffe"
COLOR_GRAY = "#94a1b2"

def farsi_text_for_chart(text):
    """مخصوص نمودارها: حروف را می‌چسباند و جهت را اصلاح می‌کند"""
    if not text: return ""
    if not HAS_RTL_SUPPORT: return str(text)
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

# ==============================================================================
# Canvas Chart (با رفع مشکل فونت)
# ==============================================================================
class ModernChart(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        self.persian_font = None
        font_path = Path(BASE_DIR) / "fonts" / "Vazirmatn.ttf"
        
        # --- رفع خطای Font not found ---
        if font_path.exists():
            try:
                # اضافه کردن فونت به کش متپلاتلیب
                fm.fontManager.addfont(str(font_path))
                # خواندن نام فونت از فایل
                self.persian_font = FontProperties(fname=str(font_path))
                # تنظیم فونت پیش‌فرض
                plt.rcParams['font.family'] = self.persian_font.get_name()
            except Exception as e:
                logger.error(f"Error loading font for chart: {e}")
        
        plt.rcParams.update({
            'axes.facecolor': COLOR_CARD,
            'figure.facecolor': COLOR_CARD,
            'text.color': COLOR_YELLOW,
            'axes.labelcolor': COLOR_GRAY,
            'xtick.color': COLOR_GRAY,
            'ytick.color': COLOR_GRAY,
            'grid.color': '#2d2e32',
        })
        
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor(COLOR_CARD)
        
        # حذف حاشیه‌های اضافی
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['left'].set_color('#333')
        self.axes.spines['bottom'].set_color('#333')
        
        super().__init__(self.fig)
        self.setParent(parent)
        self.fig.tight_layout()

# ==============================================================================
# Stat Card
# ==============================================================================
class StatCard(QFrame):
    def __init__(self, title, icon, color, parent=None):
        super().__init__(parent)
        self.setFixedHeight(130)
        self.setMinimumWidth(220)
        self.color = color
        self.setObjectName("StatCard")
        
        self.setStyleSheet(f"""
            QFrame#StatCard {{
                background-color: rgba(36, 38, 41, 0.9);
                border-radius: 15px;
                border: 1px solid #333;
            }}
            QFrame#StatCard:hover {{
                border: 1px solid {color};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25); shadow.setColor(QColor(0,0,0,120)); shadow.setOffset(0,8)
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        text_layout = QVBoxLayout()
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet(f"color: {COLOR_GRAY}; font-size: 13px;")
        
        self._value = 0
        self.lbl_value = QLabel("0")
        self.lbl_value.setStyleSheet(f"color: white; font-size: 28px; font-weight: 900;")
        
        self.lbl_trend = QLabel("")
        self.lbl_trend.setStyleSheet(f"color: {COLOR_GREEN}; font-size: 11px;")
        
        text_layout.addWidget(self.lbl_title)
        text_layout.addWidget(self.lbl_value)
        text_layout.addWidget(self.lbl_trend)
        text_layout.addStretch()
        
        layout.addLayout(text_layout)
        layout.addStretch()

        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(60, 60)
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_lbl.setStyleSheet(f"background: rgba(0,0,0,0.2); border-radius: 15px;")
        self.icon_lbl.setPixmap(qta.icon(icon, color=color).pixmap(35, 35))
        layout.addWidget(self.icon_lbl)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_count)

    def set_data(self, value, trend_val=None):
        self.target_value = value
        self.current_value = 0
        self.step = max(1, int(value / 30)) 
        self.anim_timer.start(15)
        
        if trend_val is not None:
            color = COLOR_GREEN if trend_val >= 0 else COLOR_RED
            sign = "↑" if trend_val >= 0 else "↓"
            self.lbl_trend.setText(f"{sign} {abs(trend_val)}% نسبت به دیروز")
            self.lbl_trend.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold;")

    def _update_count(self):
        if self.current_value < self.target_value:
            self.current_value += self.step
            if self.current_value > self.target_value:
                self.current_value = self.target_value
            text = f"{int(self.current_value):,}"
            self.lbl_value.setText(text)
        else:
            self.anim_timer.stop()

# ==============================================================================
# Stock Item
# ==============================================================================
class StockItem(QWidget):
    def __init__(self, name, stock, threshold=5):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(4)
        
        h_layout = QHBoxLayout()
        name_lbl = QLabel(f"📦 {name}")
        name_lbl.setStyleSheet("color: #e4e5f1; font-size: 12px; font-weight: bold;")
        
        count_lbl = QLabel(f"{stock} عدد")
        count_lbl.setStyleSheet("color: #fffffe; font-size: 12px;")
        
        h_layout.addWidget(name_lbl)
        h_layout.addStretch()
        h_layout.addWidget(count_lbl)
        layout.addLayout(h_layout)
        
        progress = QProgressBar()
        progress.setFixedHeight(6)
        progress.setTextVisible(False)
        progress.setStyleSheet("background: #1e1e24; border-radius: 3px;")
        
        max_val = max(threshold * 2, stock + 5) 
        percent = int((stock / max_val) * 100)
        progress.setValue(percent)
        
        bar_color = COLOR_GREEN
        if stock <= 2: bar_color = COLOR_RED
        elif stock <= 5: bar_color = "#ffc857"
        
        progress.setStyleSheet(f"""
            QProgressBar {{ background: #2e2e38; border-radius: 3px; }}
            QProgressBar::chunk {{ background-color: {bar_color}; border-radius: 3px; }}
        """)
        
        layout.addWidget(progress)

# ==============================================================================
# Activity Item
# ==============================================================================
class ActivityItem(QFrame):
    def __init__(self, text, time_str, platform, amount=None):
        super().__init__()
        color = COLOR_BLUE if platform == 'telegram' else COLOR_PURPLE
        icon = 'fa5b.telegram' if platform == 'telegram' else 'mdi6.infinity'
        
        self.setStyleSheet(f"background: transparent; border-bottom: 1px solid #2e2e38; padding: 5px;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 8, 5, 8)
        
        ico = QLabel()
        ico.setPixmap(qta.icon(icon, color=color).pixmap(24, 24))
        
        text_layout = QVBoxLayout()
        txt = QLabel(text)
        txt.setStyleSheet("color: #fffffe; font-size: 13px;")
        
        info_row = QHBoxLayout()
        info_row.addWidget(txt)
        info_row.addStretch()
        if amount:
            amt_lbl = QLabel(f"{int(amount):,} تومان")
            amt_lbl.setStyleSheet(f"color: {COLOR_GREEN}; font-size: 11px;")
            info_row.addWidget(amt_lbl)
            
        text_layout.addLayout(info_row)
        
        tim = QLabel(time_str)
        tim.setStyleSheet(f"color: {COLOR_GRAY}; font-size: 10px;")
        text_layout.addWidget(tim)
        
        layout.addWidget(ico)
        layout.addLayout(text_layout)

# ==============================================================================
# Dashboard Widget
# ==============================================================================
class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._data_loaded = False
        self.setup_ui()
        
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(300000)

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(25)

        # هدر
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        main_title = QLabel("داشبورد مانیتورینگ")
        main_title.setStyleSheet("font-size: 28px; font-weight: 900; color: white;")
        
        self.lbl_status = QLabel("آخرین بروزرسانی: --:--")
        self.lbl_status.setStyleSheet(f"color: {COLOR_GRAY}; font-size: 13px;")
        
        title_box.addWidget(main_title); title_box.addWidget(self.lbl_status)
        header.addLayout(title_box)
        header.addStretch()

        self.btn_status = QPushButton()
        self.btn_status.setCheckable(True)
        self.btn_status.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_status.clicked.connect(self.toggle_shop_status)
        header.addWidget(self.btn_status)

        self.btn_report = QPushButton(" گزارش پیشرفته")
        self.btn_report.setIcon(qta.icon('fa5s.file-pdf', color='white'))
        self.btn_report.setStyleSheet(f"background: {COLOR_CARD}; border: 1px solid {COLOR_PURPLE}; border-radius: 10px; padding: 8px 15px; color: white; font-weight: bold;")
        self.btn_report.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_report.clicked.connect(self.generate_sales_report)
        header.addWidget(self.btn_report)

        self.btn_refresh = QPushButton()
        self.btn_refresh.setFixedSize(45, 45)
        self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='white'))
        self.btn_refresh.setStyleSheet(f"background: {COLOR_CARD}; border: 1px solid #333; border-radius: 12px;")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.refresh_data)
        header.addWidget(self.btn_refresh)
        
        self.main_layout.addLayout(header)

        # کارت‌های آمار
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        
        self.card_rev_tg = StatCard("درآمد تلگرام", "fa5b.telegram", COLOR_BLUE)
        self.card_rev_rb = StatCard("درآمد روبیکا", "fa5s.rocket", COLOR_PURPLE)
        self.card_orders = StatCard("سفارشات جدید", "fa5s.shopping-cart", COLOR_GREEN)
        self.card_users = StatCard("مشتریان کل", "fa5s.users", COLOR_BLUE)
        
        stats_layout.addWidget(self.card_rev_tg, 0, 0)
        stats_layout.addWidget(self.card_rev_rb, 0, 1)
        stats_layout.addWidget(self.card_orders, 0, 2)
        stats_layout.addWidget(self.card_users, 0, 3)
        self.main_layout.addLayout(stats_layout)

        # نمودارها
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid #333; border-radius: 15px; background: {COLOR_CARD}; }}
            QTabBar::tab {{ background: #1c1e22; color: {COLOR_GRAY}; padding: 12px 30px; font-weight: bold; border-top-left-radius: 10px; border-top-right-radius: 10px; margin-right: 2px;}}
            QTabBar::tab:selected {{ background: {COLOR_CARD}; color: {COLOR_PURPLE}; border-bottom: 3px solid {COLOR_PURPLE}; }}
        """)
        
        self.chart_tg = ModernChart()
        self.chart_rb = ModernChart()
        self.tabs.addTab(self.chart_tg, "نمودار فروش تلگرام")
        self.tabs.addTab(self.chart_rb, "نمودار فروش روبیکا")
        self.main_layout.addWidget(self.tabs, 3)

        # بخش پایین
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)

        # فعالیت‌ها
        act_frame = QFrame()
        act_frame.setStyleSheet(f"background: {COLOR_CARD}; border-radius: 15px; border: 1px solid #333;")
        act_lay = QVBoxLayout(act_frame)
        act_header = QLabel("🔔 آخرین فعالیت‌ها")
        act_header.setStyleSheet("color: white; font-weight: bold; margin-bottom: 5px; font-size: 15px;")
        act_lay.addWidget(act_header)
        
        self.scroll_act = QScrollArea()
        self.scroll_act.setWidgetResizable(True)
        self.scroll_act.setStyleSheet("border: none; background: transparent;")
        self.act_container = QWidget()
        self.act_vbox = QVBoxLayout(self.act_container)
        self.act_vbox.addStretch()
        self.scroll_act.setWidget(self.act_container)
        act_lay.addWidget(self.scroll_act)
        bottom_row.addWidget(act_frame, 2)

        # موجودی
        stock_frame = QFrame()
        stock_frame.setFixedWidth(400)
        stock_frame.setStyleSheet(f"background: {COLOR_CARD}; border-radius: 15px; border: 1px solid #333;")
        stock_lay = QVBoxLayout(stock_frame)
        stock_header = QLabel("⚠️ وضعیت موجودی انبار")
        stock_header.setStyleSheet(f"color: {COLOR_RED}; font-weight: bold; font-size: 15px;")
        stock_lay.addWidget(stock_header)
        
        self.stock_list_lay = QVBoxLayout()
        self.stock_list_lay.setSpacing(10)
        stock_lay.addLayout(self.stock_list_lay)
        stock_lay.addStretch()
        bottom_row.addWidget(stock_frame)

        self.main_layout.addLayout(bottom_row, 2)

        # فوتر سیستم
        footer = QHBoxLayout()
        self.lbl_system = QLabel("🚀 سیستم آماده است | نسخه 11.0.1")
        self.lbl_system.setStyleSheet(f"color: {COLOR_GRAY}; font-size: 11px;")
        footer.addStretch()
        footer.addWidget(self.lbl_system)
        self.main_layout.addLayout(footer)

    def showEvent(self, event):
        if not self._data_loaded:
            QTimer.singleShot(300, self.refresh_data)
            self._data_loaded = True

    @asyncSlot()
    async def refresh_data(self):
        self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='white', animation=qta.Spin(self.btn_refresh)))
        loop = asyncio.get_running_loop()
        
        try:
            def fetch_all():
                with next(get_db()) as db:
                    # داده‌های آماری
                    rev_tg = crud.get_total_revenue_by_platform(db, "telegram")
                    rev_rb = crud.get_total_revenue_by_platform(db, "rubika")
                    pending_orders = db.query(models.Order).filter(models.Order.status == 'pending_payment').count()
                    total_users = db.query(models.User).count()
                    
                    # داده‌های نمودار
                    end_date = datetime.now()
                    dates = [(end_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
                    
                    def get_plat_data(plat):
                        res = db.query(func.date(models.Order.created_at), func.sum(models.Order.total_amount))\
                            .join(models.User).filter(models.User.platform == plat)\
                            .filter(models.Order.status.in_(['approved', 'shipped', 'paid']))\
                            .filter(models.Order.created_at >= (end_date - timedelta(days=7)))\
                            .group_by(func.date(models.Order.created_at)).all()
                        v_map = {r[0]: float(r[1]) for r in res if r[0]}
                        return [v_map.get(d, 0) for d in dates]

                    tg_sales = get_plat_data('telegram')
                    rb_sales = get_plat_data('rubika')
                    
                    # موجودی کم
                    low_stock = db.query(models.Product).filter(models.Product.stock < 10).limit(5).all()
                    
                    # فعالیت‌ها
                    recent_orders = db.query(models.Order).order_by(models.Order.created_at.desc()).limit(5).all()
                    is_open = crud.get_setting(db, "tg_is_open", "true") == "true"
                    
                    return {
                        "rev_tg": rev_tg, "rev_rb": rev_rb, "pending": pending_orders, "users": total_users,
                        "dates": dates, "tg_sales": tg_sales, "rb_sales": rb_sales,
                        "low_stock": low_stock, "recent_orders": recent_orders, "is_open": is_open
                    }

            data = await loop.run_in_executor(None, fetch_all)
            
            # آپدیت کارت‌ها
            self.card_rev_tg.set_data(int(data['rev_tg']))
            self.card_rev_rb.set_data(int(data['rev_rb']))
            self.card_orders.set_data(data['pending'])
            self.card_users.set_data(data['users'])
            
            # آپدیت نمودارها
            self.update_chart(self.chart_tg, data['dates'], data['tg_sales'], COLOR_BLUE)
            self.update_chart(self.chart_rb, data['dates'], data['rb_sales'], COLOR_PURPLE)
            
            # آپدیت فعالیت‌ها
            for i in reversed(range(self.act_vbox.count() - 1)):
                self.act_vbox.itemAt(i).widget().deleteLater()
            
            if not data['recent_orders']:
                empty_lbl = QLabel("فعالیتی ثبت نشده")
                empty_lbl.setStyleSheet("color: #555; padding: 10px;")
                empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.act_vbox.insertWidget(0, empty_lbl)
            else:
                for o in data['recent_orders']:
                    if not o.user: continue
                    msg = f"سفارش #{o.id} توسط {o.user.full_name}"
                    time_str = o.created_at.strftime("%H:%M")
                    self.act_vbox.insertWidget(0, ActivityItem(msg, time_str, o.user.platform, o.total_amount))

            # آپدیت موجودی
            for i in reversed(range(self.stock_list_lay.count())):
                self.stock_list_lay.itemAt(i).widget().deleteLater()
                
            if not data['low_stock']:
                empty_lbl = QLabel("✅ موجودی انبار مناسب است")
                empty_lbl.setStyleSheet("color: #2cb67d; font-size: 12px; padding: 10px;")
                self.stock_list_lay.addWidget(empty_lbl)
            else:
                for p in data['low_stock']:
                    item = StockItem(p.name, p.stock)
                    self.stock_list_lay.addWidget(item)

            self.update_shop_status_btn(data['is_open'])
            self.lbl_status.setText(f"آخرین بروزرسانی: {datetime.now().strftime('%H:%M:%S')}")

        except Exception as e:
            logger.error(f"Dashboard Update Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='white'))

    def update_chart(self, canvas, dates, values, color):
        ax = canvas.axes
        ax.clear()
        
        # تبدیل تاریخ برای نمایش صحیح در نمودار
        short_dates = [farsi_text_for_chart(d[5:].replace('-', '/')) for d in dates]
        
        ax.plot(short_dates, values, color=color, marker='o', linewidth=3, markersize=8, markerfacecolor=COLOR_BG, markeredgewidth=2, markeredgecolor=color)
        ax.fill_between(short_dates, values, color=color, alpha=0.1)
        
        ax.set_ylim(0, max(values) * 1.2 if any(values) else 100)
        ax.grid(True, axis='y', linestyle='--', alpha=0.1)
        
        # اعمال فونت فارسی روی محور افقی
        if canvas.persian_font:
            for label in ax.get_xticklabels():
                label.set_fontproperties(canvas.persian_font)
        canvas.draw()

    def update_shop_status_btn(self, is_open):
        self.btn_status.setChecked(is_open)
        text = "🟢 فروشگاه باز است" if is_open else "🔴 فروشگاه بسته است"
        bg = COLOR_GREEN if is_open else COLOR_RED
        self.btn_status.setText(text)
        self.btn_status.setStyleSheet(f"""
            QPushButton {{
                background: {bg}; color: white; border-radius: 10px;
                padding: 10px 20px; font-weight: bold; font-size: 14px;
            }}
        """)

    @asyncSlot()
    async def toggle_shop_status(self):
        new_status = "true" if self.btn_status.isChecked() else "false"
        await asyncio.get_running_loop().run_in_executor(
            None, lambda: crud.set_setting(next(get_db()), "tg_is_open", new_status)
        )
        self.refresh_data()

    @asyncSlot()
    async def generate_sales_report(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "ذخیره گزارش مالی", "Sales_Report.pdf", "PDF Files (*.pdf)")
        if not file_path: return

        loop = asyncio.get_running_loop()
        try:
            def fetch_report_data():
                with next(get_db()) as db:
                    total_rev = crud.get_total_revenue_by_platform(db, "telegram") + crud.get_total_revenue_by_platform(db, "rubika")
                    total_orders = db.query(models.Order).count()
                    top_prods = db.query(models.Product.name, func.sum(models.OrderItem.quantity))\
                        .join(models.OrderItem).group_by(models.Product.id)\
                        .order_by(desc(func.sum(models.OrderItem.quantity))).limit(10).all()
                    return total_rev, total_orders, top_prods

            rev, count, prods = await loop.run_in_executor(None, fetch_report_data)

            html = f"""
            <div dir='rtl' style='font-family: Tahoma;'>
            <h1 style='text-align: center; color: #7f5af0;'>گزارش عملکرد فروشگاه ققنوس</h1>
            <p style='text-align: left;'>تاریخ گزارش: {datetime.now().strftime('%Y/%m/%d')}</p>
            <hr>
            <h3>📊 آمار کلی:</h3>
            <table width='100%' border='1' cellpadding='10' style='border-collapse: collapse; border: 1px solid #ddd;'>
                <tr style='background: #f9f9f9;'><th>کل درآمد تایید شده</th><td>{int(rev):,} تومان</td></tr>
                <tr><th>تعداد کل سفارشات ثبت شده</th><td>{count} عدد</td></tr>
            </table>
            <br>
            <h3>🏆 ۱۰ محصول پرفروش:</h3>
            <table width='100%' border='1' cellpadding='5' style='border-collapse: collapse; border: 1px solid #ddd;'>
                <tr style='background: #7f5af0; color: white;'><th>نام محصول</th><th>تعداد فروش</th></tr>
            """
            for p_name, p_qty in prods:
                html += f"<tr><td>{p_name}</td><td style='text-align: center;'>{p_qty}</td></tr>"
            html += "</table></div>"

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)

            doc = QTextDocument()
            font_path = Path(BASE_DIR) / "fonts" / "Vazirmatn.ttf"
            if font_path.exists(): doc.setDefaultFont(QFont("Vazirmatn", 10))
            doc.setHtml(html)
            doc.print(printer)

            if hasattr(self.window(), 'show_toast'): self.window().show_toast("گزارش مالی با موفقیت ایجاد شد.")
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در تولید گزارش: {e}")