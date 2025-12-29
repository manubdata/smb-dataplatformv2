import dlt
from dlt.sources import DltResource
from unittest.mock import patch

from dlt_pipelines.shopify.shopify_pipeline import shopify_source, run_pipeline


@patch("dlt_pipelines.shopify.shopify_pipeline.requests.post")
def test_shopify_source_returns_resources(mock_post):
    # Mock the response from the token endpoint
    mock_post.return_value.raise_for_status.return_value = None
    mock_post.return_value.json.return_value = {"access_token": "new_dummy_token"}

    # The source now fetches credentials from dlt.secrets, so we don't need to pass them
    # if we are not testing the credential logic itself.
    # We are testing that the source returns the correct resources after auth.
    source = shopify_source(
        shop_url="dummy_shop.myshopify.com",
        client_id="dummy_client_id",
        client_secret="dummy_client_secret",
    )
    assert isinstance(source.resources["products"], DltResource)
    assert isinstance(source.resources["orders"], DltResource)
    assert isinstance(source.resources["customers"], DltResource)

    # Verify that the token request was made
    mock_post.assert_called_once_with(
        "https://dummy_shop.myshopify.com/admin/oauth/access_token",
        json={
            "grant_type": "client_credentials",
            "client_id": "dummy_client_id",
            "client_secret": "dummy_client_secret",
        },
    )


def test_pipeline_run(mocker):
    # Mock the dlt.pipeline function
    mock_pipeline = mocker.MagicMock()
    mocker.patch(
        "dlt_pipelines.shopify.shopify_pipeline.dlt.pipeline",
        return_value=mock_pipeline,
    )

    # Mock the shopify_source
    mock_shopify_source = mocker.MagicMock()
    mocker.patch(
        "dlt_pipelines.shopify.shopify_pipeline.shopify_source",
        return_value=mock_shopify_source,
    )

    run_pipeline()

    # Assert that the pipeline was called correctly
    dlt.pipeline.assert_called_once_with(
        pipeline_name="shopify",
        destination="duckdb",
        dataset_name="shopify_data",
        credentials={"database": "./duckdb_files/shopify.duckdb"}
    )
    mock_pipeline.run.assert_called_once_with(mock_shopify_source)
