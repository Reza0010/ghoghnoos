import sys
import os
import asyncio
import logging
import threading
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
    from admin_panel.login_dialog import LoginDialog
    from telegram import Update
    from telegram.ext import Application
except ImportError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
logger = logging.getLogger("Launcher")
# ==============================================================================
# ترد ایزوله تلگرام
# ==============================================================================
def run_telegram_bot():
    if not TELEGRAM_BOT_TOKEN: return
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def run_bot():
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        setup_application_handlers(app)
        await app.initialize()
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("✅ Telegram Bot Thread Started")
        # بیخیال هندل کردن سیگنال در ترد ایزوله
        while True:
            await asyncio.sleep(3600)

    try:
        loop.run_until_complete(run_bot())
    except Exception as e:
        logger.error(f"Telegram Thread Error: {e}")
# ==============================================================================
# ترد ایزوله روبیکا
# ==============================================================================
def run_rubika_bot():
    if not RUBIKA_BOT_TOKEN: return
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = RubikaWorker(RUBIKA_BOT_TOKEN)
        logger.info("✅ Rubika Bot Thread Started")
        loop.run_until_complete(bot.start_polling())
    except Exception as e:
        logger.error(f"Rubika Thread Error: {e}")
# ==============================================================================
# مدیریت برنامه
# ==============================================================================
class ApplicationManager:
    def __init__(self, loop):
        self.loop = loop
        self.window = None
        self.tg_thread = None
        self.rb_thread = None
        self._is_shutting_down = False

    async def launch(self):
        """راه‌اندازی سریع پنل"""
        # ۱. دیتابیس
        try:
            await self.loop.run_in_executor(None, init_db)
        except Exception as e:
            logger.error(f"DB Error: {e}")

        # ۲. بررسی رمز عبور (Login)
        if not await self.show_login():
            await self.shutdown()
            return

        # ۳. ایجاد پنجره
        self.window = MainWindow(bot_application=None, rubika_client=None)
        self.window.show()
        # ۴. استارت ربات‌های پس‌زمینه
        self.start_background_bots()

        # ۵. تلاش برای اتصال کلاینت‌های پنل (بدون بلاک کردن UI)
        QTimer.singleShot(500, lambda: asyncio.create_task(self.connect_light_clients()))

    async def show_login(self) -> bool:
        """نمایش دیالوگ ورود و تایید رمز"""
        def verify(password):
            from db.database import SessionLocal
            from db import crud
            with SessionLocal() as db:
                stored = crud.get_setting(db, "panel_password", "admin")
                return password == stored

        login = LoginDialog(verify)
        return login.exec() == LoginDialog.DialogCode.Accepted

    def start_background_bots(self):
        """اجرای ربات‌ها در ترد کاملاً مجزا"""
        if TELEGRAM_BOT_TOKEN:
            self.tg_thread = threading.Thread(target=run_telegram_bot, daemon=True, name="TG_Thread")
            self.tg_thread.start()
        if RUBIKA_BOT_TOKEN:
            self.rb_thread = threading.Thread(target=run_rubika_bot, daemon=True, name="RB_Thread")
            self.rb_thread.start()

    async def connect_light_clients(self):
        """اتصال کلاینت‌های مخصوص ارسال پیام در پنل (با مدیریت خطا)"""
        if self._is_shutting_down: return
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
        if self._is_shutting_down: return
        self._is_shutting_down = True
        logger.info("Shutting down...")

        if self.window:
            self.window._is_shutting_down = True
            if self.window.bot_application:
                try:
                    await self.window.bot_application.stop()
                    await self.window.bot_application.shutdown()
                except Exception as e:
                    logger.error(f"Error stopping TG client: {e}")
            self.window.close()

        # کنسل کردن تمام تسک‌های در حال اجرا برای جلوگیری از RuntimeError در ویجت‌ها
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()

        if tasks:
            # استفاده از wait با timeout برای جلوگیری از فریز شدن در صورت عدم پاسخ تسک‌ها
            await asyncio.wait(tasks, timeout=2.0)

        self.loop.stop()

def main():
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