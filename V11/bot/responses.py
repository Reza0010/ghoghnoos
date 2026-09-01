# -*- coding: utf-8 -*-
from typing import Union, Dict, Any, Optional
import re
from decimal import Decimal

# ====================================================================
# تنظیمات استیکرها (Stickers Config)
# ====================================================================
STICKERS: Dict[str, str] = {
    "welcome": "",      # استیکر خوش‌آمدگویی
    "success": "",      # تیک سبز / ثبت موفق
    "shipping": "",     # ماشین پست
    "error": "",        # علامت خطا
    "sad": "",          # سبد خالی
    "cart": "",         # آیکون سبد خرید
}

# ====================================================================
# توابع کمکی (Helpers) - برای زیبایی و نظم متون
# ====================================================================
def format_price(amount: Union[int, float, str, Decimal, None]) -> str:
    """فرمت‌بندی قیمت به صورت ۳ رقم ۳ رقم با واحد تومان."""
    try:
        if amount is None or str(amount) == "0":
            return "<b>0</b> تومان"
        val = int(float(amount))
        return f"<b>{val:,}</b> تومان"
    except (ValueError, TypeError):
        return "<b>0</b> تومان"

def get_divider() -> str:
    """جداکننده گرافیکی برای تفکیک بخش‌های پیام"""
    return "\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"

def get_progress_bar(current_step: int, total_steps: int = 4) -> str:
    """ایجاد نوار پیشرفت بصری برای مراحل خرید"""
    filled = "🟢"
    empty = "⚪️"
    bar = ""
    for i in range(1, total_steps + 1):
        if i < current_step: bar += filled
        elif i == current_step: bar += "🟠"
        else: bar += empty
    return f"<b>✨ مرحله {current_step} از {total_steps}</b>\n{bar}\n"

def get_tracking_timeline(status: str) -> str:
    """نمودار وضعیت سفارش (Timeline) با ایموجی‌های مرتبط و نوار گرافیکی"""
    config = {
        "pending_payment": (1, "⏳ در انتظار پرداخت", "⚪️⚪️⚪️⚪️"),
        "approved":        (2, "✅ تایید شده / در حال آماده‌سازی", "🟢🟠⚪️⚪️"),
        "paid":            (3, "💰 پرداخت موفق / در حال بسته‌بندی", "🟢🟢🟠⚪️"),
        "shipped":         (4, "🚚 تحویل مأمور پست گردید", "🟢🟢🟢🟢"),
        "rejected":        (0, "❌ متاسفانه لغو گردید", "🔴🔴🔴🔴"),
    }
    step_num, step_desc, bar = config.get(status, (0, "نامشخص", "◽️◽️◽️◽️"))

    timeline = (
        f"📊 <b>وضعیت فعلی: {step_desc}</b>\n"
        f"<code>{bar}</code>\n\n"
        f"{'✅' if step_num >= 1 else '◽️'} ثبت سفارش\n"
        f"{'✅' if step_num >= 2 else '◽️'} تایید مدیریت\n"
        f"{'✅' if step_num >= 3 else '◽️'} بسته‌بندی\n"
        f"{'✅' if step_num >= 4 else '🚚'} تحویل پست"
    )
    return timeline

def format_dynamic_text(template: str, user_data: Dict[str, Any]) -> str:
    """جایگزینی هوشمند متغیرها در متن"""
    if not template: return ""

    # متغیرهای پیش‌فرض
    replacements = {
        "{user_name}": str(user_data.get("user_name") or "کاربر"),
        "{shop_name}": str(user_data.get("shop_name") or "فروشگاه ما"),
        "{order_id}": str(user_data.get("order_id") or "---"),
        "{total_amount}": format_price(user_data.get("total_amount", 0)),
        "{order_count}": str(user_data.get("order_count", 0)),
        "{total_spent}": format_price(user_data.get("total_spent", 0)),
        "{discount}": str(user_data.get("discount", "0")),
    }

    text = template
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text

def get_dynamic_response(key: str, default: str, db_session=None, user_data: Dict = None) -> str:
    """دریافت متن داینامیک از دیتابیس با جایگزینی متغیرها"""
    from db import crud

    template = default
    if db_session:
        try:
            db_val = crud.get_setting(db_session, f"tmpl_{key}", default)
            if db_val: template = db_val
        except: pass

    if user_data:
        return format_dynamic_text(template, user_data)
    return template

# ====================================================================
# پیام‌های سیستمی و عمومی
# ====================================================================
ERROR_MESSAGE = (
    "⚠️ <b>خطایی در پردازش رخ داد.</b>\n"
    "لطفاً لحظاتی دیگر تلاش کنید یا با دستور /start مجدداً امتحان کنید."
)
UNKNOWN_COMMAND = "🤔 متوجه این دستور نشدم. لطفا از منوی زیر استفاده کنید."
LOADING = "⏳ <i>در حال دریافت اطلاعات...</i>"
WELCOME_MESSAGE = "سلام {user_name} عزیز 👋\nبه فروشگاه <b>{shop_name}</b> خوش آمدید.\n\n💎 بهترین محصولات با نازل‌ترین قیمت!"

# ====================================================================
# برچسب دکمه‌ها (Button Labels)
# ====================================================================
PRODUCTS_BUTTON = "🛍 مشاهده ویترین محصولات"
SEARCH_BUTTON = "🔎 جستجوی هوشمند"
SPECIAL_OFFERS_BUTTON = "🔥 تخفیفات داغ"
CART_BUTTON = "🛒 سبد خرید"
TRACK_ORDER_BUTTON = "📦 پیگیری سفارشات"
SUPPORT_BUTTON = "📞 ارتباط با ما"
ABOUT_US_BUTTON = "ℹ️ درباره فروشگاه"
BACK_BUTTON = "🔙 بازگشت"
MAIN_MENU_BUTTON = "🏠 منوی اصلی"
USER_PROFILE_BUTTON = "👤 پروفایل من"

# ====================================================================
# محصولات و جستجو
# ====================================================================
CATEGORY_SELECT = "📂 <b>لطفاً دسته‌بندی مورد نظر را انتخاب کنید:</b>"
PRODUCT_LIST = "📋 <b>لیست محصولات گروه:</b>\n{breadcrumbs}"
PRODUCT_DETAILS = """
💎 <b>{name}</b>
{divider}
📑 <b>توضیحات محصول:</b>
{description}

🔹 <b>مشخصات فنی:</b>
🏷 برند: <code>{brand}</code>
📦 وضعیت انبار: {stock_status}
{divider}
💰 <b>قیمت نهایی: {price_formatted}</b>
{cart_preview}
"""
SEARCH_PROMPT = "🔍 <b>نام یا ویژگی محصول مورد نظر را وارد کنید:</b>\n<i>مثال: سامسونگ، پیراهن مشکی، ارزان</i>"
SEARCH_NO_RESULT = "❌ <b>نتیجه‌ای یافت نشد!</b>\nلطفاً کلمات کلیدی دیگری را امتحان کنید."
SEARCH_RESULT_TITLE = "🔎 نتایج یافت شده برای: <code>{query}</code>"

# ====================================================================
# سبد خرید و علاقه‌مندی
# ====================================================================
CART_EMPTY = "🛒 <b>سبد خرید شما فعلاً خالی است!</b>\nهمین حالا می‌توانید از ویترین ما دیدن کنید."
CART_TITLE = "🛒 <b>آیتم‌های سبد خرید شما:</b>\n"
CART_ITEM_ROW = "🎁 <b>{name}</b>\n└ 🔢 {quantity} عدد | قیمت واحد: {total_formatted}\n"
CART_TOTAL = "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n💵 <b>جمع کل فاکتور: {total_amount_formatted}</b>"
ADDED_TO_CART = "✅ به سبد خرید اضافه شد."
CART_CLEARED = "🗑 سبد خرید خالی شد."
FAV_ADDED = "❤️ به لیست علاقه‌مندی‌ها اضافه شد."
FAV_REMOVED = "💔 از لیست علاقه‌مندی‌ها حذف شد."
FAV_EMPTY = "💔 لیست علاقه‌مندی‌های شما خالی است."
NOTIFY_SUCCESS = "🔔 <b>درخواست شما ثبت شد.</b>\nبه محض موجود شدن کالا، از همینجا خبرتان می‌کنیم!"

# ====================================================================
# حساب کاربری و سوابق (User Account)
# ====================================================================
USER_PROFILE_DASHBOARD = """
👤 <b>حساب کاربری من</b>
{divider}
🆔 شناسه مشتری: <code>{user_id}</code>
👤 نام و نشان: <b>{full_name}</b>
📱 شماره تماس: <code>{phone}</code>

📊 <b>گزارش عملکرد:</b>
📅 تاریخ عضویت: <code>{join_date}</code>
📦 تعداد سفارشات: <b>{order_count} مورد</b>
💰 مجموع وفاداری: <b>{total_spent}</b>
{divider}
⚙️ تنظیمات حساب کاربری:
"""

# ====================================================================
# فرآیند ثبت سفارش
# ====================================================================
def get_checkout_address(has_saved_addr: bool = False) -> str:
    msg = f"{get_progress_bar(1)}\n📍 <b>محل تحویل سفارش:</b>\n"
    if has_saved_addr:
        msg += "می‌توانید از آدرس‌های قبلی استفاده کنید یا یک آدرس جدید بنویسید:"
    else:
        msg += "لطفاً آدرس دقیق پستی خود را به همراه نام شهر وارد کنید:"
    return msg

def get_checkout_phone() -> str:
    return f"{get_progress_bar(2)}\n📱 <b>شماره تماس هماهنگی:</b>\nلطفاً شماره موبایل خود را تایید یا وارد کنید:"

def get_checkout_payment(total: Any, shipping_cost: str, final_total: Any, card_number: str, card_owner: str) -> str:
    div = get_divider()
    return (
        f"{get_progress_bar(4)}\n"
        f"💳 <b>تسویه‌حساب نهایی</b>\n"
        f"{div}"
        f"🛍 جمع مبلغ کالاها: {format_price(total)}\n"
        f"🚚 هزینه ارسال و خدمات: <b>{shipping_cost}</b>\n"
        f"{div}"
        f"💰 <b>مبلغ نهایی قابل پرداخت:</b>\n"
        f"👈 <code>{format_price(final_total)}</code>\n\n"
        f"🏦 <b>اطلاعات بانکی:</b>\n"
        f"شماره کارت: <code>{card_number}</code>\n"
        f"نام صاحب حساب: <b>{card_owner}</b>\n\n"
        f"✅ پس از واریز وجه، لطفاً <b>تصویر فیش</b> را ارسال کنید."
    )

ORDER_CONFIRMATION = """
🎉 <b>سفارش شما با موفقیت ثبت گردید!</b> 😍
🆔 شناسه سفارش: <code>#{order_id}</code>
{divider}
{timeline}
{divider}
<i>از خرید شما متشکریم! وضعیت سفارش از طریق همین ربات اطلاع‌رسانی خواهد شد.</i>
"""
