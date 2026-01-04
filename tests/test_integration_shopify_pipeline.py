import pytest
import dlt
from unittest.mock import patch, MagicMock

from dlt.destinations import duckdb
from dlt_pipelines.shopify.shopify_pipeline import shopify_source

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration

@pytest.fixture(scope="function")
def mock_shopify_api():
    """Mocks the Shopify API endpoints."""
    with patch("dlt_pipelines.shopify.shopify_pipeline.requests.get") as mock_get:
        # Mock responses for products, orders, customers
        mock_products_response = {
            "products": [
                {"id": 1, "title": "Test Product 1", "updated_at": "2023-01-01T00:00:00Z"},
                {"id": 2, "title": "Test Product 2", "updated_at": "2023-01-01T00:00:00Z"},
            ]
        }
        mock_orders_response = {
            "orders": [
                {"id": 101, "total_price": "10.00", "updated_at": "2023-01-01T00:00:00Z"},
                {"id": 102, "total_price": "20.00", "updated_at": "2023-01-01T00:00:00Z"},
            ]
        }
        mock_customers_response = {
            "customers": [
                {"id": 201, "first_name": "John", "last_name": "Doe", "updated_at": "2023-01-01T00:00:00Z"},
                {"id": 202, "first_name": "Jane", "last_name": "Doe", "updated_at": "2023-01-01T00:00:00Z"},
            ]
        }

        # The API is called multiple times for the different resources
        def get_side_effect(url, headers, params):
            response = MagicMock()
            response.raise_for_status.return_value = None
            if "products.json" in url:
                response.json.return_value = mock_products_response
            elif "orders.json" in url:
                response.json.return_value = mock_orders_response
            elif "customers.json" in url:
                response.json.return_value = mock_customers_response
            else:
                response.json.return_value = {}
            # No "Link" header means no pagination
            response.headers = {}
            return response

        mock_get.side_effect = get_side_effect
        yield mock_get

@patch("dlt_pipelines.shopify.shopify_pipeline.requests.post")
def test_full_pipeline_run(mock_post, mock_shopify_api, tmp_path):
    """
    Tests the full pipeline run with a mocked Shopify API and a temporary DuckDB destination.
    """
    # Mock the token endpoint
    mock_post.return_value.raise_for_status.return_value = None
    mock_post.return_value.json.return_value = {"access_token": "dummy_token"}

    # Configure the pipeline to use a temporary DuckDB database
    db_file = tmp_path / "test_shopify.duckdb"
    pipeline = dlt.pipeline(
        pipeline_name="shopify_test",
        destination=duckdb(credentials=str(db_file)),
        dataset_name="shopify_data_test",
    )

    # Get the source
    source = shopify_source(
        shop_url="dummy_shop.myshopify.com",
        client_id="dummy_client_id",
        client_secret="dummy_client_secret",
    )

    # Run the pipeline
    info = pipeline.run(source)
    
    # Assert that the pipeline ran successfully
    assert info.has_failed_jobs is False, f"Pipeline failed with errors: {info.load_packages[0].jobs['failed_jobs']}"


    # Check the data in the database
    with pipeline.sql_client() as client:
        # Check products
        with client.execute_query("SELECT count(*) FROM products") as cur:
            assert cur.fetchone()[0] == 2
        with client.execute_query("SELECT title FROM products WHERE id = 1") as cur:
            assert cur.fetchone()[0] == "Test Product 1"

        # Check orders
        with client.execute_query("SELECT count(*) FROM orders") as cur:
            assert cur.fetchone()[0] == 2
        with client.execute_query("SELECT total_price FROM orders WHERE id = 101") as cur:
            assert cur.fetchone()[0] == "10.00"

        # Check customers
        with client.execute_query("SELECT count(*) FROM customers") as cur:
            assert cur.fetchone()[0] == 2
        with client.execute_query("SELECT first_name FROM customers WHERE id = 201") as cur:
            assert cur.fetchone()[0] == "John"
