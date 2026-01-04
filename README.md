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

## 🚀 Deploying a New Client

This guide walks through the end-to-end process for deploying the entire data pipeline for a new client, leveraging the templatized Terraform configuration.

### 1. Manual Pre-Deployment Steps

Before running any local commands, you must perform the following setup steps manually in the Google Cloud Console and your client's Shopify store.

#### a) Google Cloud Project Setup

1.  **Create a new Google Cloud Project** for the client (e.g., `your-client-gcp-project-id`) or select an existing one.
2.  Ensure you have the **Owner** or **Editor** role for the project.
3.  Make sure **billing is enabled** for the project.
4.  **Authenticate your `gcloud` CLI** and set the project:
    ```bash
    gcloud auth login
    gcloud config set project your-gcp-project-id
    ```
    *Replace `your-gcp-project-id` with the actual project ID you created/selected.*

#### b) Shopify Custom App Setup

1.  Log in to your client's Shopify store admin interface.
2.  Navigate to **Apps** -> **Develop apps for your store**.
3.  Create a new **Custom App** (e.g., `Data Platform Integration`).
4.  In the app's settings, configure the **API scopes**. You will need at least `read_products`, `read_orders`, and `read_customers` for the ingestion pipeline.
5.  Go to the **API credentials** tab and note down the **API key** and **API secret key**. You will need these for the next step.

#### c) Google Secret Manager Setup

You must create three secrets in Google Secret Manager to securely store the Shopify credentials. The names of these secrets (`shop_url`, `client_id`, `client_secret`) are the default values expected by the Terraform configuration.

**Crucially, the secret values must be the raw text, without any surrounding quotes.** If you include quotes, the pipeline will fail with a `NameResolutionError` (DNS resolution error).

Run the following `gcloud` commands to create the secrets, replacing the placeholder values with your client's actual information:

```bash
# Create the shop_url secret (value should NOT have quotes)
echo "your-client-shop-name.myshopify.com" | gcloud secrets create shop_url --data-file=- --project=your-gcp-project-id

# Create the client_id secret (value should NOT have quotes)
echo "your-shopify-app-api-key" | gcloud secrets create client_id --data-file=- --project=your-gcp-project-id

# Create the client_secret secret (value should NOT have quotes)
echo "your-shopify-app-api-secret-key" | gcloud secrets create client_secret --data-file=- --project=your-gcp-project-id
```
*Remember to replace `your-gcp-project-id` with your project ID in these commands.*

### 2. Automated Deployment Steps

Once the manual prerequisites are met, you can deploy the entire infrastructure from your local machine using Terraform and Poe.

#### a) Configure Terraform Variables

1.  Navigate to the `terraform/` directory in your project.
2.  Create a copy of the example variables file:
    ```bash
    cp terraform.tfvars.example terraform.tfvars
    ```
3.  Open `terraform.tfvars` and fill in the values specific to your client's deployment:
    ```terraform
    # terraform/terraform.tfvars

    gcp_project_id = "your-gcp-project-id"        # e.g., "my-client-project-123"
    gcp_region     = "us-central1"                # Or your desired GCP region
    client_name    = "your-unique-client-prefix"  # e.g., "acme-corp" - used for naming resources
    
    # Optional: Override default secret names if they are different in Secret Manager
    # shopify_shop_url_secret_name      = "custom-shop-url-secret"
    # shopify_client_id_secret_name     = "custom-client-id-secret"
    # shopify_client_secret_secret_name = "custom-client-secret-secret"
    ```
    *Ensure `gcp_project_id` matches the project ID set in `gcloud config`.*

#### b) Build and Push Docker Images

These commands build the Docker images for the ingestion and transformation services, tag them with the correct Artifact Registry path (which will include your `client_name` prefix), and push them to Google Artifact Registry.

**You must be authenticated with `gcloud` and configured Docker to use Artifact Registry for this step.**
```bash
gcloud auth configure-docker ${gcp_region}-docker.pkg.dev
```
*Replace `${gcp_region}` with the region you specified in `terraform.tfvars`.*

Now, run the following `poe` commands from the **root of the project**:

```bash
# Build, tag, and push the ingestion image
uv run poe build-push-ingestion -- project_id=your-gcp-project-id client_name=your-unique-client-prefix region=your-gcp-region

# Build, tag, and push the transformation image
uv run poe build-push-transformation -- project_id=your-gcp-project-id client_name=your-unique-client-prefix region=your-gcp-region
```
*Note: The `--` separates `poe` arguments from arguments passed to the underlying `shell` command. The `project_id`, `client_name`, and `region` are passed as environment variables to the shell command executed by `poe`.*

#### c) Deploy Infrastructure with Terraform

This step will create all the GCP resources (Artifact Registry, Service Account, Cloud Run jobs, Workflow, Scheduler, IAM bindings for secrets, etc.) as defined in your Terraform files.

From the **root of the project**:
```bash
# Initialize Terraform (only needed once per project setup)
uv run poe tf-init

# Plan and apply the changes
uv run poe tf-apply
```
Terraform will read the variables from your `terraform.tfvars` file and configure the resources accordingly. Review the plan carefully before approving the apply.

### 3. Debugging and Managing the Pipeline

#### a) Checking Logs

If a Cloud Run job fails or a Workflow execution errors out, the most important step is to check the logs.

1.  **For Cloud Run Jobs:** Navigate to the Google Cloud Console -> **Cloud Run** -> **Jobs**. Select the job (e.g., `your-unique-client-prefix-ingestion-runner`), go to the **Executions** tab, and click on a failed execution to view its logs.
2.  **For Cloud Workflows:** Navigate to the Google Cloud Console -> **Workflows**. Select the workflow (e.g., `your-unique-client-prefix-main-workflow`), go to the **Executions** tab, and click on a failed execution to view its logs and identify the failing step.

#### b) Triggering the Workflow Manually

Once deployed, you can trigger the entire data pipeline immediately via the Cloud Workflow:

```bash
gcloud workflows execute your-unique-client-prefix-main-workflow --location=your-gcp-region
```
*Replace placeholders with your configured values.*

#### c) Scheduled Runs

The pipeline is scheduled to run daily via a Cloud Scheduler job (e.g., `your-unique-client-prefix-workflow-scheduler`). By default, this job is created in a **paused** state to prevent unexpected charges or executions during initial setup.

#### d) Activating/Deactivating the Schedule

To activate or pause the daily pipeline runs:

1.  Open the `terraform/main.tf` file.
2.  Find the `google_cloud_scheduler_job.workflow_scheduler` resource.
3.  Set the `paused` argument to `false` (to activate daily runs) or `true` (to pause them).
4.  Apply the change:
    ```bash
    uv run poe tf-apply
    ```

#### e) Tearing Down the Infrastructure

To completely remove all deployed cloud resources for a client and stop all associated costs, you can run `terraform destroy`.

From the **root of the project**:
```bash
uv run poe tf-destroy # This task should be added to pyproject.toml
```
*Note: A `tf-destroy` poe task simplifies this. Ensure to add `deletion_protection = false` to any newly added resources if you plan to destroy them via Terraform.*

### Extending `pyproject.toml` for Deployment

To enable the `poe` commands mentioned above, add the following tasks to your `pyproject.toml` under the `[tool.poe.tasks]` section:

```toml
# --- Deployment (GCP) ---
build-push-ingestion = { shell = "docker build -f ingestion.Dockerfile -t ${region}-docker.pkg.dev/${project_id}/${client_name}-artifact-repo/ingestion:latest . && docker push ${region}-docker.pkg.dev/${project_id}/${client_name}-artifact-repo/ingestion:latest", help = "Builds and pushes the dlt ingestion Docker image to Artifact Registry." }
build-push-transformation = { shell = "docker build -f transformation.Dockerfile -t ${region}-docker.pkg.dev/${project_id}/${client_name}-artifact-repo/transformation:latest . && docker push ${region}-docker.pkg.dev/${project_id}/${client_name}-artifact-repo/transformation:latest", help = "Builds and pushes the dbt transformation Docker image to Artifact Registry." }
tf-destroy = { cmd = "terraform destroy -auto-approve", cwd = "terraform", help = "Destroys all Terraform-managed infrastructure." }

# Example usage for build-push tasks:
# uv run poe build-push-ingestion -- project_id=... client_name=... region=...


