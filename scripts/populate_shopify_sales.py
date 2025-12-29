import duckdb
from datetime import datetime, timedelta
import random
from faker import Faker
import uuid 

def populate_shopify_sales(db_path: str, start_date_str: str, end_date_str: str, schema_name: str = "shopify_data"):
    fake = Faker()
    con = duckdb.connect(database=db_path)

    # Get max existing order_id and customer_id
    max_order_id = con.execute(f"SELECT MAX(id) FROM {schema_name}.orders").fetchone()[0] or 0
    max_customer_id_query = con.execute(f"SELECT MAX(customer__id) FROM {schema_name}.orders").fetchone()
    max_customer_id = max_customer_id_query[0] if max_customer_id_query and max_customer_id_query[0] is not None else 0
    
    current_order_id = max_order_id + 1
    current_customer_id = max_customer_id + 1

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    date_generated = [start_date + timedelta(days=x) for x in range(0, (end_date-start_date).days + 1)]

    records = []
    
    # Fetch existing customer IDs to reuse some of them
    existing_customer_ids_raw = con.execute(f"SELECT DISTINCT customer__id FROM {schema_name}.orders WHERE customer__id IS NOT NULL").fetchall()
    existing_customer_ids = [c[0] for c in existing_customer_ids_raw if c[0] is not None]

    for day in date_generated:
        num_orders_today = random.randint(5, 20) # 5 to 20 orders per day
        for _ in range(num_orders_today):
            order_id = current_order_id
            
            # Randomly pick an existing customer or create a new one
            if random.random() < 0.7 and existing_customer_ids: # 70% chance to be an existing customer
                customer_id = random.choice(existing_customer_ids)
            else:
                customer_id = current_customer_id
                existing_customer_ids.append(customer_id)
                current_customer_id += 1 # Only increment if new customer is created

            created_at = datetime.combine(day, datetime.min.time()) + timedelta(hours=random.randint(9, 17), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
            
            total_price = round(random.uniform(50.00, 500.00), 2)
            shipping_cost = round(random.uniform(5.00, 20.00), 2)
            
            # Minimal required fields for the dbt model and schema structure
            records.append({
                "id": order_id,
                "admin_graphql_api_id": str(uuid.uuid4()), 
                "created_at": created_at.isoformat(), 
                "total_price": str(total_price), # Cast to VARCHAR as per schema
                "total_shipping_price_set__shop_money__amount": str(shipping_cost), # Cast to VARCHAR
                "customer__id": customer_id,
                "currency": "USD", 
                "processed_at": created_at.isoformat(),
                "name": fake.word().upper() + str(random.randint(1000,9999)), # Random order name
                "number": random.randint(1000, 9999),
                "order_number": random.randint(1000, 9999),
                "subtotal_price": str(total_price - shipping_cost), # Mock
                "updated_at": created_at.isoformat(),
                "_dlt_load_id": str(uuid.uuid4()),
                "_dlt_id": str(uuid.uuid4())
            })
            current_order_id += 1
            
    # Define columns to insert based on the `dlt` pipeline schema
    columns_to_insert = [
        "id", "admin_graphql_api_id", "created_at", "total_price",
        "total_shipping_price_set__shop_money__amount", "customer__id",
        "currency", "processed_at", "name", "number", "order_number", "subtotal_price",
        "updated_at", "_dlt_load_id", "_dlt_id" # dlt internal columns also populated
    ]
    
    placeholders = ', '.join(['?' for _ in columns_to_insert])
    column_names_sql = ', '.join([f'"{col}"' for col in columns_to_insert])
    
    insert_sql = f"INSERT INTO {schema_name}.orders ({column_names_sql}) VALUES ({placeholders})"
    
    for rec in records:
        # Ensure values are in the correct order for the INSERT statement
        values = [rec.get(col) for col in columns_to_insert]
        con.execute(insert_sql, values)
        
    con.commit()
    con.close()
    print(f"Successfully added {len(records)} sales records to {db_path} for dates {start_date_str} to {end_date_str}")


if __name__ == "__main__":
    db_file_path = "C:/Users/manubdata/Desktop/Workspace/smb-dataplatformV2/duckdb_files/shopify.duckdb"
    start_date = "2025-12-20" # Start from the day after the existing sales
    end_date = "2025-12-31"
    
    populate_shopify_sales(db_file_path, start_date, end_date)
