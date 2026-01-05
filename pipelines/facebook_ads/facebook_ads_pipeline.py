import dlt
import pandas as pd
from pipelines.mock_data.meta_faker import AdsDataGenerator
import fire

@dlt.source(name="facebook_ads")
def facebook_ads_source(campaign_count: int = 10, days: int = 30):
    """
    A dlt source for generating mock Facebook Ads data.
    """
    generator = AdsDataGenerator()

    print(f"Generating {campaign_count} campaigns...")
    campaigns = generator.generate_campaigns(campaign_count)
    campaigns_df = pd.DataFrame(campaigns)

    print("Generating adsets...")
    adsets = generator.generate_adsets(campaigns_df)
    adsets_df = pd.DataFrame(adsets)

    print("Generating ads...")
    ads = generator.generate_ads(adsets_df)
    ads_df = pd.DataFrame(ads)

    print(f"Generating insights for the last {days} days...")
    ads_insights = generator.generate_ads_insights(ads_df, days=days)

    yield dlt.resource(campaigns, name="campaigns")
    yield dlt.resource(adsets, name="adsets")
    yield dlt.resource(ads, name="ads")
    yield dlt.resource(ads_insights, name="ads_insights")

def run_pipeline(destination: str = "duckdb", campaign_count: int = 10, days: int = 30) -> None:
    """
    Loads mock Facebook Ads data to a specified destination (duckdb or bigquery).
    """
    pipeline_name = f"facebook_ads_to_{destination}"
    dataset_name = "facebook_ads_data"

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

    print(f"Running Facebook Ads pipeline to {destination}...")
    load_info = pipeline.run(facebook_ads_source(campaign_count=campaign_count, days=days))
    print(load_info)
    print(f"✅ Facebook Ads data loaded to {destination} successfully.")

if __name__ == "__main__":
    fire.Fire(run_pipeline)