import logging
import html
import json
import traceback
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.error import Forbidden, BadRequest
from config import ADMIN_USER_IDS

logger = logging.getLogger(__name__)

async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    هندلر سراسری خطاها با قابلیت گزارش‌دهی هوشمند به ادمین‌ها.
    """
    # 1. ثبت خطا در فایل لاگ با جزئیات کامل (برای بررسی‌های فنی بعدی)
    logger.error("Exception while handling an update:", exc_info=context.error)

    # 2. استخراج Traceback (مسیر خطا در کد)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # 3. دریافت اطلاعات آپدیت (چه اتفاقی افتاد که خطا رخ داد؟)
    update_str = "N/A"
    if isinstance(update, Update):
        try:
            # تبدیل آپدیت به دیکشنری و سپس جیسون خوانا
            update_dict = update.to_dict()
            update_str = json.dumps(update_dict, indent=2, ensure_ascii=False, default=str)
        except Exception:
            update_str = str(update)

    # 4. آماده‌سازی پیام گزارش برای ادمین‌ها
    # محدودیت کاراکتر تلگرام را رعایت می‌کنیم (۴۰۹۶ کاراکتر)
    # بخش‌های مختلف را جداگانه اسکیپ (Escape) می‌کنیم تا HTML خراب نشود

    error_message = str(context.error)
    # کوتاه کردن تریس‌بک برای جا شدن در پیام
    short_tb = tb_string[-2000:] if len(tb_string) > 2000 else tb_string
    short_update = update_str[:1000] if len(update_str) > 1000 else update_str

    report_text = (
        f"🚨 <b>گزارش خطای سیستم</b>\n\n"
        f"❓ <b>نوع خطا:</b>\n<code>{html.escape(error_message)}</code>\n\n"
        f"👤 <b>کاربر:</b>\n<code>{update.effective_user.id if update and update.effective_user else 'ناشناس'} "
        f"({html.escape(update.effective_user.full_name if update and update.effective_user else 'None')})</code>\n\n"
        f"📝 <b>اطلاعات آپدیت (خلاصه):</b>\n<pre>{html.escape(short_update)}</pre>\n\n"
        f"💻 <b>Traceback:</b>\n<pre>{html.escape(short_tb)}</pre>"
    )

    # 5. ارسال گزارش به تمام ادمین‌ها (با مدیریت خطا)
    for admin_id in ADMIN_USER_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=report_text,
                parse_mode=ParseMode.HTML
            )
        except Forbidden:
            logger.warning(f"Admin {admin_id} has blocked the bot. Cannot send error report.")
        except BadRequest as e:
            logger.error(f"Failed to send error report to {admin_id} due to format: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while notifying admin {admin_id}: {e}")

    # 6. اطلاع‌رسانی مودبانه به کاربر (Graceful Failure)
    if isinstance(update, Update):
        # الف) اگر خطا روی دکمه شیشه‌ای بود، لودینگ دکمه را متوقف کن
        if update.callback_query:
            try:
                await update.callback_query.answer(
                    "⚠️ متاسفانه خطایی در پردازش رخ داد. ادمین مطلع شد.",
                    show_alert=True
                )
            except Exception:
                pass

        # ب) ارسال پیام متنی عذرخواهی
        user_msg = (
            "⚠️ <b>متاسفانه مشکلی در پردازش درخواست شما پیش آمد.</b>\n\n"
            "نگران نباشید! گزارش این خطا به صورت خودکار برای تیم فنی ارسال شد.\n"
            "لطفاً لحظاتی دیگر مجدداً تلاش کنید یا از دستور /start استفاده کنید."
        )
        try:
            if update.effective_message:
                await update.effective_message.reply_text(
                    user_msg,
                    parse_mode=ParseMode.HTML
                )
        except Exception:
            # اگر نتوانیم به کاربر پیام دهیم (مثلاً ربات را بلاک کرده باشد)، نادیده می‌گیریم
            pass