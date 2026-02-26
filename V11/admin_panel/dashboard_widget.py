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

class ModernPieChart(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=3, height=3, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor(COLOR_CARD)

        super().__init__(self.fig)
        self.setParent(parent)
        self.fig.tight_layout()

# ==============================================================================
# Stat Card
# ==============================================================================
class TopProductItem(QWidget):
    def __init__(self, name, sales_count, total_revenue):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        icon_lbl = QLabel("🔥")
        icon_lbl.setFixedWidth(25)

        v_box = QVBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")

        info_lbl = QLabel(f"{sales_count} فروش | {int(total_revenue):,} تومان")
        info_lbl.setStyleSheet(f"color: {COLOR_GRAY}; font-size: 10px;")

        v_box.addWidget(name_lbl)
        v_box.addWidget(info_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(v_box)
        layout.addStretch()

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

    def set_data(self, value, trend_val=None, trend_label="نسبت به دیروز"):
        self.target_value = value
        self.current_value = 0
        self.step = max(1, int(value / 30)) 
        self.anim_timer.start(15)
        
        if trend_val is not None:
            color = COLOR_GREEN if trend_val >= 0 else COLOR_RED
            sign = "↑" if trend_val >= 0 else "↓"
            self.lbl_trend.setText(f"{sign} {abs(trend_val)}% {trend_label}")
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
    def __init__(self, type, text, user_name, time_str, platform, amount=None):
        super().__init__()
        
        # تعیین آیکون بر اساس نوع فعالیت
        if type == "order":
             main_icon = 'fa5s.shopping-basket'
             icon_color = COLOR_GREEN
        elif type == "user":
             main_icon = 'fa5s.user-plus'
             icon_color = COLOR_BLUE
        else:
             main_icon = 'fa5s.comment-dots'
             icon_color = COLOR_PURPLE

        self.setStyleSheet(f"background: transparent; border-bottom: 1px solid #2e2e38; padding: 5px;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 8, 5, 8)
        
        ico = QLabel()
        ico.setPixmap(qta.icon(main_icon, color=icon_color).pixmap(22, 22))
        
        text_layout = QVBoxLayout()
        txt = QLabel(f"<b>{user_name}</b> {text}")
        txt.setStyleSheet("color: #fffffe; font-size: 12px;")
        
        info_row = QHBoxLayout()
        info_row.addWidget(txt)
        info_row.addStretch()

        if amount:
            amt_lbl = QLabel(f"{int(amount):,} ت")
            amt_lbl.setStyleSheet(f"color: {COLOR_GREEN}; font-size: 11px; font-weight: bold;")
            info_row.addWidget(amt_lbl)
            
        text_layout.addLayout(info_row)
        
        # ردیف پلتفرم و زمان
        meta_row = QHBoxLayout()
        plat_icon = 'fa5b.telegram' if platform == 'telegram' else 'mdi6.infinity'
        plat_color = COLOR_BLUE if platform == 'telegram' else COLOR_PURPLE

        meta_lbl = QLabel()
        meta_lbl.setPixmap(qta.icon(plat_icon, color=plat_color).pixmap(12, 12))

        tim = QLabel(time_str)
        tim.setStyleSheet(f"color: {COLOR_GRAY}; font-size: 10px;")

        meta_row.addWidget(meta_lbl); meta_row.addWidget(tim); meta_row.addStretch()
        text_layout.addLayout(meta_row)
        
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
        
        self.card_total_rev = StatCard("درآمد کل (تایید شده)", "fa5s.money-bill-wave", COLOR_GREEN)
        self.card_aov = StatCard("میانگین ارزش هر خرید", "fa5s.calculator", COLOR_BLUE)
        self.card_orders = StatCard("سفارشات جدید", "fa5s.shopping-cart", COLOR_PURPLE)
        self.card_users = StatCard("مشتریان کل", "fa5s.users", COLOR_YELLOW)
        
        stats_layout.addWidget(self.card_total_rev, 0, 0)
        stats_layout.addWidget(self.card_aov, 0, 1)
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
        
        mid_row = QHBoxLayout()
        mid_row.setSpacing(20)

        self.chart_tg = ModernChart()
        self.chart_rb = ModernChart()
        self.tabs.addTab(self.chart_tg, "فروش تلگرام (هفتگی)")
        self.tabs.addTab(self.chart_rb, "فروش روبیکا (هفتگی)")
        mid_row.addWidget(self.tabs, 2)

        # دایره‌ای سهم پلتفرم
        pie_frame = QFrame()
        pie_frame.setStyleSheet(f"background: {COLOR_CARD}; border-radius: 15px; border: 1px solid #333;")
        pie_lay = QVBoxLayout(pie_frame)
        pie_header = QLabel("📊 سهم فروش پلتفرم‌ها")
        pie_header.setStyleSheet("color: white; font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        pie_lay.addWidget(pie_header)
        self.pie_chart = ModernPieChart()
        pie_lay.addWidget(self.pie_chart)
        mid_row.addWidget(pie_frame, 1)

        self.main_layout.addLayout(mid_row, 3)

        # بخش پایین (۳ ستونه)
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)

        # ۱. فعالیت‌ها
        act_frame = QFrame()
        act_frame.setStyleSheet(f"background: {COLOR_CARD}; border-radius: 15px; border: 1px solid #333;")
        act_lay = QVBoxLayout(act_frame)
        act_header = QLabel("🔔 آخرین فعالیت‌ها")
        act_header.setStyleSheet("color: white; font-weight: bold; margin-bottom: 5px; font-size: 14px;")
        act_lay.addWidget(act_header)
        
        self.scroll_act = QScrollArea()
        self.scroll_act.setWidgetResizable(True)
        self.scroll_act.setStyleSheet("border: none; background: transparent;")
        self.act_container = QWidget()
        self.act_vbox = QVBoxLayout(self.act_container)
        self.act_vbox.addStretch()
        self.scroll_act.setWidget(self.act_container)
        act_lay.addWidget(self.scroll_act)
        bottom_row.addWidget(act_frame, 1)

        # ۲. محصولات برتر
        top_frame = QFrame()
        top_frame.setStyleSheet(f"background: {COLOR_CARD}; border-radius: 15px; border: 1px solid #333;")
        top_lay = QVBoxLayout(top_frame)
        top_header = QLabel("🏆 پرفروش‌ترین محصولات")
        top_header.setStyleSheet(f"color: {COLOR_PURPLE}; font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        top_lay.addWidget(top_header)

        self.top_prods_lay = QVBoxLayout()
        top_lay.addLayout(self.top_prods_lay)
        top_lay.addStretch()
        bottom_row.addWidget(top_frame, 1)

        # ۳. موجودی
        stock_frame = QFrame()
        stock_frame.setStyleSheet(f"background: {COLOR_CARD}; border-radius: 15px; border: 1px solid #333;")
        stock_lay = QVBoxLayout(stock_frame)
        stock_header = QLabel("⚠️ هشدار موجودی انبار")
        stock_header.setStyleSheet(f"color: {COLOR_RED}; font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        stock_lay.addWidget(stock_header)
        
        self.stock_list_lay = QVBoxLayout()
        stock_lay.addLayout(self.stock_list_lay)
        stock_lay.addStretch()
        bottom_row.addWidget(stock_frame, 1)

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
    async def refresh_data(self, *args, **kwargs):
        try:
            if not self.window() or not self.isVisible() or getattr(self.window(), '_is_shutting_down', False):
                return
            self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='white', animation=qta.Spin(self.btn_refresh)))
        except (RuntimeError, AttributeError):
            return

        loop = asyncio.get_running_loop()
        
        try:
            def fetch_all():
                with next(get_db()) as db:
                    # داده‌های آماری
                    rev_tg = crud.get_total_revenue_by_platform(db, "telegram")
                    rev_rb = crud.get_total_revenue_by_platform(db, "rubika")
                    total_rev = rev_tg + rev_rb

                    total_approved_orders = db.query(models.Order).filter(models.Order.status.in_(['approved', 'shipped', 'paid'])).count()
                    aov = total_rev / total_approved_orders if total_approved_orders > 0 else 0

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
                    
                    # محصولات برتر
                    top_prods = crud.get_top_selling_products(db, limit=5)

                    # رشد فروش
                    growth = crud.get_sales_growth(db)
                    m_growth = crud.get_monthly_growth(db)

                    # فعالیت‌ها
                    activities = crud.get_recent_activities(db, limit=10)
                    is_open = crud.get_setting(db, "tg_is_open", "true") == "true"
                    
                    return {
                        "rev_tg": rev_tg, "rev_rb": rev_rb, "pending": pending_orders, "users": total_users,
                        "dates": dates, "tg_sales": tg_sales, "rb_sales": rb_sales,
                        "low_stock": low_stock, "activities": activities, "is_open": is_open,
                        "top_prods": top_prods, "growth": growth, "m_growth": m_growth, "aov": aov
                    }

            data = await loop.run_in_executor(None, fetch_all)
            
            # آپدیت کارت‌ها (با محافظت در برابر مقادیر None)
            total_r = (data.get('rev_tg') or 0) + (data.get('rev_rb') or 0)
            self.card_total_rev.set_data(int(total_r), trend_val=data.get('growth', 0))
            self.card_aov.set_data(int(data.get('aov') or 0), trend_val=data.get('m_growth', 0), trend_label="رشد ماهانه")
            self.card_orders.set_data(data.get('pending') or 0)
            self.card_users.set_data(data.get('users') or 0)
            
            # آپدیت نمودارها
            self.update_chart(self.chart_tg, data['dates'], data['tg_sales'], COLOR_BLUE)
            self.update_chart(self.chart_rb, data['dates'], data['rb_sales'], COLOR_PURPLE)
            self.update_pie_chart(data['rev_tg'], data['rev_rb'])

            # آپدیت محصولات برتر
            for i in reversed(range(self.top_prods_lay.count())):
                self.top_prods_lay.itemAt(i).widget().deleteLater()

            if not data['top_prods']:
                self.top_prods_lay.addWidget(QLabel("داده‌ای یافت نشد"))
            else:
                for name, qty, rev in data['top_prods']:
                    self.top_prods_lay.addWidget(TopProductItem(name, qty, rev))

            # آپدیت فعالیت‌ها
            for i in reversed(range(self.act_vbox.count() - 1)):
                w = self.act_vbox.itemAt(i).widget()
                if w: w.deleteLater()
            
            if not data['activities']:
                empty_lbl = QLabel("فعالیتی ثبت نشده")
                empty_lbl.setStyleSheet("color: #555; padding: 10px;")
                empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.act_vbox.insertWidget(0, empty_lbl)
            else:
                for act in reversed(data['activities']):
                    time_str = act['time'].strftime("%H:%M")
                    item = ActivityItem(
                        type=act['type'],
                        text=act['text'],
                        user_name=act['user'],
                        time_str=time_str,
                        platform=act['platform'],
                        amount=act['amount']
                    )
                    self.act_vbox.insertWidget(0, item)

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
            try:
                self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='white'))
            except RuntimeError:
                pass

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

    def update_pie_chart(self, rev_tg, rev_rb):
        ax = self.pie_chart.axes
        ax.clear()

        labels = [farsi_text_for_chart('تلگرام'), farsi_text_for_chart('روبیکا')]
        values = [rev_tg, rev_rb]

        if sum(values) == 0:
            ax.text(0.5, 0.5, farsi_text_for_chart("داده‌ای موجود نیست"), ha='center', va='center', color=COLOR_GRAY)
        else:
            colors = [COLOR_BLUE, COLOR_PURPLE]
            ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, textprops={'color': "w"})

        self.pie_chart.draw()

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
    async def toggle_shop_status(self, *args, **kwargs):
        try:
            if not self.window() or getattr(self.window(), '_is_shutting_down', False): return
            new_status = "true" if self.btn_status.isChecked() else "false"
        except RuntimeError:
            return

        await asyncio.get_running_loop().run_in_executor(
            None, lambda: crud.set_setting(next(get_db()), "tg_is_open", new_status)
        )
        await self.refresh_data()

    @asyncSlot()
    async def generate_sales_report(self, *args, **kwargs):
        try:
            if not self.window() or getattr(self.window(), '_is_shutting_down', False): return
            file_path, _ = QFileDialog.getSaveFileName(self, "ذخیره گزارش مالی", "Sales_Report.pdf", "PDF Files (*.pdf)")
        except RuntimeError:
            return

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