import logging
import asyncio
from bot import responses
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from bot.error_handler import global_error_handler
from bot.handlers import (
    start,
    products_handler,
    search_handler,
    cart_handler,
    main_menu_handler
)
from db.database import get_db
from db import crud

logger = logging.getLogger(__name__)

async def _global_text_handler(update, context):
    """بررسی کلمات کلیدی برای پاسخ خودکار و منوی اصلی"""
    if not update.message or not update.message.text: return

    text = update.message.text.strip()
    user_id = update.effective_user.id

    # ذخیره آخرین پیام در دیتابیس برای CRM
    with next(get_db()) as db:
        crud.update_user_info(db, user_id, last_interaction_text=text)
    # نادیده گرفتن دستورات
    if text.startswith('/'): return

    # ۱. مسیریابی دکمه‌های منوی ثابت (Persistent Menu)
    if text == responses.PRODUCTS_BUTTON:
        return await products_handler.list_categories(update, context)
    elif text == responses.CART_BUTTON:
        return await cart_handler.view_cart(update, context)
    elif text == responses.SEARCH_BUTTON:
        # هندلر گفتگو (ConversationHandler) در search_handler این مورد را مدیریت می‌کند.
        # اما برای اطمینان و جلوگیری از تداخل با بقیه متون:
        return
    elif text == responses.USER_PROFILE_BUTTON:
        return await main_menu_handler.handle_user_profile(update, context)
    elif text == responses.SUPPORT_BUTTON:
        return await main_menu_handler.handle_support(update, context)
    elif text == responses.ABOUT_US_BUTTON:
        return await main_menu_handler.handle_about_us(update, context)

    # ۲. پاسخگوی خودکار هوشمند
    with next(get_db()) as db:
        response = crud.get_auto_reply(db, text)
        if response:
            # نمایش حالت Typing برای واقعی‌تر شدن
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            await asyncio.sleep(0.5)
            await update.message.reply_text(response, parse_mode='HTML')

async def _unknown_callback(update, context):
    """جلوگیری از نمایش آیکون لودینگ روی دکمه‌هایی که هندلر ندارند"""
    query = update.callback_query
    await query.answer("⚠️ این بخش در حال بروزرسانی است.")

def setup_application_handlers(app: Application, admin_handler=None):
    """
    ثبت مرکزی تمام هندلرهای ربات با رعایت سلسله‌مراتب اولویت.
    """
    logger.info("Configuring bot handlers and routers...")

    # ==================================================================
    # 1. هندلرهای مکالمه (Conversation Handlers) - اولویت ۱
    # ==================================================================
    # این موارد باید حتماً قبل از هندلرهای Callback معمولی باشند
    app.add_handler(search_handler.search_conversation_handler)
    app.add_handler(cart_handler.checkout_conversation_handler)

    # ==================================================================
    # 2. نقطه شروع و منوی اصلی - اولویت ۲
    # ==================================================================
    app.add_handler(start.start_handler) # دستور /start
    app.add_handler(CallbackQueryHandler(start.start, pattern=r"^main_menu$"))

    # ==================================================================
    # 3. مدیریت محصولات و دسته‌بندی‌ها - اولویت ۳
    # ==================================================================
    # لیست دسته‌بندی‌ها (اصلی، زیرمجموعه و بازگشت)
    app.add_handler(CallbackQueryHandler(
        products_handler.list_categories,
        pattern=r"^(products|cat:list:|cat:back:)"
    ))

    # لیست محصولات و مدیریت صفحه‌بندی
    app.add_handler(CallbackQueryHandler(
        products_handler.list_products,
        pattern=r"^(prod:list:|noop)$"
    ))

    # نمایش جزئیات کامل یک محصول
    app.add_handler(CallbackQueryHandler(
        products_handler.show_product_details,
        pattern=r"^prod:show:\d+$"
    ))

    # عملیات‌های تعاملی محصول
    app.add_handler(CallbackQueryHandler(products_handler.toggle_favorite_handler, pattern=r"^fav:toggle:\d+$"))
    app.add_handler(CallbackQueryHandler(products_handler.show_favorites, pattern=r"^favorites$"))
    app.add_handler(CallbackQueryHandler(products_handler.notify_me_handler, pattern=r"^notify:\d+$"))

    # انتخاب متغیرها (رنگ/سایز)
    app.add_handler(CallbackQueryHandler(products_handler.start_attribute_selection, pattern=r"^attr:start:\d+$"))
    app.add_handler(CallbackQueryHandler(products_handler.confirm_attribute_selection, pattern=r"^attr:sel:\d+:\w+$"))

    # ==================================================================
    # 4. سبد خرید (Shopping Cart) - اولویت ۴
    # ==================================================================
    app.add_handler(CallbackQueryHandler(cart_handler.view_cart, pattern=r"^cart:view$"))
    app.add_handler(CallbackQueryHandler(cart_handler.add_to_cart_handler, pattern=r"^cart:add:\d+$"))
    # پشتیبانی از update و upd (کوتاه شده برای محدودیت بایت تلگرام)
    app.add_handler(CallbackQueryHandler(cart_handler.update_cart_item_handler, pattern=r"^cart:upd(ate)?:"))
    app.add_handler(CallbackQueryHandler(cart_handler.clear_cart_handler, pattern=r"^cart:clear$"))

    # ==================================================================
    # 5. پروفایل و صفحات ثابت - اولویت ۵
    # ==================================================================
    app.add_handler(CallbackQueryHandler(main_menu_handler.handle_user_profile, pattern=r"^user_profile$"))
    app.add_handler(CallbackQueryHandler(main_menu_handler.handle_order_history, pattern=r"^order_history$"))

    # مدیریت آدرس‌ها
    app.add_handler(CallbackQueryHandler(main_menu_handler.handle_user_addresses, pattern=r"^user_addresses$"))
    app.add_handler(CallbackQueryHandler(main_menu_handler.handle_delete_address, pattern=r"^addr_del:\d+$"))

    # بخش‌های اطلاع‌رسانی
    app.add_handler(CallbackQueryHandler(main_menu_handler.handle_special_offers, pattern=r"^special_offers$"))
    app.add_handler(CallbackQueryHandler(main_menu_handler.handle_track_order, pattern=r"^track_order$"))
    app.add_handler(CallbackQueryHandler(main_menu_handler.handle_support, pattern=r"^support$"))
    app.add_handler(CallbackQueryHandler(main_menu_handler.handle_about_us, pattern=r"^about_us$"))

    # ==================================================================
    # 6. هندلرهای عمومی و پاسخ خودکار - اولویت ۶
    # ==================================================================
    # هندلر پاسخ خودکار هوشمند (باید قبل از unknown_callback باشد)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _global_text_handler))

    if admin_handler:
        # مدیریت تایید/رد/ارسال سفارش از داخل تلگرام توسط ادمین
        app.add_handler(CallbackQueryHandler(admin_handler, pattern=r"^adm_(approve|reject|ship):"))

    # هندلر فال‌بک برای کال‌بک‌های تعریف نشده (بسیار مهم برای UX)
    app.add_handler(CallbackQueryHandler(_unknown_callback, pattern=r".*"))

    # ==================================================================
    # 7. مدیریت خطا (Global Error Handler) - همیشه آخرین مورد
    # ==================================================================
    app.add_error_handler(global_error_handler)

    logger.info("✅ All bot routes and handlers synchronized.")
