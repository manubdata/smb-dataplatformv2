# SMB Data Platform V2

Data Platform as a Service for SMB E-commerce, using `dlt` and a modern data stack.

## 🚀 Getting Started

### 1. Installation

This project uses `uv` for package and environment management. Install the necessary dependencies, including the `etl`, `dbt`, and `dev` extras:

```bash
uv pip install -e .[etl,dbt,dev]
```

### 2. Configuration

Credentials for data sources are stored in `.dlt/secrets.toml`. Make sure this file is not committed to version control. The project's `.gitignore` is already configured to ignore the `.dlt/` directory.

For dbt, the project uses a flexible profile system (`dbt_profiles/profiles.yml`) that allows switching between local DuckDB for development and BigQuery for production. The dbt project settings are in `dbt_project/dbt_project.yml`.

---

## 📂 Project Structure

The project follows a modular structure to support scalable data pipelines and easy client deployments:

*   `pipelines/`: Contains all `dlt` ingestion pipelines. Each data source (e.g., `shopify`, `facebook_ads`, `tiktok_ads`) is a sub-directory with its own `_pipeline.py` script.
    *   `pipelines/mock_data/`: Houses faker scripts for generating local DuckDB data for rapid testing and demos.
*   `dbt_project/`: Contains the `dbt` models for data transformation, organized into staging and marts layers.
*   `terraform/`: Stores Terraform configurations for deploying the entire data platform infrastructure to Google Cloud Platform (GCP).
*   `duckdb_files/`: Local DuckDB databases generated during local development and testing.
*   `tests/`: Unit and integration tests for pipelines and other components.
*   `scripts/`: Utility scripts (e.g., for populating mock data).
*   `workflows/`: Google Cloud Workflow definitions for orchestrating jobs.

---

## 📦 Data Ingestion (dlt)

This section covers how raw data is brought into the platform. All `dlt` ingestion pipelines are standardized and can load data to either local DuckDB for development or BigQuery for production.

### Unified Pipeline Runner

A single script, `pipelines/run_pipeline.py`, acts as a centralized entry point to execute any ingestion pipeline.

**Usage:**

```bash
uv run python -m pipelines.run_pipeline <pipeline_name> --destination <destination_type>
```

*   `<pipeline_name>`: `shopify`, `facebook_ads`, `tiktok_ads`
*   `<destination_type>`: `duckdb` (for local development/testing) or `bigquery` (for GCP deployment)

**Examples:**

*   **Run Shopify pipeline to local DuckDB:**
    ```bash
    uv run python -m pipelines.run_pipeline shopify --destination duckdb
    ```
*   **Run Facebook Ads pipeline to GCP BigQuery:**
    ```bash
    uv run python -m pipelines.run_pipeline facebook_ads --destination bigquery
    ```

### Mock Data Generation (for local testing/demos)

For rapid local testing and building client demos with DuckDB, you can leverage the faker scripts located in `pipelines/mock_data/`. The standardized `dlt` pipelines (e.g., `facebook_ads`, `tiktok_ads`) will use these when `--destination duckdb` is specified. The `faker` library is now included in the `etl` dependencies to ensure mock data generation works in all environments.

*   **Populate additional mock Shopify sales data (if using local DuckDB):**
    ```bash
    uv run python scripts/populate_shopify_sales.py
    ```

---

## 📊 Data Transformation (dbt)

The project uses `dbt` to transform raw data into structured, analyzable formats, organized into silver (staging) and gold (marts) layers.

### Environment-Aware Data Sources

The `dbt` project is configured to dynamically switch between local DuckDB and cloud BigQuery data sources based on the active `dbt` profile (`target`).

*   When running with the `dev` target (DuckDB), `dbt` will look for data in the local `duckdb_files/`.
*   When running with the `prod` target (BigQuery), `dbt` will connect to the `smb-dataplatform` GCP project and relevant BigQuery datasets (e.g., `shopify_data_raw`, `facebook_ads_data`, `tiktok_ads_data`).

This ensures seamless transition between local development and cloud deployment without manual configuration changes within `dbt` models or source definitions.

### Data Layers

*   **Silver Layer (`models/staging/`)**: Contains cleaned and standardized views of the raw data. These models serve as direct interfaces to the bronze layer (raw DLT output).
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

## 🚀 Deploying to GCP for a New Client

This section outlines the refined process for deploying the entire data platform for a new client using Terraform and orchestrating it with Cloud Workflows.

### 1. Manual Pre-Deployment Steps

Before running any local commands, you must perform the following setup steps manually in the Google Cloud Console and the client's respective data source platforms (e.g., Shopify, Facebook Ads, TikTok Ads).

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

#### b) Data Source API Setup (Shopify, Facebook Ads, TikTok Ads)

For each data source, you will need to set up API access and obtain credentials.

*   **Shopify Custom App Setup:**
    1.  Log in to your client's Shopify store admin interface.
    2.  Navigate to **Apps** -> **Develop apps for your store**.
    3.  Create a new **Custom App** (e.g., `Data Platform Integration`).
    4.  In the app's settings, configure the **API scopes**. You will need at least `read_products`, `read_orders`, and `read_customers` for the ingestion pipeline.
    5.  Go to the **API credentials** tab and note down the **API key** and **API secret key**.
*   **Facebook Ads API Setup:**
    1.  Create a Facebook App and configure access to the Ads API.
    2.  Obtain an Access Token (usually a Long-Lived User Access Token or System User Access Token).
    3.  Note down the Ad Account ID(s).
*   **TikTok Ads API Setup:**
    1.  Create a TikTok for Developers App and configure access to the Ads API.
    2.  Obtain an Access Token and the Advertiser ID(s).

#### c) Google Secret Manager Setup

You must create secrets in Google Secret Manager to securely store the API credentials for each data source. The names of these secrets (e.g., `shop_url`, `client_id`, `client_secret` for Shopify; `facebook_access_token`, `facebook_ad_account_id` for Facebook Ads; `tiktok_access_token`, `tiktok_advertiser_id` for TikTok Ads) are the default values expected by the Terraform configuration and DLT.

**Crucially, the secret values must be the raw text, without any surrounding quotes.** If you include quotes, the pipeline will fail with potential parsing errors.

Run the following `gcloud` commands to create the secrets, replacing the placeholder values with your client's actual information:

```bash
# Shopify Credentials
echo "your-client-shop-name.myshopify.com" | gcloud secrets create shop_url --data-file=- --project=your-gcp-project-id
echo "your-shopify-app-api-key" | gcloud secrets create client_id --data-file=- --project=your-gcp-project-id
echo "your-shopify-app-api-secret-key" | gcloud secrets create client_secret --data-file=- --project=your-gcp-project-id

# Facebook Ads Credentials (example, adjust secret names as per dlt configuration)
echo "your-facebook-long-lived-access-token" | gcloud secrets create facebook_access_token --data-file=- --project=your-gcp-project-id
echo "your-facebook-ad-account-id" | gcloud secrets create facebook_ad_account_id --data-file=- --project=your-gcp-project-id

# TikTok Ads Credentials (example, adjust secret names as per dlt configuration)
echo "your-tiktok-access-token" | gcloud secrets create tiktok_access_token --data-file=- --project=your-gcp-project-id
echo "your-tiktok-advertiser-id" | gcloud secrets create tiktok_advertiser_id --data-file=- --project=your-gcp-project-id
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
    *Ensure `gcp_region` is consistent across all deployments.*

#### b) Build and Push Docker Images

The Docker images for the ingestion and transformation services encapsulate all necessary code and dependencies.

**Important Considerations for Python Packages & Docker:**
*   The `pipelines/` directory is treated as the top-level Python package for all ingestion logic.
*   The `faker` library, used by mock data generators, is included in the `etl` dependencies to ensure it's available in the Docker image.
*   The Docker builds ensure that the Python environment within the container (specifically the `PYTHONPATH`) is correctly configured to discover all `pipelines` modules.

**You must be authenticated with `gcloud` and configured Docker to use Artifact Registry for this step.**
```bash
gcloud auth configure-docker ${gcp_region}-docker.pkg.dev
```
*Replace `${gcp_region}` with the region you specified in `terraform.tfvars`.*

Now, run the following `poe` commands from the **root of the project**:

```bash
# Build, tag, and push the ingestion image
uv run poe build-push-ingestion

# Build, tag, and push the transformation image
uv run poe build-push-transformation
```

#### c) Deploy Infrastructure with Terraform

This step will create all the GCP resources (Artifact Registry, Service Account, Cloud Run jobs, Workflow, Scheduler, IAM bindings for secrets, etc.) as defined in your Terraform files.

**Important: Cloud Run Job Memory for dbt Transformations:**
If you encounter `Out-of-memory` errors (exit code 137) during the transformation job, it indicates that dbt requires more memory for its compilation and execution tasks. You will need to adjust the memory limit in `terraform/main.tf` for the `transformation_runner` job. Locate the `resources` block within the `containers` definition and increase the `memory` value. A good starting point is `2Gi` or `4Gi`.

Example snippet for `transformation_runner` in `terraform/main.tf` (ensure correct nesting):
```terraform
resource "google_cloud_run_v2_job" "transformation_runner" {
  # ...
  template {
    template {
      # ...
      containers {
        # ...
        resources {
          limits = {
            memory = "2Gi" # Increase this value if OOM errors occur
          }
        }
      }
    }
  }
}
```

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
2.  **For Cloud Workflows:** Navigate to the Google Cloud Console -> **Workflows**. Select the workflow (e.g., `your-unique-client-prefix-main-workflow`), go to the **Executions** tab, and click on a failed execution to view its logs and identify the failing step. The workflow is configured with robust `try/except` error handling to provide clearer insights into job failures.

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

---

## 🎨 Frontend (Evidence.dev)

This project uses [Evidence.dev](https://www.evidence.dev/) for data visualization and reporting. The Evidence project is located in the `/viz` directory and connects directly to the DuckDB database generated by the dbt models.

### Running the Frontend

To start the local development server for Evidence:

1.  **Navigate to the viz directory:**
    ```bash
    cd viz
    ```

2.  **Install NPM dependencies (only required once):**
    ```bash
    npm install
    ```

3.  **Run the dev server:**
    ```bash
    npm run dev
    ```
    The dashboard will open in your browser, typically at `http://localhost:3000`.

### Dashboards

The frontend includes two pre-built dashboards:

*   **/ (Daily Health Check)**: The main dashboard inspired by the "Health Check" design. It features interactive metric cards with conditional coloring based on goal achievement, a date range filter, and a trend chart with a built-in metric selector.
*   **/monthly-recap**: A page that provides a high-level overview of the same KPIs aggregated by month, allowing for broader trend analysis.

---

## ⚙️ Development & Testing

### Local Development with DuckDB

For local development and rapid iteration, you can run ingestion pipelines and dbt transformations against local DuckDB files.

1.  **Run Ingestion to DuckDB:**
    Use the unified pipeline runner with `--destination duckdb`:
    ```bash
    uv run python pipelines/run_pipeline.py run_pipeline shopify --destination duckdb
    uv run python pipelines/run_pipeline.py run_pipeline facebook_ads --destination duckdb
    uv run python pipelines/run_pipeline.py run_pipeline tiktok_ads --destination duckdb
    ```
    This will create or update `.duckdb` files in the `duckdb_files/` directory.

2.  **Run dbt against DuckDB:**
    Use the default `dev` dbt target, which is configured for DuckDB:
    ```bash
    uv run poe dbt-build
    ```
    This will materialize your dbt models into `duckdb_files/dbt_metrics.duckdb`.

### Testing

*   **Unit & Integration Tests**:
    ```bash
    uv run poe test
    ```
*   **Linting & Formatting**:
    ```bash
    uv run poe lint
    ```
*   **All Checks**:
    ```bash
    uv run poe check
    ```

---

## ✅ Progress & Future Work

*   **Transformation Layer**: Standardized and deployed the dbt transformation layer to GCP Cloud Run. Fixed various errors related to permissions, memory, and dbt BigQuery type compatibility.
*   **Ingestion Layer**: Standardized `dlt` ingestion pipelines for Shopify, Facebook Ads, and TikTok Ads, enabling flexible deployment to both local DuckDB and BigQuery. A unified pipeline runner has been implemented.
*   **Dbt Configuration**: Updated `dbt` source configurations to dynamically switch between DuckDB and BigQuery based on the active `dbt` target.
*   **Terraform**: Initial Terraform configuration is set up for deploying GCP resources, with client-specific parameterization handled via `terraform.tfvars`.
*   **Cloud Workflows Orchestration**: Implemented robust error handling for Cloud Run job failures within the main workflow, ensuring better visibility and stability.
*   **Docker Builds**: Ensured correct Python package discovery (`PYTHONPATH`) and dependency management (`faker` included in `etl` dependencies) within the Docker images for seamless GCP deployment.

---