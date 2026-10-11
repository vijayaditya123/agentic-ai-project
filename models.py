from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ProductCategoryTranslation(Base):
    __tablename__ = "product_category_translation"

    product_category_name: Mapped[str] = mapped_column(String, primary_key=True)
    product_category_name_english: Mapped[str] = mapped_column(String)


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_unique_id: Mapped[str] = mapped_column(String)
    customer_zip_code_prefix: Mapped[int] = mapped_column(Integer)
    customer_city: Mapped[str] = mapped_column(String)
    customer_state: Mapped[str] = mapped_column(String)


class Seller(Base):
    __tablename__ = "sellers"

    seller_id: Mapped[str] = mapped_column(String, primary_key=True)
    seller_zip_code_prefix: Mapped[int] = mapped_column(Integer)
    seller_city: Mapped[str] = mapped_column(String)
    seller_state: Mapped[str] = mapped_column(String)


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[str] = mapped_column(String, primary_key=True)
    product_category_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    product_name_lenght: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    product_description_lenght: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    product_photos_qty: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    product_weight_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    product_length_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    product_height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    product_width_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.customer_id"))
    order_status: Mapped[str] = mapped_column(String)
    order_purchase_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    order_approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    order_delivered_carrier_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    order_delivered_customer_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    order_estimated_delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class OrderItem(Base):
    __tablename__ = "order_items"

    order_id: Mapped[str] = mapped_column(ForeignKey("orders.order_id"), primary_key=True)
    order_item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id"))
    seller_id: Mapped[str] = mapped_column(ForeignKey("sellers.seller_id"))
    shipping_limit_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    price: Mapped[float] = mapped_column(Float)
    freight_value: Mapped[float] = mapped_column(Float)


class OrderPayment(Base):
    __tablename__ = "order_payments"

    order_id: Mapped[str] = mapped_column(ForeignKey("orders.order_id"), primary_key=True)
    payment_sequential: Mapped[int] = mapped_column(Integer, primary_key=True)
    payment_type: Mapped[str] = mapped_column(String)
    payment_installments: Mapped[int] = mapped_column(Integer)
    payment_value: Mapped[float] = mapped_column(Float)


class OrderReview(Base):
    __tablename__ = "order_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    review_id: Mapped[str] = mapped_column(String)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.order_id"))
    review_score: Mapped[int] = mapped_column(Integer)
    review_comment_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    review_comment_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    review_creation_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    review_answer_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)