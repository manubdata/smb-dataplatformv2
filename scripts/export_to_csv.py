import duckdb
import os
import pandas as pd

def export_tables_to_csv(db_path: str, output_dir: str):
    """
    Connects to a DuckDB database, reads specified tables, and saves them as CSV files.

    Args:
        db_path: The path to the DuckDB database file.
        output_dir: The directory to save the CSV files in.
    """
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")

    con = duckdb.connect(database=db_path, read_only=True)

    # List of tables to export
    tables_to_export = [
        "rpt_kpis",
        "int_daily_orders",
        "int_daily_ad_spend"
    ]

    for table_name in tables_to_export:
        try:
            print(f"Exporting table: {table_name}...")
            # Use DuckDB's to_df() for direct conversion to a Pandas DataFrame
            df = con.table(table_name).to_df()
            
            output_path = os.path.join(output_dir, f"{table_name}.csv")
            df.to_csv(output_path, index=False)
            
            print(f"✅ Successfully exported {table_name} to {output_path}")
        except duckdb.CatalogException:
            print(f"⚠️ Warning: Table '{table_name}' not found in the database. Skipping.")
        except Exception as e:
            print(f"❌ An error occurred while exporting {table_name}: {e}")

    con.close()

if __name__ == "__main__":
    db_file = "./duckdb_files/dbt_metrics.duckdb"
    export_dir = "./exports"
    export_tables_to_csv(db_file, export_dir)
