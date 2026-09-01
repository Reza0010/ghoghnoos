from telegram import Update, ParseMode
from telegram.ext import (
    CallbackContext, ConversationHandler, CallbackQueryHandler,
    MessageHandler, Filters, CommandHandler
)
from telegram_shop_bot.db.database import get_db
from telegram_shop_bot.db import crud
from telegram_shop_bot.bot import keyboards
from telegram_shop_bot.config import ADMIN_USER_IDS

GET_ADDRESS, GET_PHONE, GET_RECEIPT = range(3)

async def view_cart(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    with next(get_db()) as db: items = crud.get_cart_items(db, user_id)
    if not items:
        text, kbd = "سبد خرید شما خالی است.", keyboards.view_cart_keyboard([])
    else:
        total = sum(item.product.price * item.quantity for item in items)
        text = "🛒 *سبد خرید شما:*\n\n" + "\n".join([f"▪️ {item.product.name} ({item.quantity} عدد) - {item.product.price * item.quantity:,.0f} تومان" for item in items]) + f"\n\n*جمع کل:* {total:,.0f} تومان"
        kbd = keyboards.view_cart_keyboard(items)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=kbd, parse_mode=ParseMode.MARKDOWN)

async def add_to_cart_handler(update: Update, context: CallbackContext):
    q = update.callback_query
    prod_id = int(q.data.split(':')[2])
    try:
        with next(get_db()) as db: crud.add_to_cart(db, update.effective_user.id, prod_id, 1)
        await q.answer("✅ محصول به سبد خرید اضافه شد!", show_alert=False)
    except ValueError as e:
        await q.answer(f"⚠️ خطا: {e}", show_alert=True)

async def update_cart_item_handler(update: Update, context: CallbackContext):
    """Updates a cart item's quantity or removes it if quantity becomes zero."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    _, product_id_str, change_str = query.data.split(":")
    product_id = int(product_id_str)
    change = int(change_str)

    with next(get_db()) as db:
        item = crud.get_cart_item(db, user_id, product_id)
        if item:
            new_quantity = item.quantity + change
            if new_quantity > 0:
                crud.update_cart_item_quantity(db, user_id, product_id, new_quantity)
            else:
                crud.remove_from_cart(db, user_id, product_id)

    # After updating, refresh the cart view
    await view_cart(update, context)

async def clear_cart_handler(update: Update, context: CallbackContext):
    """Clears all items from the user's cart."""
    query = update.callback_query
    user_id = query.from_user.id

    with next(get_db()) as db:
        crud.clear_cart(db, user_id)

    await query.answer("🗑 سبد خرید شما پاک شد.")
    # Refresh the (now empty) cart view
    await view_cart(update, context)

async def start_checkout(update: Update, context: CallbackContext) -> int:
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("لطفاً آدرس کامل خود را برای ارسال وارد کنید:")
    return GET_ADDRESS

async def get_address(update: Update, context: CallbackContext) -> int:
    context.user_data['address'] = update.message.text
    await update.message.reply_text("عالی! حالا لطفاً شماره تماس خود را وارد کنید:")
    return GET_PHONE

async def get_phone(update: Update, context: CallbackContext) -> int:
    context.user_data['phone'] = update.message.text
    with next(get_db()) as db:
        items = crud.get_cart_items(db, update.effective_user.id)
        total = sum(item.product.price * item.quantity for item in items)
        card = crud.get_setting(db, "card_number", "شماره کارتی تنظیم نشده است")
        name = crud.get_setting(db, "shop_name", "فروشگاه")
    text = f"مبلغ قابل پرداخت: *{total:,.0f} تومان*\n\nلطفاً مبلغ را به شماره کارت زیر واریز و تصویر رسید را ارسال نمایید:\n`{card}`\nبه نام: {name}"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    return GET_RECEIPT

async def get_receipt(update: Update, context: CallbackContext) -> int:
    if not update.message.photo:
        await update.message.reply_text("لطفاً یک تصویر از رسید پرداخت ارسال کنید.")
        return GET_RECEIPT

    user_id = update.effective_user.id
    with next(get_db()) as db:
        order = crud.create_order(db, user_id, context.user_data['address'], context.user_data['phone'])
        order.payment_receipt_photo_id = update.message.photo[-1].file_id
        db.commit()
    await update.message.reply_text(f"✅ سفارش شما با موفقیت ثبت شد! شماره پیگیری: `{order.id}`")

    # Notify admin
    for admin_id in ADMIN_USER_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=f"🔔 سفارش جدید ثبت شد! شماره: {order.id}")
        except Exception as e:
            print(f"Failed to send message to admin {admin_id}: {e}")

    context.user_data.clear()
    return ConversationHandler.END

async def cancel_checkout(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("فرآیند خرید لغو شد.")
    context.user_data.clear()
    return ConversationHandler.END

checkout_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_checkout, pattern='^order:start$')],
    states={
        GET_ADDRESS: [MessageHandler(Filters.text & ~Filters.command, get_address)],
        GET_PHONE: [MessageHandler(Filters.text & ~Filters.command, get_phone)],
        GET_RECEIPT: [MessageHandler(Filters.photo, get_receipt)],
    },
    fallbacks=[CommandHandler('cancel', cancel_checkout)],
)
