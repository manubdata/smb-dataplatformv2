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


class AdsDataGenerator:
    """
    Generates mock advertising data for Meta platform, structured as dlt would output.
    """

    def __init__(self) -> None:
        # Common settings for realistic math
        self.ctr_range = (0.005, 0.035)  # 0.5% to 3.5% CTR
        self.cpc_range = (0.50, 3.50)  # $0.50 to $3.50 CPC
        self.cvr_range = (0.02, 0.15)  # 2% to 15% Conversion Rate
        self.account_id = str(fake.random_number(digits=16, fix_len=True))

    def _generate_base_metrics(self) -> tuple[int, int, float, int]:
        """
        Generates mathematically consistent base metrics for advertising data.
        """
        impressions = random.randint(1000, 100000)
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
            created_time = fake.date_time_between(start_date="-2y", end_date="now")
            start_time = created_time + timedelta(days=random.randint(1, 30))
            campaign = {
                "id": str(fake.random_number(digits=17, fix_len=True)),
                "name": f"{fake.word().title()}_Campaign_{fake.year()}",
                "status": random.choice(["ACTIVE", "PAUSED", "ARCHIVED"]),
                "objective": random.choice(["LINK_CLICKS", "CONVERSIONS", "POST_ENGAGEMENT"]),
                "created_time": created_time.isoformat(),
                "start_time": start_time.isoformat(),
                "stop_time": (start_time + timedelta(days=random.randint(30, 90))).isoformat(),
                "updated_time": fake.date_time_between(start_date=start_time, end_date="now").isoformat(),
                "account_id": self.account_id,
            }
            campaigns.append(campaign)
        return campaigns

    def generate_adsets(self, campaigns_df: pd.DataFrame) -> list[dict]:
        """Generates mock ad sets for the given campaigns."""
        adsets = []
        for campaign in campaigns_df.to_dict("records"):
            for _ in range(random.randint(1, 3)):  # 1 to 3 adsets per campaign
                created_time = pd.to_datetime(campaign["created_time"])
                start_time = created_time + timedelta(days=random.randint(1, 10))
                adset = {
                    "id": str(fake.random_number(digits=17, fix_len=True)),
                    "name": f"{fake.word().title()}_Audience_{random.choice(['US', 'CA', 'GB'])}",
                    "status": random.choice(["ACTIVE", "PAUSED", "ARCHIVED"]),
                    "campaign_id": campaign["id"],
                    "created_time": created_time.isoformat(),
                    "start_time": start_time.isoformat(),
                    "end_time": (start_time + timedelta(days=random.randint(15, 60))).isoformat(),
                    "updated_time": fake.date_time_between(start_date=start_time, end_date="now").isoformat(),
                    "targeting": json.dumps({
                        "geo_locations": {"countries": ["US"]},
                        "age_min": random.randint(18, 45),
                        "age_max": random.randint(46, 65),
                    }),
                }
                adsets.append(adset)
        return adsets

    def generate_ads(self, adsets_df: pd.DataFrame) -> list[dict]:
        """Generates mock ads for the given adsets."""
        ads = []
        campaign_adset_map = adsets_df[['id', 'campaign_id']].set_index('id').to_dict()['campaign_id']
        for adset_id in adsets_df["id"]:
            for _ in range(random.randint(1, 5)):  # 1 to 5 ads per adset
                created_time = fake.date_time_between(start_date="-1y", end_date="now")
                ad = {
                    "id": str(fake.random_number(digits=17, fix_len=True)),
                    "name": f"Ad_{fake.color_name()}_{fake.word()}",
                    "status": random.choice(["ACTIVE", "PAUSED", "ARCHIVED"]),
                    "adset_id": adset_id,
                    "campaign_id": campaign_adset_map[adset_id],
                    "created_time": created_time.isoformat(),
                    "updated_time": fake.date_time_between(start_date=created_time, end_date="now").isoformat(),
                }
                ads.append(ad)
        return ads

    def generate_ads_insights(self, ads_df: pd.DataFrame, days: int = 30) -> list[dict]:
        """Generates mock ad insights for the given ads over a period of days."""
        insights = []
        ad_map = ads_df[['id', 'adset_id', 'campaign_id']].set_index('id').to_dict('index')
        for ad_id in ads_df["id"]:
            for i in range(days):
                imp, clicks, spend, conv = self._generate_base_metrics()
                cpc = (spend / clicks) if clicks > 0 else 0
                ctr = (clicks / imp) * 100 if imp > 0 else 0
                insight_date = datetime.now() - timedelta(days=i)
                insight = {
                    "campaign_id": ad_map[ad_id]['campaign_id'],
                    "adset_id": ad_map[ad_id]['adset_id'],
                    "ad_id": ad_id,
                    "date_start": insight_date.strftime("%Y-%m-%d"),
                    "date_stop": insight_date.strftime("%Y-%m-%d"),
                    "impressions": imp,
                    "clicks": clicks,
                    "spend": spend,
                    "cpc": cpc,
                    "ctr": ctr,
                    "actions": json.dumps([
                        {"action_type": "link_click", "value": str(clicks)},
                        {"action_type": "offsite_conversion.fb_pixel_purchase", "value": str(conv)},
                    ]),
                }
                insights.append(insight)
        return insights


def main() -> None:
    """
    Main function to parse arguments and generate mock Ads data, saving it to DuckDB.
    """
    parser = argparse.ArgumentParser(description="Generate mock Facebook Ads data and save to DuckDB.")
    parser.add_argument(
        "--count", type=int, default=10, help="Number of campaigns to generate."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./mock_data",
        help="Directory to save the DuckDB file.",
    )
    parser.add_argument(
        "--db_name",
        type=str,
        default="facebook_ads.duckdb",
        help="Name of the DuckDB database file.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days for insights data."
    )

    args = parser.parse_args()

    generator = AdsDataGenerator()
    os.makedirs(args.output_dir, exist_ok=True)
    db_path = os.path.join(args.output_dir, args.db_name)

    print(f"Generating {args.count} campaigns...")
    campaigns = generator.generate_campaigns(args.count)
    campaigns_df = pd.DataFrame(campaigns)

    print("Generating adsets...")
    adsets = generator.generate_adsets(campaigns_df)
    adsets_df = pd.DataFrame(adsets)

    print("Generating ads...")
    ads = generator.generate_ads(adsets_df)
    ads_df = pd.DataFrame(ads)

    print(f"Generating insights for the last {args.days} days...")
    ads_insights = generator.generate_ads_insights(ads_df, days=args.days)
    ads_insights_df = pd.DataFrame(ads_insights)

    print(f"Writing data to DuckDB at {db_path}...")
    con = duckdb.connect(db_path, read_only=False)

    # Create tables from pandas dataframes
    con.execute("CREATE OR REPLACE TABLE campaigns AS SELECT * FROM campaigns_df")
    con.execute("CREATE OR REPLACE TABLE adsets AS SELECT * FROM adsets_df")
    con.execute("CREATE OR REPLACE TABLE ads AS SELECT * FROM ads_df")
    con.execute("CREATE OR REPLACE TABLE ads_insights AS SELECT * FROM ads_insights_df")

    con.close()
    print("✅ All tables created successfully in DuckDB.")
    
    # Example of how to query
    print("\n--- Example Query ---")
    con = duckdb.connect(db_path, read_only=True)
    result = con.execute("SELECT status, COUNT(*) as count FROM campaigns GROUP BY status").fetchdf()
    print("Campaign count by status:")
    print(result)
    con.close()


if __name__ == "__main__":
    main()