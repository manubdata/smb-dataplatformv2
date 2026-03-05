---
title: Monthly Recap
sidebar_label: Monthly Recap
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
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .health-card h3 {
        color: #b8b8b8;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.1em;
        margin-bottom: 1rem;
    }

    .health-card .value {
        font-size: 2.25rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }

    .health-card .target {
        font-size: 0.75rem;
        color: #b8b8b8;
    }

    .progress-bar-container {
        width: 100%;
        height: 8px;
        background-color: #333333;
        border-radius: 4px;
        margin-top: 1.5rem;
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
</style>

```sql kpis_all_monthly
  select
    date_trunc('month', date_day::DATE)::date as month_date,
    sum(net_sales) as net_sales,
    sum(gross_margin) as gross_margin,
    sum(ad_spend) as ad_spend,
    avg(marketing_efficiency) as marketing_efficiency,
    avg(cart_abandon_rate) as cart_abandon_rate,
    avg(refund_rate) as refund_rate,
    max(high_velocity_alerts) as high_velocity_alerts,
    max(low_velocity_alerts) as low_velocity_alerts
  from metrics.rpt_kpis
  group by 1
  order by 1 desc
```

<div style="display: flex; justify-content: flex-end; align-items: center; margin-bottom: 2rem;">
    <DateRange
        name=date_filter
        data={kpis_all_monthly}
        dates=month_date
        defaultValue={'last6months'}
    />
</div>

```sql kpis_monthly
  select 
    *,
    net_sales / 150000.0 as sales_ach,
    gross_margin / 90000.0 as margin_ach,
    ad_spend / 45000.0 as spend_ach, 
    marketing_efficiency / 3.5 as mer_ach
  from ${kpis_all_monthly}
  where month_date between '${inputs.date_filter.start}' and '${inputs.date_filter.end}'
  order by month_date desc
```

```sql latest_month_kpis
  select * from ${kpis_monthly} limit 1
```


<Grid columns=4 gap=4>
    <div class="health-card">
        <h3>Net Sales</h3>
        <div class="value" style="color: {latest_month_kpis[0]?.sales_ach >= 1 ? '#03c4a1' : '#c52a87'}">
            <Value data={latest_month_kpis} column=net_sales fmt='usd0k'/>
        </div>
        <div class="target">
            <Value data={latest_month_kpis} column=sales_ach fmt='0.0%'/> of target (150K)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_month_kpis[0]?.sales_ach * 100, 100)}%; background-color: {latest_month_kpis[0]?.sales_ach >= 1 ? '#03c4a1' : '#c52a87'};"></div>
        </div>
    </div>

    <div class="health-card">
        <h3>Gross Margin</h3>
        <div class="value" style="color: {latest_month_kpis[0]?.margin_ach >= 1 ? '#03c4a1' : '#c52a87'}">
            <Value data={latest_month_kpis} column=gross_margin fmt='usd0k'/>
        </div>
        <div class="target">
            <Value data={latest_month_kpis} column=margin_ach fmt='0.0%'/> of target (90K)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_month_kpis[0]?.margin_ach * 100, 100)}%; background-color: {latest_month_kpis[0]?.margin_ach >= 1 ? '#03c4a1' : '#c52a87'};"></div>
        </div>
    </div>

    <div class="health-card">
        <h3>Ad Spend</h3>
        <div class="value" style="color: {latest_month_kpis[0]?.spend_ach <= 1 ? '#03c4a1' : '#c52a87'}">
            <Value data={latest_month_kpis} column=ad_spend fmt='usd0k'/>
        </div>
        <div class="target">
            <Value data={latest_month_kpis} column=spend_ach fmt='0.0%'/> of budget (45K)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_month_kpis[0]?.spend_ach * 100, 100)}%; background-color: {latest_month_kpis[0]?.spend_ach <= 1 ? '#03c4a1' : '#c52a87'};"></div>
        </div>
    </div>

    <div class="health-card">
        <h3>Marketing Efficiency</h3>
        <div class="value" style="color: {latest_month_kpis[0]?.mer_ach >= 1 ? '#03c4a1' : '#c52a87'}">
            <Value data={latest_month_kpis} column=marketing_efficiency fmt='0.1x'/>
        </div>
        <div class="target">
            <Value data={latest_month_kpis} column=mer_ach fmt='0.0%'/> of target (3.5x)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_month_kpis[0]?.mer_ach * 100, 100)}%; background-color: {latest_month_kpis[0]?.mer_ach >= 1 ? '#03c4a1' : '#c52a87'};"></div>
        </div>
    </div>

    <div class="health-card">
        <h3>Cart Abandon Rate</h3>
        <div class="value" style="color: #b8b8b8">
            <Value data={latest_month_kpis} column=cart_abandon_rate fmt='0.1%'/>
        </div>
    </div>

    <div class="health-card">
        <h3>Refund Rate</h3>
        <div class="value" style="color: #b8b8b8">
            <Value data={latest_month_kpis} column=refund_rate fmt='0.1%'/>
        </div>
    </div>

    <div class="health-card">
        <h3>High Velocity Alert</h3>
        <div class="value" style="color: #c52a87">
            <Value data={latest_month_kpis} column=high_velocity_alerts/>
        </div>
    </div>

    <div class="health-card">
        <h3>Low Velocity Alert</h3>
        <div class="value" style="color: #03c4a1">
            <Value data={latest_month_kpis} column=low_velocity_alerts/>
        </div>
    </div>
</Grid>

<div style="margin-top: 3rem;"></div>

<div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
    <ButtonGroup name=metric_monthly>
        <ButtonGroupItem valueLabel="Net Sales" value="net_sales" default />
        <ButtonGroupItem valueLabel="Gross Margin" value="gross_margin" />
        <ButtonGroupItem valueLabel="Ad Spend" value="ad_spend" />
        <ButtonGroupItem valueLabel="MER" value="marketing_efficiency" />
    </ButtonGroup>
</div>

```sql monthly_chart_data
    WITH base AS (
        SELECT 
            month_date,
            CASE 
                WHEN '${inputs.metric_monthly}' = 'net_sales' THEN net_sales
                WHEN '${inputs.metric_monthly}' = 'gross_margin' THEN gross_margin
                WHEN '${inputs.metric_monthly}' = 'ad_spend' THEN ad_spend
                WHEN '${inputs.metric_monthly}' = 'marketing_efficiency' THEN marketing_efficiency
                ELSE net_sales
            END as metric_value,
            extract(epoch from month_date::timestamp) as x
        FROM ${kpis_monthly}
    ),
    stats AS (
        SELECT
            regr_slope(metric_value, x) as m,
            regr_intercept(metric_value, x) as b
        FROM base
    )
    SELECT
        month_date,
        metric_value,
        (SELECT m FROM stats) * x + (SELECT b FROM stats) as trend_line
    FROM base
    ORDER BY month_date
```

<div class="chart-container">
    <p class="chart-title">Monthly Trend</p>

    <LineChart 
        data={monthly_chart_data} 
        x=month_date 
        y={['metric_value', 'trend_line']}
        xFmt="mmm yyyy"
        colorPalette={['#03c4a1', '#666666']}
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
