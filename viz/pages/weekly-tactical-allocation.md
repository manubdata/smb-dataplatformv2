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

    .funnel-svg {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 0;
        opacity: 0.2;
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

    .product-list {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .product-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem;
        border-radius: 4px;
    }

    .product-name {
        font-size: 0.85rem;
    }

    .product-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
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

```sql funnel_data
  WITH base AS (
    SELECT
        sum(net_sales) as total_net_sales,
        sum(ad_spend) as total_ad_spend,
        sum(net_sales) / 45 as simulated_orders -- Assume $45 AOV
    FROM metrics.rpt_kpis
    WHERE date_day BETWEEN '${inputs.date_filter.start}' and '${inputs.date_filter.end}'
  )
  SELECT
    total_net_sales,
    total_ad_spend,
    simulated_orders as orders,
    simulated_orders * 5 as clicks, -- 20% CVR (visual friendly)
    simulated_orders * 25 as impressions, -- 20% CTR (visual friendly)
    simulated_orders * 2 as carts, -- 50% Cart-to-Order (visual friendly)
    total_ad_spend / (NULLIF(simulated_orders * 25, 0) / 1000) as cpm,
    total_ad_spend / NULLIF(simulated_orders * 5, 0) as cpc,
    simulated_orders / NULLIF(simulated_orders * 5, 0) as cvr,
    total_ad_spend / NULLIF(simulated_orders, 0) as cac,
    total_net_sales / NULLIF(simulated_orders, 0) as aov
  FROM base
```

```sql funnel_steps
  SELECT 'Impressions' as step, impressions as val FROM ${funnel_data}
  UNION ALL
  SELECT 'Clicks' as step, clicks as val FROM ${funnel_data}
  UNION ALL
  SELECT 'Carts' as step, carts as val FROM ${funnel_data}
  UNION ALL
  SELECT 'Checkouts' as step, orders as val FROM ${funnel_data}
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
    (total_sales * 0.6 * 0.15) / fb_spend as poas, -- Simplified POAS
    0.024 as cvr, -- Simulated
    fb_spend / (total_sales * 0.6 / 48) as cac -- Simulated
  UNION ALL
  SELECT
    'TikTok' as platform,
    tt_spend as spend,
    (total_sales * 0.4) / tt_spend as roas,
    (total_sales * 0.4 * 0.12) / tt_spend as poas, -- Simplified POAS
    0.018 as cvr, -- Simulated
    tt_spend / (total_sales * 0.4 / 42) as cac -- Simulated
```

```sql product_profit
  -- Mocked product profit data
  SELECT 'Premium Coffee Blend' as product, 1250 as profit, 0.22 as margin, '#03c4a1' as bar_color UNION ALL
  SELECT 'Eco-Friendly Filter' as product, 850 as profit, 0.18 as margin, '#03c4a1' as bar_color UNION ALL
  SELECT 'Cold Brew Kit' as product, 620 as profit, 0.15 as margin, '#03c4a1' as bar_color UNION ALL
  SELECT 'Ceramic Mug Set' as product, 310 as profit, 0.08 as margin, '#c52a87' as bar_color UNION ALL
  SELECT 'Travel Tumbler' as product, 150 as profit, 0.04 as margin, '#c52a87' as bar_color
```

```sql sorted_product_profit
  SELECT * FROM ${product_profit}
  ORDER BY 
    CASE WHEN '${inputs.profit_sort}' = 'asc' THEN profit ELSE -profit END ASC
```

```sql stock_velocity
  -- Mocked stock velocity
  SELECT 'Premium Coffee Blend' as product, 24 as days_left, '#03c4a1' as bar_color UNION ALL
  SELECT 'Eco-Friendly Filter' as product, 15 as days_left, '#03c4a1' as bar_color UNION ALL
  SELECT 'Cold Brew Kit' as product, 4 as days_left, '#c52a87' as bar_color UNION ALL
  SELECT 'Ceramic Mug Set' as product, 12 as days_left, '#03c4a1' as bar_color UNION ALL
  SELECT 'Travel Tumbler' as product, 32 as days_left, '#03c4a1' as bar_color
```

```sql sorted_stock_velocity
  SELECT * FROM ${stock_velocity}
  ORDER BY 
    CASE WHEN '${inputs.stock_sort}' = 'asc' THEN days_left ELSE -days_left END ASC
```

<div class="tactical-grid">
    <div class="card">
        <p class="card-title">Customer related -> funnel health</p>
        
        <FunnelChart 
            data={funnel_steps} 
            nameCol="step" 
            valueCol="val" 
            colorPalette={['#b8b8b8', '#7cc0b0', '#3fc2a8', '#03c4a1']}
            echartsOptions={{
                backgroundColor: 'transparent',
                series: [{
                    minSize: '5%',
                    gap: 2
                }]
            }}
        />

        <div style="margin-top: 1.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; border-top: 1px solid #333; padding-top: 1.5rem;">
            <div class="funnel-step">
                <span class="funnel-label">CPM</span>
                <span class="funnel-value"><Value data={funnel_data} column=cpm fmt=usd2k/></span>
            </div>
            <div class="funnel-step">
                <span class="funnel-label">CPC</span>
                <span class="funnel-value"><Value data={funnel_data} column=cpc fmt=usd2k/></span>
            </div>
            <div class="funnel-step">
                <span class="funnel-label">CVR</span>
                <span class="funnel-value"><Value data={funnel_data} column=cvr fmt=pct1/></span>
            </div>
            <div class="funnel-step">
                <span class="funnel-label">CAC/AOV</span>
                <span class="funnel-value"><Value data={funnel_data} column=cac fmt=usd0/>/<Value data={funnel_data} column=aov fmt=usd0/></span>
            </div>
        </div>
    </div>

    <div style="display: flex; flex-direction: column; gap: 1.5rem;">
        <div class="card">
            <p class="card-title">Marketing related: platform comparison</p>
            <div class="platform-metrics">
                {#each platform_data as platform}
                    <div class="metric-box" style="border-left: 4px solid {platform.platform === 'Meta' ? '#03c4a1' : '#c52a87'}">
                        <span class="metric-box-label">{platform.platform}</span>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                            <div>
                                <div class="funnel-subtext">ROAS</div>
                                <div class="metric-box-value">{platform.roas.toFixed(2)}x</div>
                            </div>
                            <div>
                                <div class="funnel-subtext">POAS</div>
                                <div class="metric-box-value">{platform.poas.toFixed(2)}x</div>
                            </div>
                            <div>
                                <div class="funnel-subtext">CVR</div>
                                <div class="metric-box-value">{(platform.cvr * 100).toFixed(1)}%</div>
                            </div>
                            <div>
                                <div class="funnel-subtext">CAC</div>
                                <div class="metric-box-value">${platform.cac.toFixed(2)}</div>
                            </div>
                        </div>
                    </div>
                {/each}
            </div>
        </div>

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
                fillColor='#03c4a1'
                yGridlines=false
                xGridlines=false
                sort=false
                echartsOptions={{ 
                    backgroundColor: 'transparent'
                }}
            />
            <p style="font-size: 0.7rem; color: #666; margin-top: 0.5rem;">Margin health: bars turn red when margin is under 10%</p>
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
                fillColor='#03c4a1'
                yGridlines=false
                xGridlines=false
                sort=false
                echartsOptions={{ 
                    backgroundColor: 'transparent'
                }}
            />
            <p style="font-size: 0.7rem; color: #666; margin-top: 0.5rem;">Inventory risk: bars turn red when stock is under 7 days</p>
        </div>
    </div>
</div>