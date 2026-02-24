import asyncio
import logging
import traceback
import sys
from typing import Callable, Any, TypeVar, Optional
from db.database import SessionLocal

logger = logging.getLogger("DB_Utils")

# تعریف TypeVar برای حفظ تایپ خروجی توابع (برای راهنمای کدنویسی در IDE)
T = TypeVar("T")

# انتخاب بهترین روش برای تبدیل Sync به Async بر اساس نسخه پایتون
if sys.version_info >= (3, 9):
    to_thread = asyncio.to_thread
else:
    # جایگزین برای نسخه‌های قدیمی‌تر (استفاده از ThreadPoolExecutor پیش‌فرض)
    async def to_thread(func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

async def run_db(
    func: Callable[..., T],
    *args: Any,
    timeout: Optional[float] = 30.0,
    **kwargs: Any
) -> T:
    """
    اجرای توابع دیتابیس (Sync) در ترد جداگانه (Async) برای جلوگیری از هنگ کردن ربات.
    
    این تابع یک سشن دیتابیس ایجاد کرده، آن را به عنوان اولین ورودی به تابع 
    مورد نظر (func) پاس می‌دهد و پس از پایان کار، سشن را می‌بندد.

    :param func: تابعی از لایه CRUD که ورودی اول آن 'db' است.
    :param args: سایر ورودی‌های موقعیتی تابع.
    :param timeout: حداکثر زمان مجاز برای اجرای عملیات (ثانیه).
    :param kwargs: سایر ورودی‌های نام‌دار تابع.
    :return: نتیجه خروجی تابع اجرا شده.
    """
    
    def sync_wrapper():
        # ایجاد سشن جدید مخصوص این ترد
        db = SessionLocal()
        try:
            # اجرای تابع و تزریق دیتابیس
            result = func(db, *args, **kwargs)
            return result
        except Exception as e:
            # ثبت دقیق خطا در لاگ
            logger.error(f"❌ Database Error in '{func.__name__}': {e}")
            # در حالت Debug تریس‌بک کامل چاپ شود
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(traceback.format_exc())
            # بازگشت خطا به سمت هندلر ربات برای اطلاع‌رسانی به کاربر
            raise e
        finally:
            # بستن حتمی سشن برای جلوگیری از نشت حافظه (Memory Leak)
            db.close()

    # اجرای لفافه (Wrapper) در ترد جداگانه
    try:
        if timeout:
            return await asyncio.wait_for(to_thread(sync_wrapper), timeout=timeout)
        else:
            return await to_thread(sync_wrapper)
            
    except asyncio.TimeoutError:
        logger.error(f"⏰ Database Timeout in '{func.__name__}' after {timeout}s")
        raise Exception("عملیات پایگاه داده بیش از حد طول کشید.")
    except Exception as e:
        # خطاهای دیگر که از سمت دیتابیس بالا آمده‌اند
        raise e

# --- توابع کاربردی جانبی ---

async def sleep_async(seconds: float):
    """جایگزین ایمن برای time.sleep در محیط‌های Async"""
    await asyncio.sleep(seconds)

def shorten_text(text: str, max_length: int = 50) -> str:
    """کوتاه کردن متن‌های طولانی برای نمایش در دکمه‌ها یا گزارشات"""
    if not text:
        return ""
    return (text[:max_length] + '...') if len(text) > max_length else text