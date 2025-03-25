"""
This module defines the data models for the recipe application.
"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from app.core.database import Base


class Bill(Base):
    """Represents a bill"""
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    bill_no = Column(Integer, index=True, unique=True)
    bill_date = Column(Date, default=func.current_date()) # pylint: disable=not-callable
    num_items = Column(Integer, default=0)  # Track number of ingredients

    cart = relationship("Cart", back_populates="bill")

    @hybrid_property
    def item_count(self):
        """Dynamic count of products"""
        return sum(item.quantity for item in self.cart)

class Cart(Base):
    """Represents an products in a cart"""
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    product_id = Column(Integer, ForeignKey("products_catalogue.id"), index=True, nullable=False)
    quantity = Column(Float)
    mrp = Column(Float)
    total = Column(Float)
    buy_date = Column(Date, default=func.current_date()) # pylint: disable=not-callable
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    bill = relationship("Bill", back_populates="cart")
    product = relationship("ProductCatalogue", back_populates="cart")


class ProductCatalogue(Base):
    """Represents a catalogue of products"""
    __tablename__ = "products_catalogue"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    brand = Column(String)
    mrp = Column(Float)
    pack_size = Column(String)
    category = Column(String)
    upload_date = Column(Date, default=func.current_date()) # pylint: disable=not-callable
    cart = relationship("Cart", back_populates="product")