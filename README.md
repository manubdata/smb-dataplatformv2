# SMB Data Platform V2

Data Platform as a Service for SMB E-commerce, using dlt and a modern data stack.

## 🚀 Getting Started

### 1. Installation

This project uses `uv` for package and environment management. Install the necessary dependencies, including the `etl`, `dbt`, and `dev` extras:

```bash
uv pip install -e .[etl,dbt,dev]
```

### 2. Configuration

Credentials for data sources are stored in `.dlt/secrets.toml`. Make sure this file is not committed to version control. The project's `.gitignore` is already configured to ignore the `.dlt/` directory.

---

## 📦 Data Pipelines

### Shopify Pipeline

This pipeline extracts Products, Orders, and Customers data from the Shopify API.

#### Configuration

To run the Shopify pipeline, you need to configure your Shopify App credentials in `.dlt/secrets.toml`. The pipeline uses OAuth 2.0 with a client ID and secret to fetch a fresh access token on each run.

```toml
# .dlt/secrets.toml
[shopify]
shop_url = "your-shop-name.myshopify.com"
client_id = "your_app_client_id"
client_secret = "your_app_client_secret"
```

#### Incremental Loading

The pipeline is configured for incremental loading based on the `updated_at` field for all resources. On the first run, it will load all historical data (from `2023-01-01`). Subsequent runs will only fetch records that have been created or updated since the last run, making it efficient.

#### Running the Pipeline

You can run the pipeline using the following `poe` command:

```bash
uv run poe run-pipeline
```

The data will be loaded into a local DuckDB database at `shopify.duckdb`.

---

## ⚙️ Mock Data Generation

For development and testing purposes, you can generate mock advertising data for Meta (Facebook) and TikTok.

### Meta (Facebook) Ads

To generate mock Meta Ads data, run the following script:

```bash
uv run python dlt_pipelines/mock_data/meta_faker.py --count 10 --days 30
```

This will create a `facebook_ads.duckdb` file in the `./mock_data` directory, containing `campaigns`, `adsets`, `ads`, and `ads_insights` tables.

### TikTok Ads

To generate mock TikTok Ads data, run the following script:

```bash
uv run python dlt_pipelines/mock_data/tiktok_faker.py --count 10 --days 30
```

This will create a `tiktok_ads.duckdb` file in the `./mock_data` directory, containing `campaigns`, `adgroups`, `ads`, and `ad_reports` tables.

---

## ✅ Testing

The project uses `pytest` for testing. To run all tests, use the following command:

```bash
uv run poe test
```

This will execute all tests in the `tests/` directory, ensuring that both the data pipelines and mock data generators are working correctly.