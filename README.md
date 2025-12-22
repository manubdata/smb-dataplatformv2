# SMB Data Platform V2

Data Platform as a Service for SMB E-commerce.

## Running the Shopify Pipeline

To run the Shopify pipeline, you need to configure your Shopify credentials in `dlt_pipelines/secrets.toml`. Copy the `dlt_pipelines/secrets.toml` file and replace the placeholder values with your actual Shopify credentials.

```toml
[sources.shopify_source]
api_secret_key = "your_api_secret_key"
shop_url = "your_shop_url.myshopify.com"
```

Once you have configured your credentials, you can run the pipeline using the following command:

```bash
uv run poe run-pipeline
```
