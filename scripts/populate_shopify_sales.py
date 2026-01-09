import duckdb
from datetime import datetime, timedelta
import random
from faker import Faker
import uuid
import math
import json

# --- Configuration for the Story ---

PRODUCTS = {
    "prod_A": {"id": 1, "name": "The Best Seller", "price": 50.00, "return_rate": 0.30, "sales_weight": 0.6},
    "prod_B": {"id": 2, "name": "The Sleeper", "price": 120.00, "return_rate": 0.02, "sales_weight": 0.3},
    "prod_C": {"id": 3, "name": "The Dust Collector", "price": 75.00, "return_rate": 0.05, "sales_weight": 0.1},
}

# Trend parameters
BASE_DAILY_ORDERS = 20
GROWTH_FACTOR = 1.008 # This gives ~30% growth over 30 days.

# --- End Configuration ---

def create_tables(con, schema_name):
    """Creates fresh tables for products and orders."""
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")
    
    con.execute(f"DROP TABLE IF EXISTS {schema_name}.products;")
    con.execute(f"DROP TABLE IF EXISTS {schema_name}.orders;")

    con.execute(f"""
        CREATE TABLE {schema_name}.products (
            id BIGINT PRIMARY KEY,
            title VARCHAR,
            vendor VARCHAR,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            product_type VARCHAR,
            status VARCHAR,
            handle VARCHAR,
            tags VARCHAR,
            admin_graphql_api_id VARCHAR,
            _dlt_load_id VARCHAR,
            _dlt_id VARCHAR
        );
    """)

    con.execute(f"""
        CREATE TABLE {schema_name}.orders (
            id BIGINT PRIMARY KEY,
            admin_graphql_api_id VARCHAR,
            created_at TIMESTAMP,
            processed_at TIMESTAMP,
            updated_at TIMESTAMP,
            total_price VARCHAR,
            total_line_items_price VARCHAR,
            total_discounts VARCHAR,
            total_shipping_price_set__shop_money__amount VARCHAR,
            customer__id BIGINT,
            currency VARCHAR,
            name VARCHAR,
            number BIGINT,
            order_number BIGINT,
            financial_status VARCHAR,
            product_id BIGINT,
            product_title VARCHAR,
            product_quantity BIGINT,
            product_price DOUBLE,
            _dlt_load_id VARCHAR,
            _dlt_id VARCHAR
        );
    """)
    print("✅ Fresh 'products' and 'orders' tables created with new schema.")

def insert_products(con, schema_name):
    """Populates the products table."""
    fake = Faker()
    product_records = []
    for key, val in PRODUCTS.items():
        created_at = fake.date_time_between(start_date="-2y", end_date="-1y").isoformat()
        product_records.append(
            (val['id'], val['name'], fake.company(), created_at, created_at,
             'T-Shirt', 'active', val['name'].lower().replace(' ', '-'),
             'mock, demo', str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()))
        )

    con.executemany(f"""
        INSERT INTO {schema_name}.products 
        (id, title, vendor, created_at, updated_at, product_type, status, handle, tags, admin_graphql_api_id, _dlt_load_id, _dlt_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, product_records)
    print(f"✅ Inserted {len(product_records)} products.")

def populate_shopify_sales(db_path: str, days_to_generate: int = 90, schema_name: str = "shopify_data"):
    fake = Faker()
    con = duckdb.connect(database=db_path)

    create_tables(con, schema_name)
    insert_products(con, schema_name)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_to_generate - 1)
    
    date_generated = [start_date + timedelta(days=x) for x in range(days_to_generate)]

    order_records = []
    current_order_id = 1
    current_customer_id = 1
    existing_customer_ids = []

    print(f"Generating sales data from {start_date.date()} to {end_date.date()}...")

    for i, day in enumerate(date_generated):
        num_orders_today = int(BASE_DAILY_ORDERS * (GROWTH_FACTOR ** i))
        
        for _ in range(num_orders_today):
            product_key = random.choices(list(PRODUCTS.keys()), weights=[p['sales_weight'] for p in PRODUCTS.values()], k=1)[0]
            product = PRODUCTS[product_key]

            quantity = random.randint(1, 3)
            line_item_price = product['price'] * quantity

            is_returned = random.random() < product['return_rate']
            refund_amount = 0
            if is_returned:
                refund_amount = line_item_price
                financial_status = "partially_refunded"
            else:
                financial_status = "paid"
            
            shipping_cost = round(random.uniform(5.00, 20.00), 2)
            total_price = line_item_price + shipping_cost

            if random.random() < 0.7 and existing_customer_ids:
                customer_id = random.choice(existing_customer_ids)
            else:
                customer_id = current_customer_id
                existing_customer_ids.append(customer_id)
                current_customer_id += 1

            created_at = datetime.combine(day, datetime.min.time()) + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))

            order_records.append({
                "id": current_order_id,
                "admin_graphql_api_id": f"gid://shopify/Order/{current_order_id}",
                "created_at": created_at,
                "processed_at": created_at + timedelta(minutes=random.randint(5, 60)),
                "updated_at": created_at,
                "total_price": str(total_price),
                "total_line_items_price": str(line_item_price),
                "total_discounts": str(refund_amount),
                "total_shipping_price_set__shop_money__amount": str(shipping_cost),
                "customer__id": customer_id,
                "currency": "USD",
                "name": f"#{1000 + current_order_id}",
                "number": current_order_id,
                "order_number": 1000 + current_order_id,
                "financial_status": financial_status,
                "product_id": product['id'],
                "product_title": product['name'],
                "product_quantity": quantity,
                "product_price": product['price'],
                "_dlt_load_id": "load_id_mock_data",
                "_dlt_id": str(uuid.uuid4())
            })
            current_order_id += 1
            
    con.executemany(f"""
        INSERT INTO {schema_name}.orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [list(rec.values()) for rec in order_records])

    con.close()
    print(f"✅ Successfully generated and inserted {len(order_records)} orders into {db_path}")

if __name__ == "__main__":
    db_file_path = "./duckdb_files/shopify.duckdb"
    populate_shopify_sales(db_file_path, days_to_generate=90)
