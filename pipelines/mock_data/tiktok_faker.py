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
    Generates mock advertising data for TikTok, telling a specific story.
    - Medium spend, trending up.
    - Lower reported ROAS of 2.5.
    """

    def __init__(self) -> None:
        self.advertiser_id = str(fake.random_number(digits=19, fix_len=True))
        # Ad Spend Trend: ~30% MoM growth. Total spend over 90 days is ~15k.
        self.base_spend = 80  # Starting daily spend 90 days ago
        self.growth_factor = 1.01 # Approx 30% MoM growth
        self.target_roas = 2.5

    def generate_campaigns(self, count: int = 2) -> list[dict]:
        """Generates a few active, high-intent campaigns."""
        campaigns = []
        for _ in range(count):
            created_time = fake.date_time_between(start_date="-1y", end_date="-6m")
            campaign = {
                "id": str(fake.random_number(digits=19, fix_len=True)),
                "name": f"TT_Performance_{fake.word().upper()}",
                "objective": "CONVERSIONS",
                "status": "CAMPAIGN_STATUS_ACTIVE",
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
            for _ in range(random.randint(1, 2)):
                created_time = pd.to_datetime(campaign["created_time"])
                adgroup = {
                    "id": str(fake.random_number(digits=19, fix_len=True)),
                    "name": f"AdGroup_Interest_{fake.word()}",
                    "campaign_id": campaign["id"],
                    "status": "ADGROUP_STATUS_ACTIVE",
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
            for _ in range(random.randint(1, 2)):
                created_time = fake.date_time_between(start_date="-1y", end_date="now")
                ad = {
                    "id": str(fake.random_number(digits=19, fix_len=True)),
                    "name": f"SparkAd_{fake.slug()}",
                    "adgroup_id": adgroup_id,
                    "campaign_id": adgroup_map[adgroup_id],
                    "status": "AD_STATUS_ACTIVE",
                    "created_time": created_time.isoformat(),
                    "updated_time": fake.date_time_between(start_date=created_time, end_date="now").isoformat(),
                    "advertiser_id": self.advertiser_id,
                }
                ads.append(ad)
        return ads

    def generate_ad_reports(self, ads_df: pd.DataFrame, days: int = 90) -> list[dict]:
        """
        Generates mock daily ad reports with a deliberate trend.
        - Spend increases exponentially.
        - Reported ROAS stays at 2.5.
        """
        reports = []
        active_ads = [ad_id for ad_id in ads_df["id"]]
        if not active_ads:
            return []

        for i in range(days):
            daily_spend = self.base_spend * (self.growth_factor ** (days - 1 - i))
            
            report_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            
            spend_per_ad = daily_spend / len(active_ads)

            for ad_id in active_ads:
                spend = round(spend_per_ad * random.uniform(0.8, 1.2), 2)
                
                # Engineer metrics to hit target ROAS
                purchase_value = spend * self.target_roas
                conversions = int(purchase_value / 100) # Assume $100 AOV

                clicks = int(spend / random.uniform(0.50, 2.00))
                impressions = int(clicks / random.uniform(0.015, 0.045))

                ctr = (clicks / impressions) if impressions > 0 else 0
                
                report = {
                    "ad_id": ad_id,
                    "stat_time_day": report_date,
                    "spend": spend,
                    "impressions": impressions,
                    "clicks": clicks,
                    "ctr": ctr,
                    "conversions": conversions,
                    "conversion_value": purchase_value,
                }
                reports.append(report)
        return reports


def main() -> None:
    """
    Main function to parse arguments and generate mock TikTok Ads data, saving it to DuckDB.
    """
    parser = argparse.ArgumentParser(description="Generate mock TikTok Ads data and save to DuckDB.")
    parser.add_argument("--count", type=int, default=2, help="Number of campaigns to generate.")
    parser.add_argument("--output_dir", type=str, default="./duckdb_files", help="Directory to save the DuckDB file.")
    parser.add_argument("--db_name", type=str, default="tiktok_ads.duckdb", help="Name of the DuckDB database file.")
    parser.add_argument("--days", type=int, default=90, help="Number of days for report data.")
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

if __name__ == "__main__":
    main()
