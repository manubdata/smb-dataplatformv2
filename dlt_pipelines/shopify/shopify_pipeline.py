
import dlt
from dlt.sources.helpers import requests
from dlt.common.typing import TDataItem

@dlt.source(name="shopify", section="shopify")
def shopify_source(api_secret_key: str = dlt.secrets.value, shop_url: str = dlt.secrets.value):
    
    base_url = f"https://{shop_url}/admin/api/2024-04/"

    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": api_secret_key,
    }

    @dlt.resource(primary_key="id", write_disposition="merge")
    def products():
        
        url = base_url + "products.json"
        
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            yield data.get("products", [])

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

    @dlt.resource(primary_key="id", write_disposition="merge")
    def orders():
        
        url = base_url + "orders.json"
        
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            yield data.get("orders", [])
            
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

    @dlt.resource(primary_key="id", write_disposition="merge")
    def customers():
        
        url = base_url + "customers.json"
        
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            yield data.get("customers", [])
            
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

def run_pipeline():
    
    pipeline = dlt.pipeline(
        pipeline_name="shopify",
        destination="duckdb",
        dataset_name="shopify_data",
    )

    load_info = pipeline.run(shopify_source())

    print(load_info)

if __name__ == "__main__":
    run_pipeline()