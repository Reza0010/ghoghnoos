import sys
import os
import asyncio
import logging
import threading
import multiprocessing
import warnings
from pathlib import Path
# --- تنظیمات محیطی ---
os.environ["QT_FONT_DPI"] = "96"
os.environ["QT_LOGGING_RULES"] = "qt.qpa.screen=false"
from telegram.warnings import PTBUserWarning
warnings.filterwarnings("ignore", category=PTBUserWarning)
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from config import TELEGRAM_BOT_TOKEN, LOG_DIR, RUBIKA_BOT_TOKEN
from db.database import init_db
from bot.loader import setup_application_handlers
from rubika_bot.bot_logic import RubikaWorker
from rubika_bot.rubika_client import RubikaAPI
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QTimer
    import qasync
    from admin_panel.main_window import MainWindow
    from telegram import Update
    from telegram.ext import Application
except ImportError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
logger = logging.getLogger("Launcher")
# ==============================================================================
# فرایندهای ایزوله ربات‌ها
# ==============================================================================
def run_telegram_bot(token):
    """اجرای ربات تلگرام در پروسس مجزا"""
    if not token: return
    try:
        # در ویندوز/مولتی‌پروسس ممکن است نیاز به تنظیم مجدد لاگر باشد
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        from telegram.ext import Application
        from telegram import Update
        from bot.loader import setup_application_handlers

        app = Application.builder().token(token).build()
        setup_application_handlers(app)
        logging.info("🚀 Telegram Bot Process Started")

        # استفاده از close_loop=False برای جلوگیری از تداخل در بستن پروسس
        app.run_polling(allowed_updates=Update.ALL_TYPES, close_loop=False)
    except Exception as e:
        logging.error(f"Telegram Process Error: {e}")

def run_rubika_bot(token):
    """اجرای ربات روبیکا در پروسس مجزا"""
    if not token: return
    try:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        from rubika_bot.bot_logic import RubikaWorker
        bot = RubikaWorker(token)
        logging.info("🚀 Rubika Bot Process Started")
        loop.run_until_complete(bot.start_polling())
    except Exception as e:
        logging.error(f"Rubika Process Error: {e}")

# ==============================================================================
# مدیریت برنامه
# ==============================================================================
class ApplicationManager:
    def __init__(self, loop):
        self.loop = loop
        self.window = None
        self.tg_process = None
        self.rb_process = None

    async def launch(self):
        """راه‌اندازی سریع پنل"""
        # ۱. دیتابیس (بدون نیاز به شبکه)
        try:
            await self.loop.run_in_executor(None, init_db)
        except Exception as e:
            logger.error(f"DB Error: {e}")
        # ۲. ایجاد پنجره (بلافاصله نمایش داده شود)
        self.window = MainWindow(bot_application=None, rubika_client=None)

        # اتصال دکمه ریستارت پنل به متد مدیریت
        self.window.btn_restart_bots.clicked.disconnect()
        self.window.btn_restart_bots.clicked.connect(self.restart_services)

        self.window.show()
        # ۳. استارت ربات‌های پس‌زمینه
        self.start_background_bots()
        # ۴. تلاش برای اتصال کلاینت‌های پنل (بدون بلاک کردن UI)
        QTimer.singleShot(500, lambda: asyncio.create_task(self.connect_light_clients()))

    def start_background_bots(self):
        """اجرای ربات‌ها در پروسس کاملاً مجزا (Stability)"""
        if TELEGRAM_BOT_TOKEN:
            self.tg_process = multiprocessing.Process(
                target=run_telegram_bot,
                args=(TELEGRAM_BOT_TOKEN,),
                name="TG_Process",
                daemon=True
            )
            self.tg_process.start()
            logger.info(f"✅ Telegram Process PID: {self.tg_process.pid}")

        if RUBIKA_BOT_TOKEN:
            self.rb_process = multiprocessing.Process(
                target=run_rubika_bot,
                args=(RUBIKA_BOT_TOKEN,),
                name="RB_Process",
                daemon=True
            )
            self.rb_process.start()
            logger.info(f"✅ Rubika Process PID: {self.rb_process.pid}")

    def restart_services(self):
        """توقف و اجرای مجدد ربات‌ها بدون بستن پنل"""
        logger.info("Restarting bot services...")
        self.window.show_toast("در حال بازنشانی سرویس‌ها...")

        if self.tg_process and self.tg_process.is_alive():
            self.tg_process.terminate()
        if self.rb_process and self.rb_process.is_alive():
            self.rb_process.terminate()

        # اجرای مجدد با تاخیر کوتاه
        QTimer.singleShot(1500, self.start_background_bots)
        QTimer.singleShot(2000, lambda: self.window.show_toast("سرویس‌ها با موفقیت بازنشانی شدند."))

    async def connect_light_clients(self):
        """اتصال کلاینت‌های مخصوص ارسال پیام در پنل (با مدیریت خطا)"""
        # کلاینت تلگرام برای پنل
        if TELEGRAM_BOT_TOKEN:
            try:
                # ایجاد اپلیکیشن سبک با تایم‌اوت کم
                tg_light = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
                # استفاده از wait_for برای جلوگیری از فریز طولانی در صورت خرابی پروکسی
                await asyncio.wait_for(tg_light.initialize(), timeout=5.0)
                self.window.bot_application = tg_light
                logger.info("✅ Panel Telegram Client Connected")
            except Exception as e:
                logger.warning(f"⚠️ Panel Telegram Client failed (Check Proxy/Internet): {e}")
        # کلاینت روبیکا برای پنل
        if RUBIKA_BOT_TOKEN:
            try:
                rb_light = RubikaAPI(RUBIKA_BOT_TOKEN)
                self.window.rubika_client = rb_light
                logger.info("✅ Panel Rubika Client Connected")
            except Exception as e:
                logger.warning(f"⚠️ Panel Rubika Client failed: {e}")
        # آپدیت آیکون‌های وضعیت در گوشه پنل
        if hasattr(self.window, '_safe_check_connection'):
            self.window._safe_check_connection()

    async def shutdown(self):
        logger.info("Shutting down...")
        if self.tg_process and self.tg_process.is_alive():
            self.tg_process.terminate()
        if self.rb_process and self.rb_process.is_alive():
            self.rb_process.terminate()
        self.loop.stop()

def main():
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    manager = ApplicationManager(loop)
    app.lastWindowClosed.connect(lambda: asyncio.create_task(manager.shutdown()))
    loop.create_task(manager.launch())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()