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
    Generates mock advertising data for the Meta platform, telling a specific story.
    - High spend, trending up 50% MoM.
    - High reported ROAS of 4.2.
    """

    def __init__(self) -> None:
        self.account_id = str(fake.random_number(digits=16, fix_len=True))
        # Ad Spend Trend: 50% MoM growth
        # (1.0135^90) * 150 = ~550 daily spend on day 90. Total spend over 90 days is ~30k.
        self.base_spend = 150  # Starting daily spend 90 days ago
        self.growth_factor = 1.0135 # Approx 50% MoM growth
        self.target_roas = 4.2

    def generate_campaigns(self, count: int = 3) -> list[dict]:
        """Generates a few active, high-intent campaigns."""
        campaigns = []
        for _ in range(count):
            created_time = fake.date_time_between(start_date="-1y", end_date="-6m")
            start_time = created_time + timedelta(days=random.randint(1, 30))
            campaign = {
                "id": str(fake.random_number(digits=17, fix_len=True)),
                "name": f"PMax_{fake.word().title()}",
                "status": "ACTIVE",
                "objective": "CONVERSIONS",
                "created_time": created_time.isoformat(),
                "start_time": start_time.isoformat(),
                "stop_time": None,
                "updated_time": fake.date_time_between(start_date=start_time, end_date="now").isoformat(),
                "account_id": self.account_id,
            }
            campaigns.append(campaign)
        return campaigns

    def generate_adsets(self, campaigns_df: pd.DataFrame) -> list[dict]:
        """Generates mock ad sets for the given campaigns."""
        adsets = []
        for campaign in campaigns_df.to_dict("records"):
            for _ in range(random.randint(1, 2)):
                created_time = pd.to_datetime(campaign["created_time"])
                start_time = created_time + timedelta(days=random.randint(1, 10))
                adset = {
                    "id": str(fake.random_number(digits=17, fix_len=True)),
                    "name": f"Lookalike_Audience_{random.choice(['1%', '5%'])}",
                    "status": "ACTIVE",
                    "campaign_id": campaign["id"],
                    "created_time": created_time.isoformat(),
                    "start_time": start_time.isoformat(),
                    "end_time": None,
                    "updated_time": fake.date_time_between(start_date=start_time, end_date="now").isoformat(),
                    "targeting": json.dumps({"geo_locations": {"countries": ["US"]}}),
                }
                adsets.append(adset)
        return adsets

    def generate_ads(self, adsets_df: pd.DataFrame) -> list[dict]:
        """Generates mock ads for the given adsets."""
        ads = []
        campaign_adset_map = adsets_df[['id', 'campaign_id']].set_index('id').to_dict()['campaign_id']
        for adset_id in adsets_df["id"]:
            for _ in range(random.randint(1, 3)):
                created_time = fake.date_time_between(start_date="-1y", end_date="now")
                ad = {
                    "id": str(fake.random_number(digits=17, fix_len=True)),
                    "name": f"Video_Ad_{fake.color_name()}",
                    "status": "ACTIVE",
                    "adset_id": adset_id,
                    "campaign_id": campaign_adset_map[adset_id],
                    "created_time": created_time.isoformat(),
                    "updated_time": fake.date_time_between(start_date=created_time, end_date="now").isoformat(),
                }
                ads.append(ad)
        return ads

    def generate_ads_insights(self, ads_df: pd.DataFrame, days: int = 90) -> list[dict]:
        """
        Generates mock ad insights with a deliberate trend.
        - Spend increases exponentially.
        - Reported ROAS stays high at 4.2.
        """
        insights = []
        ad_map = ads_df[['id', 'adset_id', 'campaign_id']].set_index('id').to_dict('index')
        active_ads = [ad_id for ad_id in ads_df["id"]]
        
        if not active_ads:
            return []

        for i in range(days):
            # Calculate spend for the day with exponential growth
            daily_spend = self.base_spend * (self.growth_factor ** (days - 1 - i))
            
            insight_date = datetime.now() - timedelta(days=i)
            
            # Distribute spend among ads and platforms
            spend_per_slot = daily_spend / (len(active_ads) * 2) # 2 platforms

            for ad_id in active_ads:
                for platform in ["facebook", "instagram"]:
                    spend = round(spend_per_slot * random.uniform(0.8, 1.2), 2)
                    
                    # Engineer the metrics to hit the target ROAS
                    purchase_value = spend * self.target_roas
                    # Assume an Average Order Value of $100 for conversion count
                    conversions = int(purchase_value / 100) 
                    
                    clicks = int(spend / random.uniform(0.75, 2.50)) # Realistic CPC
                    impressions = int(clicks / random.uniform(0.01, 0.03)) # Realistic CTR
                    
                    cpc = (spend / clicks) if clicks > 0 else 0
                    ctr = (clicks / impressions) * 100 if impressions > 0 else 0

                    insight = {
                        "campaign_id": ad_map[ad_id]['campaign_id'],
                        "adset_id": ad_map[ad_id]['adset_id'],
                        "ad_id": ad_id,
                        "date_start": insight_date.strftime("%Y-%m-%d"),
                        "date_stop": insight_date.strftime("%Y-%m-%d"),
                        "publisher_platform": platform,
                        "impressions": impressions,
                        "clicks": clicks,
                        "spend": spend,
                        "cpc": cpc,
                        "ctr": ctr,
                        "actions": json.dumps([
                            {"action_type": "link_click", "value": str(clicks)},
                            {"action_type": "offsite_conversion.fb_pixel_purchase", "value": str(conversions)},
                        ]),
                        # Add a field for the value of those conversions
                        "action_values": json.dumps([
                             {"action_type": "offsite_conversion.fb_pixel_purchase", "value": str(round(purchase_value, 2))},
                        ])
                    }
                    insights.append(insight)
        return insights


def main() -> None:
    """
    Main function to parse arguments and generate mock Ads data, saving it to DuckDB.
    """
    parser = argparse.ArgumentParser(description="Generate mock Facebook Ads data and save to DuckDB.")
    parser.add_argument("--count", type=int, default=3, help="Number of campaigns to generate.")
    parser.add_argument("--output_dir", type=str, default="./duckdb_files", help="Directory to save the DuckDB file.")
    parser.add_argument("--db_name", type=str, default="facebook_ads.duckdb", help="Name of the DuckDB database file.")
    parser.add_argument("--days", type=int, default=90, help="Number of days for insights data.")

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

if __name__ == "__main__":
    main()