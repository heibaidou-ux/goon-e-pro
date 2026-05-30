from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    subcategories = Column(Text, default="[]")  # JSON array
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    # Products accessed via string category name, not FK
    # products = relationship("Product", ...)  # removed — Product uses string category


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, index=True)
    name = Column(String(200), nullable=False)
    brand = Column(String(100))
    category = Column(String(50), nullable=False)
    sub_category = Column(String(50))
    spec = Column(String(100))
    unit = Column(String(20))
    internal_price = Column(Float, default=0)
    retail_price = Column(Float, default=0)
    market_price = Column(Float, default=0)
    is_food = Column(Boolean, default=False)
    shelf_life = Column(Integer)  # days
    is_active = Column(Boolean, default=True)
    status = Column(String(10), default="上架")  # 上架 | 下架

    # E-commerce fields (Gemini review)
    story = Column(Text)
    origin = Column(String(200))
    brewing_tips = Column(Text)  # JSON
    description = Column(Text)

    # Inventory
    default_supplier = Column(String(200))
    lead_time = Column(Integer, default=7)  # days
    safe_stock = Column(Float, default=0)
    max_stock = Column(Float, default=0)
    current_stock = Column(Float, default=0)

    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan",
                          order_by="ProductImage.sort_order")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    url_original = Column(String(500), nullable=False)
    url_thumbnail = Column(String(500))   # 240px
    url_medium = Column(String(500))      # 480px
    url_large = Column(String(500))       # 800px
    is_cover = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="images")
