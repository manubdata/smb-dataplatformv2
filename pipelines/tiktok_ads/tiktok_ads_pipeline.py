import dlt
import pandas as pd
from pipelines.mock_data.tiktok_faker import TikTokAdsDataGenerator
import fire

@dlt.source(name="tiktok_ads")
def tiktok_ads_source(campaign_count: int = 8, days: int = 30):
    """
    A dlt source for generating mock TikTok Ads data.
    """
    generator = TikTokAdsDataGenerator()

    print(f"Generating {campaign_count} TikTok campaigns...")
    campaigns = generator.generate_campaigns(campaign_count)
    campaigns_df = pd.DataFrame(campaigns)

    print("Generating TikTok adgroups...")
    adgroups = generator.generate_adgroups(campaigns_df)
    adgroups_df = pd.DataFrame(adgroups)

    print("Generating TikTok ads...")
    ads = generator.generate_ads(adgroups_df)
    ads_df = pd.DataFrame(ads)

    print(f"Generating TikTok ad reports for the last {days} days...")
    ad_reports = generator.generate_ad_reports(ads_df, days=days)

    yield dlt.resource(campaigns, name="campaigns")
    yield dlt.resource(adgroups, name="adgroups")
    yield dlt.resource(ads, name="ads")
    yield dlt.resource(ad_reports, name="ad_reports")

def run_pipeline(destination: str = "duckdb", campaign_count: int = 8, days: int = 30) -> None:
    """
    Loads mock TikTok Ads data to a specified destination (duckdb or bigquery).
    """
    pipeline_name = f"tiktok_ads_to_{destination}"
    dataset_name = "tiktok_ads_data"

    if destination == "bigquery":
        pipeline = dlt.pipeline(
            pipeline_name=pipeline_name,
            destination="bigquery",
            dataset_name=dataset_name,
        )
    elif destination == "duckdb":
        pipeline = dlt.pipeline(
            pipeline_name=pipeline_name,
            destination="duckdb",
            dataset_name=dataset_name,
            credentials={"database": f"./duckdb_files/{dataset_name}.duckdb"},
        )
    else:
        raise ValueError(f"Unsupported destination: {destination}")

    print(f"Running TikTok Ads pipeline to {destination}...")
    load_info = pipeline.run(tiktok_ads_source(campaign_count=campaign_count, days=days))
    print(load_info)
    print(f"✅ TikTok Ads data loaded to {destination} successfully.")

if __name__ == "__main__":
    fire.Fire(run_pipeline)