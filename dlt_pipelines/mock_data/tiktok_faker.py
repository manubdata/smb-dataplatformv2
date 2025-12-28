import json
import random
import argparse
import os
from datetime import datetime, timedelta
from faker import Faker
import duckdb
import pandas as pd

# Initialize Faker
fake = Faker()


class TikTokAdsDataGenerator:
    """
    Generates mock advertising data for TikTok platform, structured as dlt would output.
    """

    def __init__(self) -> None:
        self.ctr_range = (0.005, 0.045)  # TikTok may have slightly different CTRs
        self.cpc_range = (0.30, 2.50)
        self.cvr_range = (0.01, 0.12)
        self.advertiser_id = str(fake.random_number(digits=19, fix_len=True))

    def _generate_base_metrics(self) -> tuple[int, int, float, int]:
        """
        Generates mathematically consistent base metrics for advertising data.
        """
        impressions = random.randint(500, 150000)
        ctr = random.uniform(*self.ctr_range)
        clicks = int(impressions * ctr)
        cpc = random.uniform(*self.cpc_range)
        spend = round(clicks * cpc, 2)
        cvr = random.uniform(*self.cvr_range)
        conversions = int(clicks * cvr)
        return impressions, clicks, spend, conversions

    def generate_campaigns(self, count: int = 5) -> list[dict]:
        """Generates a list of mock campaigns."""
        campaigns = []
        for _ in range(count):
            created_time = fake.date_time_between(start_date="-1y", end_date="now")
            campaign = {
                "id": str(fake.random_number(digits=19, fix_len=True)),
                "name": f"TT_{{fake.word().upper()}}_{fake.color_name()}_Campaign",
                "objective": random.choice(["REACH", "VIDEO_VIEWS", "CONVERSIONS"]),
                "status": random.choice(["CAMPAIGN_STATUS_ACTIVE", "CAMPAIGN_STATUS_PAUSED", "CAMPAIGN_STATUS_DELETED"]),
                "created_time": created_time.isoformat(),
                "updated_time": fake.date_time_between(start_date=created_time, end_date="now").isoformat(),
                "advertiser_id": self.advertiser_id,
            }
            campaigns.append(campaign)
        return campaigns

    def generate_adgroups(self, campaigns_df: pd.DataFrame) -> list[dict]:
        """Generates mock ad groups for the given campaigns."""
        adgroups = []
        for campaign in campaigns_df.to_dict("records"):
            for _ in range(random.randint(1, 4)):  # 1 to 4 adgroups per campaign
                created_time = pd.to_datetime(campaign["created_time"])
                adgroup = {
                    "id": str(fake.random_number(digits=19, fix_len=True)),
                    "name": f"AdGroup_{{fake.word()}}_{random.choice(['Lookalike', 'Interest'])}",
                    "campaign_id": campaign["id"],
                    "status": random.choice(["ADGROUP_STATUS_ACTIVE", "ADGROUP_STATUS_PAUSED", "ADGROUP_STATUS_DELETED"]),
                    "created_time": created_time.isoformat(),
                    "updated_time": fake.date_time_between(start_date=created_time, end_date="now").isoformat(),
                    "advertiser_id": self.advertiser_id,
                    "targeting": json.dumps({"age_groups": ["AGE_18_24", "AGE_25_34"]}),
                }
                adgroups.append(adgroup)
        return adgroups

    def generate_ads(self, adgroups_df: pd.DataFrame) -> list[dict]:
        """Generates mock ads for the given adgroups."""
        ads = []
        adgroup_map = adgroups_df[['id', 'campaign_id']].set_index('id').to_dict()['campaign_id']
        for adgroup_id in adgroups_df["id"]:
            for _ in range(random.randint(1, 3)):  # 1 to 3 ads per adgroup
                created_time = fake.date_time_between(start_date="-1y", end_date="now")
                ad = {
                    "id": str(fake.random_number(digits=19, fix_len=True)),
                    "name": f"Creative_{{fake.slug()}}",
                    "adgroup_id": adgroup_id,
                    "campaign_id": adgroup_map[adgroup_id],
                    "status": random.choice(["AD_STATUS_ACTIVE", "AD_STATUS_PAUSED", "AD_STATUS_DELETED"]),
                    "created_time": created_time.isoformat(),
                    "updated_time": fake.date_time_between(start_date=created_time, end_date="now").isoformat(),
                    "advertiser_id": self.advertiser_id,
                }
                ads.append(ad)
        return ads

    def generate_ad_reports(self, ads_df: pd.DataFrame, days: int = 30) -> list[dict]:
        """Generates mock daily ad reports for the given ads."""
        reports = []
        for ad_id in ads_df["id"]:
            for i in range(days):
                imp, clicks, spend, conv = self._generate_base_metrics()
                ctr = (clicks / imp) if imp > 0 else 0
                report_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                report = {
                    "ad_id": ad_id,
                    "stat_time_day": report_date,
                    "spend": spend,
                    "impressions": imp,
                    "clicks": clicks,
                    "ctr": ctr,
                    "conversions": conv,
                }
                reports.append(report)
        return reports


def main() -> None:
    """
    Main function to parse arguments and generate mock TikTok Ads data, saving it to DuckDB.
    """
    parser = argparse.ArgumentParser(description="Generate mock TikTok Ads data and save to DuckDB.")
    parser.add_argument("--count", type=int, default=8, help="Number of campaigns to generate.")
    parser.add_argument("--output_dir", type=str, default="./mock_data", help="Directory to save the DuckDB file.")
    parser.add_argument("--db_name", type=str, default="tiktok_ads.duckdb", help="Name of the DuckDB database file.")
    parser.add_argument("--days", type=int, default=30, help="Number of days for report data.")
    args = parser.parse_args()

    generator = TikTokAdsDataGenerator()
    os.makedirs(args.output_dir, exist_ok=True)
    db_path = os.path.join(args.output_dir, args.db_name)

    print(f"Generating {args.count} TikTok campaigns...")
    campaigns = generator.generate_campaigns(args.count)
    campaigns_df = pd.DataFrame(campaigns)

    print("Generating TikTok adgroups...")
    adgroups = generator.generate_adgroups(campaigns_df)
    adgroups_df = pd.DataFrame(adgroups)

    print("Generating TikTok ads...")
    ads = generator.generate_ads(adgroups_df)
    ads_df = pd.DataFrame(ads)

    print(f"Generating TikTok ad reports for the last {args.days} days...")
    ad_reports = generator.generate_ad_reports(ads_df, days=args.days)
    ad_reports_df = pd.DataFrame(ad_reports)

    print(f"Writing data to DuckDB at {db_path}...")
    with duckdb.connect(db_path, read_only=False) as con:
        con.execute("CREATE OR REPLACE TABLE campaigns AS SELECT * FROM campaigns_df")
        con.execute("CREATE OR REPLACE TABLE adgroups AS SELECT * FROM adgroups_df")
        con.execute("CREATE OR REPLACE TABLE ads AS SELECT * FROM ads_df")
        con.execute("CREATE OR REPLACE TABLE ad_reports AS SELECT * FROM ad_reports_df")
    
    print("✅ All tables created successfully in DuckDB.")
    
    # Example of how to query
    print("\n--- Example Query ---")
    with duckdb.connect(db_path, read_only=True) as con:
        result = con.execute("SELECT status, COUNT(*) as count FROM campaigns GROUP BY status").fetchdf()
        print("Campaign count by status:")
        print(result)

if __name__ == "__main__":
    main()
