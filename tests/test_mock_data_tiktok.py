
import os
import pytest
from unittest.mock import patch
import pandas as pd
import duckdb

from dlt_pipelines.mock_data.tiktok_faker import TikTokAdsDataGenerator, main

# Define the path for the test DuckDB database
TEST_DB_PATH = "./duckdb_files/test_tiktok_ads.duckdb"


@pytest.fixture
def generator():
    """Provides an instance of TikTokAdsDataGenerator for tests."""
    return TikTokAdsDataGenerator()


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


class TestTikTokFakerDataGeneration:
    """Tests for the data generation methods in TikTokAdsDataGenerator."""

    @pytest.fixture(autouse=True)
    def setup_method(self, generator):
        self.generator = generator

    def test_generate_campaigns_structure(self):
        campaigns = self.generator.generate_campaigns(count=2)
        assert isinstance(campaigns, list)
        assert len(campaigns) == 2
        for campaign in campaigns:
            assert all(k in campaign for k in ["id", "name", "objective", "status", "created_time", "updated_time", "advertiser_id"])

    def test_generate_adgroups_structure_and_relations(self):
        campaigns_df = pd.DataFrame(self.generator.generate_campaigns(count=1))
        adgroups = self.generator.generate_adgroups(campaigns_df)
        assert isinstance(adgroups, list)
        assert len(adgroups) >= 1
        for adgroup in adgroups:
            assert all(k in adgroup for k in ["id", "name", "campaign_id", "status", "created_time", "updated_time", "advertiser_id", "targeting"])
            assert adgroup["campaign_id"] in campaigns_df["id"].values

    def test_generate_ads_structure_and_relations(self):
        campaigns_df = pd.DataFrame(self.generator.generate_campaigns(count=1))
        adgroups_df = pd.DataFrame(self.generator.generate_adgroups(campaigns_df))
        ads = self.generator.generate_ads(adgroups_df)
        assert isinstance(ads, list)
        assert len(ads) >= len(adgroups_df)
        for ad in ads:
            assert all(k in ad for k in ["id", "name", "adgroup_id", "campaign_id", "status", "created_time", "updated_time", "advertiser_id"])
            assert ad["adgroup_id"] in adgroups_df["id"].values
            assert ad["campaign_id"] in campaigns_df["id"].values

    def test_generate_ad_reports_structure_and_relations(self):
        campaigns_df = pd.DataFrame(self.generator.generate_campaigns(count=1))
        adgroups_df = pd.DataFrame(self.generator.generate_adgroups(campaigns_df))
        ads_df = pd.DataFrame(self.generator.generate_ads(adgroups_df))
        reports = self.generator.generate_ad_reports(ads_df, days=1)
        assert isinstance(reports, list)
        assert len(reports) >= len(ads_df)
        for report in reports:
            assert all(k in report for k in ["ad_id", "stat_time_day", "spend", "impressions", "clicks", "ctr", "conversions"])
            assert report["ad_id"] in ads_df["id"].values


@patch("dlt_pipelines.mock_data.tiktok_faker.duckdb.connect")
@patch("dlt_pipelines.mock_data.tiktok_faker.os.makedirs")
@patch("dlt_pipelines.mock_data.tiktok_faker.argparse.ArgumentParser")
def test_main_function_creates_duckdb_and_tables(
    mock_argparse, mock_makedirs, mock_duckdb_connect
):
    """
    Test that the main function creates a DuckDB file and the expected tables.
    """
    # Configure argparse mock
    mock_args = mock_argparse.return_value.parse_args.return_value
    mock_args.count = 1
    mock_args.output_dir = "./duckdb_files"
    mock_args.db_name = "test_tiktok_ads.duckdb"
    mock_args.days = 1

    # Mock the duckdb connection
    mock_con = mock_duckdb_connect.return_value.__enter__.return_value
    mock_con.execute.return_value = mock_con
    mock_con.fetchdf.return_value = pd.DataFrame()
    
    # Run the main function
    main()

    # Assertions
    mock_makedirs.assert_called_once_with("./duckdb_files", exist_ok=True)
    assert mock_duckdb_connect.call_count == 2
    mock_duckdb_connect.assert_any_call(os.path.join("./duckdb_files", "test_tiktok_ads.duckdb"), read_only=False)
    mock_duckdb_connect.assert_any_call(os.path.join("./duckdb_files", "test_tiktok_ads.duckdb"), read_only=True)
    
    expected_tables = ["campaigns", "adgroups", "ads", "ad_reports"]
    create_table_calls = [call for call in mock_con.execute.call_args_list if "CREATE OR REPLACE TABLE" in call.args[0]]
    assert len(create_table_calls) == len(expected_tables)
    for table_name in expected_tables:
        assert any(table_name in call.args[0] for call in create_table_calls)


@pytest.fixture(scope="module", autouse=True)
def cleanup_duckdb():
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
