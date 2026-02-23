import sys
import os
import asyncio
import logging
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
from config import TELEGRAM_BOT_TOKEN, LOG_DIR, RUBIKA_BOT_TOKEN, PROXY_URL, ADMIN_USER_IDS
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
def run_telegram_bot(token, proxy=None, admin_ids=None):
    """اجرای ربات تلگرام در پروسه مجزا با مدیریت دستی حلقه برای پایداری در ویندوز"""
    if not token: return

    # تزریق تنظیمات به ماژول کانفیگ در پروسه جدید
    import config
    config.TELEGRAM_BOT_TOKEN = token
    config.PROXY_URL = proxy
    if admin_ids: config.ADMIN_USER_IDS = admin_ids

    from config import setup_logging
    setup_logging()

    from telegram.ext import Application
    from telegram import Update
    from bot.loader import setup_application_handlers

    # ساخت حلقه رویداد جدید برای پروسه فرزند
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def main_loop():
        try:
            builder = Application.builder().token(token)
            if proxy:
                builder.proxy_url(proxy)
                builder.get_updates_proxy_url(proxy)
                logger.info(f"Using Proxy: {proxy}")

            app = builder.build()
            setup_application_handlers(app)

            logger.info("✅ Telegram Bot Process Starting Polling...")
            # استفاده از run_polling با تنظیمات ایمن برای ساب‌پروسس
            # stop_signals=None باعث می‌شود PTB سعی نکند هندلر سیگنال نصب کند (که در ترد/پروسه فرعی خطا می‌دهد)
            # close_loop=False اجازه می‌دهد خودمان حلقه را مدیریت کنیم
            await app.run_polling(
                allowed_updates=Update.ALL_TYPES,
                stop_signals=None,
                close_loop=False
            )

        except asyncio.CancelledError:
            logger.info("TG Bot Process Cancelled")
        except Exception as e:
            logger.error(f"TG Bot Fatal Error: {e}")

    try:
        loop.run_until_complete(main_loop())
    except Exception as e:
        logger.error(f"TG Process Loop Exception: {e}")

# ==============================================================================
# ترد ایزوله روبیکا
# ==============================================================================
def run_rubika_bot(token, proxy=None, admin_ids=None):
    """اجرای ربات روبیکا در پروسه مجزا"""
    if not token: return

    import config
    config.RUBIKA_BOT_TOKEN = token
    if admin_ids: config.ADMIN_USER_IDS = admin_ids

    from config import setup_logging
    setup_logging()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = RubikaWorker(token, proxy=proxy)
        logger.info("✅ Rubika Bot Process Started")
        loop.run_until_complete(bot.start_polling())
    except Exception as e:
        logger.error(f"Rubika Process Error: {e}")
# ==============================================================================
# مدیریت برنامه
# ==============================================================================
from bot.proxy_utils import XrayManager, parse_v2ray_link

class ApplicationManager:
    def __init__(self, loop):
        self.loop = loop
        self.window = None
        self.tg_process = None
        self.rb_process = None
        self.xray_manager = XrayManager()
        self._is_shutting_down = False

    async def _load_db_config(self):
        """بارگذاری تنظیمات حساس و سیستم هوشمند پروکسی از دیتابیس"""
        from db.database import SessionLocal
        from db import crud
        import config

        try:
            def fetch():
                with SessionLocal() as db:
                    active_proxy = crud.get_active_proxy(db)
                    proxy_str = None
                    if active_proxy:
                        if active_proxy.raw_link:
                            proxy_str = active_proxy.raw_link
                        else:
                            proxy_str = f"{active_proxy.protocol}://"
                            if active_proxy.username and active_proxy.password:
                                proxy_str += f"{active_proxy.username}:{active_proxy.password}@"
                            proxy_str += f"{active_proxy.host}:{active_proxy.port}"

                    return {
                        "tg_token": crud.get_setting(db, "telegram_bot_token"),
                        "rb_token": crud.get_setting(db, "rubika_bot_token"),
                        "proxy_url_v2": proxy_str,
                        "proxy_url_v1": crud.get_setting(db, "proxy_url"),
                        "proxy_enabled": crud.get_setting(db, "proxy_enabled", "false") == "true",
                        "admin_ids": crud.get_admin_ids(db)
                    }

            db_conf = await self.loop.run_in_executor(None, fetch)

            if db_conf["tg_token"]:
                config.TELEGRAM_BOT_TOKEN = db_conf["tg_token"]
                global TELEGRAM_BOT_TOKEN
                TELEGRAM_BOT_TOKEN = db_conf["tg_token"]

            if db_conf["rb_token"]:
                config.RUBIKA_BOT_TOKEN = db_conf["rb_token"]
                global RUBIKA_BOT_TOKEN
                RUBIKA_BOT_TOKEN = db_conf["rb_token"]

            if db_conf["admin_ids"]:
                config.ADMIN_USER_IDS = db_conf["admin_ids"]
                global ADMIN_USER_IDS
                ADMIN_USER_IDS = db_conf["admin_ids"]

            # اولویت با پروکسی پیشرفته (v2) است، اگر نبود از v1 استفاده می‌شود
            base_proxy = db_conf["proxy_url_v2"] or (db_conf["proxy_url_v1"] if db_conf["proxy_enabled"] else None)
            final_proxy = None

            # مدیریت لینک‌های V2Ray
            if base_proxy and any(proto in base_proxy for proto in ["vless://", "vmess://", "ss://", "trojan://"]):
                if self.xray_manager.is_available():
                    logger.info("Starting Xray bridge for V2Ray link...")
                    proxy_data = parse_v2ray_link(base_proxy)
                    if proxy_data:
                        try:
                            self.xray_manager.stop()
                            final_proxy = await self.xray_manager.start(proxy_data)
                            logger.info(f"Xray bridge started at {final_proxy}")
                        except Exception as e:
                            logger.error(f"Failed to start Xray bridge: {e}")
                            final_proxy = None
                else:
                    logger.warning("V2Ray link detected but Xray core is not available. Please place xray.exe in tools/xray/")
                    final_proxy = None
            else:
                # پروکسی استاندارد
                self.xray_manager.stop()
                final_proxy = base_proxy

            global PROXY_URL
            if final_proxy:
                config.PROXY_URL = final_proxy
                PROXY_URL = final_proxy
                logger.info(f"Connected using dynamic proxy: {final_proxy}")
            else:
                config.PROXY_URL = None
                PROXY_URL = None

        except Exception as e:
            logger.error(f"Error loading DB config: {e}")

    async def launch(self, app):
        """راه‌اندازی سریع پنل"""
        # ۱. دیتابیس
        try:
            await self.loop.run_in_executor(None, init_db)
        except Exception as e:
            logger.error(f"DB Error: {e}")

        # بارگذاری تنظیمات از دیتابیس
        await self._load_db_config()

        # ۲. بررسی رمز عبور (Login)
        if not await self.show_login():
            await self.shutdown()
            return

        # ۳. ایجاد پنجره
        self.window = MainWindow(bot_application=None, rubika_client=None)
        # تزریق منیجر برای عملیات سیستمی
        self.window.app_manager = self
        self.window.show()

        # بازگرداندن رفتار استاندارد برای خروج
        app.setQuitOnLastWindowClosed(True)

        # ۴. اتصال سیگنال بستن نهایی بعد از نمایش پنجره اصلی
        app.lastWindowClosed.connect(lambda: asyncio.create_task(self.shutdown()))
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
        """اجرای ربات‌ها در پروسه‌های مجزا برای پایداری بیشتر (Process Isolation)"""
        # نکته: در ویندوز حتما باید متد spawn استفاده شود که پیش‌فرض است.

        # استفاده از متغیرهای لوکال که از دیتابیس لود شده‌اند (اطمینان از انتقال به پروسه جدید)
        if TELEGRAM_BOT_TOKEN:
            if self.tg_process and self.tg_process.is_alive():
                logger.info("TG process already running, terminating...")
                self.tg_process.terminate()

            self.tg_process = multiprocessing.Process(
                target=run_telegram_bot,
                args=(TELEGRAM_BOT_TOKEN, PROXY_URL, ADMIN_USER_IDS),
                name="TG_Process",
                daemon=True
            )
            self.tg_process.start()
            logger.info(f"✅ Telegram Bot Process Started (PID: {self.tg_process.pid})")

        if RUBIKA_BOT_TOKEN:
            if self.rb_process and self.rb_process.is_alive():
                logger.info("Rubika process already running, terminating...")
                self.rb_process.terminate()

            self.rb_process = multiprocessing.Process(
                target=run_rubika_bot,
                args=(RUBIKA_BOT_TOKEN, PROXY_URL, ADMIN_USER_IDS),
                name="RB_Process",
                daemon=True
            )
            self.rb_process.start()
            logger.info(f"✅ Rubika Bot Process Started (PID: {self.rb_process.pid})")

    async def restart_services(self):
        """بارگذاری مجدد تنظیمات و راه‌اندازی مجدد سرویس‌ها (Hot Reload)"""
        logger.info("🔄 Restarting services with process isolation...")
        await self._load_db_config()

        # ریستارت کلاینت‌های سبک داخل پنل
        await self.connect_light_clients()

        # ریستارت پروسه‌های پس‌زمینه (بستن قبلی و باز کردن جدید)
        self.start_background_bots()

        if self.window:
            self.window.show_toast("سرویس‌ها با تنظیمات جدید ریستارت شدند.")

    async def connect_light_clients(self):
        """اتصال کلاینت‌های مخصوص ارسال پیام در پنل (با مدیریت خطا)"""
        if self._is_shutting_down: return

        # کلاینت تلگرام برای پنل (فقط جهت ارسال پیام)
        if TELEGRAM_BOT_TOKEN:
            try:
                from telegram import Bot
                from telegram.request import HTTPXRequest

                request = None
                if PROXY_URL:
                    request = HTTPXRequest(proxy_url=PROXY_URL)

                # استفاده از کلاس کمکی برای حفظ سازگاری با کدهای موجود در ویجت‌ها
                class PanelBotWrapper:
                    def __init__(self, bot_obj):
                        self.bot = bot_obj
                    async def initialize(self): pass
                    async def shutdown(self): pass
                    async def stop(self): pass
                    @property
                    def running(self): return True

                bot_obj = Bot(token=TELEGRAM_BOT_TOKEN, request=request)
                await bot_obj.initialize()
                self.window.bot_application = PanelBotWrapper(bot_obj)
                logger.info("✅ Panel Telegram Client Connected (Direct Bot Mode)")
            except Exception as e:
                logger.warning(f"⚠️ Panel Telegram Client failed: {e}")
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
        logger.info("Shutting down Application...")

        # بستن پل Xray
        self.xray_manager.stop()

        # بستن پروسه‌های فرزند
        if self.tg_process and self.tg_process.is_alive():
            self.tg_process.terminate()
        if self.rb_process and self.rb_process.is_alive():
            self.rb_process.terminate()

        if self.window:
            self.window._is_shutting_down = True
            if self.window.bot_application:
                try:
                    # فقط در صورتی stop صدا شود که اپلیکیشن در حال اجرا باشد و updater داشته باشد
                    if self.window.bot_application.running:
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
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    # جلوگیری از بسته شدن خودکار برنامه وقتی دیالوگ لاگین بسته می‌شود
    app.setQuitOnLastWindowClosed(False)

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    manager = ApplicationManager(loop)

    # انتقال مدیریت سیگنال به داخل متد launch
    loop.create_task(manager.launch(app))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()