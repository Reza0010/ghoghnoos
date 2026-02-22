import logging
import json
from typing import List, Optional, Tuple, Any, Dict, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import or_, desc, asc, func, case, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from . import models
from config import ADMIN_USER_IDS

logger = logging.getLogger("CRUD")

def get_admin_ids(db: Session) -> List[int]:
    """ترکیب ادمین‌های فایل کانفیگ و دیتابیس"""
    ids = list(ADMIN_USER_IDS)
    db_ids_str = get_setting(db, "admin_user_ids", "")
    if db_ids_str:
        try:
            extra_ids = [int(x.strip()) for x in db_ids_str.split(',') if x.strip().isdigit()]
            for eid in extra_ids:
                if eid not in ids:
                    ids.append(eid)
        except:
            pass
    return ids

# ======================================================================
# 1. مدیریت کاربران (User Management)
# ======================================================================
def get_user_by_id(db: Session, user_id: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.user_id == str(user_id)).first()

def get_or_create_user(
    db: Session,
    telegram_id: Union[int, str],
    full_name: str,
    username: str = None,
    platform: str = "telegram",
    referred_by: str = None
) -> models.User:
    """ایجاد یا آپدیت کاربر (سازگار با تلگرام و روبیکا)"""
    user_id_str = str(telegram_id)
    try:
        user = db.query(models.User).filter(models.User.user_id == user_id_str).first()
        
        # بررسی ادمین بودن (فقط برای تلگرام و بر اساس کانفیگ)
        is_admin_flag = False
        if platform == "telegram" and user_id_str.isdigit():
            if int(user_id_str) in ADMIN_USER_IDS:
                is_admin_flag = True

        if not user:
            user = models.User(
                user_id=user_id_str,
                full_name=full_name,
                username=username,
                platform=platform,
                is_admin=is_admin_flag,
                referred_by_id=referred_by,
                created_at=datetime.now()
            )
            db.add(user)
        else:
            # آپدیت اطلاعات اگر تغییر کرده باشد
            changes = False
            if user.full_name != full_name:
                user.full_name = full_name
                changes = True
            if user.username != username:
                user.username = username
                changes = True
            if platform == "telegram" and user.is_admin != is_admin_flag:
                user.is_admin = is_admin_flag
                changes = True
            
            user.last_seen = datetime.now()
            if changes:
                user.updated_at = datetime.now()

        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error in get_or_create_user: {e}")
        # تلاش مجدد برای خواندن (اگر در ترد دیگری ساخته شده باشد)
        return db.query(models.User).filter(models.User.user_id == user_id_str).first()

def get_all_users(db: Session, limit: int = 50, offset: int = 0) -> List[models.User]:
    """دریافت لیست کاربران با لود کردن سفارشات (برای محاسبه CRM)"""
    return (
        db.query(models.User)
        .options(selectinload(models.User.orders)) # بهینه سازی کوئری
        .order_by(desc(models.User.last_seen))
        .limit(limit)
        .offset(offset)
        .all()
    )

def get_users_count(db: Session, query: str = "", platform: str = "all", status: str = "all") -> int:
    """تعداد کل کاربران با فیلترها (برای صفحه‌بندی)"""
    q = db.query(func.count(models.User.user_id))

    if platform != "all" and platform != "همه پلتفرم‌ها":
        q = q.filter(models.User.platform == platform.lower())

    if status == "فعال":
        q = q.filter(models.User.is_banned == False)
    elif status == "مسدود":
        q = q.filter(models.User.is_banned == True)

    if query:
        search = f"%{query}%"
        q = q.filter(or_(models.User.full_name.ilike(search), models.User.user_id.ilike(search)))

    return q.scalar()

def update_user_info(db: Session, user_id: Union[int, str], **kwargs) -> bool:
    try:
        user_id_str = str(user_id)
        db.query(models.User).filter(models.User.user_id == user_id_str).update(kwargs)
        db.commit()
        return True
    except SQLAlchemyError:
        db.rollback()
        return False

def update_user_phone(db: Session, user_id: Union[int, str], phone: str):
    return update_user_info(db, user_id, phone_number=phone)

def get_user_stats(db: Session, user_id: Union[int, str]) -> Dict:
    """آمار سریع کاربر برای نمایش در پروفایل"""
    try:
        uid = str(user_id)
        # استفاده از func.sum و func.count دیتابیس (سریعتر از پایتون)
        stats = db.query(
            func.count(models.Order.id).label('count'),
            func.coalesce(func.sum(models.Order.total_amount), 0).label('total')
        ).filter(
            models.Order.user_id == uid,
            models.Order.status.in_(['approved', 'shipped', 'paid'])
        ).first()

        user = db.query(models.User).filter_by(user_id=uid).first()
        return {
            "join_date": user.created_at if user else datetime.now(),
            "total_orders": stats.count,
            "total_spent": float(stats.total)
        }
    except Exception as e:
        logger.error(f"Stats Error: {e}")
        return {}

# ======================================================================
# 2. مدیریت دسته‌بندی‌ها
# ======================================================================
def get_all_categories(db: Session) -> List[models.Category]:
    return db.query(models.Category).order_by(models.Category.id).all()

def get_root_categories(db: Session) -> List[models.Category]:
    return db.query(models.Category).filter(models.Category.parent_id.is_(None)).order_by(models.Category.id).all()

def get_subcategories(db: Session, parent_id: int) -> List[models.Category]:
    return db.query(models.Category).filter(models.Category.parent_id == parent_id).all()

def get_categories_with_counts(db: Session) -> List[Tuple[models.Category, int]]:
    """دریافت دسته‌ها به همراه تعداد محصولات (برای پنل ادمین)"""
    return (
        db.query(models.Category, func.count(models.Product.id))
        .outerjoin(models.Product)
        .group_by(models.Category.id)
        .order_by(models.Category.id)
        .all()
    )

def create_category(db: Session, name: str, parent_id: Optional[int] = None) -> models.Category:
    cat = models.Category(name=name.strip(), parent_id=parent_id)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

def update_category(db: Session, cat_id: int, name: str, parent_id: Optional[int] = None):
    cat = db.query(models.Category).filter_by(id=cat_id).first()
    if cat:
        cat.name = name.strip()
        cat.parent_id = parent_id
        db.commit()
        return cat

def delete_category(db: Session, cat_id: int):
    # ابتدا محصولات این دسته را بی‌پناه می‌کنیم (category_id = NULL)
    db.query(models.Product).filter_by(category_id=cat_id).update({models.Product.category_id: None})
    # سپس حذف دسته
    db.query(models.Category).filter_by(id=cat_id).delete()
    db.commit()

# ======================================================================
# 3. مدیریت محصولات
# ======================================================================
def get_product(db: Session, prod_id: int) -> Optional[models.Product]:
    """دریافت محصول با تمام وابستگی‌ها (Variants, Images)"""
    return db.query(models.Product).options(
        selectinload(models.Product.variants),
        selectinload(models.Product.images),
        joinedload(models.Product.category)
    ).filter_by(id=prod_id).first()

def is_product_discount_active(product: models.Product) -> bool:
    """بررسی فعال بودن تخفیف بر اساس زمان‌بندی"""
    if not product.discount_price or product.discount_price <= 0:
        return False

    now = datetime.now()
    if product.discount_start_date and now < product.discount_start_date:
        return False
    if product.discount_end_date and now > product.discount_end_date:
        return False

    return True

def get_active_products_by_category(db: Session, category_id: int) -> List[models.Product]:
    return db.query(models.Product).filter(
        models.Product.category_id == category_id,
        models.Product.stock > 0,
        models.Product.is_active == True
    ).order_by(desc(models.Product.is_top_seller), desc(models.Product.created_at)).all()

def advanced_search_products(
    db: Session,
    query: str = "",
    category_id: int = None,
    min_price: int = 0,
    max_price: int = 0,
    in_stock_only: bool = False,
    sort_by: str = "newest",
    limit: int = 100,
    offset: int = 0
) -> List[models.Product]:
    q = db.query(models.Product).options(
        selectinload(models.Product.images),
        joinedload(models.Product.category)
    )
    
    if query:
        search = f"%{query}%"
        q = q.filter(
            or_(
                models.Product.name.ilike(search),
                models.Product.brand.ilike(search),
                models.Product.tags.ilike(search),
                models.Product.description.ilike(search)
            )
        )
    
    if category_id:
        q = q.filter(models.Product.category_id == category_id)
    if min_price > 0:
        q = q.filter(models.Product.price >= min_price)
    if max_price > 0:
        q = q.filter(models.Product.price <= max_price)
    if in_stock_only:
        q = q.filter(models.Product.stock > 0)

    # Sorting
    if sort_by == "price_asc":
        q = q.order_by(asc(models.Product.price))
    elif sort_by == "price_desc":
        q = q.order_by(desc(models.Product.price))
    elif sort_by == "top_seller":
        q = q.order_by(desc(models.Product.is_top_seller), desc(models.Product.created_at))
    elif sort_by == "stock_asc":
        q = q.order_by(asc(models.Product.stock))
    elif sort_by == "stock_desc":
        q = q.order_by(desc(models.Product.stock))
    else: # newest
        q = q.order_by(desc(models.Product.created_at))

    return q.limit(limit).offset(offset).all()

def get_product_search_count(
    db: Session,
    query: str = "",
    category_id: int = None,
    min_price: int = 0,
    max_price: int = 0,
    in_stock_only: bool = False,
    **kwargs
) -> int:
    """تعداد نتایج جستجو (برای صفحه‌بندی)"""
    q = db.query(func.count(models.Product.id))

    if query:
        search = f"%{query}%"
        q = q.filter(
            or_(
                models.Product.name.ilike(search),
                models.Product.brand.ilike(search),
                models.Product.tags.ilike(search)
            )
        )

    if category_id:
        q = q.filter(models.Product.category_id == category_id)
    if min_price > 0:
        q = q.filter(models.Product.price >= min_price)
    if max_price > 0:
        q = q.filter(models.Product.price <= max_price)
    if in_stock_only:
        q = q.filter(models.Product.stock > 0)

    return q.scalar()

def create_product_with_variants(
    db: Session,
    product_data: dict,
    variants_data: List[dict],
    image_paths: List[str] = None
) -> models.Product:
    try:
        # جدا کردن فیلد image_path قدیمی اگر وجود دارد
        main_img = None
        if image_paths:
            main_img = image_paths[0]
            
        # ساخت محصول
        # حذف کلیدهای اضافی که در مدل نیستند
        valid_keys = {c.name for c in models.Product.__table__.columns}
        clean_data = {k: v for k, v in product_data.items() if k in valid_keys}
        
        # ست کردن تصویر اصلی برای سازگاری
        if main_img:
            clean_data['image_path'] = main_img

        prod = models.Product(**clean_data)
        db.add(prod)
        db.flush() # برای گرفتن ID

        # افزودن تصاویر به جدول جدید
        if image_paths:
            for path in image_paths:
                db.add(models.ProductImage(product_id=prod.id, image_path=path))

        # افزودن متغیرها
        if variants_data:
            for v in variants_data:
                db.add(models.ProductVariant(product_id=prod.id, **v))

        db.commit()
        db.refresh(prod)
        return prod
    except Exception as e:
        db.rollback()
        logger.error(f"Create Product Error: {e}")
        raise e

def update_product_with_variants(
    db: Session,
    prod_id: int,
    product_data: dict,
    variants_data: List[dict],
    image_paths: List[str] = None
):
    """آپدیت کامل محصول شامل عکس‌ها و متغیرها"""
    try:
        prod = db.query(models.Product).filter_by(id=prod_id).first()
        if not prod: raise ValueError("Product not found")

        # آپدیت فیلدهای اصلی
        valid_keys = {c.name for c in models.Product.__table__.columns}
        for k, v in product_data.items():
            if k in valid_keys:
                setattr(prod, k, v)
        
        # آپدیت تصویر اصلی (Backward Compatibility)
        if image_paths:
            prod.image_path = image_paths[0]

        prod.updated_at = datetime.now()

        # آپدیت تصاویر: حذف قدیمی‌ها و افزودن جدیدها
        if image_paths is not None:
            db.query(models.ProductImage).filter_by(product_id=prod_id).delete()
            for path in image_paths:
                db.add(models.ProductImage(product_id=prod_id, image_path=path))

        # آپدیت متغیرها
        if variants_data is not None:
            db.query(models.ProductVariant).filter_by(product_id=prod_id).delete()
            for v in variants_data:
                db.add(models.ProductVariant(product_id=prod_id, **v))

        db.commit()
        db.refresh(prod)
        return prod
    except Exception as e:
        db.rollback()
        raise e

def delete_product(db: Session, prod_id: int):
    return bulk_delete_products(db, [prod_id])

def bulk_delete_products(db: Session, product_ids: List[int]):
    try:
        # حذف وابسته ها خودکار انجام میشود (Cascade) اما برای اطمینان:
        db.query(models.Product).filter(models.Product.id.in_(product_ids)).delete(synchronize_session=False)
        db.commit()
        return True
    except SQLAlchemyError:
        db.rollback()
        return False

def get_low_stock_products(db: Session, limit: int = 5):
    return db.query(models.Product).filter(
        models.Product.stock > 0,
        models.Product.stock <= 5
    ).limit(limit).all()

def get_all_products_raw(db: Session):
    """دریافت تمام محصولات برای خروجی اکسل"""
    return db.query(models.Product).options(joinedload(models.Product.category)).all()

# ======================================================================
# 4. سبد خرید
# ======================================================================
def get_cart_items(db: Session, user_id: Union[int, str]) -> List[models.CartItem]:
    return db.query(models.CartItem).options(
        joinedload(models.CartItem.product)
    ).filter_by(user_id=str(user_id)).all()

def add_to_cart(db: Session, user_id: Union[int, str], product_id: int, quantity: int = 1, attributes: str = None):
    try:
        user_id = str(user_id)
        prod = db.query(models.Product).filter_by(id=product_id).first()
        if not prod or prod.stock < quantity:
            raise ValueError("موجودی کافی نیست")

        item = db.query(models.CartItem).filter_by(
            user_id=user_id, product_id=product_id, selected_attributes=attributes
        ).first()

        if item:
            if prod.stock < (item.quantity + quantity):
                raise ValueError("موجودی کافی نیست")
            item.quantity += quantity
        else:
            item = models.CartItem(
                user_id=user_id, product_id=product_id,
                quantity=quantity, selected_attributes=attributes
            )
            db.add(item)
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

def remove_from_cart(db: Session, item_id: int):
    db.query(models.CartItem).filter_by(id=item_id).delete()
    db.commit()

def clear_cart(db: Session, user_id: Union[int, str]):
    db.query(models.CartItem).filter_by(user_id=str(user_id)).delete()
    db.commit()

# ======================================================================
# 5. سفارشات (Orders) - Critical
# ======================================================================
def create_order_from_cart(db: Session, user_id: Union[int, str], shipping_data: dict) -> models.Order:
    """ایجاد سفارش و کسر موجودی به صورت اتمیک"""
    user_id = str(user_id)
    try:
        # شروع تراکنش
        with db.begin_nested():
            cart_items = get_cart_items(db, user_id)
            if not cart_items:
                raise ValueError("Cart is empty")

            total_amount = 0
            order_items = []

            for item in cart_items:
                # قفل کردن ردیف محصول برای جلوگیری از Race Condition (در دیتابیس‌های پیشرفته مثل PG)
                # در SQLite این کار با تراکنش معمولی انجام می‌شود
                prod = db.query(models.Product).filter_by(id=item.product_id).first()
                
                if prod.stock < item.quantity:
                    raise ValueError(f"موجودی '{prod.name}' تمام شده است.")
                
                # کسر موجودی
                prod.stock -= item.quantity
                
                # محاسبه قیمت (با تخفیف)
                price = prod.discount_price if (prod.discount_price and prod.discount_price > 0) else prod.price
                line_total = price * item.quantity
                total_amount += line_total
                
                order_items.append(models.OrderItem(
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    quantity=item.quantity,
                    price_at_purchase=price,
                    selected_attributes=item.selected_attributes
                ))

            # هزینه ارسال
            ship_cost = int(get_setting(db, "shipping_cost", "0"))
            free_limit = int(get_setting(db, "free_shipping_limit", "0"))
            if free_limit > 0 and total_amount >= free_limit:
                ship_cost = 0
            
            total_amount += ship_cost

            # ایجاد سفارش
            order = models.Order(
                user_id=user_id,
                total_amount=total_amount,
                status="pending_payment",
                shipping_address=shipping_data.get("address", ""),
                postal_code=shipping_data.get("postal_code", ""),
                phone_number=shipping_data.get("phone", ""),
                shipping_cost=ship_cost,
                items=order_items
            )
            db.add(order)
            
            # پاک کردن سبد خرید
            db.query(models.CartItem).filter_by(user_id=user_id).delete()
            
        db.commit()
        db.refresh(order)
        return order
    except Exception as e:
        db.rollback()
        logger.error(f"Order Creation Failed: {e}")
        raise e

def get_filtered_orders(db: Session, status: str = "all", limit: int = 500) -> List[models.Order]:
    q = db.query(models.Order).options(
        joinedload(models.Order.user),
        selectinload(models.Order.items).joinedload(models.OrderItem.product)
    )
    if status != "all":
        q = q.filter(models.Order.status == status)
    
    return q.order_by(desc(models.Order.created_at)).limit(limit).all()

def update_order_status(db: Session, order_id: int, new_status: str) -> Optional[models.Order]:
    order = db.query(models.Order).filter_by(id=order_id).first()
    if order:
        old_status = order.status
        order.status = new_status

        # منطق وفادارسازی: اگر سفارش تایید شد، امتیاز اضافه کن
        if new_status in ['approved', 'paid'] and old_status not in ['approved', 'paid']:
            _award_loyalty_points(db, order)

        db.commit()
        db.refresh(order)
    return order

def _award_loyalty_points(db: Session, order: models.Order):
    """محاسبه و واریز امتیاز وفاداری"""
    try:
        # درصد امتیاز از تنظیمات (پیش‌فرض ۱٪)
        percent = int(get_setting(db, "loyalty_percent", "1"))
        points = int(float(order.total_amount) * (percent / 100))

        if points > 0 and order.user:
            order.user.loyalty_points += points
            logger.info(f"Awarded {points} points to user {order.user_id}")

            # اگر زیرمجموعه کسی باشد، به معرف هم امتیاز بده (مثلاً نیم درصد)
            if order.user.referred_by_id:
                referrer = db.query(models.User).get(order.user.referred_by_id)
                if referrer:
                    ref_points = int(float(order.total_amount) * 0.005) # 0.5%
                    referrer.loyalty_points += ref_points
                    logger.info(f"Awarded {ref_points} referral points to {referrer.user_id}")
    except Exception as e:
        logger.error(f"Loyalty Award Error: {e}")

def get_order_by_id(db: Session, order_id: int) -> Optional[models.Order]:
    return db.query(models.Order).options(
        selectinload(models.Order.items).joinedload(models.OrderItem.product),
        joinedload(models.Order.user)
    ).filter_by(id=order_id).first()

def get_user_orders(db: Session, user_id: Union[int, str]) -> List[models.Order]:
    return db.query(models.Order).filter_by(user_id=str(user_id)).order_by(desc(models.Order.created_at)).limit(20).all()

# ======================================================================
# 6. تنظیمات (Settings)
# ======================================================================
def get_setting(db: Session, key: str, default: str = "") -> str:
    s = db.query(models.Setting).filter_by(key=key).first()
    return s.value if s else default

def set_setting(db: Session, key: str, value: str):
    s = db.query(models.Setting).filter_by(key=key).first()
    if s:
        s.value = str(value)
        s.updated_at = datetime.now()
    else:
        db.add(models.Setting(key=key, value=str(value)))
    db.commit()

def is_shop_currently_open(db: Session) -> bool:
    """بررسی باز یا بسته بودن فروشگاه با لحاظ کردن ساعات کاری"""
    manual_open = get_setting(db, "tg_is_open", "true") == "true"
    if not manual_open:
        return False

    op_hours_enabled = get_setting(db, "op_hours_enabled", "false") == "true"
    if not op_hours_enabled:
        return True

    try:
        now = datetime.now().time()
        start_str = get_setting(db, "op_hours_start", "08:00")
        end_str = get_setting(db, "op_hours_end", "22:00")

        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()

        if start_time < end_time:
            return start_time <= now <= end_time
        else: # بازه از شب تا صبح روز بعد
            return now >= start_time or now <= end_time
    except:
        return True

def get_admins_by_role(db: Session, role: str) -> List[int]:
    """دریافت لیست ادمین‌ها بر اساس نقش (sales, support, system)"""
    try:
        roles_json = get_setting(db, "admin_notification_roles", "{}")
        roles = json.loads(roles_json)
        return [int(uid) for uid in roles.get(role, [])]
    except:
        return get_admin_ids(db)

def log_setting_change(db: Session, admin_id, keys, values):
    logger.info(f"Admin {admin_id} changed settings: {keys}")

# ======================================================================
# 7. آمار داشبورد (Analytics)
# ======================================================================
def get_total_revenue_by_platform(db: Session, platform: str) -> float:
    return db.query(func.coalesce(func.sum(models.Order.total_amount), 0))\
        .join(models.User)\
        .filter(
            models.Order.status.in_(['approved', 'shipped', 'paid']),
            models.User.platform == platform
        ).scalar()

def get_orders_count_by_platform_and_status(db: Session, platform: str, status: str) -> int:
    return db.query(func.count(models.Order.id))\
        .join(models.User)\
        .filter(
            models.Order.status == status,
            models.User.platform == platform
        ).scalar()

def get_top_selling_products(db: Session, limit: int = 5):
    """لیست محصولات پرفروش به همراه تعداد و درآمد کل"""
    return db.query(
        models.Product.name,
        func.sum(models.OrderItem.quantity).label('total_qty'),
        func.sum(models.OrderItem.quantity * models.OrderItem.price_at_purchase).label('total_revenue')
    ).join(models.OrderItem).group_by(models.Product.id)\
    .order_by(desc('total_qty')).limit(limit).all()

def get_recent_activities(db: Session, limit: int = 15) -> List[Dict]:
    """دریافت فعالیت‌های متنوع برای فید داشبورد"""
    activities = []

    # سفارشات اخیر
    orders = db.query(models.Order).order_by(desc(models.Order.created_at)).limit(limit).all()
    for o in orders:
        activities.append({
            "type": "order",
            "text": f"سفارش #{o.id} ثبت شد",
            "user": o.user.full_name if o.user else "ناشناس",
            "time": o.created_at,
            "platform": o.user.platform if o.user else "telegram",
            "amount": float(o.total_amount)
        })

    # کاربران جدید
    users = db.query(models.User).order_by(desc(models.User.created_at)).limit(limit).all()
    for u in users:
        activities.append({
            "type": "user",
            "text": f"کاربر جدید پیوست",
            "user": u.full_name or "بدون نام",
            "time": u.created_at,
            "platform": u.platform,
            "amount": None
        })

    # تیکت‌های جدید
    tickets = db.query(models.Ticket).order_by(desc(models.Ticket.created_at)).limit(limit).all()
    for t in tickets:
        activities.append({
            "type": "ticket",
            "text": f"تیکت جدید: {t.subject[:20]}...",
            "user": t.user.full_name if t.user else "ناشناس",
            "time": t.created_at,
            "platform": t.user.platform if t.user else "telegram",
            "amount": None
        })

    # مرتب‌سازی کل بر اساس زمان
    activities.sort(key=lambda x: x["time"], reverse=True)
    return activities[:limit]

def get_sales_growth(db: Session):
    """محاسبه درصد رشد فروش امروز نسبت به دیروز"""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    def get_day_revenue(day):
        return db.query(func.coalesce(func.sum(models.Order.total_amount), 0))\
            .filter(func.date(models.Order.created_at) == day)\
            .filter(models.Order.status.in_(['approved', 'shipped', 'paid']))\
            .scalar()

    rev_today = get_day_revenue(today)
    rev_yesterday = get_day_revenue(yesterday)

    if rev_yesterday == 0:
        return 100 if rev_today > 0 else 0

    growth = ((rev_today - rev_yesterday) / rev_yesterday) * 100
    return round(growth, 1)

def get_monthly_growth(db: Session):
    """محاسبه رشد درآمد ماه جاری نسبت به ماه قبل"""
    now = datetime.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0)
    last_month_end = this_month_start - timedelta(seconds=1)
    last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0)

    def get_period_revenue(start, end):
        return db.query(func.coalesce(func.sum(models.Order.total_amount), 0))\
            .filter(models.Order.created_at >= start, models.Order.created_at <= end)\
            .filter(models.Order.status.in_(['approved', 'shipped', 'paid']))\
            .scalar()

    rev_this = get_period_revenue(this_month_start, now)
    rev_last = get_period_revenue(last_month_start, last_month_end)

    if rev_last == 0:
        return 100 if rev_this > 0 else 0
    return round(((rev_this - rev_last) / rev_last) * 100, 1)

# ======================================================================
# 8. آدرس‌ها و علاقه‌مندی‌ها
# ======================================================================
def get_user_addresses(db: Session, user_id):
    return db.query(models.UserAddress).filter_by(user_id=str(user_id)).all()

def add_user_address(db: Session, user_id, title, text, postal_code=None):
    # جلوگیری از تکراری
    exists = db.query(models.UserAddress).filter_by(user_id=str(user_id), address_text=text).first()
    if exists: return exists
    
    addr = models.UserAddress(user_id=str(user_id), title=title, address_text=text, postal_code=postal_code)
    db.add(addr)
    db.commit()
    return addr

def delete_user_address(db: Session, addr_id, user_id):
    c = db.query(models.UserAddress).filter_by(id=addr_id, user_id=str(user_id)).delete()
    db.commit()
    return c > 0

def toggle_favorite(db: Session, user_id, product_id):
    uid = str(user_id)
    fav = db.query(models.Favorite).filter_by(user_id=uid, product_id=product_id).first()
    if fav:
        db.delete(fav)
        res = False
    else:
        db.add(models.Favorite(user_id=uid, product_id=product_id))
        res = True
    db.commit()
    return res

def get_user_favorites(db: Session, user_id):
    return db.query(models.Product).join(models.Favorite).filter(models.Favorite.user_id == str(user_id)).all()

def add_product_notification(db: Session, user_id, product_id):
    exists = db.query(models.ProductNotification).filter_by(user_id=str(user_id), product_id=product_id).first()
    if not exists:
        db.add(models.ProductNotification(user_id=str(user_id), product_id=product_id))
        db.commit()

# ======================================================================
# 9. سیستم تیکتینگ (Ticketing System)
# ======================================================================
def create_ticket(db: Session, user_id: str, subject: str, initial_message: str) -> models.Ticket:
    ticket = models.Ticket(user_id=str(user_id), subject=subject)
    db.add(ticket)
    db.flush()

    msg = models.TicketMessage(ticket_id=ticket.id, sender_id=str(user_id), text=initial_message, is_admin=False)
    db.add(msg)
    db.commit()
    db.refresh(ticket)
    return ticket

def add_ticket_message(db: Session, ticket_id: int, sender_id: str, text: str, is_admin: bool = False):
    msg = models.TicketMessage(ticket_id=ticket_id, sender_id=str(sender_id), text=text, is_admin=is_admin)
    db.add(msg)
    # آپدیت زمان آخرین تغییر تیکت
    ticket = db.query(models.Ticket).get(ticket_id)
    if ticket:
        ticket.updated_at = datetime.now()
        if is_admin:
            ticket.status = "pending" # در انتظار پاسخ کاربر
        else:
            ticket.status = "open" # باز (نیاز به پاسخ ادمین)
    db.commit()
    return msg

def get_user_activity_history(db: Session, user_id: str) -> List[Dict]:
    """دریافت تمام فعالیت‌های یک کاربر خاص به صورت زمانی"""
    history = []
    uid = str(user_id)

    # سفارشات
    orders = db.query(models.Order).filter_by(user_id=uid).all()
    for o in orders:
        history.append({
            "type": "order",
            "title": f"ثبت سفارش #{o.id}",
            "desc": f"مبلغ {int(o.total_amount):,} تومان | وضعیت: {o.status}",
            "time": o.created_at
        })

    # تیکت‌ها
    tickets = db.query(models.Ticket).filter_by(user_id=uid).all()
    for t in tickets:
        history.append({
            "type": "ticket",
            "title": f"ایجاد تیکت: {t.subject}",
            "desc": f"وضعیت نهایی: {t.status}",
            "time": t.created_at
        })

    # زمان عضویت
    user = db.query(models.User).filter_by(user_id=uid).first()
    if user:
        history.append({
            "type": "join",
            "title": "عضویت در فروشگاه",
            "desc": f"پلتفرم: {user.platform}",
            "time": user.created_at
        })

    history.sort(key=lambda x: x["time"], reverse=True)
    return history

def get_user_tickets(db: Session, user_id: str) -> List[models.Ticket]:
    return db.query(models.Ticket).filter_by(user_id=str(user_id)).order_by(desc(models.Ticket.updated_at)).all()

def get_all_tickets(db: Session, status: str = None) -> List[models.Ticket]:
    q = db.query(models.Ticket).options(joinedload(models.Ticket.user))
    if status and status != "all":
        q = q.filter(models.Ticket.status == status)
    return q.order_by(desc(models.Ticket.updated_at)).all()

def get_ticket_with_messages(db: Session, ticket_id: int) -> Optional[models.Ticket]:
    return db.query(models.Ticket).options(
        selectinload(models.Ticket.messages),
        joinedload(models.Ticket.user)
    ).filter_by(id=ticket_id).first()

def get_all_auto_responses(db: Session) -> List[models.AutoResponse]:
    return db.query(models.AutoResponse).all()

def set_auto_response(db: Session, keyword: str, response: str, match_type: str = "exact"):
    res = db.query(models.AutoResponse).filter_by(keyword=keyword).first()
    if res:
        res.response_text = response
        res.match_type = match_type
    else:
        db.add(models.AutoResponse(keyword=keyword, response_text=response, match_type=match_type))
    db.commit()

def delete_auto_response(db: Session, res_id: int):
    db.query(models.AutoResponse).filter_by(id=res_id).delete()
    db.commit()

def find_auto_response(db: Session, text: str) -> Optional[str]:
    """یافتن بهترین پاسخ خودکار برای متن ورودی"""
    text = text.strip().lower()
    # اول تطابق دقیق
    exact = db.query(models.AutoResponse).filter(
        models.AutoResponse.keyword == text,
        models.AutoResponse.is_active == True,
        models.AutoResponse.match_type == "exact"
    ).first()
    if exact: return exact.response_text

    # سپس تطابق محتوایی
    contains = db.query(models.AutoResponse).filter(
        models.AutoResponse.match_type == "contains",
        models.AutoResponse.is_active == True
    ).all()
    for item in contains:
        if item.keyword.lower() in text:
            return item.response_text
    return None

def close_ticket(db: Session, ticket_id: int):
    ticket = db.query(models.Ticket).get(ticket_id)
    if ticket:
        ticket.status = "closed"
        db.commit()
    return ticket

# ======================================================================
# 10. مدیریت پروکسی (Proxy Management)
# ======================================================================
def get_all_proxies(db: Session) -> List[models.Proxy]:
    return db.query(models.Proxy).order_by(desc(models.Proxy.created_at)).all()

def add_proxy(db: Session, data: dict) -> models.Proxy:
    proxy = models.Proxy(**data)
    db.add(proxy)
    db.commit()
    db.refresh(proxy)
    return proxy

def delete_proxy(db: Session, proxy_id: int):
    db.query(models.Proxy).filter_by(id=proxy_id).delete()
    db.commit()

def set_active_proxy(db: Session, proxy_id: Optional[int]):
    # غیرفعال کردن همه
    db.query(models.Proxy).update({models.Proxy.is_active: False})
    if proxy_id:
        db.query(models.Proxy).filter_by(id=proxy_id).update({models.Proxy.is_active: True})
    db.commit()

def get_active_proxy(db: Session) -> Optional[models.Proxy]:
    return db.query(models.Proxy).filter_by(is_active=True).first()

def update_proxy_latency(db: Session, proxy_id: int, latency: int):
    proxy = db.query(models.Proxy).get(proxy_id)
    if proxy:
        proxy.latency = latency
        proxy.last_tested = datetime.now()
        db.commit()