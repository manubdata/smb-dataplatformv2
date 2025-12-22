# Gemini Code Assistant Context

This document provides context for the Gemini Code Assistant to understand the structure and conventions of the `smb-dataplatformv2` project.

## Project Overview

`smb-dataplatformv2` is a Data Platform as a Service for SMB E-commerce. It uses a modern data stack built on Python.

**Key Technologies:**

*   **Programming Language:** Python 3.11+
*   **ETL/Ingestion:** `dlt` (Data Loading Tool)
*   **Transformation:** `dbt` (Data Build Tool)
*   **Infrastructure as Code:** Terraform
*   **Task Runner:** `poethepoet` (invoked via `uv run poe`)
*   **Dependency Management:** `uv`
*   **Testing:** `pytest`
*   **Linting & Formatting:** `ruff`

**Architecture:**

The project is structured as a monorepo with the following key directories:

*   `pipelines/`: Contains the data ingestion and processing pipelines.
*   `dbt_project/`: Contains the dbt models for data transformation.
*   `terraform/`: Contains the Terraform code for managing infrastructure.
*   `tests/`: Contains tests for the pipelines and other components.

## Building and Running

This project uses `uv` and `poethepoet` to manage dependencies and run tasks.

**Common Commands:**

*   **Install dependencies:**
    ```bash
    uv pip install -e .[etl,dbt,dev]
    ```

*   **Run the data ingestion pipeline:**
    ```bash
    uv run poe run-pipeline
    ```
    *Note: The `pipelines/run_pipeline.py` script does not exist yet.*

*   **Run dbt transformations:**
    ```bash
    uv run poe dbt-run
    ```

*   **Run tests:**
    ```bash
    uv run poe test
    ```

*   **Lint and format code:**
    ```bash
    uv run poe lint
    uv run poe format
    ```

*   **Run all checks:**
    ```bash
    uv run poe check
    ```

*   **Manage infrastructure with Terraform:**
    ```bash
    uv run poe tf-init
    uv run poe tf-plan
    uv run poe tf-apply
    ```

## Development Conventions

*   **Testing:** All new features should be accompanied by tests. Tests are located in the `tests/` directory and are run with `pytest`.
*   **Linting:** The project uses `ruff` for linting. Run `uv run poe lint` to check for issues.
*   **Formatting:** The project uses `ruff` for code formatting. Run `uv run poe format` to format the code.
*   **Commits:** Follow conventional commit standards.
*   **Branching:** Create a new branch for each new feature or bug fix.

# Rules