import logging
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
    main_menu_handler,
    support_handler
)

logger = logging.getLogger(__name__)

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
    app.add_handler(support_handler.support_conversation_handler)

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
    app.add_handler(CallbackQueryHandler(support_handler.support_menu, pattern=r"^support$"))
    app.add_handler(CallbackQueryHandler(support_handler.list_tickets, pattern=r"^ticket:list$"))
    app.add_handler(CallbackQueryHandler(support_handler.show_ticket, pattern=r"^ticket:show:\d+$"))
    app.add_handler(CallbackQueryHandler(main_menu_handler.handle_about_us, pattern=r"^about_us$"))

    # ==================================================================
    # 6. پنل مدیریت و پاکسازی نهایی - اولویت ۶
    # ==================================================================
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