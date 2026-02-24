import asyncio
import threading
import traceback
import contextvars
import logging
from typing import Any, Callable, Optional, Generator, Union
from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt

logger = logging.getLogger("AsyncWorker")

class AsyncWorker(QObject):
    """
    کارگر غیرهمگام (Async Worker) پیشرفته و ایمن برای PyQt6.
    تمامی قابلیت‌های نسخه اصلی از جمله پشتیبانی از Generatorها و ContextVars حفظ شده است.
    """

    # سیگنال‌ها (ارتباط با محیط UI)
    started = pyqtSignal()
    finished = pyqtSignal(object)      # بازگشت نتیجه نهایی
    progress = pyqtSignal(object)      # گزارش پیشرفت (عدد، متن، یا تاپل)
    error = pyqtSignal(object)         # ارسال خطا
    cancelled = pyqtSignal()

    def __init__(self, async_func: Callable, *args: Any, **kwargs: Any):
        super().__init__()
        self.async_func = async_func
        self.args = args
        self.kwargs = kwargs
        
        # حفظ کانتکست فعلی (بسیار حیاتی برای SQLAlchemy و جلوگیری از خطای Thread local)
        self.context = contextvars.copy_context()
        
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._task: Optional[asyncio.Task] = None
        self._is_cancelled = False
        self._thread: Optional[QThread] = None
        self._lock = threading.Lock()

    def run(self) -> None:
        """نقطه ورود اجرا در ترد جدید"""
        if self.check_cancelled():
            return

        self.started.emit()

        try:
            # ایجاد لوپ اختصاصی برای این ترد
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

            # اجرای تابع در کانتکست کپی شده (ContextVars Support)
            async def wrapped_task():
                if asyncio.iscoroutinefunction(self.async_func):
                    return await self.async_func(*self.args, **self.kwargs)
                else:
                    # اگر تابع معمولی بود اما قرار بود در ترد اجرا شود
                    return self.async_func(*self.args, **self.kwargs)

            self._task = self._loop.create_task(wrapped_task(), name="AsyncWorkerTask")
            
            # اجرای تسک و مدیریت جنراتورها (پشتیبانی کامل از Async Generator برای Progress)
            result = self._loop.run_until_complete(self._task)
            
            # بررسی اینکه آیا خروجی یک جنراتور ناهمگام است (برای yield کردن Progress)
            if hasattr(result, '__aiter__'):
                self._loop.run_until_complete(self._consume_generator(result))
                result = None # در حالت جنراتور، نتیجه نهایی معمولاً در yieldهاست

            if not self.check_cancelled():
                self.finished.emit(result)

        except asyncio.CancelledError:
            if not self._is_cancelled:
                self.error.emit(Exception("عملیات به صورت غیرمنتظره متوقف شد."))
            else:
                self.cancelled.emit()
        except Exception as e:
            if not self.check_cancelled():
                logger.error(f"AsyncWorker Critical Error: {e}", exc_info=True)
                self.error.emit(e)
        finally:
            self._cleanup()

    async def _consume_generator(self, agen):
        """مصرف‌کننده جنراتور ناهمگام برای ارسال سیگنال‌های progress"""
        try:
            async for item in agen:
                if self._is_cancelled:
                    break
                if item is not None:
                    self.progress.emit(item)
        except Exception as e:
            logger.error(f"Generator Consumption Error: {e}")
            raise e

    def auto_start(self, thread_name: str = "AsyncWorkerThread"):
        """ساخت ترد، انتقال ورکر و استارت خودکار (با رعایت ایمنی ترد)"""
        self._thread = QThread()
        self._thread.setObjectName(thread_name)
        self.moveToThread(self._thread)
        
        self._thread.started.connect(self.run)
        
        # استفاده از QueuedConnection برای اطمینان از انتقال صحیح سیگنال بین تردها
        self.finished.connect(self._stop_thread, Qt.ConnectionType.QueuedConnection)
        self.error.connect(self._stop_thread, Qt.ConnectionType.QueuedConnection)
        self.cancelled.connect(self._stop_thread, Qt.ConnectionType.QueuedConnection)
        
        self._thread.start()

    def cancel(self) -> None:
        """درخواست لغو عملیات (Thread-Safe)"""
        with self._lock:
            self._is_cancelled = True

        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._cancel_task_internal)

    def _cancel_task_internal(self):
        if self._task and not self._task.done():
            self._task.cancel()

    def check_cancelled(self) -> bool:
        with self._lock:
            return self._is_cancelled

    def _cleanup(self):
        """پاکسازی منابع و بستن لوپ"""
        try:
            if self._loop and not self._loop.is_closed():
                pending = asyncio.all_tasks(self._loop)
                if pending:
                    for task in pending: task.cancel()
                    self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                self._loop.close()
        except Exception as e:
            logger.warning(f"AsyncWorker cleanup warning: {e}")
        finally:
            self._loop = None
            self._task = None

    def _stop_thread(self):
        """توقف نهایی ترد و حذف ایمن از حافظه"""
        if self._thread:
            self._thread.quit()
            # حذف آبجکت از حافظه برای جلوگیری از Memory Leak
            self.deleteLater()

    def __del__(self):
        """جلوگیری از باقی‌ماندن تردهای یتیم در حافظه"""
        if hasattr(self, '_thread') and self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()

# ==============================================================================
# Helper Function (نسخه بهینه شده)
# ==============================================================================
def run_async(func: Callable, *args, on_success=None, on_error=None, on_progress=None, **kwargs):
    """
    اجرای سریع یک تسک ناهمگام.
    پشتیبانی کامل از توابع async، توابع معمولی و Async Generators.
    """
    worker = AsyncWorker(func, *args, **kwargs)

    if on_success:
        worker.finished.connect(on_success)
    if on_error:
        worker.error.connect(on_error)
    if on_progress:
        worker.progress.connect(on_progress)
        
    worker.auto_start()
    return worker