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

    /* Hide selection chips and separators in multi-select dropdowns */
    .hide-selection :global(div.sm\:flex),
    .hide-selection :global(span.bg-base-200),
    .hide-selection :global(div[role="separator"]),
    .hide-selection :global(.mx-2.h-4) {
        display: none !important;
    }

    /* Prevent the dropdown button from expanding */
    .hide-selection :global(button) {
        max-width: 180px;
        overflow: hidden;
        white-space: nowrap;
    }
</style>

```sql kpis_raw
  select * from metrics.rpt_kpis order by date_day
```

```sql channel_metrics
  WITH base AS (
    SELECT
        sum(net_sales) as total_net_sales,
        sum(ad_spend) as total_ad_spend,
        sum(net_sales) / 45 as total_simulated_orders
    FROM metrics.rpt_kpis
    WHERE date_day BETWEEN '${inputs.date_filter.start}' and '${inputs.date_filter.end}'
  ),
  channels AS (
    SELECT 'SEO' as channel, 'Organic' as type, 0.12 as order_share, 0 as spend_share
    UNION ALL SELECT 'Social Media', 'Organic', 0.08, 0
    UNION ALL SELECT 'Email', 'Organic', 0.10, 0
    UNION ALL SELECT 'FB Ads', 'Paid', 0.40, 0.4
    UNION ALL SELECT 'Instagram Ads', 'Paid', 0.10, 0.2
    UNION ALL SELECT 'TikTok Ads', 'Paid', 0.20, 0.3
  )
  SELECT
    c.channel,
    c.type,
    b.total_simulated_orders * c.order_share as orders,
    b.total_simulated_orders * c.order_share * 2 as carts,
    CASE WHEN c.type = 'Organic' THEN b.total_simulated_orders * c.order_share * 10 ELSE b.total_simulated_orders * c.order_share * 5 END as clicks,
    CASE WHEN c.type = 'Organic' THEN b.total_simulated_orders * c.order_share * 100 ELSE b.total_simulated_orders * c.order_share * 25 END as impressions,
    b.total_net_sales * c.order_share as revenue,
    b.total_ad_spend * c.spend_share as spend
  FROM channels c, base b
```

```sql organic_channels
  SELECT 'SEO' as channel UNION ALL SELECT 'Social Media' UNION ALL SELECT 'Email'
```

```sql paid_channels
  SELECT 'FB Ads' as channel UNION ALL SELECT 'Instagram Ads' UNION ALL SELECT 'TikTok Ads'
```

<div style="display: flex; justify-content: flex-end; align-items: center; margin-bottom: 2rem;">
    <DateRange
        name=date_filter
        data={kpis_raw}
        dates=date_day
        defaultValue={'last7days'}
    />
</div>

```sql organic_funnel_filtered
  SELECT
    COALESCE(sum(impressions), 0) as impressions,
    COALESCE(sum(clicks), 0) as clicks,
    COALESCE(sum(carts), 0) as carts,
    COALESCE(sum(orders), 0) as orders,
    COALESCE(sum(revenue), 0) as revenue
  FROM ${channel_metrics}
  WHERE channel IN ${inputs.organic_channels_filter.value}
```

```sql paid_funnel_filtered
  SELECT
    COALESCE(sum(impressions), 0) as impressions,
    COALESCE(sum(clicks), 0) as clicks,
    COALESCE(sum(carts), 0) as carts,
    COALESCE(sum(orders), 0) as orders,
    COALESCE(sum(revenue), 0) as revenue,
    COALESCE(sum(spend), 0) as spend,
    COALESCE(sum(revenue) / NULLIF(sum(orders), 0), 0) as aov
  FROM ${channel_metrics}
  WHERE channel IN ${inputs.paid_channels_filter.value}
```

```sql organic_funnel_steps
  SELECT 'Impressions' as step, impressions as val FROM ${organic_funnel_filtered}
  UNION ALL
  SELECT 'Clicks' as step, clicks as val FROM ${organic_funnel_filtered}
  UNION ALL
  SELECT 'Carts' as step, carts as val FROM ${organic_funnel_filtered}
  UNION ALL
  SELECT 'Orders' as step, orders as val FROM ${organic_funnel_filtered}
```

```sql paid_funnel_steps
  SELECT 'Impressions' as step, impressions as val FROM ${paid_funnel_filtered}
  UNION ALL
  SELECT 'Clicks' as step, clicks as val FROM ${paid_funnel_filtered}
  UNION ALL
  SELECT 'Carts' as step, carts as val FROM ${paid_funnel_filtered}
  UNION ALL
  SELECT 'Orders' as step, orders as val FROM ${paid_funnel_filtered}
```

```sql platform_data
  WITH base AS (
    SELECT
        sum(ad_spend) as total_ad_spend,
        sum(net_sales) as total_sales
    FROM metrics.rpt_kpis
    WHERE date_day BETWEEN '${inputs.date_filter.start}' and '${inputs.date_filter.end}'
  )
  SELECT
    'Meta' as platform,
    total_ad_spend * 0.7 as spend,
    (total_sales * 0.6) / NULLIF(total_ad_spend * 0.7, 0) as roas,
    (total_sales * 0.6 * 0.15) / NULLIF(total_ad_spend * 0.7, 0) as poas,
    0.024 as cvr,
    (total_ad_spend * 0.7) / (total_sales * 0.6 / 48) as cac
  UNION ALL
  SELECT
    'TikTok' as platform,
    total_ad_spend * 0.3 as spend,
    (total_sales * 0.4) / NULLIF(total_ad_spend * 0.3, 0) as roas,
    (total_sales * 0.4 * 0.12) / NULLIF(total_ad_spend * 0.3, 0) as poas,
    0.018 as cvr,
    (total_ad_spend * 0.3) / (total_sales * 0.4 / 42) as cac
```

```sql channel_health
  WITH base AS (
    SELECT
        sum(net_sales) as total_net_sales,
        sum(ad_spend) as total_ad_spend,
        sum(net_sales) / 45 as total_simulated_orders
    FROM metrics.rpt_kpis
    WHERE date_day BETWEEN '${inputs.date_filter.start}' and '${inputs.date_filter.end}'
  ),
  channels AS (
    SELECT 'SEO' as channel, 'Organic' as type, 0.12 as order_share, 0 as spend
    UNION ALL SELECT 'Social Media', 'Organic', 0.08, 0
    UNION ALL SELECT 'Email', 'Organic', 0.10, 0
    UNION ALL SELECT 'FB Ads', 'Paid', 0.40, total_ad_spend * 0.4 FROM base
    UNION ALL SELECT 'Instagram Ads', 'Paid', 0.10, total_ad_spend * 0.2 FROM base
    UNION ALL SELECT 'TikTok Ads', 'Paid', 0.20, total_ad_spend * 0.3 FROM base
  ),
  calculated AS (
    SELECT
        c.channel,
        c.type,
        b.total_simulated_orders * c.order_share as orders,
        c.spend,
        b.total_net_sales * c.order_share as revenue
    FROM channels c, base b
  )
  SELECT
    channel,
    type,
    CASE WHEN type = 'Organic' THEN orders * 100 ELSE orders * 25 END as impressions,
    CASE WHEN spend > 0 THEN (spend / (orders * 25)) * 1000 ELSE 0 END as cpm,
    CASE WHEN type = 'Organic' THEN orders * 10 ELSE orders * 5 END as clicks,
    CASE WHEN type = 'Organic' THEN 0.10 ELSE 0.20 END as ctr,
    CASE WHEN spend > 0 THEN spend / (orders * 5) ELSE 0 END as cpc,
    orders * 2 as carts,
    0.40 as atc_rate,
    CASE WHEN spend > 0 THEN spend / (orders * 2) ELSE 0 END as atc_cost,
    orders,
    CASE WHEN type = 'Organic' THEN 0.10 ELSE 0.20 END as cvr,
    CASE WHEN spend > 0 THEN spend / orders ELSE 0 END as cac,
    revenue / NULLIF(orders, 0) as aov,
    CASE WHEN spend > 0 THEN revenue / spend ELSE 0 END as roas,
    CASE 
        WHEN channel IN ('FB Ads', 'Instagram Ads') THEN (revenue * 0.15) / NULLIF(spend, 0)
        WHEN channel = 'TikTok Ads' THEN (revenue * 0.12) / NULLIF(spend, 0)
        ELSE 0 
    END as poas
  FROM calculated
```

```sql organic_channel_health
  SELECT * FROM ${channel_health} 
  WHERE type = 'Organic' 
  AND channel IN ${inputs.organic_channels_filter.value}
```

```sql paid_channel_health
  SELECT * FROM ${channel_health} 
  WHERE type = 'Paid' 
  AND channel IN ${inputs.paid_channels_filter.value}
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
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <p class="card-title" style="margin: 0;">Organic Reach -> Conversion</p>
            <div class="hide-selection" style="font-size: 0.8rem; width: 180px;">
                <Dropdown
                    name=organic_channels_filter
                    data={organic_channels}
                    value=channel
                    multiple=true
                    selectAllByDefault=true
                />
            </div>
        </div>
        <FunnelChart 
            data={organic_funnel_steps} 
            nameCol="step" 
            valueCol="val" 
            colorPalette={['#b8b8b8', '#95bdb0', '#69c1a9', '#03c4a1']}
            echartsOptions={{
                backgroundColor: 'transparent',
                series: [{ minSize: '5%', gap: 2 }]
            }}
        />
        <div style="margin-top: 1.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; border-top: 1px solid #333; padding-top: 1.5rem;">
            <div class="funnel-step">
                <span class="funnel-label">Organic Sales</span>
                <span class="funnel-value"><Value data={organic_funnel_filtered} column=revenue fmt=usd0k/></span>
            </div>
            <div class="funnel-step">
                <span class="funnel-label">Orders</span>
                <span class="funnel-value"><Value data={organic_funnel_filtered} column=orders fmt=num0/></span>
            </div>
        </div>
    </div>

    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <p class="card-title" style="margin: 0;">Paid Ads -> Funnel Health</p>
            <div class="hide-selection" style="font-size: 0.8rem; width: 180px;">
                <Dropdown
                    name=paid_channels_filter
                    data={paid_channels}
                    value=channel
                    multiple=true
                    selectAllByDefault=true
                />
            </div>
        </div>
        <FunnelChart 
            data={paid_funnel_steps} 
            nameCol="step" 
            valueCol="val" 
            colorPalette={['#b8b8b8', '#95bdb0', '#69c1a9', '#03c4a1']}
            echartsOptions={{
                backgroundColor: 'transparent',
                series: [{ minSize: '5%', gap: 2 }]
            }}
        />
        <div style="margin-top: 1.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; border-top: 1px solid #333; padding-top: 1.5rem;">
            <div class="funnel-step">
                <span class="funnel-label">Paid Sales</span>
                <span class="funnel-value"><Value data={paid_funnel_filtered} column=revenue fmt=usd0k/></span>
            </div>
            <div class="funnel-step">
                <span class="funnel-label">CAC/AOV</span>
                <span class="funnel-value">
                    <Value data={paid_funnel_filtered} column=spend fmt=usd0/> / 
                    <Value data={paid_funnel_filtered} column=aov fmt=usd0/>
                </span>
            </div>
        </div>
    </div>
</div>

<div class="card" style="margin-top: 1.5rem;">
    <p class="card-title">Organic Channel Funnel Health</p>
    <DataTable data={organic_channel_health}>
        <Column id="channel" label="Channel"/>
        <Column id="impressions" label="Impr." fmt=num0k/>
        <Column id="clicks" label="Clicks" fmt=num0/>
        <Column id="ctr" label="CTR" fmt=pct/>
        <Column id="carts" label="Carts" fmt=num0/>
        <Column id="atc_rate" label="ATC %" fmt=pct/>
        <Column id="orders" label="Orders" fmt=num0/>
        <Column id="cvr" label="CVR" fmt=pct/>
        <Column id="aov" label="AOV" fmt=usd/>
    </DataTable>

    <div style="margin-top: 1rem; border-top: 1px solid #333; padding-top: 1rem;">
        <p class="card-title">Paid Channel Funnel Health</p>
        <DataTable data={paid_channel_health}>
            <Column id="channel" label="Channel"/>
            <Column id="impressions" label="Impr." fmt=num0k/>
            <Column id="cpm" label="CPM" fmt=usd/>
            <Column id="clicks" label="Clicks" fmt=num0/>
            <Column id="ctr" label="CTR" fmt=pct/>
            <Column id="cpc" label="CPC" fmt=usd/>
            <Column id="carts" label="Carts" fmt=num0/>
            <Column id="atc_rate" label="ATC %" fmt=pct/>
            <Column id="atc_cost" label="ATC Cost" fmt=usd/>
            <Column id="orders" label="Orders" fmt=num0/>
            <Column id="cvr" label="CVR" fmt=pct/>
            <Column id="cac" label="CAC" fmt=usd/>
            <Column id="aov" label="AOV" fmt=usd/>
            <Column id="roas" label="ROAS" fmt=num2/>
            <Column id="poas" label="POAS" fmt=num2/>
        </DataTable>
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
