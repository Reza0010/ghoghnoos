import logging
import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from bot import keyboards, responses
from bot.utils import run_db
from db import crud

logger = logging.getLogger("MainMenuHandler")

# ==============================================================================
# تابع کمکی (Helper Function) برای مدیریت ارسال/ویرایش پیام
# ==============================================================================
async def _safe_edit(update: Update, text: str, reply_markup: InlineKeyboardMarkup):
    """
    ویرایش هوشمند پیام. اگر پیام قبلی دارای مدیا (عکس) باشد و قابل ویرایش نباشد،
    آن را حذف کرده و پیام متنی جدید ارسال می‌کند.
    """
    query = update.callback_query
    try:
        if query:
            # تلاش برای ویرایش متن پیام
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.effective_chat.send_message(text, reply_markup=reply_markup, parse_mode='HTML')
    except BadRequest as e:
        if "Message is not modified" in str(e):
            return
        # اگر خطا به دلیل وجود عکس در پیام قبلی بود، حذف و ارسال مجدد
        try:
            await query.message.delete()
        except:
            pass
        await update.effective_chat.send_message(
            text=text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

# ==============================================================================
# هندلرهای بخش پروفایل و اطلاعات
# ==============================================================================

async def handle_user_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش داشبورد پروفایل کاربری با آمار خرید"""
    query = update.callback_query
    if query: await query.answer()
    
    user = update.effective_user
    # ثبت/بروزرسانی کاربر با ساختار جدید CRUD
    db_user = await run_db(crud.get_or_create_user, user.id, user.full_name, user.username, "telegram")
    stats = await run_db(crud.get_user_stats, user.id)

    safe_name = html.escape(user.full_name or "کاربر عزیز")
    join_date = db_user.created_at.strftime("%Y/%m/%d") if db_user.created_at else "-"

    text = responses.USER_PROFILE_DASHBOARD.format(
        divider=responses.get_divider(),
        user_id=user.id,
        full_name=safe_name,
        phone=db_user.phone_number or "ثبت نشده ❌",
        join_date=join_date,
        order_count=stats.get("total_orders", 0),
        total_spent=responses.format_price(stats.get("total_spent", 0))
    )

    await _safe_edit(update, text, keyboards.get_user_profile_keyboard())

async def handle_order_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست آخرین سفارشات کاربر"""
    query = update.callback_query
    await query.answer()
    
    orders = await run_db(crud.get_user_orders, update.effective_user.id)

    if not orders:
        history_text = "🤷‍♂️ <b>شما هنوز هیچ سفارشی در این فروشگاه ثبت نکرده‌اید.</b>"
    else:
        lines = []
        status_map = {
            "pending_payment": "⏳ در انتظار پرداخت",
            "approved": "⚙️ در حال آماده‌سازی",
            "shipped": "🚚 ارسال شده",
            "paid": "✅ پرداخت شده",
            "rejected": "❌ لغو شده"
        }
        for o in orders[:10]:  # نمایش ۱۰ سفارش اخیر
            st_text = status_map.get(o.status, o.status)
            lines.append(f"📦 <b>#{o.id}</b> | {responses.format_price(o.total_amount)} | {st_text}")
        
        history_text = "\n".join(lines)
        
    text = responses.ORDER_HISTORY_LIST.format(
        divider=responses.get_divider(),
        orders_text=history_text
    )

    await _safe_edit(update, text, keyboards.get_order_history_keyboard())

async def handle_track_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پیگیری وضعیت آخرین سفارش به صورت سریع"""
    query = update.callback_query
    await query.answer()
    
    orders = await run_db(crud.get_user_orders, update.effective_user.id)
    last_order = orders[0] if orders else None

    if last_order:
        timeline = responses.get_tracking_timeline(last_order.status)
        trk = f"\n📬 <b>کد رهگیری پستی:</b> <code>{last_order.tracking_code}</code>" if last_order.tracking_code else ""
        
        text = (
            f"📋 <b>وضعیت آخرین سفارش شما:</b>\n"
            f"🆔 شناسه: <code>{last_order.id}</code>\n"
            f"💰 مبلغ: {responses.format_price(last_order.total_amount)}\n"
            f"📅 تاریخ ثبت: {last_order.created_at.strftime('%Y-%m-%d')}\n\n"
            f"{timeline}{trk}\n\n"
            f"<i>برای مشاهده لیست تمام سفارشات به بخش پروفایل بروید.</i>"
        )
    else:
        text = "❌ شما سفارشی برای پیگیری ندارید."

    await _safe_edit(update, text, keyboards.get_main_menu_keyboard())

# ==============================================================================
# مدیریت آدرس‌ها
# ==============================================================================

async def handle_user_addresses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لیست دفترچه آدرس کاربر"""
    query = update.callback_query
    await query.answer()
    
    addrs = await run_db(crud.get_user_addresses, update.effective_user.id)
    kbd = keyboards.get_address_book_keyboard(addrs, is_checkout=False)

    await _safe_edit(update, responses.ADDRESS_MANAGEMENT_TITLE, kbd)

async def handle_delete_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف آدرس از دفترچه"""
    query = update.callback_query
    try:
        addr_id = int(query.data.split(':')[1])
        success = await run_db(crud.delete_user_address, addr_id, update.effective_user.id)
        
        if success:
            await query.answer("✅ آدرس با موفقیت حذف شد.")
        else:
            await query.answer("❌ خطا در حذف آدرس.")
            
        # رفرش لیست
        await handle_user_addresses(update, context)
        
    except (IndexError, ValueError):
        await query.answer("خطا در پردازش درخواست.")

# ==============================================================================
# بخش‌های اطلاع‌رسانی ثابت
# ==============================================================================

async def handle_special_offers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بخش پیشنهادات ویژه (نمایش محصولات تخفیف‌دار و پرفروش)"""
    query = update.callback_query
    await query.answer()
    
    def _fetch_specials(db):
        # محصولات تخفیف‌دار
        discounted = db.query(models.Product).filter(models.Product.discount_price > 0, models.Product.stock > 0).limit(5).all()
        # محصولات پرفروش
        top_sellers = db.query(models.Product).filter(models.Product.is_top_seller == True, models.Product.stock > 0).limit(5).all()
        return discounted, top_sellers

    discounted, top_sellers = await run_db(_fetch_specials)

    text = f"🔥 <b>پیشنهادات ویژه و جشنواره‌ها</b>\n{responses.get_divider()}\n"

    btns = []
    if discounted:
        text += "💰 <b>محصولات دارای تخفیف:</b>\n"
        for p in discounted:
            text += f"• {p.name}\n"
            btns.append([InlineKeyboardButton(f"🎁 {p.name}", callback_data=f"prod:show:{p.id}")])

    if top_sellers:
        text += "\n🏆 <b>محبوب‌ترین‌های این هفته:</b>\n"
        for p in top_sellers:
            text += f"• {p.name}\n"
            # جلوگیری از دکمه تکراری
            if not any(b[0].callback_data == f"prod:show:{p.id}" for b in btns):
                btns.append([InlineKeyboardButton(f"⭐ {p.name}", callback_data=f"prod:show:{p.id}")])

    if not discounted and not top_sellers:
        text += "در حال حاضر جشنواره فعالی وجود ندارد. منتظر خبرهای خوب باشید!"

    btns.append([InlineKeyboardButton(responses.BACK_BUTTON, callback_data="main_menu")])

    await _safe_edit(update, text, InlineKeyboardMarkup(btns))

async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اطلاعات تماس با پشتیبانی"""
    query = update.callback_query
    await query.answer()
    
    # دریافت لیست آیدی‌های پشتیبانی از تنظیمات (به صورت لیست JSON)
    raw_support = await run_db(crud.get_setting, "tg_support_ids", "[]")
    import json
    try:
        ids = json.loads(raw_support)
        supp_link = ids[0] if ids else "@Admin"
    except:
        supp_link = "@Admin"

    text = responses.SUPPORT_TEXT.format(support_id=supp_link, divider=responses.get_divider())
    await _safe_edit(update, text, keyboards.get_main_menu_keyboard())

async def handle_about_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """درباره فروشگاه"""
    query = update.callback_query
    await query.answer()
    
    shop_name = await run_db(crud.get_setting, "tg_shop_name", "فروشگاه ما")
    phone = await run_db(crud.get_setting, "tg_phones", "ثبت نشده")
    addr = await run_db(crud.get_setting, "tg_shop_address", "فروشگاه اینترنتی")

    text = responses.ABOUT_US_TEXT.format(
        shop_name=shop_name,
        phone=phone,
        address=addr,
        divider=responses.get_divider()
    )
    await _safe_edit(update, text, keyboards.get_main_menu_keyboard())