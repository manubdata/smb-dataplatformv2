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

For dbt, the project uses DuckDB. The dbt profiles are configured in `dbt_profiles/profiles.yml`, and the dbt project settings are in `dbt_project/dbt_project.yml`. These configurations define how dbt connects to the DuckDB files for both source data and materialized models.

---

## 📦 Data Ingestion (dlt)

This section covers how raw data is brought into the platform, either from external sources via `dlt` pipelines or generated as mock data for development.

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

The data will be loaded into a local DuckDB database at `./duckdb_files/shopify.duckdb`.

### Mock Data Generation

For development and testing purposes, you can generate and populate mock data for various sources.

#### Meta (Facebook) Ads

To generate mock Meta Ads data, run the following script:

```bash
uv run python dlt_pipelines/mock_data/meta_faker.py --count 10 --days 30
```

This will create a `facebook_ads.duckdb` file in the `./duckdb_files` directory, containing `campaigns`, `adsets`, `ads`, and `ads_insights` tables.

#### TikTok Ads

To generate mock TikTok Ads data, run the following script:

```bash
uv run python dlt_pipelines/mock_data/tiktok_faker.py --count 10 --days 30
```

This will create a `tiktok_ads.duckdb` file in the `./duckdb_files` directory, containing `campaigns`, `adgroups`, `ads`, and `ad_reports` tables.

#### Populate Mock Shopify Sales

To add more sales data to the `shopify.duckdb` for testing various date ranges:

```bash
uv run python scripts/populate_shopify_sales.py
```
This script populates sales data from 2025-12-20 to 2025-12-31.

---

## 📊 Data Transformation (dbt)

The project uses `dbt` to transform raw data into structured, analyzable formats, organized into silver (staging) and gold (marts) layers. The target data warehouse for dbt models is `duckdb_files/dbt_metrics.duckdb`.

### Data Layers

*   **Silver Layer (`models/staging/`)**: Contains cleaned and standardized views of the raw data. These models serve as direct interfaces to the bronze layer (raw DuckDB files).
*   **Gold Layer (`models/marts/`)**: Houses aggregated and business-ready tables for reporting and analytics. This layer includes intermediate aggregates (`models/marts/intermediate/`) and final Key Performance Indicator (KPI) reports.

### Calculated Metrics

The gold layer provides the following key e-commerce metrics:

*   **Contribution Margin**: `Net Sales - COGS - Shipping - Transaction Fees - Total Ad Spend`
*   **Marketing Efficiency Ratio (MER)**:
    *   `mer_total_paid_ads`: `Net Sales / (Facebook Spend + Instagram Spend + TikTok Spend)`
    *   `mer_facebook`: `Net Sales / Facebook Spend`
    *   `mer_instagram`: `Net Sales / Instagram Spend`
*   **New Customer Cost Per Acquisition (ncCPA)**: `Total Ad Spend / Count(First Time Orders)`
*   **Net Profit on Ad Spend (NPOAS)**: `Contribution Margin / Total Ad Spend`
*   **LTV:CAC Ratio**: `(Avg Order Value * Purchase Freq) / ncCPA`

### Data Quality and Transformations

*   **COGS Mocking**: Since raw COGS data is not available, a mock value of `50% of net_sales` is applied in the `stg_orders` model.
*   **Ad Platform Granularity**: Meta (Facebook) ad spend is broken down by `publisher_platform` (Facebook vs. Instagram) in the `int_daily_ad_spend` model, enabling granular performance comparison.
*   **Safe Division**: A `safe_divide` macro is implemented to prevent division-by-zero errors in metric calculations.

### dbt Commands

Use the following `poe` commands to interact with the dbt project:

*   **Install dbt packages**:
    ```bash
    uv run poe dbt-deps
    ```
*   **Run all models and tests**: (Recommended for full pipeline execution)
    ```bash
    uv run poe dbt-build
    ```
*   **Run dbt models only**:
    ```bash
    uv run poe dbt-run
    ```
*   **Run dbt tests only**:
    ```bash
    uv run poe dbt-test
    ```
*   **Debug dbt connection**:
    ```bash
    uv run poe dbt-debug
    ```
*   **Clean dbt target and packages directories**:
    ```bash
    uv run poe dbt-clean
    ```

### Data Quality Testing

The dbt project includes comprehensive data quality tests:

*   **Generic Tests**: Applied in `schema.yml` files to enforce constraints like `unique`, `not_null`, `not_negative`, and `accepted_values` (e.g., ensuring `publisher_platform` is either 'facebook' or 'instagram').
*   **Singular Tests**: Custom SQL tests (e.g., `assert_contribution_margin_logic.sql`) to validate specific business rules and data behaviors.

---

## ✅ Testing

The project uses `pytest` for Python unit tests. For comprehensive data transformation testing, `dbt test` (or `dbt build`) is used.

To run all Python tests:

```bash
uv run poe test
```

To run all dbt models and tests (including Python tests is outside dbt scope):

```bash
uv run poe dbt-build
```
