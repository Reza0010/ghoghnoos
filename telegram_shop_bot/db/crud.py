import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc, asc
from typing import List, Optional
from . import models
from telegram_shop_bot.config import ADMIN_USER_IDS

logger = logging.getLogger(__name__)

def get_or_create_user(db: Session, user_id: int, full_name: str) -> models.User:
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    is_admin = user_id in ADMIN_USER_IDS
    if not db_user:
        db_user = models.User(user_id=user_id, full_name=full_name, is_admin=is_admin)
        db.add(db_user)
    elif db_user.full_name != full_name or db_user.is_admin != is_admin:
        db_user.full_name = full_name
        db_user.is_admin = is_admin
    db.commit()
    db.refresh(db_user)
    return db_user

def get_categories(db: Session, parent_id: Optional[int] = None) -> List[models.Category]:
    return db.query(models.Category).filter(models.Category.parent_id == parent_id).all()

def get_all_categories(db: Session) -> List[models.Category]:
    """Retrieves all categories, useful for building trees."""
    return db.query(models.Category).all()

def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    """Retrieves a single category by its ID."""
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def create_category(db: Session, name: str, parent_id: Optional[int] = None) -> models.Category:
    cat = models.Category(name=name, parent_id=parent_id)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

def update_category(db: Session, cat_id: int, name: str, parent_id: Optional[int] = None) -> Optional[models.Category]:
    cat = db.query(models.Category).filter_by(id=cat_id).first()
    if cat:
        cat.name = name
        cat.parent_id = parent_id
        db.commit()
        db.refresh(cat)
    return cat

def delete_category(db: Session, category_id: int) -> bool:
    """
    Deletes a category and all its sub-categories and associated products recursively.
    """
    # Use joinedload to efficiently fetch related items and reduce DB queries.
    db_category = db.query(models.Category).options(
        joinedload(models.Category.sub_categories),
        joinedload(models.Category.products)
    ).filter(models.Category.id == category_id).first()

    if not db_category:
        return False

    # Recursively delete all sub-categories.
    # We iterate over a copy of the list because the original list will be modified.
    for sub_category in list(db_category.sub_categories):
        delete_category(db, sub_category.id)

    # Delete all products in the current category.
    for product in list(db_category.products):
        # Also remove associated cart items to prevent foreign key violations.
        db.query(models.CartItem).filter(models.CartItem.product_id == product.id).delete()
        db.delete(product)

    # After handling children and products, delete the category itself.
    db.delete(db_category)

    # A single commit at the end of the top-level operation is often best,
    # but for simplicity in this context, we'll commit here.
    db.commit()

    return True

def get_products_by_category(db: Session, cat_id: int, page: int = 1, page_size: int = 6) -> List[models.Product]:
    offset = (page - 1) * page_size
    return db.query(models.Product).filter_by(category_id=cat_id).offset(offset).limit(page_size).all()

def get_product_count_by_category(db: Session, cat_id: int) -> int:
    return db.query(models.Product).filter_by(category_id=cat_id).count()

def get_all_products_paginated(db: Session, page: int = 1, page_size: int = 20) -> List[models.Product]:
    offset = (page - 1) * page_size
    return db.query(models.Product).options(joinedload(models.Product.category)).offset(offset).limit(page_size).all()

def get_total_product_count(db: Session) -> int:
    return db.query(models.Product).count()

def get_product(db: Session, prod_id: int) -> Optional[models.Product]:
    return db.query(models.Product).filter_by(id=prod_id).first()

def create_product(db: Session, **kwargs) -> models.Product:
    prod = models.Product(**kwargs)
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return prod

def update_product(db: Session, prod_id: int, **kwargs) -> Optional[models.Product]:
    prod = get_product(db, prod_id)
    if prod:
        for key, value in kwargs.items():
            setattr(prod, key, value)
        db.commit()
        db.refresh(prod)
    return prod

def delete_product(db: Session, prod_id: int) -> bool:
    prod = get_product(db, prod_id)
    if prod:
        db.delete(prod)
        db.commit()
        return True
    return False

def search_products(db: Session, query: str, page: int = 1, page_size: int = 6, sort_by: str = "default") -> (List[models.Product], int):
    search = f"%{query}%"
    base = db.query(models.Product).filter(or_(models.Product.name.ilike(search), models.Product.brand.ilike(search), models.Product.description.ilike(search)))
    if sort_by == "price_asc": base = base.order_by(asc(models.Product.price))
    elif sort_by == "price_desc": base = base.order_by(desc(models.Product.price))
    elif sort_by == "newest": base = base.order_by(desc(models.Product.created_at))
    elif sort_by == "top_seller": base = base.filter(models.Product.is_top_seller == True)
    total = base.count()
    prods = base.offset((page - 1) * page_size).limit(page_size).all()
    return prods, total

def add_to_cart(db: Session, user_id: int, prod_id: int, quantity: int) -> models.CartItem:
    item = db.query(models.CartItem).filter_by(user_id=user_id, product_id=prod_id).first()
    prod = get_product(db, prod_id)
    if not prod or prod.stock < quantity: raise ValueError("Product not available or insufficient stock.")
    if item: item.quantity += quantity
    else:
        item = models.CartItem(user_id=user_id, product_id=prod_id, quantity=quantity)
        db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_cart_items(db: Session, user_id: int) -> List[models.CartItem]:
    return db.query(models.CartItem).filter_by(user_id=user_id).options(joinedload(models.CartItem.product)).all()

def clear_cart(db: Session, user_id: int):
    db.query(models.CartItem).filter_by(user_id=user_id).delete()
    db.commit()

def create_order(db: Session, user_id: int, address: str, phone: str) -> models.Order:
    items = get_cart_items(db, user_id)
    if not items: raise ValueError("Cart is empty.")
    total = sum(item.product.price * item.quantity for item in items)
    order = models.Order(user_id=user_id, shipping_address=address, total_amount=total)
    db.add(order)
    db.commit()
    db.refresh(order)
    for item in items:
        db.add(models.OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price_at_purchase=item.product.price))
    clear_cart(db, user_id)
    db.commit()
    return order

def get_orders_by_status(db: Session, status: str) -> List[models.Order]:
    return db.query(models.Order).filter_by(status=status).options(joinedload(models.Order.user)).order_by(desc(models.Order.created_at)).all()

def get_order(db: Session, order_id: int) -> Optional[models.Order]:
    return db.query(models.Order).filter_by(id=order_id).options(joinedload(models.Order.items).joinedload(models.OrderItem.product)).first()

def update_order_status(db: Session, order_id: int, new_status: str) -> Optional[models.Order]:
    order = get_order(db, order_id)
    if order:
        order.status = new_status
        db.commit()
        db.refresh(order)
    return order

def get_setting(db: Session, key: str, default: Optional[str] = None) -> str:
    setting = db.query(models.Setting).filter_by(key=key).first()
    return setting.value if setting else default

def set_setting(db: Session, key: str, value: str):
    setting = db.query(models.Setting).filter_by(key=key).first()
    if setting: setting.value = value
    else:
        setting = models.Setting(key=key, value=value)
        db.add(setting)
    db.commit()
