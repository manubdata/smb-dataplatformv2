variable "gcp_project_id" {
  description = "The Google Cloud project ID to deploy the resources to."
  type        = string
}

variable "gcp_region" {
  description = "The Google Cloud region to deploy the resources to."
  type        = string
  default     = "us-central1"
}

variable "client_name" {
  description = "A unique name for the client (e.g., 'acme-corp'). This will be used to prefix resource names."
  type        = string
}

variable "shopify_shop_url_secret_name" {
  description = "The name of the secret in Secret Manager that holds the Shopify shop URL."
  type        = string
  default     = "shop_url"
}

variable "shopify_client_id_secret_name" {
  description = "The name of the secret in Secret Manager that holds the Shopify client ID."
  type        = string
  default     = "client_id"
}

variable "shopify_client_secret_secret_name" {
  description = "The name of the secret in Secret Manager that holds the Shopify client secret."
  type        = string
  default     = "client_secret"
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# 1. Enable APIs
resource "google_project_service" "apis" {
  project = var.gcp_project_id
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudscheduler.googleapis.com",
    "bigquery.googleapis.com",
    "workflows.googleapis.com",
    "workflowexecutions.googleapis.com",
    "secretmanager.googleapis.com"
  ])
  service            = each.key
  disable_on_destroy = false
}

# 2. Create the Docker Registry
resource "google_artifact_registry_repository" "repo" {
  project       = var.gcp_project_id
  location      = var.gcp_region
  repository_id = "${var.client_name}-artifact-repo"
  format        = "DOCKER"
  depends_on    = [google_project_service.apis]
}

# 3. Create the Service Account
resource "google_service_account" "job_runner" {
  project      = var.gcp_project_id
  account_id   = "${var.client_name}-job-runner"
  display_name = "Service Account for ${var.client_name}"
}

# 4. Give Permissions to the Service Account
resource "google_project_iam_member" "bq_admin" {
  project = var.gcp_project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.job_runner.email}"
}

resource "google_project_iam_member" "log_writer" {
  project = var.gcp_project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.job_runner.email}"
}

resource "google_project_iam_member" "run_jobs_runner" {
  project = var.gcp_project_id
  role    = "roles/run.admin" # Using run.admin to ensure it can run jobs
  member  = "serviceAccount:${google_service_account.job_runner.email}"
}

resource "google_project_iam_member" "workflow_invoker" {
  project = var.gcp_project_id
  role    = "roles/workflows.invoker"
  member  = "serviceAccount:${google_service_account.job_runner.email}"
}

resource "google_project_iam_member" "bq_job_user" {
  project = var.gcp_project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.job_runner.email}"
}

# --- 5. Secret Management (Shopify API Credentials) ---

# Look up the secrets that were created manually
data "google_secret_manager_secret" "shopify_shop_url" {
  project   = var.gcp_project_id
  secret_id = var.shopify_shop_url_secret_name
}

data "google_secret_manager_secret" "shopify_client_id" {
  project   = var.gcp_project_id
  secret_id = var.shopify_client_id_secret_name
}

data "google_secret_manager_secret" "shopify_client_secret" {
  project   = var.gcp_project_id
  secret_id = var.shopify_client_secret_secret_name
}

# Grant the Service Account access to the secrets
resource "google_secret_manager_secret_iam_member" "shopify_shop_url_accessor" {
  project   = var.gcp_project_id
  secret_id = data.google_secret_manager_secret.shopify_shop_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.job_runner.email}"
}

resource "google_secret_manager_secret_iam_member" "shopify_client_id_accessor" {
  project   = var.gcp_project_id
  secret_id = data.google_secret_manager_secret.shopify_client_id.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.job_runner.email}"
}

resource "google_secret_manager_secret_iam_member" "shopify_client_secret_accessor" {
  project   = var.gcp_project_id
  secret_id = data.google_secret_manager_secret.shopify_client_secret.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.job_runner.email}"
}

output "sa_email" {
  value = google_service_account.job_runner.email
}

# 6. Define the Cloud Run Jobs
resource "google_cloud_run_v2_job" "shopify_ingestion_runner" {
  project             = var.gcp_project_id
  name                = "${var.client_name}-shopify-ingestion-runner"
  location            = var.gcp_region
  deletion_protection = false

  template {
    template {
      service_account = google_service_account.job_runner.email
      max_retries     = 1
      timeout         = "300s" # 5 minutes
      containers {
        image = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.repo.repository_id}/ingestion:latest"
        command = ["python", "-m", "pipelines.run_pipeline", "shopify", "--destination", "bigquery"]

        env {
          name = "SOURCES__SHOPIFY__SHOP_URL"
          value_source {
            secret_key_ref {
              secret  = data.google_secret_manager_secret.shopify_shop_url.secret_id
              version = "latest"
            }
          }
        }
        env {
          name = "SOURCES__SHOPIFY__CLIENT_ID"
          value_source {
            secret_key_ref {
              secret  = data.google_secret_manager_secret.shopify_client_id.secret_id
              version = "latest"
            }
          }
        }
        env {
          name = "SOURCES__SHOPIFY__CLIENT_SECRET"
          value_source {
            secret_key_ref {
              secret  = data.google_secret_manager_secret.shopify_client_secret.secret_id
              version = "latest"
            }
          }
        }
      }
    }
  }
  depends_on = [
    google_secret_manager_secret_iam_member.shopify_shop_url_accessor,
    google_secret_manager_secret_iam_member.shopify_client_id_accessor,
    google_secret_manager_secret_iam_member.shopify_client_secret_accessor,
  ]
}

resource "google_cloud_run_v2_job" "facebook_ads_ingestion_runner" {
  project             = var.gcp_project_id
  name                = "${var.client_name}-facebook-ads-ingestion-runner"
  location            = var.gcp_region
  deletion_protection = false

  template {
    template {
      service_account = google_service_account.job_runner.email
      max_retries     = 1
      timeout         = "300s" # 5 minutes
      containers {
        image = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.repo.repository_id}/ingestion:latest"
        command = ["python", "-m", "pipelines.run_pipeline", "facebook_ads", "--destination", "bigquery"]
      }
    }
  }
}

resource "google_cloud_run_v2_job" "tiktok_ads_ingestion_runner" {
  project             = var.gcp_project_id
  name                = "${var.client_name}-tiktok-ads-ingestion-runner"
  location            = var.gcp_region
  deletion_protection = false

  template {
    template {
      service_account = google_service_account.job_runner.email
      max_retries     = 1
      timeout         = "300s" # 5 minutes
      containers {
        image = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.repo.repository_id}/ingestion:latest"
        command = ["python", "-m", "pipelines.run_pipeline", "tiktok_ads", "--destination", "bigquery"]
      }
    }
  }
}

resource "google_cloud_run_v2_job" "transformation_runner" {
  project  = var.gcp_project_id
  name     = "${var.client_name}-transformation-runner"
  location = var.gcp_region

  template {
    template {
      service_account = google_service_account.job_runner.email
      containers {
        image   = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.repo.repository_id}/transformation:latest"
        command = ["uv", "run", "poe", "dbt-build-prod"]
        resources {
          limits = {
            memory = "2Gi"
          }
        }
      }
    }
  }
}

# 7. Define the Orchestration Workflow
resource "google_workflows_workflow" "main_workflow" {
  project         = var.gcp_project_id
  name            = "${var.client_name}-main-workflow"
  region          = var.gcp_region
  description     = "Orchestrates the ingestion and transformation jobs for ${var.client_name}."
  service_account = google_service_account.job_runner.email
  source_contents = file("${path.module}/../workflows/main_workflow.yaml")
  deletion_protection = false
  depends_on = [
    google_project_service.apis,
    google_cloud_run_v2_job.shopify_ingestion_runner,
    google_cloud_run_v2_job.facebook_ads_ingestion_runner,
    google_cloud_run_v2_job.tiktok_ads_ingestion_runner,
    google_cloud_run_v2_job.transformation_runner,
  ]
}

# 8. Schedule the Workflow
resource "google_cloud_scheduler_job" "workflow_scheduler" {
  project     = var.gcp_project_id
  name        = "${var.client_name}-workflow-scheduler"
  description = "Triggers the main data pipeline workflow daily for ${var.client_name}"
  schedule    = "0 0 * * *" # Runs daily at midnight UTC
  time_zone   = "Etc/UTC"
  paused      = true # Set to true to deactivate the scheduler

  http_target {
    uri         = "https://workflowexecutions.googleapis.com/v1/${google_workflows_workflow.main_workflow.id}/executions"
    http_method = "POST"
    body        = base64encode(jsonencode({
      "argument" = {
        "shopify_ingestion_job_name"      = google_cloud_run_v2_job.shopify_ingestion_runner.name
        "facebook_ads_ingestion_job_name" = google_cloud_run_v2_job.facebook_ads_ingestion_runner.name
        "tiktok_ads_ingestion_job_name"   = google_cloud_run_v2_job.tiktok_ads_ingestion_runner.name
        "transformation_job_name"         = google_cloud_run_v2_job.transformation_runner.name
      }
    }))
    oauth_token {
      service_account_email = google_service_account.job_runner.email
    }
  }
}

data "google_project" "project" {
  project_id = var.gcp_project_id
}