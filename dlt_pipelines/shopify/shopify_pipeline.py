import dlt
from dlt.sources.helpers import requests


@dlt.source(name="shopify", section="shopify")
def shopify_source(
    shop_url: str = dlt.secrets.value,
    client_id: str = dlt.secrets.value,
    client_secret: str = dlt.secrets.value,
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

    @dlt.resource(primary_key="id", write_disposition="merge")
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

    @dlt.resource(primary_key="id", write_disposition="merge")
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

    @dlt.resource(primary_key="id", write_disposition="merge")
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
