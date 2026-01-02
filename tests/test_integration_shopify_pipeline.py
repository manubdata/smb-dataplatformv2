import pytest
import dlt
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from dlt_pipelines.shopify.shopify_pipeline import shopify_source

TEST_DATASET_NAME = "shopify_test_data_raw_ci"


def setup_test_dataset(client: bigquery.Client, project_id: str, dataset_name: str) -> str:
    """Creates a BQ dataset for the test if it doesn't exist and sets table expiration."""
    dataset_id = f"{project_id}.{dataset_name}"
    try:
        client.get_dataset(dataset_id)
        print(f"Dataset {dataset_id} already exists.")
    except NotFound:
        print(f"Creating dataset {dataset_id}.")
        dataset = bigquery.Dataset(dataset_id)
        dataset.default_table_expiration_ms = 24 * 60 * 60 * 1000  # 24 hours
        client.create_dataset(dataset, exists_ok=True)
    return dataset_name


def cleanup_test_dataset(client: bigquery.Client, project_id: str, dataset_name: str):
    """Deletes the BQ dataset."""
    dataset_id = f"{project_id}.{dataset_name}"
    try:
        client.delete_dataset(dataset_id, delete_contents=True, not_found_ok=True)
        print(f"Deleted dataset {dataset_id}.")
    except Exception as e:
        print(f"Error deleting dataset {dataset_id}: {e}")


@pytest.fixture(scope="module")
def bq_client_and_dataset():
    """Pytest fixture to set up and tear down the BigQuery test dataset."""
    try:
        client = bigquery.Client()
        project_id = client.project
    except Exception as e:
        pytest.fail(
            f"Could not connect to BigQuery. Ensure you are authenticated with 'gcloud auth application-default login'. Error: {e}"
        )

    dataset_name = setup_test_dataset(client, project_id, TEST_DATASET_NAME)

    yield client, dataset_name

    print("\n---Tearing down BigQuery test dataset---")
    cleanup_test_dataset(client, project_id, dataset_name)


@pytest.mark.integration
def test_shopify_pipeline_to_bigquery(bq_client_and_dataset):
    """
    Tests the Shopify dlt pipeline by running it against a test BigQuery dataset.
    The dataset is created with a 24-hour table expiration and is torn down after the test.
    """
    client, dataset_name = bq_client_and_dataset

    pipeline = dlt.pipeline(
        pipeline_name="shopify",
        destination="bigquery",
        dataset_name=dataset_name,
    )

    load_info = pipeline.run(shopify_source())

    assert not load_info.has_failed_jobs, "Some packages failed to load"
    assert len(load_info.loads_ids) > 0, "No data was loaded"

    # Check if at least one of the expected tables was created.
    expected_tables = ["products", "orders", "customers"]
    table_found = False
    for table_name in expected_tables:
        table_id = f"{client.project}.{dataset_name}.{table_name}"
        try:
            client.get_table(table_id)
            print(f"Table '{table_id}' found in BigQuery.")
            table_found = True
        except NotFound:
            continue
    
    assert table_found, f"None of the expected tables {expected_tables} were found in dataset {dataset_name}."
