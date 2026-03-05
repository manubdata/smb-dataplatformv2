import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_mock_metrics():
    # Set seed for reproducibility
    np.random.seed(42)
    
    # Generate dates for the last 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    n_days = len(dates)
    
    # Mock basic sales data
    net_sales = np.random.normal(5000, 1000, n_days)
    net_sales = np.where(net_sales < 0, 0, net_sales) # No negative sales
    
    cogs = net_sales * np.random.uniform(0.3, 0.4, n_days)
    gross_margin = net_sales - cogs
    
    ad_spend = np.random.normal(1500, 300, n_days)
    ad_spend = np.where(ad_spend < 0, 0, ad_spend)
    
    marketing_efficiency = net_sales / (ad_spend + 1) # Avoid division by zero
    
    # Mock behavioral data
    cart_abandon_rate = np.random.uniform(0.6, 0.8, n_days)
    refund_rate = np.random.uniform(0.02, 0.08, n_days)
    
    # Mock inventory alerts (these could be daily snapshots or just current)
    # Let's make them slightly variable for visualization
    high_velocity_alerts = np.random.randint(2, 10, n_days)
    low_velocity_alerts = np.random.randint(5, 20, n_days)
    
    df = pd.DataFrame({
        'date_day': dates,
        'net_sales': net_sales,
        'gross_margin': gross_margin,
        'ad_spend': ad_spend,
        'marketing_efficiency': marketing_efficiency,
        'cart_abandon_rate': cart_abandon_rate,
        'refund_rate': refund_rate,
        'high_velocity_alerts': high_velocity_alerts,
        'low_velocity_alerts': low_velocity_alerts
    })
    
    # Create DuckDB file
    db_path = 'duckdb_files/mock_metrics.duckdb'
    con = duckdb.connect(db_path)
    # Explicitly cast date_day to DATE type
    con.execute("CREATE OR REPLACE TABLE rpt_kpis AS SELECT date_day::DATE as date_day, * EXCLUDE (date_day) FROM df")
    con.close()
    print(f"Mocked metrics created at {db_path}")

if __name__ == "__main__":
    create_mock_metrics()
