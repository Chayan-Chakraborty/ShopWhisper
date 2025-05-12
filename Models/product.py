from sqlalchemy import (
    create_engine, Column, String, Integer, BigInteger, Text, Boolean,
    ForeignKey, DateTime, Double, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

# DB Connection (replace with your actual credentials)
DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/your_database"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Category Model
class Category(Base):
    __tablename__ = 'category'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(1000))
    is_active = Column(Boolean, default=True, nullable=False)
    identifier = Column(String(255), unique=True, nullable=False)
    sku_prefix = Column(String(13), unique=True, nullable=False)

    products = relationship("Product", back_populates="category")
    category_attributes = relationship("CategoryAttribute", back_populates="category")

# Global Attribute Model
class GlobalAttribute(Base):
    __tablename__ = 'global_attribute'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100))
    description = Column(String(1000))

    category_attributes = relationship("CategoryAttribute", back_populates="global_attribute")

# Category Brand Index Model
class CategoryBrandIndex(Base):
    __tablename__ = 'category_brand_index'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    products = relationship("Product", back_populates="category_brand_index")

# Product Model
class Product(Base):
    __tablename__ = 'product'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sku = Column(String(255), nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    category_id = Column(BigInteger, ForeignKey('category.id'))
    description = Column(String(1000))
    mrp = Column(Double)
    status = Column(String(255), nullable=False)
    per_unit_mrp_price = Column(Double)
    unit_type = Column(String(255))
    per_unit_selling_price = Column(Double)
    unit_value = Column(Double)
    selling_price = Column(Double)
    category_brand_index_id = Column(BigInteger, ForeignKey('category_brand_index.id'))
    is_active = Column(Boolean, default=True)
    discount = Column(Double)

    category = relationship("Category", back_populates="products")
    category_brand_index = relationship("CategoryBrandIndex", back_populates="products")
    attributes = relationship("ProductAttribute", back_populates="product")

# Category Attribute Model
class CategoryAttribute(Base):
    __tablename__ = 'category_attribute'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_id = Column(BigInteger, ForeignKey('category.id'))
    global_attribute_id = Column(BigInteger, ForeignKey('global_attribute.id'))
    is_mandate = Column(Boolean)
    filter_values = Column(Text)

    category = relationship("Category", back_populates="category_attributes")
    global_attribute = relationship("GlobalAttribute", back_populates="category_attributes")
    product_attributes = relationship("ProductAttribute", back_populates="category_attribute")

# Product Attribute Model
class ProductAttribute(Base):
    __tablename__ = 'product_attribute'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_attribute_id = Column(BigInteger, ForeignKey('category_attribute.id'))
    product_id = Column(BigInteger, ForeignKey('product.id'))
    description = Column(String(1000))
    variant_tag = Column(String(255))
    value = Column(String(1000), nullable=False)
    sequence_id = Column(BigInteger)

    product = relationship("Product", back_populates="attributes")
    category_attribute = relationship("CategoryAttribute", back_populates="product_attributes")

# Create all tables
Base.metadata.create_all(engine)

