import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QPushButton, QGraphicsDropShadowEffect,
    QScrollArea, QTabWidget, QSizePolicy, QProgressBar, QComboBox,
    QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, pyqtProperty, QRect, QPoint
from PyQt6.QtGui import QColor, QFont, QPainter, QLinearGradient, QBrush, QPen, QCursor, QPixmap
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
from sqlalchemy import func

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
# Canvas Chart (Interactive with Tooltips)
# ==============================================================================
class ModernChart(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        self.persian_font = None
        font_path = Path(BASE_DIR) / "fonts" / "Vazirmatn.ttf"
        
        if font_path.exists():
            try:
                fm.fontManager.addfont(str(font_path))
                self.persian_font = FontProperties(fname=str(font_path))
                plt.rcParams['font.family'] = self.persian_font.get_name()
            except Exception as e:
                logger.error(f"Error loading font for chart: {e}")
        
        plt.rcParams.update({
            'axes.facecolor': 'none', # Transparent to show glassmorphism
            'figure.facecolor': 'none',
            'text.color': COLOR_YELLOW,
            'axes.labelcolor': COLOR_GRAY,
            'xtick.color': COLOR_GRAY,
            'ytick.color': COLOR_GRAY,
            'grid.color': '#2d2e32',
        })
        
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.patch.set_alpha(0) # Background transparency
        
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['left'].set_color('#333')
        self.axes.spines['bottom'].set_color('#333')
        
        super().__init__(self.fig)
        self.setParent(parent)

        # Tooltip Handling
        self.annot = self.axes.annotate("", xy=(0,0), xytext=(20,20),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round", fc=COLOR_BG, ec=COLOR_PURPLE, alpha=0.9),
                            arrowprops=dict(arrowstyle="->", color=COLOR_PURPLE))
        self.annot.set_visible(False)
        self.mpl_connect("motion_notify_event", self.on_hover)

    def on_hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.axes:
            for line in self.axes.get_lines():
                cont, ind = line.contains(event)
                if cont:
                    pos = line.get_offsets()[ind["ind"][0]] if hasattr(line, 'get_offsets') else (line.get_xdata()[ind["ind"][0]], line.get_ydata()[ind["ind"][0]])
                    self.annot.xy = pos
                    text = f"{int(pos[1]):,} تومان"
                    self.annot.set_text(farsi_text_for_chart(text))
                    self.annot.set_visible(True)
                    self.fig.canvas.draw_idle()
                    return
        if vis:
            self.annot.set_visible(False)
            self.fig.canvas.draw_idle()

# ==============================================================================
# Circular KPI Widget
# ==============================================================================
class CircularKPI(QWidget):
    def __init__(self, value=0, label="KPI", color=COLOR_PURPLE, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)
        self.value = value # 0 to 100
        self.label = label
        self.color = QColor(color)

    def set_value(self, val):
        self.value = min(100, max(0, val))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            rect = self.rect().adjusted(10, 10, -10, -10)

            # Background Circle
            pen = QPen(QColor("#2e2e38"), 8)
            painter.setPen(pen)
            painter.drawEllipse(rect)

            # Progress Arc
            pen.setColor(self.color)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            span_angle = int(-self.value * 3.6 * 16)
            painter.drawArc(rect, 90 * 16, span_angle)

            # Text
            painter.setPen(QColor("white"))
            font = QFont("Vazirmatn", 14, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{int(self.value)}%")

            font.setPointSize(8)
            painter.setFont(font)
            painter.setPen(QColor(COLOR_GRAY))
            painter.drawText(self.rect().adjusted(0, 80, 0, 0), Qt.AlignmentFlag.AlignHCenter, self.label)
        finally:
            painter.end()

# ==============================================================================
# Stat Card (Animated & Glassmorphism)
# ==============================================================================
class StatCard(QFrame):
    def __init__(self, title, icon, color, parent=None):
        super().__init__(parent)
        self.setFixedHeight(140)
        self.setMinimumWidth(240)
        self.color = QColor(color)
        self.setObjectName("StatCard")
        
        self.setStyleSheet(f"""
            QFrame#StatCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 rgba(255, 255, 255, 0.05), stop:1 rgba(255, 255, 255, 0.02));
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30); shadow.setColor(QColor(0,0,0,150)); shadow.setOffset(0,10)
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        
        text_layout = QVBoxLayout()
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet(f"color: {COLOR_GRAY}; font-size: 13px; font-weight: bold;")
        
        self.lbl_value = QLabel("0")
        self.lbl_value.setStyleSheet(f"color: white; font-size: 32px; font-weight: 900;")
        
        self.lbl_trend = QLabel("")
        self.lbl_trend.setStyleSheet(f"color: {COLOR_GREEN}; font-size: 12px; background: rgba(0,0,0,0.3); padding: 3px 8px; border-radius: 10px;")
        
        text_layout.addWidget(self.lbl_title)
        text_layout.addWidget(self.lbl_value)
        text_layout.addWidget(self.lbl_trend)
        text_layout.addStretch()
        
        layout.addLayout(text_layout)
        layout.addStretch()

        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(65, 65)
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_lbl.setStyleSheet(f"background: {color}20; border-radius: 20px; border: 1px solid {color}40;")
        self.icon_lbl.setPixmap(qta.icon(icon, color=color).pixmap(35, 35))
        layout.addWidget(self.icon_lbl)

        # Animations
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_count)

    def enterEvent(self, event):
        self.setStyleSheet(f"""
            QFrame#StatCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 rgba(255, 255, 255, 0.1), stop:1 rgba(255, 255, 255, 0.05));
                border-radius: 20px;
                border: 1px solid {self.color.name()}80;
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(f"""
            QFrame#StatCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 rgba(255, 255, 255, 0.05), stop:1 rgba(255, 255, 255, 0.02));
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)
        super().leaveEvent(event)

    def set_data(self, value, trend_val=0, range_text="دیروز"):
        self.target_value = value
        self.current_value = 0
        self.step = max(1, int(value / 30))
        self.anim_timer.start(15)
        
        color = COLOR_GREEN if trend_val >= 0 else COLOR_RED
        sign = "↑" if trend_val >= 0 else "↓"
        self.lbl_trend.setText(f"{sign} {abs(trend_val)}% نسبت به {range_text}")
        self.lbl_trend.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold; background: {color}15; padding: 4px 10px; border-radius: 12px;")

    def _update_count(self):
        if self.current_value < self.target_value:
            self.current_value += self.step
            if self.current_value > self.target_value:
                self.current_value = self.target_value
            self.lbl_value.setText(f"{int(self.current_value):,}")
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
# Activity Item (Live with Pulse)
# ==============================================================================
class ActivityItem(QFrame):
    def __init__(self, text, time_str, platform, amount=None):
        super().__init__()
        color = COLOR_BLUE if platform == 'telegram' else COLOR_PURPLE
        icon = 'fa5b.telegram' if platform == 'telegram' else 'mdi6.infinity'
        
        self.setStyleSheet(f"""
            QFrame {{ background: rgba(255, 255, 255, 0.02); border-radius: 12px; margin-bottom: 4px; border: 1px solid transparent; }}
            QFrame:hover {{ border: 1px solid rgba(255, 255, 255, 0.1); background: rgba(255, 255, 255, 0.04); }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        # Pulse Indicator
        self.pulse = QLabel()
        self.pulse.setFixedSize(10, 10)
        self.pulse.setStyleSheet(f"background: {SUCCESS_COLOR}; border-radius: 5px;")

        self.pulse_anim = QPropertyAnimation(self.pulse, b"geometry") # Simulated pulse
        # Actually better to just animate opacity
        self.pulse_eff = QGraphicsOpacityEffect(self.pulse)
        self.pulse.setGraphicsEffect(self.pulse_eff)
        self.pa = QPropertyAnimation(self.pulse_eff, b"opacity")
        self.pa.setDuration(1000); self.pa.setStartValue(1.0); self.pa.setEndValue(0.2); self.pa.setLoopCount(-1); self.pa.start()
        
        ico = QLabel()
        ico.setPixmap(qta.icon(icon, color=color).pixmap(24, 24))
        
        text_layout = QVBoxLayout()
        txt = QLabel(text)
        txt.setStyleSheet("color: #fffffe; font-size: 13px; font-weight: bold;")
        
        info_row = QHBoxLayout()
        info_row.addWidget(txt)
        info_row.addStretch()
        if amount:
            amt_lbl = QLabel(f"{int(amount):,} ت")
            amt_lbl.setStyleSheet(f"color: {COLOR_GREEN}; font-size: 12px; font-weight: 900;")
            info_row.addWidget(amt_lbl)
            
        text_layout.addLayout(info_row)
        
        tim = QLabel(time_str)
        tim.setStyleSheet(f"color: {COLOR_GRAY}; font-size: 10px;")
        text_layout.addWidget(tim)
        
        layout.addWidget(self.pulse)
        layout.addWidget(ico)
        layout.addLayout(text_layout)

# ==============================================================================
# Top Product Card
# ==============================================================================
class TopProductCard(QFrame):
    def __init__(self, name, sales, img_path=None):
        super().__init__()
        self.setFixedSize(180, 100)
        self.setStyleSheet(f"""
            QFrame {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 15px; }}
            QFrame:hover {{ background: rgba(255,255,255,0.06); border-color: {ACCENT_COLOR}50; }}
        """)

        layout = QHBoxLayout(self)

        self.img = QLabel()
        self.img.setFixedSize(60, 60)
        self.img.setStyleSheet("background: #000; border-radius: 10px;")
        if img_path:
            full_path = Path(BASE_DIR) / img_path
            if full_path.exists():
                self.img.setPixmap(QPixmap(str(full_path)).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))

        info = QVBoxLayout()
        n = QLabel(name); n.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        n.setWordWrap(True)
        s = QLabel(f"🔥 {sales} فروش"); s.setStyleSheet(f"color: {WARNING_COLOR}; font-size: 10px; font-weight: bold;")
        info.addWidget(n); info.addWidget(s)

        layout.addWidget(self.img)
        layout.addLayout(info)

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
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(30)

        # هدر با Glassmorphism
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{ background: rgba(255,255,255,0.03); border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); }}
        """)
        header = QHBoxLayout(header_frame)
        header.setContentsMargins(20, 15, 20, 15)

        title_box = QVBoxLayout()
        main_title = QLabel("داشبورد مانیتورینگ هوشمند")
        main_title.setStyleSheet("font-size: 26px; font-weight: 900; color: white; background: transparent; border: none;")
        
        self.lbl_status = QLabel("آخرین بروزرسانی: --:--")
        self.lbl_status.setStyleSheet(f"color: {COLOR_GRAY}; font-size: 12px; background: transparent; border: none;")
        
        title_box.addWidget(main_title); title_box.addWidget(self.lbl_status)
        header.addLayout(title_box)
        header.addStretch()

        # Time-Range Selector
        self.cmb_range = QComboBox()
        self.cmb_range.addItems(["امروز", "۷ روز اخیر", "۳۰ روز اخیر"])
        self.cmb_range.setFixedWidth(150)
        self.cmb_range.setStyleSheet(f"""
            QComboBox {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 8px 15px; color: white; }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{ background: {COLOR_BG}; color: white; selection-background-color: {COLOR_PURPLE}; }}
        """)
        self.cmb_range.currentIndexChanged.connect(self.refresh_data)
        header.addWidget(self.cmb_range)

        self.btn_status = QPushButton()
        self.btn_status.setCheckable(True)
        self.btn_status.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_status.clicked.connect(self.toggle_shop_status)
        header.addWidget(self.btn_status)

        self.btn_refresh = QPushButton()
        self.btn_refresh.setFixedSize(45, 45)
        self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='white'))
        self.btn_refresh.setStyleSheet(f"background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.refresh_data)
        header.addWidget(self.btn_refresh)
        
        self.main_layout.addWidget(header_frame)

        # کارت‌های آمار
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.card_rev = StatCard("درآمد کل", "fa5s.money-bill-wave", COLOR_BLUE)
        self.card_profit = StatCard("سود خالص", "fa5s.hand-holding-usd", COLOR_YELLOW)
        self.card_orders = StatCard("تعداد سفارش", "fa5s.shopping-cart", COLOR_GREEN)
        self.card_users = StatCard("مشتریان جدید", "fa5s.users", COLOR_BLUE)

        stats_layout.addWidget(self.card_rev)
        stats_layout.addWidget(self.card_profit)
        stats_layout.addWidget(self.card_orders)
        stats_layout.addWidget(self.card_users)
        self.main_layout.addLayout(stats_layout)

        # محصولات پرفروش (جدید)
        top_prods_box = QFrame()
        top_prods_box.setStyleSheet("background: rgba(255,255,255,0.02); border-radius: 20px; border: 1px solid rgba(255,255,255,0.05);")
        tp_lay = QVBoxLayout(top_prods_box)
        tp_lay.setContentsMargins(20, 15, 20, 15)
        tp_header = QLabel("🏆 محصولات پرفروش این دوره")
        tp_header.setStyleSheet("color: white; font-weight: 900; font-size: 14px; border: none;")
        tp_lay.addWidget(tp_header)

        self.tp_scroll = QScrollArea()
        self.tp_scroll.setWidgetResizable(True)
        self.tp_scroll.setStyleSheet("background: transparent; border: none;")
        self.tp_container = QWidget()
        self.tp_hbox = QHBoxLayout(self.tp_container)
        self.tp_hbox.setSpacing(15); self.tp_hbox.addStretch()
        self.tp_scroll.setWidget(self.tp_container)
        tp_lay.addWidget(self.tp_scroll)
        self.main_layout.addWidget(top_prods_box)

        # نمودارها با Glassmorphism
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; background: rgba(255,255,255,0.02); }}
            QTabBar::tab {{ background: rgba(0,0,0,0.2); color: {COLOR_GRAY}; padding: 12px 35px; font-weight: bold; border-top-left-radius: 12px; border-top-right-radius: 12px; margin-right: 5px;}}
            QTabBar::tab:selected {{ background: rgba(255,255,255,0.05); color: {COLOR_PURPLE}; border-bottom: 3px solid {COLOR_PURPLE}; }}
        """)
        
        self.chart_tg = ModernChart()
        self.chart_rb = ModernChart()
        self.tabs.addTab(self.chart_tg, "📈 تحلیل فروش تلگرام")
        self.tabs.addTab(self.chart_rb, "📈 تحلیل فروش روبیکا")
        self.main_layout.addWidget(self.tabs, 4)

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

        # KPI و موجودی
        bottom_right_lay = QVBoxLayout()

        # بخش KPIهای دایره‌ای
        kpi_frame = QFrame()
        kpi_frame.setStyleSheet(f"background: {COLOR_CARD}; border-radius: 15px; border: 1px solid #333;")
        kpi_lay = QHBoxLayout(kpi_frame)
        self.kpi_conv = CircularKPI(0, "نرخ تبدیل", COLOR_GREEN)
        self.kpi_target = CircularKPI(0, "تحقق هدف", COLOR_BLUE)
        kpi_lay.addWidget(self.kpi_conv)
        kpi_lay.addWidget(self.kpi_target)
        bottom_right_lay.addWidget(kpi_frame)

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

        bottom_row.addLayout(bottom_right_lay)
        self.main_layout.addLayout(bottom_row, 2)

    def showEvent(self, event):
        if not self._data_loaded:
            QTimer.singleShot(300, self.refresh_data)
            self._data_loaded = True

    @asyncSlot()
    async def refresh_data(self):
        self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='white', animation=qta.Spin(self.btn_refresh)))
        loop = asyncio.get_running_loop()
        
        range_idx = self.cmb_range.currentIndex()
        days_map = {0: 1, 1: 7, 2: 30}
        days = days_map.get(range_idx, 30)
        range_text = self.cmb_range.currentText()

        try:
            def fetch_all():
                with next(get_db()) as db:
                    # ۱. آمار پیشرفته
                    stats = crud.get_dashboard_stats_advanced(db, days)
                    
                    # ۲. محصولات پرفروش
                    top_prods = crud.get_top_selling_products(db, limit=8, days=days)

                    # ۳. داده‌های نمودار (همیشه ۷ روز اخیر برای تحلیل روند)
                    end_date = datetime.now()
                    dates = [(end_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
                    
                    def get_plat_chart_data(plat):
                        res = db.query(func.date(models.Order.created_at), func.sum(models.Order.total_amount))\
                            .join(models.User).filter(models.User.platform == plat)\
                            .filter(models.Order.status.in_(['approved', 'shipped', 'paid']))\
                            .filter(models.Order.created_at >= (end_date - timedelta(days=7)))\
                            .group_by(func.date(models.Order.created_at)).all()
                        v_map = {r[0]: float(r[1]) for r in res if r[0]}
                        return [v_map.get(d, 0) for d in dates]

                    tg_sales = get_plat_chart_data('telegram')
                    rb_sales = get_plat_chart_data('rubika')
                    
                    # ۴. موجودی کم و فعالیت‌ها
                    low_stock = db.query(models.Product).filter(models.Product.stock < 10).limit(5).all()
                    recent_orders = db.query(models.Order).order_by(models.Order.created_at.desc()).limit(8).all()
                    is_open = crud.get_setting(db, "tg_is_open", "true") == "true"
                    
                    total_users = db.query(models.User).count()
                    conv_rate = min(95, (stats['current']['orders'] / total_users * 100)) if total_users > 0 else 0
                    target_rate = min(100, (stats['current']['rev']) / 50000000 * 100) # هدف ۵۰ میلیونی

                    return {
                        "stats": stats, "top_prods": top_prods,
                        "dates": dates, "tg_sales": tg_sales, "rb_sales": rb_sales,
                        "low_stock": low_stock, "recent_orders": recent_orders, "is_open": is_open,
                        "conv": conv_rate, "target": target_rate
                    }

            data = await loop.run_in_executor(None, fetch_all)
            
            # آپدیت کارت‌ها
            s = data['stats']
            self.card_rev.set_data(int(s['current']['rev']), s['trends']['rev'], range_text)
            self.card_profit.set_data(int(s['current']['profit']), s['trends']['profit'], range_text)
            self.card_orders.set_data(s['current']['orders'], s['trends']['orders'], range_text)
            self.card_users.set_data(s['current']['users'], s['trends']['users'], range_text)
            
            # آپدیت محصولات پرفروش
            for i in reversed(range(self.tp_hbox.count() - 1)):
                self.tp_hbox.itemAt(i).widget().deleteLater()

            for p_info in data['top_prods']:
                p = p_info['product']
                card = TopProductCard(p.name, p_info['total_qty'], p.image_path)
                self.tp_hbox.insertWidget(self.tp_hbox.count()-1, card)

            # آپدیت نمودارها
            self.update_chart(self.chart_tg, data['dates'], data['tg_sales'], COLOR_BLUE)
            self.update_chart(self.chart_rb, data['dates'], data['rb_sales'], COLOR_PURPLE)
            
            # آپدیت KPIها
            self.kpi_conv.set_value(data['conv'])
            self.kpi_target.set_value(data['target'])

            # آپدیت فعالیت‌ها
            for i in reversed(range(self.act_vbox.count() - 1)):
                self.act_vbox.itemAt(i).widget().deleteLater()
            
            for o in data['recent_orders']:
                if not o.user: continue
                msg = f"سفارش جدید #{o.id} از {o.user.full_name}"
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
        
        # استایل حرفه‌ای‌تر با نقاط توخالی و خط ضخیم‌تر
        ax.plot(short_dates, values, color=color, marker='o', linewidth=4,
                markersize=10, markerfacecolor=COLOR_CARD, markeredgewidth=3, markeredgecolor=color)

        # گرادینت زیر نمودار (شبیه‌سازی با آلفاهای مختلف)
        ax.fill_between(short_dates, values, color=color, alpha=0.15)
        ax.fill_between(short_dates, values, color=color, alpha=0.05)

        # تنظیمات فواصل و مقیاس
        if any(values):
            ax.set_ylim(0, max(values) * 1.3)
        else:
            ax.set_ylim(0, 100)

        ax.grid(True, axis='y', linestyle=':', alpha=0.2)
        
        # حذف لبه‌های نمودار
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # اعمال فونت فارسی روی محور افقی
        if canvas.persian_font:
            for label in ax.get_xticklabels():
                label.set_fontproperties(canvas.persian_font)
                label.set_fontsize(9)
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