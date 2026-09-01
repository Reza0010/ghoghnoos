"""
FixBoard Miner Manager - Dashboard Widget
Displays gorgeous, animated KPIs (Total, Online, Offline, Error, Warning, Avg Temp, Total Hashrate)
along with custom-painted high-performance live status charts (Hashrate, Temp, Fan RPM).
"""

from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QGridLayout
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont

class DynamicGraphWidget(QWidget):
    """
    High-performance real-time chart custom-painted with QPainter.
    Displays smooth anti-aliased curves with glowing gradients.
    """
    def __init__(self, title: str, color_hex: str, unit: str):
        super().__init__()
        self.title = title
        self.color = QColor(color_hex)
        self.unit = unit
        self.data_points = []
        self.max_points = 30
        self.setMinimumHeight(150)

    def add_value(self, val: float):
        self.data_points.append(val)
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        # Draw beautiful translucent dark background grid
        p.setBrush(QBrush(QColor(30, 30, 35, 180)))
        p.setPen(QPen(QColor(60, 60, 70, 50), 1))
        p.drawRoundedRect(0, 0, width, height, 8, 8)

        # Draw grid lines
        p.setPen(QPen(QColor(80, 80, 90, 30), 1, Qt.DashLine))
        for i in range(1, 4):
            y_grid = int(height * i / 4)
            p.drawLine(10, y_grid, width - 10, y_grid)
        for i in range(1, 6):
            x_grid = int(width * i / 6)
            p.drawLine(x_grid, 10, x_grid, height - 10)

        # Draw Title and latest value
        p.setPen(QColor(220, 220, 230))
        p.setFont(QFont("Segoe UI", 10, QFont.Bold))
        p.drawText(15, 25, self.title)

        if self.data_points:
            latest = self.data_points[-1]
            p.setFont(QFont("Segoe UI", 10))
            p.drawText(width - 120, 25, f"{latest:.1f} {self.unit}")

        if len(self.data_points) < 2:
            p.setFont(QFont("Segoe UI", 9))
            p.setPen(QColor(120, 120, 130))
            p.drawText(width // 2 - 50, height // 2, "در حال دریافت داده...")
            p.end()
            return

        # Calculate limits
        min_v = min(self.data_points)
        max_v = max(self.data_points)
        v_range = max_v - min_v if max_v != min_v else 1.0

        # Draw curve and filled region under the curve
        points = []
        for i, val in enumerate(self.data_points):
            x = 10 + (width - 20) * i / (len(self.data_points) - 1)
            # Inverse Y scale (Y increases downwards in Qt coordinates)
            y = (height - 30) - (height - 50) * (val - min_v) / v_range
            points.append(QPointF(x, y))

        # 1. Fill region with gradient
        grad = QLinearGradient(0, 0, 0, height)
        grad.setColorAt(0, QColor(self.color.red(), self.color.green(), self.color.blue(), 60))
        grad.setColorAt(1, QColor(self.color.red(), self.color.green(), self.color.blue(), 5))

        from PySide6.QtGui import QPainterPath
        path = QPainterPath()
        path.moveTo(points[0].x(), height - 10)
        for pt in points:
            path.lineTo(pt.x(), pt.y())
        path.lineTo(points[-1].x(), height - 10)
        path.closeSubpath()
        p.fillPath(path, QBrush(grad))

        # 2. Draw smooth path line
        pen = QPen(self.color, 2, Qt.SolidLine)
        p.setPen(pen)
        for i in range(len(points) - 1):
            p.drawLine(points[i], points[i+1])

        # 3. Draw dots on key vertices
        p.setBrush(QBrush(QColor(255, 255, 255)))
        p.setPen(QPen(self.color, 2))
        p.drawEllipse(points[-1], 4, 4)

        p.end()


class KPICard(QFrame):
    """
    Elegant dark Glassmorphic metric card.
    """
    def __init__(self, title: str, value: str, icon_color_hex: str):
        super().__init__()
        self.setObjectName("KPICard")
        self.setStyleSheet(f"""
            #KPICard {{
                background-color: rgba(33, 33, 40, 180);
                border: 1px solid rgba(255, 255, 255, 10);
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Title
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("color: #8E9297; font-family: 'Segoe UI'; font-size: 11px; font-weight: bold;")
        self.title_lbl.setAlignment(Qt.AlignRight)
        layout.addWidget(self.title_lbl)

        # Value
        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(f"color: {icon_color_hex}; font-family: 'Segoe UI'; font-size: 20px; font-weight: 900;")
        self.val_lbl.setAlignment(Qt.AlignRight)
        layout.addWidget(self.val_lbl)


class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 1. Header Title
        header_lbl = QLabel("داشبورد مانیتورینگ ماینر")
        header_lbl.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: bold; font-family: 'Segoe UI';")
        header_lbl.setAlignment(Qt.AlignRight)
        main_layout.addWidget(header_lbl)

        # 2. KPI Cards Grid Layout (Total, Online, Offline, Error/Warning, Avg Temp, Hashrate)
        kpis_layout = QGridLayout()
        kpis_layout.setSpacing(15)

        self.card_total = KPICard("کل دستگاه‌ها", "0", "#E1E1E5")
        self.card_online = KPICard("دستگاه‌های آنلاین", "0", "#2ECC71")
        self.card_offline = KPICard("دستگاه‌های آفلاین", "0", "#E74C3C")
        self.card_error = KPICard("خطاها (Error)", "0", "#E67E22")
        self.card_avg_temp = KPICard("میانگین دمای چیپ", "دریافت نشد", "#3498DB")
        self.card_total_hr = KPICard("مجموع هش‌ریت شبکه‌", "0.00 TH/s", "#F1C40F")

        kpis_layout.addWidget(self.card_total, 0, 0)
        kpis_layout.addWidget(self.card_online, 0, 1)
        kpis_layout.addWidget(self.card_offline, 0, 2)
        kpis_layout.addWidget(self.card_error, 1, 0)
        kpis_layout.addWidget(self.card_avg_temp, 1, 1)
        kpis_layout.addWidget(self.card_total_hr, 1, 2)

        main_layout.addLayout(kpis_layout)

        # 3. Dynamic Live Charts Area
        charts_header = QLabel("نمودار زنده شبکه و سخت‌افزار")
        charts_header.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: bold; font-family: 'Segoe UI'; margin-top: 10px;")
        charts_header.setAlignment(Qt.AlignRight)
        main_layout.addWidget(charts_header)

        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)

        self.chart_hashrate = DynamicGraphWidget("مجموع هش‌ریت شبکه", "#F1C40F", "TH/s")
        self.chart_temp = DynamicGraphWidget("میانگین دمای چیپ‌ها", "#3498DB", "°C")
        self.chart_fans = DynamicGraphWidget("سرعت متوسط فن‌ها", "#E74C3C", "RPM")

        charts_layout.addWidget(self.chart_hashrate)
        charts_layout.addWidget(self.chart_temp)
        charts_layout.addWidget(self.chart_fans)

        main_layout.addLayout(charts_layout)
        main_layout.addStretch()

    def update_stats(self, total: int, online: int, offline: int, error: int, avg_temp: float, total_hr_th: float, avg_fan_rpm: float):
        """Updates all dynamic metrics and charts across the dashboard panel."""
        self.card_total.val_lbl.setText(str(total))
        self.card_online.val_lbl.setText(str(online))
        self.card_offline.val_lbl.setText(str(offline))
        self.card_error.val_lbl.setText(str(error))

        if avg_temp > 0:
            self.card_avg_temp.val_lbl.setText(f"{avg_temp:.1f} °C")
            self.chart_temp.add_value(avg_temp)
        else:
            self.card_avg_temp.val_lbl.setText("دریافت نشد")

        self.card_total_hr.val_lbl.setText(f"{total_hr_th:.2f} TH/s")

        if online > 0:
            self.chart_hashrate.add_value(total_hr_th)
            if avg_fan_rpm > 0:
                self.chart_fans.add_value(avg_fan_rpm)
