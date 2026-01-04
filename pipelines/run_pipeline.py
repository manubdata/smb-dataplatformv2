"""
This script runs the Shopify DLT pipeline.
"""

from dlt_pipelines.shopify.shopify_pipeline import run_pipeline


def main():
    """
    Runs the Shopify DLT pipeline with the default destination.
    """
    print("Starting Shopify DLT pipeline...")
    run_pipeline(destination="bigquery")
    print("Shopify DLT pipeline finished.")


if __name__ == "__main__":
    main()
