from pathlib import Path
import pandas as pd 
from db import engine

data_path = Path(__file__).parent / "data" / "raw"

def load(table,filename,data_col= None):
    df = pd.read_csv(data_path  / filename)
    for col in data_col or []:
        df[col] = pd.to_datetime(df[col])
    df.to_sql(table,engine,if_exists="append",index=False,chunksize=5000)
    print(f"{table}: {len(df)} rows loaded")


load("product_category_translation", "product_category_name_translation.csv")
load("customers", "olist_customers_dataset.csv")
load("sellers", "olist_sellers_dataset.csv")
load("products", "olist_products_dataset.csv")
load(
    "orders",
    "olist_orders_dataset.csv",
    [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
)
load("order_items", "olist_order_items_dataset.csv", ["shipping_limit_date"])
load("order_payments", "olist_order_payments_dataset.csv")
load(
    "order_reviews",
    "olist_order_reviews_dataset.csv",
    ["review_creation_date", "review_answer_timestamp"],
)
