import logging
import asyncio
from pathlib import Path
from telegram import Update, constants
from telegram.ext import ContextTypes, CommandHandler
from telegram.error import BadRequest

from bot import responses, keyboards
from bot.utils import run_db
from db import crud
from config import BASE_DIR

logger = logging.getLogger("StartHandler")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    هندلر اصلی دستور /start و دکمه بازگشت به خانه.
    مدیریت لینک‌های مستقیم محصولات و نمایش منوی اصلی.
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    query = update.callback_query

    if not user:
        return

    # ۱. پردازش Deep Linking (ورود مستقیم به صفحه محصول)
    # مثال: t.me/bot?start=p_12
    if context.args and context.args[0].startswith('p_'):
        try:
            prod_id = int(context.args[0].replace('p_', ''))
            # شبیه‌سازی یک CallbackQuery برای استفاده از هندلر جزئیات محصول
            from bot.handlers.products_handler import show_product_details
            
            # ذخیره دیتای محصول در آبجکت موقت جهت پردازش در products_handler
            fake_update = update
            if not fake_update.callback_query:
                fake_update.callback_query = type('FakeQuery', (object,), {
                    'data': f"prod:show:{prod_id}",
                    'answer': lambda *a, **k: None,
                    'message': update.message,
                    'from_user': user
                })
            
            await show_product_details(fake_update, context)
            return
        except (ValueError, IndexError):
            pass # در صورت بروز خطا در آیدی، منوی اصلی نمایش داده می‌شود

    # ۲. دریافت اطلاعات مورد نیاز به صورت موازی (بهبود چشمگیر سرعت لود)
    try:
        tasks = [
            run_db(crud.get_or_create_user, user.id, user.full_name or "کاربر", user.username, "telegram"),
            run_db(crud.get_setting, "tg_shop_name", "فروشگاه"),
            run_db(crud.get_setting, "tg_is_open", "true"),
            run_db(crud.get_setting, "tg_welcome_message", ""),
            run_db(crud.get_setting, "tg_welcome_image", ""),
            run_db(crud.get_setting, "channel_link", ""),
            run_db(crud.get_user_stats, user.id)
        ]
        results = await asyncio.gather(*tasks)
        
        db_user, shop_name, is_open, welcome_tpl, banner_rel, channel_url, stats = results
    except Exception as e:
        logger.error(f"Error in Start-Gather: {e}")
        await context.bot.send_message(chat_id=chat_id, text="⚠️ خطا در ارتباط با سرور. لطفاً مجدداً /start کنید.")
        return

    # ۳. آماده‌سازی محتوای پیام
    welcome_text = welcome_tpl if welcome_tpl else responses.WELCOME_MESSAGE
    
    # جایگزینی متغیرهای داینامیک در متن (نام کاربر، تعداد سفارشات و...)
    dynamic_data = {
        "user_name": user.first_name or "کاربر",
        "shop_name": shop_name,
        "order_count": stats.get("total_orders", 0),
        "total_spent": stats.get("total_spent", 0)
    }
    welcome_text = responses.format_dynamic_text(welcome_text, dynamic_data)

    # افزودن فوتر برندینگ
    from bot.utils import get_branded_text
    welcome_text = await get_branded_text(welcome_text)

    # افزودن هشدار وضعیت فروشگاه
    if str(is_open).lower() == "false":
        welcome_text += f"\n\n{responses.get_divider()}\n⛔️ <b>در حال حاضر فروشگاه بسته است و سفارش جدید ثبت نمی‌شود.</b>"

    # آماده‌سازی کیبورد و تصویر بنر
    kbd = keyboards.get_main_menu_keyboard(channel_url=channel_url)
    banner_full_path = (Path(BASE_DIR) / banner_rel) if banner_rel else None
    has_valid_banner = banner_full_path and banner_full_path.exists()

    # ۴. مدیریت ارسال یا ویرایش پیام (منطق هوشمند مدیا)
    if query:
        await query.answer()

    try:
        if has_valid_banner:
            # اگر بنر داریم:
            with open(banner_full_path, 'rb') as photo:
                if query and query.message:
                    # در تلگرام نمی‌توان پیام متنی را به عکس‌دار ادیت کرد؛ پس پیام قبلی حذف و جدید ارسال می‌شود
                    await query.message.delete()
                
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=welcome_text,
                    reply_markup=kbd,
                    parse_mode=constants.ParseMode.HTML
                )
        else:
            # اگر بنر نداریم (فقط متن):
            if query and query.message:
                if query.message.photo:
                    # اگر پیام قبلی عکس‌دار بود، آن را حذف کن (چون ادیت عکس به متن مقدور نیست)
                    await query.message.delete()
                    await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=kbd, parse_mode=constants.ParseMode.HTML)
                else:
                    # اگر پیام قبلی هم متنی بود، به راحتی ادیت کن
                    await query.edit_message_text(text=welcome_text, reply_markup=kbd, parse_mode=constants.ParseMode.HTML)
            else:
                # پیام جدید
                await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=kbd, parse_mode=constants.ParseMode.HTML)

    except BadRequest as e:
        if "Message is not modified" not in str(e):
            logger.error(f"Start Send Error: {e}")
            await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=kbd, parse_mode=constants.ParseMode.HTML)

# تعریف هندلر برای ثبت در loader
start_handler = CommandHandler("start", start)