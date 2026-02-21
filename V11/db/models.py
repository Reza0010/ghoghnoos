from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    DateTime, Numeric, Text, Index
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    # user_id استرینگ است تا هم تلگرام و هم روبیکا را ساپورت کند
    user_id = Column(String(50), primary_key=True, autoincrement=False)
    platform = Column(String(20), default="telegram", nullable=False)  # 'telegram', 'rubika'
    full_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    
    # اطلاعات ذخیره شده برای تسریع پروسه خرید
    saved_address = Column(Text, nullable=True)
    saved_phone = Column(String(20), nullable=True)
    private_note = Column(Text, nullable=True)  # یادداشت ادمین برای کاربر
    
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    addresses = relationship("UserAddress", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("ProductNotification", back_populates="user", cascade="all, delete-orphan")

    # Indexing for faster lookups in Admin Panel
    __table_args__ = (
        Index('idx_user_platform', 'platform'),
        Index('idx_user_created', 'created_at'),
        Index('idx_user_banned', 'is_banned'),
    )

    def __repr__(self):
        return f"<User(id={self.user_id}, name={self.full_name}, plat={self.platform})>"


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True)
    
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    brand = Column(String(100), nullable=True)
    
    price = Column(Numeric(12, 0), nullable=False)
    discount_price = Column(Numeric(12, 0), nullable=True)
    discount_start_date = Column(DateTime(timezone=True), nullable=True)
    discount_end_date = Column(DateTime(timezone=True), nullable=True)
    stock = Column(Integer, default=0, nullable=False)
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_top_seller = Column(Boolean, default=False, nullable=False)
    
    # image_path قدیمی (برای سازگاری نگه‌داشته شده اما از جدول ProductImage استفاده می‌شود)
    image_path = Column(String(512), nullable=True)
    image_file_id = Column(String(255), nullable=True)  # File ID تلگرام برای سرعت ارسال
    
    tags = Column(Text, nullable=True)  # Comma separated
    related_product_ids = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan", lazy="selectin")
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    favorited_by = relationship("Favorite", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_prod_active_stock', 'is_active', 'stock'),
        Index('idx_prod_price', 'price'),
    )

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name})>"


class ProductVariant(Base):
    __tablename__ = "product_variants"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False) # مثلا: قرمز، XL
    price_adjustment = Column(Numeric(12, 0), default=0) # مبلغ اضافه یا کسر شده
    stock = Column(Integer, default=0)

    product = relationship("Product", back_populates="variants")


class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    image_path = Column(String(512), nullable=False)
    image_file_id = Column(String(255), nullable=True)

    product = relationship("Product", back_populates="images")


class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, default=1)
    selected_attributes = Column(Text, nullable=True) # توضیحات متنی اضافه
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Statuses: pending_payment, approved, shipped, rejected, paid
    status = Column(String(32), default="pending_payment", nullable=False, index=True)
    
    total_amount = Column(Numeric(12, 0), nullable=False)
    shipping_cost = Column(Numeric(12, 0), default=0)
    
    shipping_address = Column(Text, nullable=False)
    postal_code = Column(String(20), nullable=True)
    phone_number = Column(String(20), nullable=True)
    
    payment_receipt_photo_id = Column(String(255), nullable=True) # File ID عکس فیش
    tracking_code = Column(String(100), nullable=True) # کد رهگیری پست
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self):
        return f"<Order(id={self.id}, status={self.status})>"


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Numeric(12, 0), nullable=False)
    selected_attributes = Column(Text, nullable=True)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Favorite(Base):
    __tablename__ = "favorites"
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="favorited_by")


class ProductNotification(Base):
    __tablename__ = "product_notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")


class UserAddress(Base):
    __tablename__ = "user_addresses"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(50), nullable=False) # خانه، محل کار
    address_text = Column(Text, nullable=False)
    postal_code = Column(String(20), nullable=True)

    user = relationship("User", back_populates="addresses")


class Setting(Base):
    __tablename__ = "settings"
    key = Column(String(100), primary_key=True, unique=True)
    value = Column(Text, nullable=True)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    status = Column(String(20), default="open", index=True)  # open, pending, closed
    priority = Column(String(20), default="normal")  # low, normal, high
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), index=True)

    user = relationship("User")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketMessage.created_at")


class TicketMessage(Base):
    __tablename__ = "ticket_messages"
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(String(50), nullable=False)  # user_id or admin_id
    text = Column(Text, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket = relationship("Ticket", back_populates="messages")


class Proxy(Base):
    __tablename__ = "proxies"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    protocol = Column(String(20), default="http") # http, socks5
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(100), nullable=True)
    password = Column(String(100), nullable=True)

    is_active = Column(Boolean, default=False, index=True)
    latency = Column(Integer, nullable=True) # ms
    last_tested = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())