import dlt
from dlt.sources import DltResource

from dlt_pipelines.shopify.shopify_pipeline import shopify_source, run_pipeline


def test_shopify_source_returns_resources():
    source = shopify_source(
        api_secret_key="dummy_key", shop_url="dummy_shop.myshopify.com"
    )
    assert isinstance(source.resources["products"], DltResource)
    assert isinstance(source.resources["orders"], DltResource)
    assert isinstance(source.resources["customers"], DltResource)


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
    )
    mock_pipeline.run.assert_called_once_with(mock_shopify_source)
