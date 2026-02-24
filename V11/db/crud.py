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

# ======================================================================
# 0. سیستم لاگ و امنیت (Security & Logging)
# ======================================================================
def record_audit_log(db: Session, action: str, admin_id: str = "system", target_type: str = None, target_id: str = None, description: str = None):
    try:
        log = models.AuditLog(
            admin_id=str(admin_id),
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id else None,
            description=description
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"Audit Log Error: {e}")

def record_stock_log(db: Session, product_id: int, change: int, reason: str):
    try:
        log = models.StockLog(product_id=product_id, change_amount=change, reason=reason)
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"Stock Log Error: {e}")

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
    platform: str = "telegram"
) -> models.User:
    """ایجاد یا آپدیت کاربر (سازگار با تلگرام و روبیکا)"""
    user_id_str = str(telegram_id)
    try:
        user = db.query(models.User).filter(models.User.user_id == user_id_str).first()
        
        # بررسی ادمین بودن (اولویت با لیست دیتابیس)
        is_admin_flag = False
        db_admin_ids = get_setting(db, "admin_ids", "")
        allowed_ids = [i.strip() for i in db_admin_ids.split(",") if i.strip()]

        if not allowed_ids: # فال‌بک به کانفیگ
            allowed_ids = [str(i) for i in ADMIN_USER_IDS]

        if user_id_str in allowed_ids:
            is_admin_flag = True

        if not user:
            user = models.User(
                user_id=user_id_str,
                full_name=full_name,
                username=username,
                platform=platform,
                is_admin=is_admin_flag,
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

def get_all_users(db: Session, limit: int = 10000) -> List[models.User]:
    """دریافت لیست کاربران با لود کردن سفارشات (برای محاسبه CRM)"""
    return (
        db.query(models.User)
        .options(selectinload(models.User.orders)) # بهینه سازی کوئری
        .order_by(desc(models.User.last_seen))
        .limit(limit)
        .all()
    )

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
    else: # newest
        q = q.order_by(desc(models.Product.created_at))

    return q.limit(limit).offset(offset).all()

def get_product_search_count(db: Session, query: str = "", **kwargs) -> int:
    """تعداد نتایج جستجو (برای صفحه‌بندی)"""
    q = db.query(func.count(models.Product.id))
    if query:
        search = f"%{query}%"
        q = q.filter(or_(models.Product.name.ilike(search), models.Product.brand.ilike(search)))
    # سایر فیلترها مشابه advanced_search_products اعمال شود...
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

        # ثبت لاگ
        record_audit_log(db, "create_product", target_type="product", target_id=prod.id, description=f"محصول '{prod.name}' ایجاد شد.")
        if prod.stock > 0:
            record_stock_log(db, prod.id, prod.stock, "موجودی اولیه هنگام ایجاد")

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

        # ثبت لاگ
        record_audit_log(db, "update_product", target_type="product", target_id=prod_id, description=f"محصول '{prod.name}' ویرایش شد.")

        return prod
    except Exception as e:
        db.rollback()
        raise e

def delete_product(db: Session, prod_id: int):
    return bulk_delete_products(db, [prod_id])

def bulk_delete_products(db: Session, product_ids: List[int]):
    try:
        # دریافت نام محصولات قبل از حذف برای لاگ
        products = db.query(models.Product).filter(models.Product.id.in_(product_ids)).all()
        prod_names = [p.name for p in products]

        # حذف وابسته ها خودکار انجام میشود (Cascade) اما برای اطمینان:
        db.query(models.Product).filter(models.Product.id.in_(product_ids)).delete(synchronize_session=False)
        db.commit()

        for pid, name in zip(product_ids, prod_names):
            record_audit_log(db, "delete_product", target_type="product", target_id=pid, description=f"محصول '{name}' حذف شد.")

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

        # ثبت لاگ موجودی برای هر آیتم
        for item in order.items:
            record_stock_log(db, item.product_id, -item.quantity, f"خرید در سفارش #{order.id}")

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
        db.commit()
        db.refresh(order)

        # ثبت لاگ
        record_audit_log(db, "update_order_status", target_type="order", target_id=order_id,
                         description=f"وضعیت سفارش از '{old_status}' به '{new_status}' تغییر یافت.")

    return order

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
# 9. مدیریت کوپن و کد تخفیف
# ======================================================================
def get_all_coupons(db: Session) -> List[models.Coupon]:
    return db.query(models.Coupon).all()

def create_coupon(db: Session, data: dict) -> models.Coupon:
    coupon = models.Coupon(**data)
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon

def validate_coupon(db: Session, code: str, amount: float) -> Tuple[bool, Optional[models.Coupon], str]:
    """بررسی اعتبار کد تخفیف"""
    coupon = db.query(models.Coupon).filter_by(code=code.strip().upper(), is_active=True).first()
    if not coupon:
        return False, None, "کد تخفیف معتبر نیست."

    if coupon.expire_date and coupon.expire_date < datetime.now():
        return False, None, "کد تخفیف منقضی شده است."

    if coupon.max_uses > 0 and coupon.current_uses >= coupon.max_uses:
        return False, None, "ظرفیت استفاده از این کد به پایان رسیده است."

    if amount < float(coupon.min_purchase):
        return False, None, f"حداقل مبلغ خرید برای این کد {int(coupon.min_purchase):,} تومان است."

    return True, coupon, "کد تایید شد."

def use_coupon(db: Session, coupon_id: int):
    coupon = db.query(models.Coupon).get(coupon_id)
    if coupon:
        coupon.current_uses += 1
        db.commit()

# ======================================================================
# 10. پاسخگوی خودکار (Auto Reply)
# ======================================================================
def get_all_auto_replies(db: Session) -> List[models.AutoReply]:
    return db.query(models.AutoReply).all()

def set_auto_reply(db: Session, keyword: str, response: str):
    ar = db.query(models.AutoReply).filter_by(keyword=keyword.strip()).first()
    if ar:
        ar.response = response
        ar.is_active = True
    else:
        ar = models.AutoReply(keyword=keyword.strip(), response=response)
        db.add(ar)
    db.commit()
    return ar

def get_auto_reply(db: Session, text: str) -> Optional[str]:
    """یافتن پاسخ مناسب برای متن ورودی"""
    # در اینجا یک جستجوی ساده انجام می‌دهیم
    replies = db.query(models.AutoReply).filter(models.AutoReply.is_active == True).all()
    text = text.lower().strip()
    for r in replies:
        if r.keyword.lower() in text:
            return r.response
    return None