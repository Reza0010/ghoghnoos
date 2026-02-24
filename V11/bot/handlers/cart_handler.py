import logging
import json
from telegram import Update, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler, 
    MessageHandler, filters, CommandHandler
)
from telegram.error import BadRequest

from bot.utils import run_db
from db import crud, models
from bot import keyboards, responses
from config import ADMIN_USER_IDS

logger = logging.getLogger("CartHandler")

# وضعیت‌های گفتگوی خرید (Checkout States)
GET_ADDRESS, GET_POSTAL_CODE, GET_PHONE, GET_RECEIPT = range(4)

# ==============================================================================
# توابع کمکی (Helpers)
# ==============================================================================
async def _safe_edit(update: Update, text: str, reply_markup: InlineKeyboardMarkup = None):
    """ویرایش ایمن پیام برای جلوگیری از خطای تلگرام"""
    query = update.callback_query
    try:
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            # اگر پیام عکس‌دار بود یا قابل ویرایش نبود، پیام جدید بفرست
            await update.effective_chat.send_message(text, reply_markup=reply_markup, parse_mode='HTML')

# ==============================================================================
# مدیریت سبد خرید (Cart Management)
# ==============================================================================
async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش محتویات سبد خرید"""
    user_id = update.effective_user.id
    if update.callback_query:
        await update.callback_query.answer()

    items = await run_db(crud.get_cart_items, user_id)
    
    if not items:
        text = responses.CART_EMPTY
        await _safe_edit(update, text, keyboards.get_main_menu_keyboard())
        return

    # محاسبه مجموع
    items_total = sum(float(item.product.price) * item.quantity for item in items)
    
    # ساخت متن لیست خرید
    cart_text = f"{responses.CART_TITLE}{responses.get_divider()}"
    for item in items:
        attr = f" ({item.selected_attributes})" if item.selected_attributes else ""
        row_price = float(item.product.price) * item.quantity
        cart_text += responses.CART_ITEM_ROW.format(
            name=f"{item.product.name}{attr}",
            quantity=item.quantity,
            total_formatted=responses.format_price(row_price)
        )
    
    cart_text += responses.CART_TOTAL.format(
        total_amount_formatted=responses.format_price(items_total)
    )

    await _safe_edit(update, cart_text, keyboards.view_cart_keyboard(items))

async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """افزودن مستقیم به سبد (بدون متغیر)"""
    query = update.callback_query
    prod_id = int(query.data.split(':')[2])
    
    try:
        await run_db(crud.add_to_cart, query.from_user.id, prod_id, 1)
        await query.answer(responses.ADDED_TO_CART)
        # رفرش صفحه محصول
        from bot.handlers.products_handler import show_product_details
        await show_product_details(update, context)
    except ValueError as e:
        await query.answer(f"⚠️ {str(e)}", show_alert=True)

async def update_cart_item_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """کم و زیاد کردن تعداد آیتم در سبد"""
    query = update.callback_query
    parts = query.data.split(':')
    prod_id = int(parts[2])
    change = int(parts[3])
    
    def _logic(db, uid, pid, delta):
        item = db.query(models.CartItem).filter_by(user_id=str(uid), product_id=pid).first()
        if not item: return False
        
        new_qty = item.quantity + delta
        if new_qty <= 0:
            db.delete(item)
        else:
            if delta > 0 and item.product.stock < new_qty:
                raise ValueError("موجودی انبار کافی نیست.")
            item.quantity = new_qty
        db.commit()
        return True

    try:
        await run_db(_logic, query.from_user.id, prod_id, change)
        await query.answer()
        await view_cart(update, context)
    except ValueError as e:
        await query.answer(str(e), show_alert=True)

async def clear_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """خالی کردن کامل سبد"""
    await run_db(crud.clear_cart, update.effective_user.id)
    await update.callback_query.answer(responses.CART_CLEARED)
    await view_cart(update, context)

# ==============================================================================
# فرآیند نهایی‌سازی خرید (Checkout Conversation)
# ==============================================================================
async def start_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع ثبت سفارش و پرسش آدرس"""
    query = update.callback_query
    await query.answer()
    
    # چک کردن وضعیت فروشگاه
    is_open = await run_db(crud.get_setting, "tg_is_open", "true")
    if is_open == "false":
        await query.message.reply_text("⛔️ پوزش می‌طلبیم، فروشگاه در حال حاضر سفارش جدید نمی‌پذیرد.")
        return ConversationHandler.END

    user_id = query.from_user.id
    addresses = await run_db(crud.get_user_addresses, user_id)
    
    if addresses:
        kbd = keyboards.get_address_book_keyboard(addresses, is_checkout=True)
        text = responses.get_checkout_address(has_saved_addr=True)
        await query.message.reply_text(text, reply_markup=kbd, parse_mode='HTML')
    else:
        text = responses.get_checkout_address(has_saved_addr=False)
        await query.message.reply_text(text, reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
        
    return GET_ADDRESS

async def handle_address_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """انتخاب آدرس از لیست یا درخواست آدرس جدید"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("use_addr:"):
        addr_id = int(query.data.split(':')[1])
        
        def _fetch_addr(db, aid):
            return db.query(models.UserAddress).filter_by(id=aid).first()
            
        addr = await run_db(_fetch_addr, addr_id)
        if addr:
            context.user_data['address'] = addr.address_text
            context.user_data['postal_code'] = addr.postal_code
            
            # اگر کد پستی داشت، مرحله بعد را بپر (Skip)
            if addr.postal_code and len(addr.postal_code) >= 5:
                return await ask_phone_step(query.message, context)
    
    await query.message.reply_text("📍 لطفا آدرس دقیق خود را تایپ کنید:")
    return GET_ADDRESS

async def get_address_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت آدرس متنی و رفتن به کد پستی"""
    text = update.message.text.strip()
    if len(text) < 10:
        await update.message.reply_text("⚠️ آدرس ارسالی بسیار کوتاه است. لطفا دقیق‌تر بنویسید:")
        return GET_ADDRESS
        
    context.user_data['address'] = text
    await update.message.reply_text("📮 لطفا کد پستی ۱۰ رقمی خود را وارد کنید (یا عدد 0 را بفرستید):")
    return GET_POSTAL_CODE

async def get_postal_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت کد پستی"""
    code = update.message.text.strip()
    if code != "0" and (not code.isdigit() or len(code) < 5):
        await update.message.reply_text("⚠️ کد پستی نامعتبر است. فقط عدد وارد کنید:")
        return GET_POSTAL_CODE
    
    context.user_data['postal_code'] = code if code != "0" else None
    
    # ذخیره در دفترچه آدرس برای مراجعات بعدی
    await run_db(crud.add_user_address, update.effective_user.id, "آدرس اخیر", 
                context.user_data['address'], context.user_data['postal_code'])
    
    return await ask_phone_step(update.message, context)

async def ask_phone_step(message, context) -> int:
    """درخواست شماره تماس (منطق مشترک)"""
    user = await run_db(crud.get_user_by_id, context._user_id)
    
    if user and user.phone_number:
        kbd = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"📞 استفاده از {user.phone_number}", callback_data="use_saved_phone")],
            [InlineKeyboardButton("✏️ ورود شماره جدید", callback_data="new_phone")]
        ])
        await message.reply_text("📱 شماره تماس جهت هماهنگی ارسال:", reply_markup=kbd)
    else:
        await message.reply_text(responses.get_checkout_phone(), reply_markup=keyboards.get_contact_keyboard())
        
    return GET_PHONE

async def handle_phone_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == "use_saved_phone":
        user = await run_db(crud.get_user_by_id, query.from_user.id)
        context.user_data['phone'] = user.phone_number
        return await show_invoice_step(query.message, context)
    
    await query.message.reply_text("لطفا شماره موبایل خود را بفرستید:", reply_markup=keyboards.get_contact_keyboard())
    return GET_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت شماره موبایل"""
    phone = update.message.contact.phone_number if update.message.contact else update.message.text.strip()
    
    if not phone.replace('+', '').isdigit():
        await update.message.reply_text("⚠️ شماره موبایل نامعتبر است:")
        return GET_PHONE
        
    context.user_data['phone'] = phone
    await run_db(crud.update_user_phone, update.effective_user.id, phone)
    return await show_invoice_step(update.message, context)

async def show_invoice_step(message, context) -> int:
    """نمایش فاکتور نهایی و اطلاعات کارت بانکی"""
    user_id = context._user_id
    items = await run_db(crud.get_cart_items, user_id)
    
    if not items:
        await message.reply_text("سبد خرید شما خالی شده است.", reply_markup=keyboards.get_main_menu_keyboard())
        return ConversationHandler.END

    # محاسبات مالی
    items_total = sum(float(item.product.price) * item.quantity for item in items)
    ship_cost = float(await run_db(crud.get_setting, "shipping_cost", "0"))
    free_limit = float(await run_db(crud.get_setting, "free_shipping_limit", "0"))
    
    final_ship = 0 if (free_limit > 0 and items_total >= free_limit) else ship_cost
    final_total = items_total + final_ship

    # دریافت اطلاعات کارت از تنظیمات (پشتیبانی از لیست کارت‌ها)
    raw_cards = await run_db(crud.get_setting, "bank_cards", "[]")
    try:
        cards = json.loads(raw_cards)
        card = cards[0] if cards else {"number": "در حال بروزرسانی", "owner": "مدیریت"}
    except:
        card = {"number": "----", "owner": "مدیریت"}

    text = responses.get_checkout_payment(
        total=items_total,
        shipping_cost="رایگان" if final_ship == 0 else f"{int(final_ship):,} ت",
        final_total=final_total,
        card_number=card['number'],
        card_owner=card['owner']
    )

    await message.reply_text(text, reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
    return GET_RECEIPT

async def get_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت فیش و ثبت نهایی سفارش"""
    if not update.message.photo:
        await update.message.reply_text("⚠️ لطفا تصویر فیش واریزی را ارسال کنید.")
        return GET_RECEIPT

    user = update.effective_user
    photo_id = update.message.photo[-1].file_id
    
    shipping_data = {
        "address": context.user_data.get('address'),
        "phone": context.user_data.get('phone'),
        "postal_code": context.user_data.get('postal_code')
    }

    try:
        # ثبت در دیتابیس (اتمیک)
        order = await run_db(crud.create_order_from_cart, user.id, shipping_data)
        
        # ذخیره آیدی عکس فیش در سفارش
        def _update_receipt(db, oid, pid):
            order_obj = db.query(models.Order).filter_by(id=oid).first()
            if order_obj: order_obj.payment_receipt_photo_id = pid
            db.commit()
        
        await run_db(_update_receipt, order.id, photo_id)

        # پیام موفقیت به کاربر
        success_text = responses.ORDER_CONFIRMATION.format(
            order_id=order.id,
            timeline=responses.get_tracking_timeline("pending_payment"),
            divider=responses.get_divider()
        )
        await update.message.reply_text(success_text, reply_markup=keyboards.get_main_menu_keyboard(), parse_mode='HTML')

        # اطلاع‌رسانی به ادمین‌ها
        admin_text = (
            f"🔔 <b>سفارش جدید ثبت شد! #{order.id}</b>\n\n"
            f"👤 مشتری: {user.full_name}\n"
            f"💰 مبلغ نهایی: {int(order.total_amount):,} تومان\n"
            f"📞 تلفن: <code>{shipping_data['phone']}</code>\n"
            f"📍 آدرس: {shipping_data['address']}"
        )
        admin_kb = keyboards.get_admin_order_keyboard(order.id, user.id)
        
        for admin_id in ADMIN_USER_IDS:
            try:
                await context.bot.send_photo(admin_id, photo_id, caption=admin_text, reply_markup=admin_kb, parse_mode='HTML')
            except: pass

    except Exception as e:
        logger.error(f"Checkout Error: {e}")
        await update.message.reply_text("❌ خطا در ثبت سفارش. مبلغ واریزی محفوظ است، لطفا به پشتیبانی پیام دهید.")

    context.user_data.clear()
    return ConversationHandler.END

async def cancel_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.effective_chat.send_message("❌ فرآیند خرید لغو شد.", reply_markup=keyboards.get_main_menu_keyboard())
    context.user_data.clear()
    return ConversationHandler.END

# تعریف هندلر مکالمه برای خروجی
checkout_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_checkout, pattern=r'^cart:checkout$')],
    states={
        GET_ADDRESS: [
            CallbackQueryHandler(handle_address_choice, pattern=r"^(use_addr:|new_address)$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_address_text)
        ],
        GET_POSTAL_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_postal_code)],
        GET_PHONE: [
            CallbackQueryHandler(handle_phone_choice, pattern=r"^(use_saved_phone|new_phone)$"),
            MessageHandler((filters.TEXT | filters.CONTACT) & ~filters.COMMAND, get_phone)
        ],
        GET_RECEIPT: [MessageHandler(filters.PHOTO, get_receipt)],
    },
    fallbacks=[
        CommandHandler('cancel', cancel_checkout),
        CallbackQueryHandler(cancel_checkout, pattern="^main_menu$")
    ],
    per_chat=True,
    per_user=True,
)