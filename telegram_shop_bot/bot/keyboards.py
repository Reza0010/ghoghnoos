from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List
from telegram_shop_bot.db import models
from . import responses

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(responses.PRODUCTS_BUTTON, callback_data="products"), InlineKeyboardButton(responses.SEARCH_BUTTON, callback_data="search:start")],
        [InlineKeyboardButton(responses.SPECIAL_OFFERS_BUTTON, callback_data="special_offers"), InlineKeyboardButton(responses.CART_BUTTON, callback_data="cart:view")],
        [InlineKeyboardButton(responses.TRACK_ORDER_BUTTON, callback_data="track_order"), InlineKeyboardButton(responses.SUPPORT_BUTTON, callback_data="support")],
        [InlineKeyboardButton(responses.ABOUT_US_BUTTON, callback_data="about_us")],
    ]
    return InlineKeyboardMarkup(keyboard)

def build_category_keyboard(categories: List[models.Category], parent_id: int = None) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(cat.name, callback_data=f"cat:show:{cat.id}") for cat in categories[i:i+2]] for i in range(0, len(categories), 2)]
    if parent_id: keyboard.append([InlineKeyboardButton(f" {responses.BACK_BUTTON}", callback_data=f"cat:back:{parent_id}")])
    else: keyboard.append([InlineKeyboardButton(f" {responses.BACK_BUTTON}", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def build_product_keyboard(products: List[models.Product], cat_id: int, page: int, total_pages: int) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(p.name, callback_data=f"prod:show:{p.id}") for p in products[i:i+2]] for i in range(0, len(products), 2)]
    pg_row = []
    if page > 1: pg_row.append(InlineKeyboardButton(" « قبلی", callback_data=f"prod:list:{cat_id}:{page-1}"))
    if page < total_pages: pg_row.append(InlineKeyboardButton("بعدی » ", callback_data=f"prod:list:{cat_id}:{page+1}"))
    if pg_row: keyboard.append(pg_row)
    keyboard.append([InlineKeyboardButton(f" {responses.BACK_BUTTON}", callback_data=f"cat:show:{cat_id}")])
    return InlineKeyboardMarkup(keyboard)

def product_details_keyboard(product: models.Product) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("افزودن به سبد خرید", callback_data=f"cart:add:{product.id}")],
        [InlineKeyboardButton(f" {responses.BACK_BUTTON}", callback_data=f"prod:list:{product.category_id}:1")]
    ])

def get_search_filter_keyboard(query: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ارزان‌ترین", callback_data=f"search:filter:{query}:price_asc"), InlineKeyboardButton("گران‌ترین", callback_data=f"search:filter:{query}:price_desc")],
        [InlineKeyboardButton("جدیدترین", callback_data=f"search:filter:{query}:newest"), InlineKeyboardButton("پرفروش‌ها", callback_data=f"search:filter:{query}:top_seller")],
        [InlineKeyboardButton(f" {responses.BACK_BUTTON}", callback_data="main_menu")]
    ])

def build_search_results_keyboard(prods: List[models.Product], query: str, sort: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(p.name, callback_data=f"prod:show:{p.id}") for p in prods[i:i+2]] for i in range(0, len(prods), 2)]
    pg_row = []
    if page > 1: pg_row.append(InlineKeyboardButton(" « قبلی", callback_data=f"search:page:{query}:{sort}:{page-1}"))
    if page < total_pages: pg_row.append(InlineKeyboardButton("بعدی » ", callback_data=f"search:page:{query}:{sort}:{page+1}"))
    if pg_row: keyboard.append(pg_row)
    keyboard.append([InlineKeyboardButton(f" {responses.BACK_BUTTON}", callback_data="search:start")])
    return InlineKeyboardMarkup(keyboard)

def view_cart_keyboard(items: List[models.CartItem]) -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(f"➖", callback_data=f"cart:update:{item.product_id}:-1"),
        InlineKeyboardButton(f"{item.quantity} x {item.product.name}", callback_data=f"prod:show:{item.product_id}"),
        InlineKeyboardButton(f"➕", callback_data=f"cart:update:{item.product_id}:1"),
    ] for item in items]
    if items: keyboard.append([InlineKeyboardButton("🗑 پاک کردن سبد", callback_data="cart:clear"), InlineKeyboardButton("✅ ثبت نهایی و پرداخت", callback_data="order:start")])
    keyboard.append([InlineKeyboardButton(f" {responses.BACK_BUTTON}", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)
