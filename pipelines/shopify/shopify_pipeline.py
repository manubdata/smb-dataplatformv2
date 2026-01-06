import dlt
from dlt.sources.helpers import requests
import os
import argparse # Import argparse

@dlt.source(name="shopify", section="shopify")
def shopify_source(
    shop_url: str = os.environ.get("SHOP_URL"),
    client_id: str = os.environ.get("CLIENT_ID"),
    client_secret: str = os.environ.get("CLIENT_SECRET"),
):
    # First, get a fresh access token using client credentials
    token_url = f"https://{shop_url}/admin/oauth/access_token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(token_url, json=payload)
    response.raise_for_status()
    access_token = response.json()["access_token"]

    # Now, use the obtained access token for subsequent API calls
    base_url = f"https://{shop_url}/admin/api/2024-04/"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token,
    }

    @dlt.resource(primary_key="id", write_disposition="merge", columns={
        "template_suffix": {"data_type": "text"},
        "image": {"data_type": "text"}, # This is a complex object, might need more specific handling
    })
    def products(updated_at=dlt.sources.incremental("updated_at", initial_value="2023-01-01T00:00:00Z")):
        url = base_url + "products.json"
        params = {"updated_at_min": updated_at.last_value, "order": "updated_at asc"}

        while url:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            yield data.get("products", [])

            # For the next paginated request, Shopify includes the parameters in the Link header URL
            params = {}

            # https://shopify.dev/docs/api/admin-rest/2024-04/resources/product#get-products?page_info
            # The page_info is a header, we need to parse it to get the next url
            if "Link" in response.headers:
                links = requests.utils.parse_header_links(response.headers["Link"])
                next_url = None
                for link in links:
                    if link.get("rel") == "next":
                        next_url = link.get("url")
                        break
                url = next_url
            else:
                url = None

    @dlt.resource(primary_key="id", write_disposition="merge", columns={
        "browser_ip": {"data_type": "text"},
        "cancel_reason": {"data_type": "text"},
        "cancelled_at": {"data_type": "timestamp"},
        "cart_token": {"data_type": "text"},
        "checkout_id": {"data_type": "text"},
        "checkout_token": {"data_type": "text"},
        "client_details": {"data_type": "text"},
        "closed_at": {"data_type": "timestamp"},
        "current_total_additional_fees_set": {"data_type": "text"},
        "current_total_duties_set": {"data_type": "text"},
        "customer_locale": {"data_type": "text"},
        "device_id": {"data_type": "text"},
        "fulfillment_status": {"data_type": "text"},
        "landing_site": {"data_type": "text"},
        "landing_site_ref": {"data_type": "text"},
        "location_id": {"data_type": "bigint"},
        "merchant_of_record_app_id": {"data_type": "text"},
        "note": {"data_type": "text"},
        "original_total_additional_fees_set": {"data_type": "text"},
        "original_total_duties_set": {"data_type": "text"},
        "phone": {"data_type": "text"},
        "po_number": {"data_type": "text"},
        "reference": {"data_type": "text"},
        "referring_site": {"data_type": "text"},
        "source_identifier": {"data_type": "text"},
        "source_url": {"data_type": "text"},
        "user_id": {"data_type": "bigint"},
        "billing_address__address2": {"data_type": "text"},
        "billing_address__company": {"data_type": "text"},
        "customer__note": {"data_type": "text"},
        "customer__multipass_identifier": {"data_type": "text"},
        "customer__email_marketing_consent__consent_updated_at": {"data_type": "timestamp"},
        "customer__sms_marketing_consent__consent_updated_at": {"data_type": "timestamp"},
        "customer__default_address__company": {"data_type": "text"},
        "customer__default_address__address2": {"data_type": "text"},
        "payment_terms": {"data_type": "text"},
        "shipping_address__address2": {"data_type": "text"},
        "shipping_address__company": {"data_type": "text"},
    })
    def orders(updated_at=dlt.sources.incremental("updated_at", initial_value="2023-01-01T00:00:00Z")):
        url = base_url + "orders.json"
        params = {"updated_at_min": updated_at.last_value, "order": "updated_at asc", "status": "any"}


        while url:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            yield data.get("orders", [])

            params = {}

            if "Link" in response.headers:
                links = requests.utils.parse_header_links(response.headers["Link"])
                next_url = None
                for link in links:
                    if link.get("rel") == "next":
                        next_url = link.get("url")
                        break
                url = next_url
            else:
                url = None

    @dlt.resource(primary_key="id", write_disposition="merge", columns={
        "multipass_identifier": {"data_type": "text"},
        "email_marketing_consent__consent_updated_at": {"data_type": "timestamp"},
        "sms_marketing_consent__consent_updated_at": {"data_type": "timestamp"},
        "default_address__address2": {"data_type": "text"},
    })
    def customers(updated_at=dlt.sources.incremental("updated_at", initial_value="2023-01-01T00:00:00Z")):
        url = base_url + "customers.json"
        params = {"updated_at_min": updated_at.last_value, "order": "updated_at asc"}

        while url:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            yield data.get("customers", [])

            params = {}

            if "Link" in response.headers:
                links = requests.utils.parse_header_links(response.headers["Link"])
                next_url = None
                for link in links:
                    if link.get("rel") == "next":
                        next_url = link.get("url")
                        break
                url = next_url
            else:
                url = None

    return (
        products,
        orders,
        customers,
    )

def run_pipeline(destination: str = "duckdb"): # Modified function signature
    pipeline_name = f"shopify_to_{destination}" # Use f-string for pipeline name
    dataset_name = "shopify_data_raw" # Use consistent dataset name

    if destination == "bigquery":
        print("Running pipeline to BigQuery")
        pipeline = dlt.pipeline(
            pipeline_name=pipeline_name,
            destination="bigquery",
            dataset_name=dataset_name,
        )
    elif destination == "duckdb": # Added elif for duckdb
        from dlt.destinations import duckdb
        print("Running pipeline to DuckDB")
        pipeline = dlt.pipeline(
            pipeline_name=pipeline_name, # Use consistent pipeline name
            destination=duckdb(credentials=f"./duckdb_files/{dataset_name}.duckdb"), # Use f-string for credentials
            dataset_name=dataset_name,
        )
    else: # Added else for unsupported destinations
        raise ValueError(f"Unsupported destination: {destination}")

    load_info = pipeline.run(shopify_source())

    print(load_info)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", default="duckdb", help="The destination to load data to (e.g., 'duckdb', 'bigquery')")
    args = parser.parse_args()
    
    run_pipeline(args.destination)