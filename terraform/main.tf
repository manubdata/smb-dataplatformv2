provider "google" {
  project = "smb-dataplatform"
  region  = "us-central1"
}

# 1. Enable APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudscheduler.googleapis.com",
    "bigquery.googleapis.com",
    "workflows.googleapis.com",
    "workflowexecutions.googleapis.com"
  ])
  service = each.key
  disable_on_destroy = false
}

# 2. Create the Docker Registry
resource "google_artifact_registry_repository" "repo" {
  location      = "us-central1"
  repository_id = "smb-dataplatform-artifact-repo"
  format        = "DOCKER"
  depends_on    = [google_project_service.apis]
}

# 3. Create the Service Account
resource "google_service_account" "job_runner" {
  account_id   = "smb-dataplatform-job-runner"
  display_name = "Service Account for Cloud Run Jobs & Workflows"
}

# 4. Give Permissions to the Service Account
resource "google_project_iam_member" "bq_admin" {
  project = "smb-dataplatform"
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.job_runner.email}"
}

resource "google_project_iam_member" "log_writer" {
  project = "smb-dataplatform"
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.job_runner.email}"
}

resource "google_project_iam_member" "run_jobs_runner" {
  project = "smb-dataplatform"
  role    = "roles/run.admin" # Using run.admin to ensure it can run jobs
  member  = "serviceAccount:${google_service_account.job_runner.email}"
}

resource "google_project_iam_member" "workflow_invoker" {
  project = "smb-dataplatform"
  role    = "roles/workflows.invoker"
  member  = "serviceAccount:${google_service_account.job_runner.email}"
}

output "sa_email" {
  value = google_service_account.job_runner.email
}

# 5. Define the Cloud Run Jobs
resource "google_cloud_run_v2_job" "ingestion_runner" {
  name     = "smb-dataplatform-ingestion-runner"
  location = "us-central1"

  template {
    template {
      service_account = google_service_account.job_runner.email
      containers {
        image = "us-central1-docker.pkg.dev/smb-dataplatform/smb-dataplatform-artifact-repo/ingestion:latest"
        command = ["python", "-m", "pipelines.run_pipeline"]
      }
    }
  }
}

resource "google_cloud_run_v2_job" "transformation_runner" {
  name     = "smb-dataplatform-transformation-runner"
  location = "us-central1"

  template {
    template {
      service_account = google_service_account.job_runner.email
      containers {
        image   = "us-central1-docker.pkg.dev/smb-dataplatform/smb-dataplatform-artifact-repo/transformation:latest"
        command = ["sh", "-c", "cd dbt_project && dbt build --profiles-dir ../dbt_profiles"]
      }
    }
  }
}

# 6. Define the Orchestration Workflow
resource "google_workflows_workflow" "main_workflow" {
  name            = "main-workflow"
  region          = "us-central1"
  description     = "Orchestrates the ingestion and transformation jobs."
  service_account = google_service_account.job_runner.email
  source_contents = file("${path.module}/../workflows/main_workflow.yaml")
  depends_on = [
    google_project_service.apis,
    google_cloud_run_v2_job.ingestion_runner,
    google_cloud_run_v2_job.transformation_runner
  ]
}

# 7. Schedule the Workflow
resource "google_cloud_scheduler_job" "workflow_scheduler" {
  name        = "smb-dataplatform-workflow-scheduler"
  description = "Triggers the main data pipeline workflow daily"
  schedule    = "0 0 * * *" # Runs daily at midnight UTC
  time_zone   = "Etc/UTC"
  paused      = true # Set to true to deactivate the scheduler

  http_target {
    uri         = "https://workflowexecutions.googleapis.com/v1/${google_workflows_workflow.main_workflow.id}/executions"
    http_method = "POST"
    oauth_token {
      service_account_email = google_service_account.job_runner.email
    }
  }
}

data "google_project" "project" {}