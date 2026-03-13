---
title: Weekly Tactical Allocation
sidebar_label: Weekly Tactical
sidebar_position: 2
---

<style>
    :global(body) {
        background-color: #1a1a1a !important;
    }

    :global(#evidence-main-content) {
        background-color: #1a1a1a !important;
    }

    h1 {
        color: #f5f5f5 !important;
        margin-bottom: 2rem;
    }

    .card {
        background-color: #1e1e1e;
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .card-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #b8b8b8;
        margin: 0 0 1.2rem 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .tactical-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
    }

    .funnel-container {
        display: flex;
        flex-direction: column;
        gap: 2rem;
        padding: 1rem;
        position: relative;
    }

    .funnel-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        z-index: 1;
    }

    .funnel-label {
        font-size: 0.8rem;
        color: #b8b8b8;
        margin-bottom: 0.25rem;
    }

    .funnel-value {
        font-size: 1.2rem;
        font-weight: bold;
        color: #f5f5f5;
    }

    .funnel-subtext {
        font-size: 0.7rem;
        color: #666;
    }

    .platform-metrics {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
    }

    .metric-box {
        padding: 1rem;
        background: #252525;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .metric-box-label {
        font-size: 0.7rem;
        color: #888;
        text-transform: uppercase;
    }

    .metric-box-value {
        font-size: 1.1rem;
        font-weight: bold;
    }
</style>

```sql kpis_raw
  select * from metrics.rpt_kpis order by date_day
```

<div style="display: flex; justify-content: flex-end; align-items: center; margin-bottom: 2rem;">
    <DateRange
        name=date_filter
        data={kpis_raw}
        dates=date_day
        defaultValue={'last7days'}
    />
</div>

```sql funnel_data_split
  WITH base AS (
    SELECT
        sum(net_sales) as total_net_sales,
        sum(ad_spend) as total_ad_spend,
        sum(net_sales) / 45 as total_simulated_orders
    FROM metrics.rpt_kpis
    WHERE date_day BETWEEN '${inputs.date_filter.start}' and '${inputs.date_filter.end}'
  ),
  split AS (
    SELECT
        total_net_sales * 0.3 as organic_sales,
        total_net_sales * 0.7 as paid_sales,
        total_ad_spend,
        total_simulated_orders * 0.3 as organic_orders,
        total_simulated_orders * 0.7 as paid_orders,
        total_net_sales / NULLIF(total_simulated_orders, 0) as aov
    FROM base
  )
  SELECT
    *,
    -- Organic steps (simulated)
    organic_orders * 2 as organic_carts,
    organic_orders * 10 as organic_clicks,
    organic_orders * 100 as organic_impressions,
    -- Paid steps (simulated)
    paid_orders * 2 as paid_carts,
    paid_orders * 5 as paid_clicks,
    paid_orders * 25 as paid_impressions,
    -- Paid efficiency
    total_ad_spend / (NULLIF(paid_orders * 25, 0) / 1000) as paid_cpm,
    total_ad_spend / NULLIF(paid_orders * 5, 0) as paid_cpc,
    paid_orders / NULLIF(paid_orders * 5, 0) as paid_cvr,
    total_ad_spend / NULLIF(paid_orders, 0) as paid_cac
  FROM split
```

```sql organic_funnel_steps
  SELECT 'Impressions' as step, organic_impressions as val FROM ${funnel_data_split}
  UNION ALL
  SELECT 'Clicks' as step, organic_clicks as val FROM ${funnel_data_split}
  UNION ALL
  SELECT 'Carts' as step, organic_carts as val FROM ${funnel_data_split}
  UNION ALL
  SELECT 'Orders' as step, organic_orders as val FROM ${funnel_data_split}
```

```sql paid_funnel_steps
  SELECT 'Impressions' as step, paid_impressions as val FROM ${funnel_data_split}
  UNION ALL
  SELECT 'Clicks' as step, paid_clicks as val FROM ${funnel_data_split}
  UNION ALL
  SELECT 'Carts' as step, paid_carts as val FROM ${funnel_data_split}
  UNION ALL
  SELECT 'Orders' as step, paid_orders as val FROM ${funnel_data_split}
```

```sql platform_data
  WITH base AS (
    SELECT
        sum(facebook_spend) as fb_spend,
        sum(tiktok_spend) as tt_spend,
        sum(net_sales) as total_sales
    FROM metrics.rpt_kpis
    WHERE date_day BETWEEN '${inputs.date_filter.start}' and '${inputs.date_filter.end}'
  )
  SELECT
    'Meta' as platform,
    fb_spend as spend,
    (total_sales * 0.6) / fb_spend as roas,
    (total_sales * 0.6 * 0.15) / fb_spend as poas,
    0.024 as cvr,
    fb_spend / (total_sales * 0.6 / 48) as cac
  UNION ALL
  SELECT
    'TikTok' as platform,
    tt_spend as spend,
    (total_sales * 0.4) / tt_spend as roas,
    (total_sales * 0.4 * 0.12) / tt_spend as poas,
    0.018 as cvr,
    tt_spend / (total_sales * 0.4 / 42) as cac
```

```sql product_profit
  -- Mocked product profit data
  SELECT 'Premium Coffee Blend' as product, 1250 as profit, 0.22 as margin UNION ALL
  SELECT 'Eco-Friendly Filter' as product, 850 as profit, 0.18 as margin UNION ALL
  SELECT 'Cold Brew Kit' as product, 620 as profit, 0.15 as margin UNION ALL
  SELECT 'Ceramic Mug Set' as product, 310 as profit, 0.08 as margin UNION ALL
  SELECT 'Travel Tumbler' as product, -50 as profit, -0.04 as margin
```

```sql sorted_product_profit
  SELECT * FROM ${product_profit}
  ORDER BY 
    CASE WHEN '${inputs.profit_sort}' = 'asc' THEN profit ELSE -profit END ASC
```

```sql stock_velocity
  -- Mocked stock velocity
  SELECT 'Premium Coffee Blend' as product, 24 as days_left UNION ALL
  SELECT 'Eco-Friendly Filter' as product, 15 as days_left UNION ALL
  SELECT 'Cold Brew Kit' as product, 4 as days_left UNION ALL
  SELECT 'Ceramic Mug Set' as product, 12 as days_left UNION ALL
  SELECT 'Travel Tumbler' as product, 32 as days_left
```

```sql sorted_stock_velocity
  SELECT * FROM ${stock_velocity}
  ORDER BY 
    CASE WHEN '${inputs.stock_sort}' = 'asc' THEN days_left ELSE -days_left END ASC
```

<div class="tactical-grid">
    <!-- TOP SECTION: ORGANIC vs PAID -->
    <div class="card">
        <p class="card-title">Organic Reach -> Conversion</p>
        <FunnelChart 
            data={organic_funnel_steps} 
            nameCol="step" 
            valueCol="val" 
            colorPalette={['#c52a87', '#ae6f90', '#879c99', '#03c4a1']}
            echartsOptions={{
                backgroundColor: 'transparent',
                series: [{ minSize: '5%', gap: 2 }]
            }}
        />
        <div style="margin-top: 1.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; border-top: 1px solid #333; padding-top: 1.5rem;">
            <div class="funnel-step">
                <span class="funnel-label">Organic Sales</span>
                <span class="funnel-value"><Value data={funnel_data_split} column=organic_sales fmt=usd0k/></span>
            </div>
            <div class="funnel-step">
                <span class="funnel-label">Contribution</span>
                <span class="funnel-value">30%</span>
            </div>
        </div>
    </div>

    <div class="card">
        <p class="card-title">Paid Ads -> Funnel Health</p>
        <FunnelChart 
            data={paid_funnel_steps} 
            nameCol="step" 
            valueCol="val" 
            colorPalette={['#c52a87', '#ae6f90', '#879c99', '#03c4a1']}
            echartsOptions={{
                backgroundColor: 'transparent',
                series: [{ minSize: '5%', gap: 2 }]
            }}
        />
        <div style="margin-top: 1.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; border-top: 1px solid #333; padding-top: 1.5rem;">
            <div class="funnel-step">
                <span class="funnel-label">Paid Sales</span>
                <span class="funnel-value"><Value data={funnel_data_split} column=paid_sales fmt=usd0k/></span>
            </div>
            <div class="funnel-step">
                <span class="funnel-label">CAC/AOV</span>
                <span class="funnel-value"><Value data={funnel_data_split} column=paid_cac fmt=usd0/>/<Value data={funnel_data_split} column=aov fmt=usd0/></span>
            </div>
        </div>
    </div>
</div>

<div class="tactical-grid" style="margin-top: 1.5rem;">
    <!-- BOTTOM SECTION: PRODUCT PROFIT vs STOCK VELOCITY -->
    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem;">
            <p class="card-title" style="margin: 0;">Product Related: Profit</p>
            <div style="font-size: 0.75rem;">
                <ButtonGroup name=profit_sort>
                    <ButtonGroupItem value="desc" valueLabel="High" default />
                    <ButtonGroupItem value="asc" valueLabel="Low" />
                </ButtonGroup>
            </div>
        </div>
        <BarChart 
            data={sorted_product_profit}
            x=product
            y=profit 
            swapXY=true
            yFmt=usd0k
            yGridlines=false
            xGridlines=false
            sort=false
            echartsOptions={{ 
                backgroundColor: 'transparent',
                visualMap: {
                    show: false,
                    dimension: 0,
                    pieces: [
                        {gt: 0, color: '#03c4a1'},
                        {lte: 0, color: '#c52a87'}
                    ]
                }
            }}
        />
        <p style="font-size: 0.7rem; color: #666; margin-top: 0.5rem;">Profitability risk: bars turn pink when profit is $0 or less</p>
    </div>

    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem;">
            <p class="card-title" style="margin: 0;">Stock Velocity (Days Left)</p>
            <div style="font-size: 0.75rem;">
                <ButtonGroup name=stock_sort>
                    <ButtonGroupItem value="desc" valueLabel="High" default />
                    <ButtonGroupItem value="asc" valueLabel="Low" />
                </ButtonGroup>
            </div>
        </div>
        <BarChart 
            data={sorted_stock_velocity}
            x=product
            y=days_left 
            swapXY=true
            yFmt=num0
            yGridlines=false
            xGridlines=false
            sort=false
            echartsOptions={{ 
                backgroundColor: 'transparent',
                visualMap: {
                    show: false,
                    dimension: 0,
                    pieces: [
                        {gt: 5, color: '#03c4a1'},
                        {lte: 5, color: '#c52a87'}
                    ]
                }
            }}
        />
        <p style="font-size: 0.7rem; color: #666; margin-top: 0.5rem;">Inventory risk: bars turn pink when stock is 5 days or less</p>
    </div>
</div>
