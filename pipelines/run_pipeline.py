import argparse
import importlib

def run_pipeline(pipeline_name: str, destination: str = "duckdb"):
    """
    Runs a specified dlt pipeline to a given destination.

    Args:
        pipeline_name: The name of the pipeline to run (e.g., 'shopify', 'facebook_ads', 'tiktok_ads').
        destination: The destination to load data to (e.g., 'duckdb', 'bigquery').
    """
    try:
        # Dynamically import the pipeline module
        pipeline_module = importlib.import_module(f"pipelines.{pipeline_name}.{pipeline_name}_pipeline")
        
        # Call the run_pipeline function from the imported module
        pipeline_module.run_pipeline(destination=destination)
        
    except ModuleNotFoundError:
        print(f"Error: Pipeline '{pipeline_name}' not found. Available pipelines: shopify, facebook_ads, tiktok_ads")
    except Exception as e:
        print(f"An error occurred while running pipeline '{pipeline_name}': {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pipeline_name", help="The name of the pipeline to run (e.g., 'shopify', 'facebook_ads', 'tiktok_ads')")
    parser.add_argument("--destination", default="duckdb", help="The destination to load data to (e.g., 'duckdb', 'bigquery')")
    args = parser.parse_args()
    
    run_pipeline(args.pipeline_name, args.destination)