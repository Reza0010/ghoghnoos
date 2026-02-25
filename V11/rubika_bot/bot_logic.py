import asyncio
import logging
from typing import Optional, Dict, Any, List

# واردات نسبتی به ساختار پروژه
from .rubika_client import RubikaAPI, RubikaError
from db.database import SessionLocal
from db import crud, models

logger = logging.getLogger("RubikaBot")

class RubikaWorker:
    def __init__(self, token: str):
        self.api = RubikaAPI(token)
        self.running = False
        self.bot_guid: Optional[str] = None

    async def _initialize_bot(self):
        """دریافت شناسه ربات برای جلوگیری از لوپ"""
        try:
            res = await self.api.get_me()
            # ساختار پاسخ getMe طبق مستندات: {'bot': {'bot_id': ...}}
            if res and "bot" in res:
                self.bot_guid = res["bot"]["bot_id"]
                logger.info(f"Rubika Bot ID identified: {self.bot_guid}")
        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")

    async def start_polling(self):
        """شروع حلقه دریافت پیام‌ها"""
        self.running = True
        await self._initialize_bot()
        logger.info("🚀 Rubika Polling Service Started...")

        while self.running:
            try:
                # دریافت آپدیت‌ها (مدیریت offset داخل کلاینت انجام می‌شود)
                updates = await self.api.get_updates(limit=20)

                if updates:
                    for update in updates:
                        try:
                            await self.process_update(update)
                        except Exception as inner_e:
                            logger.error(f"Error processing update: {inner_e}")

                # وقفه کوتاه برای کاهش فشار سرور
                await asyncio.sleep(1.5)

            except RubikaError as e:
                logger.warning(f"Rubika API Error: {e}. Retrying...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Polling Loop Critical Error: {e}")
                await asyncio.sleep(10)

    async def stop(self):
        self.running = False
        await self.api.close()

    async def process_update(self, update: Dict[str, Any]):
        """توزیع‌کننده رویدادها (Dispatcher)"""
        # ساختار آپدیت طبق مدل Update در 03.txt
        update_type = update.get("type")

        # ۱. پیام جدید (NewMessage)
        if update_type == "NewMessage":
            msg = update.get("new_message", {})
            chat_id = update.get("chat_id")
            sender_id = msg.get("sender_id")

            # فیلتر پیام‌های خود ربات (جلوگیری از لوپ)
            if sender_id == self.bot_guid:
                return

            text = msg.get("text", "")
            aux_data = msg.get("aux_data", {})
            button_id = aux_data.get("button_id")

            if button_id:
                # اگر روی دکمه ای کلیک شده باشد
                await self.handle_button_click(chat_id, sender_id, button_id, aux_data)
            elif text:
                # اگر متن ارسال شده باشد
                await self.handle_text_message(chat_id, sender_id, text)

        # ۲. سایر رویدادها (StartedBot, StoppedBot, etc.)
        elif update_type == "StartedBot":
            user_id = update.get("chat_id") # در StartedBot معمولا chat_id همان کاربر است
            # ارسال پیام خوش‌آمدگویی
            await self.send_main_menu(user_id)

    # ================= Handlers =================

    async def handle_text_message(self, chat_id: str, user_id: str, text: str):
        """مدیریت پیام‌های متنی"""
        # ثبت یا آپدیت کاربر در دیتابیس
        with SessionLocal() as db:
            user = crud.get_or_create_user(db, user_id, "کاربر روبیکا", None, "rubika")
            # آپدیت آخرین پیام کاربر
            crud.update_user_info(db, user_id, last_interaction_text=text[:100])
            shop_name = crud.get_setting(db, "shop_name", "فروشگاه ما")

        text = text.strip()

        if text == "/start" or text == "🏠 منوی اصلی" or text == "🏠 بازگشت به منو":
            await self.send_main_menu(chat_id)
        elif text == "🛍 مشاهده محصولات" or text == "🛍 محصولات":
            await self.send_categories(chat_id)
        elif text == "🛒 سبد خرید":
            await self.send_cart(chat_id, user_id)
        elif text == "📞 پشتیبانی":
            await self.send_support(chat_id)
        else:
            # بررسی پاسخ خودکار
            with SessionLocal() as db:
                response = crud.get_auto_reply(db, text)
                if response:
                    return await self.api.send_message(chat_id, response)

            # پاسخ پیش‌فرض
            await self.api.send_message(chat_id, "⚠️ متوجه این دستور نشدم. لطفا از منوی زیر استفاده کنید.")

    async def handle_button_click(self, chat_id: str, user_id: str, btn_id: str, aux_data: Dict):
        """مدیریت کلیک روی دکمه‌های Inline"""

        # ساختار ID دکمه‌ها: `action:data` مثلا `cat:5`
        parts = btn_id.split(":")
        action = parts[0]
        data = parts[1] if len(parts) > 1 else None

        if action == "cat":
            await self.send_products(chat_id, int(data))
        elif action == "prod":
            await self.send_product_detail(chat_id, int(data))
        elif action == "add":
            await self.add_to_cart(chat_id, user_id, int(data))
        elif action == "checkout":
            await self.process_checkout(chat_id, user_id)
        elif action == "nav" and data == "back_cat":
            await self.send_categories(chat_id)

    # ================= UI Methods =================

    async def send_main_menu(self, chat_id: str):
        """ارسال منوی اصلی با Reply Keyboard"""
        with SessionLocal() as db:
            shop_name = crud.get_setting(db, "shop_name", "فروشگاه ما")
            welcome_tpl = crud.get_setting(db, "tmpl_welcome", "")

        if welcome_tpl:
            from bot.responses import format_dynamic_text
            text = format_dynamic_text(welcome_tpl, {"user_name": "کاربر", "shop_name": shop_name})
        else:
            text = (
                f"💎 **به فروشگاه {shop_name} خوش آمدید**\n"
                "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                "بهترین کالاها را با تضمین قیمت و کیفیت از ما بخواهید. 👋\n\n"
                "👇 لطفا یکی از گزینه‌های زیر را انتخاب کنید:"
            )

        # ساختار Reply Keyboard طبق مستندات (لیست سطرها)
        keyboard = [
            [{"id": "menu:shop", "text": "🛍 مشاهده محصولات"}],
            [{"id": "menu:cart", "text": "🛒 سبد خرید"}, {"id": "menu:support", "text": "📞 پشتیبانی"}]
        ]

        await self.api.send_message(chat_id, text, reply_keyboard=keyboard)

    async def send_categories(self, chat_id: str):
        """نمایش لیست دسته‌بندی‌ها"""
        with SessionLocal() as db:
            cats = crud.get_root_categories(db)

        if not cats:
            return await self.api.send_message(chat_id, "⚠️ در حال حاضر هیچ دسته‌بندی فعالی وجود ندارد.")

        text = "📂 **لطفا دسته‌بندی مورد نظر را انتخاب کنید:**"
        inline_rows = []
        for c in cats:
            inline_rows.append([{"id": f"cat:{c.id}", "text": f"🔹 {c.name}", "type": "Simple"}])

        await self.api.send_message(chat_id, text, inline_keyboard=inline_rows)

    async def send_products(self, chat_id: str, cat_id: int):
        """نمایش محصولات یک دسته"""
        with SessionLocal() as db:
            prods = crud.get_active_products_by_category(db, cat_id)

        if not prods:
            return await self.api.send_message(chat_id, "❌ متاسفانه در این بخش محصولی یافت نشد.")

        text = f"📋 **لیست محصولات یافت شده ({len(prods)} مورد):**"
        inline_rows = []
        for p in prods[:10]:
            inline_rows.append([{"id": f"prod:{p.id}", "text": f"🎁 {p.name} - {int(p.price):,} تومان"}])

        # دکمه بازگشت
        inline_rows.append([{"id": "nav:back_cat", "text": "🔙 بازگشت به دسته‌بندی‌ها"}])

        await self.api.send_message(chat_id, text, inline_keyboard=inline_rows)

    async def send_product_detail(self, chat_id: str, prod_id: int):
        """جزئیات محصول (با پشتیبانی از گالری تصاویر)"""
        from pathlib import Path
        from config import BASE_DIR

        with SessionLocal() as db:
            p = crud.get_product(db, prod_id)
            if not p: return

            all_images = []
            if p.images:
                all_images = [img.image_path for img in p.images]
            elif hasattr(p, 'image_path') and p.image_path:
                all_images = [p.image_path]

        div = "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
        stock_status = "✅ موجود در انبار" if p.stock > 0 else "❌ ناموجود"

        txt = (
            f"💎 **{p.name}**\n"
            f"{div}\n"
            f"📑 **توضیحات محصول:**\n"
            f"{p.description or 'توضیحاتی ثبت نشده است.'}\n\n"
            f"🏷 برند: {p.brand or 'متفرقه'}\n"
            f"📦 وضعیت: {stock_status}\n"
            f"{div}\n"
            f"💰 **قیمت نهایی: {int(p.price):,} تومان**"
        )

        inline_rows = [
            [{"id": f"add:{p.id}", "text": "🛒 افزودن به سبد خرید", "type": "Simple"}],
            [{"id": "nav:back_cat", "text": "🔙 بازگشت به لیست"}]
        ]

        # ارسال تصاویر (حداکثر ۳ تصویر اول برای جلوگیری از اسپم در روبیکا)
        if all_images:
            try:
                for i, img_path in enumerate(all_images[:3]):
                    full_path = Path(BASE_DIR) / img_path
                    if full_path.exists():
                        # فقط آخرین عکس شامل کپشن و دکمه‌ها باشد
                        caption = txt if i == len(all_images[:3]) - 1 else None
                        kb = inline_rows if i == len(all_images[:3]) - 1 else None

                        file_id = await self.api.upload_file(str(full_path))
                        await self.api.send_file(chat_id, file_id, caption=caption, inline_keyboard=kb)
                return # کار تمام است
            except Exception as e:
                logger.error(f"Error sending images to Rubika: {e}")

        # اگر تصویری فرستاده نشد، متن خالی بفرست
        await self.api.send_message(chat_id, txt, inline_keyboard=inline_rows)

    async def add_to_cart(self, chat_id: str, user_id: str, prod_id: int):
        try:
            with SessionLocal() as db:
                crud.add_to_cart(db, user_id, prod_id, 1)
            await self.api.send_message(chat_id, "✅ محصول با موفقیت به سبد خرید شما اضافه شد.")
        except ValueError as e:
            await self.api.send_message(chat_id, f"⚠️ {str(e)}")

    async def send_cart(self, chat_id: str, user_id: str):
        """نمایش سبد خرید"""
        with SessionLocal() as db:
            items = crud.get_cart_items(db, user_id)

        if not items:
            return await self.api.send_message(chat_id, "🛒 **سبد خرید شما در حال حاضر خالی است.**")

        div = "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
        msg = "🛒 **جزئیات سبد خرید شما:**\n\n"
        total = 0
        for item in items:
            p = item.product
            total += p.price * item.quantity
            msg += f"🎁 **{p.name}**\n└ 🔢 {item.quantity} عدد × {int(p.price):,} تومان\n\n"

        msg += f"{div}\n💰 **مجموع کل فاکتور: {int(total):,} تومان**"

        inline_rows = [[{"id": "checkout", "text": "✅ تکمیل و نهایی کردن سفارش"}]]
        await self.api.send_message(chat_id, msg, inline_keyboard=inline_rows)

    async def process_checkout(self, chat_id: str, user_id: str):
        """ثبت سفارش نهایی"""
        try:
            with SessionLocal() as db:
                order = crud.create_order_from_cart(db, user_id, {
                    "address": "نیاز به هماهنگی تلفنی",
                    "phone": "ثبت نشده",
                    "postal_code": ""
                })

            msg = (
                f"🎉 **سفارش شما با موفقیت در سیستم ثبت شد!**\n\n"
                f"🆔 شماره سفارش: `#{order.id}`\n"
                f"💰 مبلغ قابل پرداخت: `{int(order.total_amount):,}` تومان\n\n"
                f"📞 کارشناسان ما به زودی جهت هماهنگی نهایی با شما تماس خواهند گرفت.\n"
                f"از اعتماد شما سپاسگزاریم. ❤️"
            )
            await self.api.send_message(chat_id, msg)

        except Exception as e:
            logger.error(f"Checkout Error: {e}")
            await self.api.send_message(chat_id, "❌ متاسفانه خطایی در ثبت نهایی سفارش رخ داد. لطفا با پشتیبانی تماس بگیرید.")

    async def send_support(self, chat_id: str):
        with SessionLocal() as db:
            msg = crud.get_setting(db, "tmpl_support", "")

        if not msg:
            div = "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
            msg = (
                "📞 **مرکز پشتیبانی مشتریان**\n"
                f"{div}\n"
                "در صورت داشتن هرگونه سوال یا مشکل در فرآیند خرید، از طریق آیدی زیر با ما در ارتباط باشید:\n\n"
                "🆔 @YourSupportID\n\n"
                "⏰ ساعت پاسخگویی: ۱۰ صبح الی ۲۲"
            )
        await self.api.send_message(chat_id, msg)
