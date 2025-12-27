from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from . import responses

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Returns the main menu inline keyboard.
    """
    keyboard = [
        [
            InlineKeyboardButton(responses.PRODUCTS_BUTTON, callback_data="products:menu:0"),
            InlineKeyboardButton(responses.SEARCH_BUTTON, callback_data="search:start"),
        ],
        [
            InlineKeyboardButton(responses.SPECIAL_OFFERS_BUTTON, callback_data="offers:view"),
            InlineKeyboardButton(responses.CART_BUTTON, callback_data="cart:view"),
        ],
        [
            InlineKeyboardButton(responses.TRACK_ORDER_BUTTON, callback_data="order:track"),
            InlineKeyboardButton(responses.SUPPORT_BUTTON, callback_data="support:start"),
        ],
        [
            InlineKeyboardButton(responses.ABOUT_US_BUTTON, callback_data="about_us"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
