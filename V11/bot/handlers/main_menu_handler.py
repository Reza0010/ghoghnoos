import logging
import html
import json
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
    if query: await query.answer()
    
    orders = await run_db(crud.get_user_orders, update.effective_user.id)
    last_order = orders[0] if orders else None

    if last_order:
        timeline = responses.get_tracking_timeline(last_order.status)
        trk = f"\n📬 <b>کد رهگیری پستی:</b>\n<code>{last_order.tracking_code}</code>" if last_order.tracking_code else ""
        
        text = (
            f"📋 <b>جزئیات سفارش #{last_order.id}:</b>\n\n"
            f"💰 مبلغ کل: {responses.format_price(last_order.total_amount)}\n"
            f"📅 تاریخ: {last_order.created_at.strftime('%Y/%m/%d')}\n\n"
            f"{timeline}{trk}\n\n"
            f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"<i>برای مشاهده سوابق کامل به بخش «حساب من» بروید.</i>"
        )
    else:
        text = "❌ شما هنوز سفارشی ثبت نکرده‌اید."

    if query:
        await _safe_edit(update, text, keyboards.get_main_menu_keyboard())
    else:
        await update.effective_chat.send_message(text, reply_markup=keyboards.get_main_menu_keyboard(), parse_mode='HTML')

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
    """بخش پیشنهادات ویژه (جایگاه کمپین‌های تبلیغاتی)"""
    query = update.callback_query
    await query.answer()
    
    # می‌توان این متن را از یک Setting در دیتابیس خواند
    text = f"🔥 <b>جشنواره تخفیفات ویژه</b>\n{responses.get_divider()}\nدر حال حاضر کمپین فعالی وجود ندارد.\nبا عضویت در کانال ما از کدهای تخفیف باخبر شوید!"
    await _safe_edit(update, text, keyboards.get_main_menu_keyboard())

async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اطلاعات تماس با پشتیبانی"""
    query = update.callback_query
    await query.answer()
    
    raw_support = await run_db(crud.get_setting, "support_contacts", "[]")
    try:
        contacts = json.loads(raw_support)
    except:
        contacts = []

    if not contacts:
        contacts = [{"title": "پشتیبانی", "phone": "ثبت نشده", "hours": ""}]

    contact_lines = ""
    for c in contacts:
        hours = f" ({c.get('hours')})" if c.get('hours') else ""
        contact_lines += f"👤 {c['title']}\n📞 <code>{c['phone']}</code>{hours}\n\n"

    text = (
        f"🎧 <b>مرکز پشتیبانی مشتریان</b>\n\n"
        f"در صورت بروز هرگونه مشکل یا سوال، از راه‌های زیر با ما در ارتباط باشید:\n\n"
        f"{contact_lines}"
        f"⏰ کارشناسان ما در سریع‌ترین زمان پاسخگوی شما خواهند بود."
    )
    await _safe_edit(update, text, keyboards.get_main_menu_keyboard())

async def handle_about_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """درباره فروشگاه"""
    query = update.callback_query
    await query.answer()
    
    shop_name = await run_db(crud.get_setting, "shop_name", "فروشگاه ما")
    addr = await run_db(crud.get_setting, "shop_address", "ایران - فروشگاه اینترنتی")

    text = (
        f"🏛 <b>درباره فروشگاه {shop_name}</b>\n"
        f"{responses.get_divider()}\n"
        f"ما همواره در تلاشیم تا بهترین خدمات و محصولات را با بالاترین کیفیت و مناسب‌ترین قیمت به شما عزیزان ارائه دهیم.\n\n"
        f"📍 <b>آدرس دفتر مرکزی:</b>\n{addr}\n\n"
        f"✅ نماد اعتماد و اصالت کالا"
    )
    await _safe_edit(update, text, keyboards.get_main_menu_keyboard())