import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler,
    MessageHandler, filters, CommandHandler
)
from bot.utils import run_db
from db import crud, models
from bot import keyboards, responses

logger = logging.getLogger("SupportHandler")

# States
GET_SUBJECT, GET_MESSAGE, REPLY_TICKET = range(3)

async def support_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query: await query.answer()

    user_id = update.effective_user.id
    tickets = await run_db(crud.get_user_tickets, user_id)

    text = "📞 <b>پشتیبانی و تیکتینگ</b>\n\nدر این بخش می‌توانید سوالات و مشکلات خود را مطرح کنید."

    btns = [[InlineKeyboardButton("➕ ثبت تیکت جدید", callback_data="ticket:new")]]

    if tickets:
        text += f"\n\nتعداد تیکت‌های شما: {len(tickets)}"
        btns.append([InlineKeyboardButton("📂 مشاهده تیکت‌های قبلی", callback_data="ticket:list")])

    btns.append([InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")])

    if query:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode='HTML')
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode='HTML')

async def start_new_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("💡 لطفا موضوع تیکت خود را بنویسید (مثلاً: سوال در مورد محصول، پیگیری ارسال و ...):")
    return GET_SUBJECT

async def get_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subject = update.message.text.strip()
    if len(subject) < 3:
        await update.message.reply_text("⚠️ موضوع خیلی کوتاه است. لطفا دقیق‌تر بنویسید:")
        return GET_SUBJECT

    context.user_data['ticket_subject'] = subject
    await update.message.reply_text("📝 حالا متن پیام خود را بنویسید:")
    return GET_MESSAGE

async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip()
    subject = context.user_data.get('ticket_subject')
    user_id = update.effective_user.id

    ticket = await run_db(crud.create_ticket, user_id, subject, message)

    await update.message.reply_text(
        f"✅ تیکت شما با موفقیت ثبت شد.\n🆔 شماره تیکت: #{ticket.id}\n\nمنتظر پاسخ کارشناسان ما باشید.",
        reply_markup=keyboards.get_main_menu_keyboard()
    )

    # اطلاع‌رسانی به ادمین‌های بخش پشتیبانی
    def _get_support_admins(db):
        return crud.get_admins_by_role(db, "support")

    support_admins = await run_db(_get_support_admins)
    admin_msg = f"🔔 **تیکت جدید ثبت شد! #{ticket.id}**\n👤 کاربر: {update.effective_user.full_name}\n📌 موضوع: {subject}\n\n💬 متن: {message}"

    for admin_id in support_admins:
        try:
            await context.bot.send_message(admin_id, admin_msg, parse_mode='Markdown')
        except: pass

    context.user_data.clear()
    return ConversationHandler.END

async def list_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    tickets = await run_db(crud.get_user_tickets, user_id)

    if not tickets:
        await query.edit_message_text("تیکتی یافت نشد.", reply_markup=keyboards.get_main_menu_keyboard())
        return

    btns = []
    for t in tickets:
        status_emoji = "🟢" if t.status == "pending" else ("🟡" if t.status == "open" else "⚪️")
        btns.append([InlineKeyboardButton(f"{status_emoji} #{t.id} - {t.subject}", callback_data=f"ticket:show:{t.id}")])

    btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="support")])
    await query.edit_message_text("📂 <b>لیست تیکت‌های شما:</b>\n\n🟢 پاسخ داده شده\n🟡 در انتظار بررسی\n⚪️ بسته شده",
                                 reply_markup=InlineKeyboardMarkup(btns), parse_mode='HTML')

async def show_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ticket_id = int(query.data.split(':')[2])

    ticket = await run_db(crud.get_ticket_with_messages, ticket_id)
    if not ticket: return

    text = f"🎫 <b>تیکت #{ticket.id}</b>\n📌 موضوع: {ticket.subject}\n📊 وضعیت: {ticket.status}\n{responses.get_divider()}\n"

    for m in ticket.messages:
        sender = "👤 شما" if not m.is_admin else "👨‍💻 پشتیبان"
        text += f"<b>{sender}:</b>\n{m.text}\n\n"

    btns = []
    if ticket.status != "closed":
        btns.append([InlineKeyboardButton("✍️ ارسال پاسخ", callback_data=f"ticket:reply:{ticket.id}")])

    btns.append([InlineKeyboardButton("🔙 بازگشت به لیست", callback_data="ticket:list")])

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode='HTML')

async def start_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ticket_id = int(query.data.split(':')[2])
    context.user_data['reply_ticket_id'] = ticket_id
    await query.message.reply_text("✍️ پیام خود را بنویسید:")
    return REPLY_TICKET

async def get_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    ticket_id = context.user_data.get('reply_ticket_id')
    user_id = update.effective_user.id

    await run_db(crud.add_ticket_message, ticket_id, user_id, text, is_admin=False)

    await update.message.reply_text("✅ پاسخ شما ثبت شد.", reply_markup=keyboards.get_main_menu_keyboard())

    # اطلاع‌رسانی پاسخ به ادمین‌های پشتیبانی
    def _get_support_admins(db):
        return crud.get_admins_by_role(db, "support")

    support_admins = await run_db(_get_support_admins)
    admin_msg = f"📩 **پاسخ جدید برای تیکت #{ticket_id}**\n👤 کاربر: {update.effective_user.full_name}\n\n💬 متن: {text}"

    for admin_id in support_admins:
        try:
            await context.bot.send_message(admin_id, admin_msg, parse_mode='Markdown')
        except: pass

    context.user_data.clear()
    return ConversationHandler.END

support_conversation_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_new_ticket, pattern="^ticket:new$"),
        CallbackQueryHandler(start_reply, pattern="^ticket:reply:")
    ],
    states={
        GET_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_subject)],
        GET_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_message)],
        REPLY_TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_reply)],
    },
    fallbacks=[CallbackQueryHandler(support_menu, pattern="^support$")],
)
