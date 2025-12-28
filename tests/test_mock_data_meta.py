import os
import pytest
from unittest.mock import patch, mock_open
import pandas as pd
import duckdb

from dlt_pipelines.mock_data.meta_faker import AdsDataGenerator, main

# Define the path for the test DuckDB database
TEST_DB_PATH = "./mock_data/test_facebook_ads.duckdb"


@pytest.fixture
def generator():
    """Provides an instance of AdsDataGenerator for tests."""
    return AdsDataGenerator()


def test_generate_base_metrics(generator):
    """
    Test that _generate_base_metrics returns mathematically consistent values
    within expected ranges.
    """
    impressions, clicks, spend, conversions = generator._generate_base_metrics()

    assert isinstance(impressions, int)
    assert isinstance(clicks, int)
    assert isinstance(spend, float)
    assert isinstance(conversions, int)

    assert impressions >= 1000
    assert impressions <= 100000

    if impressions > 0:
        calculated_ctr = clicks / impressions
        assert generator.ctr_range[0] <= calculated_ctr <= generator.ctr_range[1]

    if clicks > 0:
        calculated_cpc = spend / clicks
        assert generator.cpc_range[0] <= calculated_cpc <= generator.cpc_range[1]

        calculated_cvr = conversions / clicks
        assert generator.cvr_range[0] <= calculated_cvr <= generator.cvr_range[1]


class TestMetaFakerDataGeneration:
    """Tests for the data generation methods in AdsDataGenerator."""

    @pytest.fixture(autouse=True)
    def setup_method(self, generator):
        self.generator = generator

    def test_generate_campaigns_structure(self):
        campaigns = self.generator.generate_campaigns(count=2)
        assert isinstance(campaigns, list)
        assert len(campaigns) == 2
        for campaign in campaigns:
            assert "id" in campaign
            assert "name" in campaign
            assert "status" in campaign
            assert "objective" in campaign
            assert "created_time" in campaign
            assert "start_time" in campaign
            assert "stop_time" in campaign
            assert "updated_time" in campaign
            assert "account_id" in campaign

    def test_generate_adsets_structure_and_relations(self):
        campaigns_df = pd.DataFrame(self.generator.generate_campaigns(count=1))
        adsets = self.generator.generate_adsets(campaigns_df)
        assert isinstance(adsets, list)
        assert len(adsets) >= 1  # At least one adset per campaign
        for adset in adsets:
            assert "id" in adset
            assert "name" in adset
            assert "status" in adset
            assert "campaign_id" in adset
            assert adset["campaign_id"] in campaigns_df["id"].values
            assert "created_time" in adset
            assert "start_time" in adset
            assert "end_time" in adset
            assert "updated_time" in adset
            assert "targeting" in adset

    def test_generate_ads_structure_and_relations(self):
        campaigns_df = pd.DataFrame(self.generator.generate_campaigns(count=1))
        adsets_df = pd.DataFrame(self.generator.generate_adsets(campaigns_df))
        ads = self.generator.generate_ads(adsets_df)
        assert isinstance(ads, list)
        assert len(ads) >= len(adsets_df) # At least one ad per adset
        for ad in ads:
            assert "id" in ad
            assert "name" in ad
            assert "status" in ad
            assert "adset_id" in ad
            assert ad["adset_id"] in adsets_df["id"].values
            assert "campaign_id" in ad
            assert ad["campaign_id"] in campaigns_df["id"].values
            assert "created_time" in ad
            assert "updated_time" in ad

    def test_generate_ads_insights_structure_and_relations(self):
        campaigns_df = pd.DataFrame(self.generator.generate_campaigns(count=1))
        adsets_df = pd.DataFrame(self.generator.generate_adsets(campaigns_df))
        ads_df = pd.DataFrame(self.generator.generate_ads(adsets_df))
        insights = self.generator.generate_ads_insights(ads_df, days=1)
        assert isinstance(insights, list)
        assert len(insights) >= len(ads_df)  # At least one insight per ad per day
        for insight in insights:
            assert "campaign_id" in insight
            assert "adset_id" in insight
            assert "ad_id" in insight
            assert insight["ad_id"] in ads_df["id"].values
            assert "date_start" in insight
            assert "date_stop" in insight
            assert "impressions" in insight
            assert "clicks" in insight
            assert "spend" in insight
            assert "cpc" in insight
            assert "ctr" in insight
            assert "actions" in insight


@patch("dlt_pipelines.mock_data.meta_faker.duckdb.connect")
@patch("dlt_pipelines.mock_data.meta_faker.os.makedirs")
@patch("dlt_pipelines.mock_data.meta_faker.argparse.ArgumentParser")
def test_main_function_creates_duckdb_and_tables(
    mock_argparse, mock_makedirs, mock_duckdb_connect
):
    """
    Test that the main function creates a DuckDB file and the expected tables,
    and that these tables contain data.
    """
    # Configure argparse mock
    mock_args = mock_argparse.return_value.parse_args.return_value
    mock_args.count = 2
    mock_args.output_dir = "./mock_data"
    mock_args.db_name = "test_facebook_ads.duckdb"
    mock_args.days = 1

    # Mock the duckdb connection and cursor
    mock_con = mock_duckdb_connect.return_value
    mock_con.execute.return_value = mock_con # execute returns self for chaining
    mock_con.fetchdf.return_value = pd.DataFrame() # Mock fetchdf to return an empty DataFrame
    
    # Run the main function
    main()

    # Assert that output directory is created
    mock_makedirs.assert_called_once_with("./mock_data", exist_ok=True)

    # Assert duckdb connection is made twice (once for writing, once for example query)
    assert mock_duckdb_connect.call_count == 2
    mock_duckdb_connect.assert_any_call(
        os.path.join("./mock_data", "test_facebook_ads.duckdb"), read_only=False
    )
    mock_duckdb_connect.assert_any_call(
        os.path.join("./mock_data", "test_facebook_ads.duckdb"), read_only=True
    )
    
    # Assert tables are created. We expect 4 tables to be created
    expected_tables = ["campaigns", "adsets", "ads", "ads_insights"]
    assert mock_con.execute.call_count == 5 # 4 CREATE and 1 SELECT
    # Verify each table creation command
    create_table_calls = [call for call in mock_con.execute.call_args_list if "CREATE OR REPLACE TABLE" in call.args[0]]
    assert len(create_table_calls) == len(expected_tables)
    for table_name in expected_tables:
        assert any(table_name in call.args[0] for call in create_table_calls)

    # Check that the connection was closed
    mock_con.close.assert_called()

# Helper to clean up the test database after tests
@pytest.fixture(scope="module", autouse=True)
def cleanup_duckdb():
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)