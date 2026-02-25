import sys
import os
import asyncio
import logging
import threading
import multiprocessing
import warnings
from pathlib import Path
import subprocess
import json
import socket
# --- تنظیمات محیطی ---
os.environ["QT_FONT_DPI"] = "96"
os.environ["QT_LOGGING_RULES"] = "qt.qpa.screen=false"
from telegram.warnings import PTBUserWarning
warnings.filterwarnings("ignore", category=PTBUserWarning)
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from config import TELEGRAM_BOT_TOKEN, LOG_DIR, RUBIKA_BOT_TOKEN
from db import crud
from db.database import init_db
from bot.loader import setup_application_handlers
from rubika_bot.bot_logic import RubikaWorker
from rubika_bot.rubika_client import RubikaAPI
try:
    from PyQt6.QtWidgets import (
        QApplication, QSplashScreen, QProgressBar, QVBoxLayout,
        QLabel, QWidget, QLineEdit, QPushButton, QFrame, QMessageBox
    )
    from PyQt6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, pyqtSignal
    from PyQt6.QtGui import QColor, QFont, QPixmap, QLinearGradient, QBrush, QPainter
    import qasync
    import qtawesome as qta
    from admin_panel.main_window import MainWindow
    from telegram import Update
    from telegram.ext import Application
except ImportError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
logger = logging.getLogger("Launcher")

# ==============================================================================
# 0. ابزارهای کمکی سیستم (Single Instance, Xray)
# ==============================================================================
def is_already_running(port=45912):
    """جلوگیری از اجرای چندباره با استفاده از سوکت محلی"""
    try:
        lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lock_socket.bind(("127.0.0.1", port))
        # سوکت را باز نگه می‌داریم تا برنامه بسته شود
        globals()['_lock_socket'] = lock_socket
        return False
    except socket.error:
        return True

class XrayManager:
    """مدیریت هسته Xray برای تبدیل لینک V2Ray به پروکسی محلی"""
    def __init__(self, binary_path, config_path):
        self.bin = binary_path
        self.cfg = config_path
        self.process = None

    def generate_config(self, v2ray_link, local_port):
        """تولید کانفیگ JSON واقعی برای Xray بر اساس لینک دریافتی"""
        from bot.proxy_utils import parse_v2ray_link
        data = parse_v2ray_link(v2ray_link)
        if not data: return False

        config = {
            "inbounds": [{
                "port": local_port, "listen": "127.0.0.1", "protocol": "socks",
                "settings": {"auth": "noauth", "udp": True}
            }],
            "outbounds": [{
                "protocol": data['protocol'],
                "settings": {
                    "vnext": [{
                        "address": data['address'], "port": data['port'],
                        "users": [{"id": data['id'], "encryption": "none"}]
                    }]
                },
                "streamSettings": {
                    "network": data['type'], "security": data['security'],
                    "tlsSettings": {"serverName": data.get('sni', data['address']), "fingerprint": data.get('fp', 'chrome')}
                }
            }]
        }

        with open(self.cfg, 'w') as f:
            json.dump(config, f, indent=4)
        return True

    def start(self, v2ray_link, local_port=2080):
        if not os.path.exists(self.bin):
            logger.error(f"Xray binary not found at {self.bin}")
            return False

        self.generate_config(v2ray_link, local_port)
        try:
            self.process = subprocess.Popen(
                [str(self.bin), "run", "-c", str(self.cfg)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            logger.info(f"🚀 Xray Bridge started on port {local_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start Xray: {e}")
            return False

    def stop(self):
        if self.process:
            self.process.terminate()
            logger.info("🛑 Xray Bridge stopped")

# ==============================================================================
# 1. المان‌های بصری مدرن (UI Components)
# ==============================================================================
class ModernSplashScreen(QSplashScreen):
    def __init__(self):
        # ایجاد یک Pixmap شیشه‌ای
        pixmap = QPixmap(500, 350)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        self.frame = QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 rgba(22, 22, 26, 0.95), stop:1 rgba(36, 38, 41, 0.95));
                border: 2px solid #7f5af0;
                border-radius: 20px;
            }
        """)
        f_layout = QVBoxLayout(self.frame)
        f_layout.setContentsMargins(30, 30, 30, 30)

        # Logo/Title
        title = QLabel("GHOGHNOOS SHOP")
        title.setStyleSheet("color: white; font-size: 28px; font-weight: 900; letter-spacing: 2px; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status = QLabel("در حال بارگذاری...")
        self.status.setStyleSheet("color: #94a1b2; font-size: 14px; border: none;")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                background: #16161a; border-radius: 5px; height: 6px; text-align: center; border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7f5af0, stop:1 #2cb67d);
                border-radius: 5px;
            }
        """)
        self.progress.setRange(0, 100)
        self.progress.setValue(10)

        f_layout.addStretch()
        f_layout.addWidget(title)
        f_layout.addSpacing(20)
        f_layout.addWidget(self.status)
        f_layout.addWidget(self.progress)
        f_layout.addStretch()

        layout.addWidget(self.frame)

    def set_message(self, text, value):
        self.status.setText(text)
        self.progress.setValue(value)
        QApplication.processEvents()

class ModernLoginDialog(QWidget):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.frame = QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 rgba(40, 44, 52, 0.98), stop:1 rgba(22, 22, 26, 0.98));
                border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        f_lay = QVBoxLayout(self.frame)
        f_lay.setContentsMargins(40, 40, 40, 40)
        f_lay.setSpacing(20)

        # Header
        icon = QLabel()
        icon.setPixmap(qta.icon("fa5s.user-shield", color="#7f5af0").pixmap(60, 60))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("ورود به مدیریت")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Inputs
        self.inp_user = QLineEdit()
        self.inp_user.setPlaceholderText("نام کاربری")
        self.inp_pass = QLineEdit()
        self.inp_pass.setPlaceholderText("رمز عبور")
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)

        style = """
            QLineEdit {
                background: #16161a; border: 1px solid #3a3a4e; border-radius: 10px;
                padding: 12px; color: white; font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #7f5af0; }
        """
        self.inp_user.setStyleSheet(style); self.inp_pass.setStyleSheet(style)

        self.btn_login = QPushButton("ورود به پنل")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background: #7f5af0; color: white; border-radius: 10px;
                padding: 12px; font-weight: bold; font-size: 15px; border: none;
            }
            QPushButton:hover { background: #6246ea; }
        """)
        self.btn_login.clicked.connect(self.do_login)

        self.btn_close = QPushButton("انصراف")
        self.btn_close.setFlat(True)
        self.btn_close.setStyleSheet("color: #94a1b2;")
        self.btn_close.clicked.connect(self.close)

        f_lay.addWidget(icon); f_lay.addWidget(title)
        f_lay.addWidget(self.inp_user); f_lay.addWidget(self.inp_pass)
        f_lay.addWidget(self.btn_login); f_lay.addWidget(self.btn_close)
        layout.addWidget(self.frame)

    def do_login(self):
        """اعتبارسنجی مدیر از طریق تنظیمات دیتابیس"""
        from db.database import get_db
        try:
            with next(get_db()) as db:
                saved_user = crud.get_setting(db, "admin_username", "admin")
                saved_pass = crud.get_setting(db, "admin_password", "1234")

                if self.inp_user.text() == saved_user and self.inp_pass.text() == saved_pass:
                    self.login_successful.emit()
                    self.close()
                else:
                    QMessageBox.warning(self, "خطا", "اطلاعات ورود اشتباه است.")
        except Exception as e:
            logger.error(f"Login DB Error: {e}")
            # Fallback برای بار اول
            if self.inp_user.text() == "admin" and self.inp_pass.text() == "1234":
                self.login_successful.emit()
                self.close()

# ==============================================================================
# فرایندهای ایزوله ربات‌ها
# ==============================================================================
def run_telegram_bot(token, proxy=None):
    """اجرای ربات تلگرام در پروسس مجزا"""
    if not token: return
    try:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        from telegram.ext import Application
        from telegram import Update
        from bot.loader import setup_application_handlers

        builder = Application.builder().token(token)
        if proxy:
            builder.proxy(proxy).get_updates_proxy(proxy)

        app = builder.build()
        setup_application_handlers(app)
        logging.info(f"🚀 Telegram Bot Process Started (Proxy: {'Yes' if proxy else 'No'})")

        # استفاده از close_loop=False برای جلوگیری از تداخل در بستن پروسس
        app.run_polling(allowed_updates=Update.ALL_TYPES, close_loop=False)
    except Exception as e:
        logging.error(f"Telegram Process Error: {e}")

def run_rubika_bot(token, proxy=None):
    """اجرای ربات روبیکا در پروسس مجزا"""
    if not token: return
    try:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        from rubika_bot.bot_logic import RubikaWorker
        bot = RubikaWorker(token)
        # اعمال پروکسی به کلاینت روبیکا
        bot.api.proxy = proxy

        logging.info(f"🚀 Rubika Bot Process Started (Proxy: {'Yes' if proxy else 'No'})")
        loop.run_until_complete(bot.start_polling())
    except Exception as e:
        logging.error(f"Rubika Process Error: {e}")

# ==============================================================================
# مدیریت برنامه (Application Life Cycle & Watchdog)
# ==============================================================================
class ApplicationManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ApplicationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, loop=None):
        if hasattr(self, '_initialized'): return
        self._initialized = True
        self.loop = loop
        self.window = None
        self.splash = None
        self.tg_process = None
        self.rb_process = None
        self.xray = None
        self.tg_start_time = None
        self.rb_start_time = None

        # تنظیمات سیستم واچ‌داگ
        self.watchdog_timer = QTimer()
        self.watchdog_timer.timeout.connect(self._check_processes_health)

    async def launch(self):
        """اجرای گام‌به‌گام با اسپلش اسکرین"""
        self.splash = ModernSplashScreen()
        self.splash.show()

        # ۱. آماده‌سازی دیتابیس
        self.splash.set_message("در حال بررسی پایگاه داده...", 30)
        try:
            await self.loop.run_in_executor(None, init_db)
            await asyncio.sleep(0.5) # برای جنبه بصری
        except Exception as e:
            logger.error(f"DB Error: {e}")

        # ۲. بررسی پروکسی و Xray
        self.splash.set_message("بررسی تنظیمات اتصال (Xray)...", 60)
        from db.database import get_db
        from config import XRAY_BIN_PATH, XRAY_CONFIG_PATH, DEFAULT_LOCAL_PROXY_PORT
        with next(get_db()) as db:
            active_p = crud.get_active_proxy(db)
            if active_p and active_p.type == 'v2ray':
                self.xray = XrayManager(XRAY_BIN_PATH, XRAY_CONFIG_PATH)
                self.xray.start(active_p.url, DEFAULT_LOCAL_PROXY_PORT)

        # ۳. نمایش دیالوگ لاگین
        self.splash.set_message("در انتظار تایید هویت...", 90)
        self.login = ModernLoginDialog()
        self.login.login_successful.connect(self._after_login)
        self.login.show()

    def _after_login(self):
        """اجرا بعد از ورود موفق کاربر"""
        self.splash.set_message("آماده‌سازی پنل مدیریت...", 100)

        # ۴. ایجاد پنجره اصلی
        self.window = MainWindow(bot_application=None, rubika_client=None)
        self.window.app_manager = self

        # ریستارت سرویس‌ها
        try: self.window.btn_restart_bots.clicked.disconnect()
        except: pass
        self.window.btn_restart_bots.clicked.connect(self.restart_services)

        self.window.show()
        # بازگرداندن رفتار عادی خروج
        QApplication.instance().setQuitOnLastWindowClosed(True)
        self.splash.finish(self.window)

        # ۵. استارت ربات‌های پس‌زمینه
        self.start_background_bots()

        # ۶. فعال‌سازی واچ‌داگ
        self.watchdog_timer.start(10000) # هر ۱۰ ثانیه بررسی سلامت

        # ۷. اتصال کلاینت‌های پنل
        QTimer.singleShot(500, lambda: asyncio.create_task(self.connect_light_clients()))

    def start_background_bots(self):
        """اجرای ربات‌ها (با پشتیبانی از واچ‌داگ و پروکسی محلی)"""
        from db.database import get_db
        with next(get_db()) as db:
            tg_token = crud.get_setting(db, "tg_bot_token", TELEGRAM_BOT_TOKEN)
            rb_token = crud.get_setting(db, "rb_bot_token", RUBIKA_BOT_TOKEN)

            # سلسله مراتب پروکسی: ۱. پروکسی فعال جدید ۲. پروکسی قدیمی ۳. هیچ‌کدام
            proxy = None
            if self.xray:
                 proxy = f"socks5://127.0.0.1:2080"
            else:
                 active_p = crud.get_active_proxy(db)
                 if active_p:
                     proxy = active_p.url
                 else:
                     proxy = crud.get_setting(db, "proxy_url", "")

        if tg_token and (not self.tg_process or not self.tg_process.is_alive()):
            self.tg_process = multiprocessing.Process(
                target=run_telegram_bot, args=(tg_token, proxy), name="TG_Bot", daemon=True
            )
            self.tg_process.start()
            self.tg_start_time = datetime.now()
            logger.info("✅ Telegram Watchdog: Process started")

        if rb_token and (not self.rb_process or not self.rb_process.is_alive()):
            self.rb_process = multiprocessing.Process(
                target=run_rubika_bot, args=(rb_token, proxy), name="RB_Bot", daemon=True
            )
            self.rb_process.start()
            self.rb_start_time = datetime.now()
            logger.info("✅ Rubika Watchdog: Process started")

    def _check_processes_health(self):
        """سیستم واچ‌داگ: بررسی زنده بودن پروسس‌ها"""
        if self.tg_process and not self.tg_process.is_alive():
            logger.warning("⚠️ Telegram Bot crashed! Restarting...")
            self.start_background_bots()

        if self.rb_process and not self.rb_process.is_alive():
            logger.warning("⚠️ Rubika Bot crashed! Restarting...")
            self.start_background_bots()

    def get_bot_stats(self):
        """دریافت آمار مصرف منابع ربات‌ها"""
        import psutil
        res = {"telegram": {"alive": False}, "rubika": {"alive": False}}

        def fill_stats(proc, start_time):
            if proc and proc.is_alive():
                try:
                    p = psutil.Process(proc.pid)
                    uptime = datetime.now() - start_time if start_time else timedelta(0)
                    return {
                        "alive": True,
                        "cpu": p.cpu_percent(interval=0.1),
                        "ram": p.memory_info().rss / (1024 * 1024), # MB
                        "uptime": str(uptime).split('.')[0]
                    }
                except: pass
            return {"alive": False}

        res["telegram"] = fill_stats(self.tg_process, self.tg_start_time)
        res["rubika"] = fill_stats(self.rb_process, self.rb_start_time)
        return res

    def restart_services(self):
        logger.info("Manual Restart triggered...")
        if self.tg_process: self.tg_process.terminate()
        if self.rb_process: self.rb_process.terminate()

        if self.xray:
             self.xray.stop()
             self.xray = None

        # استارت مجدد Xray اگر پروکسی فعال جدید V2Ray است
        from db.database import get_db
        from config import XRAY_BIN_PATH, XRAY_CONFIG_PATH, DEFAULT_LOCAL_PROXY_PORT
        with next(get_db()) as db:
            active_p = crud.get_active_proxy(db)
            if active_p and active_p.type == 'v2ray':
                self.xray = XrayManager(XRAY_BIN_PATH, XRAY_CONFIG_PATH)
                self.xray.start(active_p.url, DEFAULT_LOCAL_PROXY_PORT)

        QTimer.singleShot(2000, self.start_background_bots)
        self.window.show_toast("تمام سرویس‌ها بازنشانی شدند.")

    async def connect_light_clients(self):
        """اتصال کلاینت‌های سبک برای پنل (UI)"""
        from db.database import get_db
        with next(get_db()) as db:
            tg_token = crud.get_setting(db, "tg_bot_token", TELEGRAM_BOT_TOKEN)
            rb_token = crud.get_setting(db, "rb_bot_token", RUBIKA_BOT_TOKEN)

            # تنظیم پروکسی برای کلاینت‌های داخلی پنل
            proxy_url = None
            if self.xray:
                proxy_url = "socks5://127.0.0.1:2080"
            else:
                active_p = crud.get_active_proxy(db)
                proxy_url = active_p.url if active_p else crud.get_setting(db, "proxy_url", None)

        if tg_token:
            try:
                builder = Application.builder().token(tg_token)
                if proxy_url: builder.proxy(proxy_url).get_updates_proxy(proxy_url)
                tg_light = builder.build()
                await asyncio.wait_for(tg_light.initialize(), timeout=5.0)
                self.window.bot_application = tg_light
            except Exception as e: logger.warning(f"Panel TG Client Error: {e}")

        if rb_token:
            try:
                self.window.rubika_client = RubikaAPI(rb_token, proxy=proxy_url)
                logger.info("Panel Rubika Client Connected")
            except Exception as e: logger.warning(f"Panel RB Client Error: {e}")

        if hasattr(self.window, '_safe_check_connection'):
            self.window._safe_check_connection()

    async def shutdown(self):
        logger.info("Graceful Shutdown Initiated...")
        self.watchdog_timer.stop()
        if self.tg_process: self.tg_process.terminate()
        if self.rb_process: self.rb_process.terminate()
        if self.xray: self.xray.stop()

        # بستن صحیح سشن‌های دیتابیس
        from db.database import SessionLocal
        SessionLocal.remove()

        self.loop.stop()

def main():
    multiprocessing.freeze_support()

    # ۰. جلوگیری از اجرای چندباره
    if is_already_running():
        # نمایش پیام ساده قبل از استارت اپلیکیشن
        temp_app = QApplication(sys.argv)
        QMessageBox.critical(None, "خطا", "یک نسخه از برنامه در حال اجرا است.")
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    # جلوگیری از بسته شدن خودکار با بسته شدن دیالوگ لاگین
    app.setQuitOnLastWindowClosed(False)

    manager = ApplicationManager(loop)
    app.lastWindowClosed.connect(lambda: asyncio.create_task(manager.shutdown()))

    loop.create_task(manager.launch())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()