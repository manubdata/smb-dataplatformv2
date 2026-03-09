---
title: Daily Health Check
sidebar_label: Daily Health Check
sidebar_position: 1
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

    .health-card {
        background-color: #1e1e1e;
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .health-card h3 {
        color: #b8b8b8;
        text-transform: uppercase;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }

    .health-card .value {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.25rem;
    }

    .health-card .target {
        font-size: 0.7rem;
        color: #b8b8b8;
    }

    .progress-bar-container {
        width: 100%;
        height: 9px;
        background-color: #333333;
        border-radius: 4.5px;
        margin-top: 1rem;
        overflow: hidden;
    }

    .progress-bar {
        height: 100%;
        border-radius: 4px;
    }

    .chart-container {
        background-color: #1e1e1e;
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }

    .chart-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #f5f5f5;
        margin: 0 0 1.5rem 0;
    }

    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1rem;
    }
</style>

```sql kpis_all
  select date_day::DATE as date_day, * EXCLUDE (date_day) from metrics.rpt_kpis order by date_day desc
```

<div style="display: flex; justify-content: flex-end; align-items: center; margin-bottom: 2rem;">
    <DateRange
        name=date_filter
        data={kpis_all}
        dates=date_day
        defaultValue={'last30days'}
    />
</div>

```sql kpis
  select 
    *,
    net_sales / 5000.0 as sales_ach,
    gross_margin / 3000.0 as margin_ach,
    ad_spend / 1500.0 as spend_ach, 
    marketing_efficiency / 3.5 as mer_ach,
    cart_abandon_rate / 0.6 as abandon_ach,
    refund_rate / 0.06 as refund_ach
  from metrics.rpt_kpis
  where date_day between '${inputs.date_filter.start}' and '${inputs.date_filter.end}'
  order by date_day desc
```

```sql latest_kpis
  select * from ${kpis} limit 1
```

<div class="metrics-grid">
    <div class="health-card">
        <h3 title="Sum of total net sales.">Net Sales</h3>
        <div class="value" style="color: {latest_kpis[0]?.sales_ach >= 1 ? '#03c4a1' : '#c52a87'}">
            <Value data={latest_kpis} column=net_sales fmt='usd2k'/>
        </div>
        <div class="target">
            <Value data={latest_kpis} column=sales_ach fmt='0.0%'/> of target (5.0K)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_kpis[0]?.sales_ach * 100, 100)}%; background-color: {latest_kpis[0]?.sales_ach >= 1 ? '#03c4a1' : '#c52a87'};"></div>
        </div>
    </div>

    <div class="health-card">
        <h3 title="Net Sales minus Cost of Goods Sold (COGS).">Gross Margin</h3>
        <div class="value" style="color: {latest_kpis[0]?.margin_ach >= 1 ? '#03c4a1' : '#c52a87'}">
            <Value data={latest_kpis} column=gross_margin fmt='usd2k'/>
        </div>
        <div class="target">
            <Value data={latest_kpis} column=margin_ach fmt='0.0%'/> of target (3.0K)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_kpis[0]?.margin_ach * 100, 100)}%; background-color: {latest_kpis[0]?.margin_ach >= 1 ? '#03c4a1' : '#c52a87'};"></div>
        </div>
    </div>

    <div class="health-card">
        <h3 title="Sum of total ad spend across all platforms.">Ad Spend</h3>
        <div class="value" style="color: {latest_kpis[0]?.spend_ach <= 1 ? '#03c4a1' : '#c52a87'}">
            <Value data={latest_kpis} column=ad_spend fmt='usd2k'/>
        </div>
        <div class="target">
            <Value data={latest_kpis} column=spend_ach fmt='0.0%'/> of budget (1.5K)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_kpis[0]?.spend_ach * 100, 100)}%; background-color: {latest_kpis[0]?.spend_ach <= 1 ? '#03c4a1' : '#c52a87'};"></div>
        </div>
    </div>

    <div class="health-card">
        <h3 title="Total Net Sales divided by Total Ad Spend.">Marketing Efficiency</h3>
        <div class="value" style="color: {latest_kpis[0]?.mer_ach >= 1 ? '#03c4a1' : '#c52a87'}">
            <Value data={latest_kpis} column=marketing_efficiency fmt='0.1x'/>
        </div>
        <div class="target">
            <Value data={latest_kpis} column=mer_ach fmt='0.0%'/> of target (3.5x)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_kpis[0]?.mer_ach * 100, 100)}%; background-color: {latest_kpis[0]?.mer_ach >= 1 ? '#03c4a1' : '#c52a87'};"></div>
        </div>
    </div>

    <div class="health-card">
        <h3 title="Ratio of abandoned carts to total carts.">Cart Abandon Rate</h3>
        <div class="value" style="color: {latest_kpis[0]?.abandon_ach <= 1 ? '#03c4a1' : '#c52a87'}">
            <Value data={latest_kpis} column=cart_abandon_rate fmt='0%'/>
        </div>
        <div class="target">
            <Value data={latest_kpis} column=abandon_ach fmt='0%'/> of limit (60%)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_kpis[0]?.abandon_ach * 100, 100)}%; background-color: {latest_kpis[0]?.abandon_ach <= 1 ? '#03c4a1' : '#c52a87'};"></div>
        </div>
    </div>

    <div class="health-card">
        <h3 title="Ratio of refunded orders to total orders.">Refund Rate</h3>
        <div class="value" style="color: {latest_kpis[0]?.refund_ach <= 1 ? '#03c4a1' : '#c52a87'}">
            <Value data={latest_kpis} column=refund_rate fmt='0%'/>
        </div>
        <div class="target">
            <Value data={latest_kpis} column=refund_ach fmt='0%'/> of limit (6%)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_kpis[0]?.refund_ach * 100, 100)}%; background-color: {latest_kpis[0]?.refund_ach <= 1 ? '#03c4a1' : '#c52a87'};"></div>
        </div>
    </div>

    <div class="health-card">
        <h3 title="Count of items predicted to run out within 7 days.">High Velocity Alert</h3>
        <div class="value" style="color: {latest_kpis[0]?.high_velocity_alerts !== 0 ? '#c52a87' : '#03c4a1'}">
            <Value data={latest_kpis} column=high_velocity_alerts/>
        </div>
        <div class="target">Items running out in 7 days</div>
    </div>

    <div class="health-card">
        <h3 title="Count of items not sold for over 1 month.">Low Velocity Alert</h3>
        <div class="value" style="color: {latest_kpis[0]?.low_velocity_alerts !== 0 ? '#c52a87' : '#03c4a1'}">
            <Value data={latest_kpis} column=low_velocity_alerts/>
        </div>
        <div class="target">Items over 1 month threshold</div>
    </div>
</div>

```sql daily_chart_data
    WITH base AS (
        SELECT 
            date_day,
            CASE 
                WHEN '${inputs.metric_daily}' = 'net_sales' THEN net_sales
                WHEN '${inputs.metric_daily}' = 'gross_margin' THEN gross_margin
                WHEN '${inputs.metric_daily}' = 'ad_spend' THEN ad_spend
                WHEN '${inputs.metric_daily}' = 'marketing_efficiency' THEN marketing_efficiency
                WHEN '${inputs.metric_daily}' = 'cart_abandon_rate' THEN cart_abandon_rate
                ELSE net_sales
            END as metric_value,
            extract(epoch from date_day::timestamp) as x
        FROM ${kpis}
    ),
    stats AS (
        SELECT
            regr_slope(metric_value, x) as m,
            regr_intercept(metric_value, x) as b
        FROM base
    )
    SELECT
        date_day,
        metric_value,
        (SELECT m FROM stats) * x + (SELECT b FROM stats) as trend_line,
        (SELECT m FROM stats) as slope
    FROM base
    ORDER BY date_day
```

<div class="chart-container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <p class="chart-title" style="margin: 0;">Metric Trend</p>
        <div style="font-size: 0.75rem;">
            <ButtonGroup name=metric_daily>
                <ButtonGroupItem valueLabel="Sales" value="net_sales" default />
                <ButtonGroupItem valueLabel="Margin" value="gross_margin" />
                <ButtonGroupItem valueLabel="Ads" value="ad_spend" />
                <ButtonGroupItem valueLabel="MER" value="marketing_efficiency" />
                <ButtonGroupItem valueLabel="Rate" value="cart_abandon_rate" />
            </ButtonGroup>
        </div>
    </div>

    <LineChart 
        data={daily_chart_data} 
        x=date_day 
        y={['metric_value', 'trend_line']}
        xFmt="dd mmm yyyy"
        colorPalette={
            ( ['ad_spend', 'cart_abandon_rate'].includes(inputs.metric_daily) 
                ? daily_chart_data[0]?.slope <= 0 
                : daily_chart_data[0]?.slope >= 0
            ) 
            ? ['#03c4a1', '#666666'] 
            : ['#c52a87', '#666666']
        }
        yGridlines=false
        legend=false
        echartsOptions={{
            backgroundColor: '#1e1e1e',
            series: [
                { }, 
                { lineStyle: { type: 'dashed', width: 1 } }
            ]
        }}
    />
</div>
