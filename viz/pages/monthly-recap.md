---
title: Monthly Recap
---

<style>
    :root {
        --evidence-base-dark: #1a1a1a;
        --evidence-card-background: #222222;
    }
    
    .health-card {
        background-color: var(--evidence-card-background);
        border-radius: 12px;
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        border: 1px solid #333;
    }

    .health-card h3 {
        color: #999;
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
        color: #666;
    }

    .progress-bar-container {
        width: 100%;
        height: 8px;
        background-color: #333;
        border-radius: 4px;
        margin-top: 1.5rem;
        overflow: hidden;
    }

    .progress-bar {
        height: 100%;
        border-radius: 4px;
    }
</style>

```sql kpis_all_monthly
  select
    date_trunc('month', date_day)::date as month_date,
    sum(total_net_sales) as total_net_sales,
    sum(total_ad_spend) as total_ad_spend,
    sum(contribution_margin) as contribution_margin,
    avg(mer_total_paid_ads) as mer_total_paid_ads,
    avg(nc_cpa) as nc_cpa,
    avg(npoas) as npoas,
    avg(ltv_cac_ratio) as ltv_cac_ratio
  from metrics.rpt_kpis
  group by 1
  order by 1 desc
```

<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
    <div></div>
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
    -- Achievement logic (Current / Target) - Note: Targets are now monthly
    total_net_sales / 150000.0 as sales_ach,
    contribution_margin / 75000.0 as margin_ach,
    total_ad_spend / 30000.0 as spend_ach,
    mer_total_paid_ads / 8.0 as mer_ach
  from ${kpis_all_monthly}
  where month_date between '${inputs.date_filter.start}' and '${inputs.date_filter.end}'
  order by month_date desc
```

```sql latest_month_kpis
  select * from ${kpis_monthly} limit 1
```

<Grid columns=4 gap=4>
    <!-- Net Sales -->
    <div class="health-card">
        <h3>Net Sales</h3>
        <div class="value" style="color: {latest_month_kpis[0]?.sales_ach >= 1 ? '#10b981' : '#ef4444'}">
            <Value data={latest_month_kpis} column=total_net_sales fmt='usd0k'/>
        </div>
        <div class="target">
            <Value data={latest_month_kpis} column=sales_ach fmt='0.0%'/> of target (150K)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_month_kpis[0]?.sales_ach * 100, 100)}%; background-color: {latest_month_kpis[0]?.sales_ach >= 1 ? '#10b981' : '#ef4444'};"></div>
        </div>
    </div>

    <!-- Margin -->
    <div class="health-card">
        <h3>Contribution Margin</h3>
        <div class="value" style="color: {latest_month_kpis[0]?.margin_ach >= 1 ? '#10b981' : '#ef4444'}">
            <Value data={latest_month_kpis} column=contribution_margin fmt='usd0k'/>
        </div>
        <div class="target">
            <Value data={latest_month_kpis} column=margin_ach fmt='0.0%'/> of target (75K)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_month_kpis[0]?.margin_ach * 100, 100)}%; background-color: {latest_month_kpis[0]?.margin_ach >= 1 ? '#10b981' : '#ef4444'};"></div>
        </div>
    </div>

    <!-- Ad Spend -->
    <div class="health-card">
        <h3>Ad Spend</h3>
        <div class="value" style="color: {latest_month_kpis[0]?.spend_ach <= 1 ? '#10b981' : '#ef4444'}">
            <Value data={latest_month_kpis} column=total_ad_spend fmt='usd0k'/>
        </div>
        <div class="target">
            <Value data={latest_month_kpis} column=spend_ach fmt='0.0%'/> of budget (30K)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_month_kpis[0]?.spend_ach * 100, 100)}%; background-color: {latest_month_kpis[0]?.spend_ach <= 1 ? '#10b981' : '#ef4444'};"></div>
        </div>
    </div>

    <!-- MER -->
    <div class="health-card">
        <h3>Marketing Efficiency</h3>
        <div class="value" style="color: {latest_month_kpis[0]?.mer_ach >= 1 ? '#10b981' : '#ef4444'}">
            <Value data={latest_month_kpis} column=mer_total_paid_ads fmt='0.1x'/>
        </div>
        <div class="target">
            <Value data={latest_month_kpis} column=mer_ach fmt='0.0%'/> of target (8.0x)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_month_kpis[0]?.mer_ach * 100, 100)}%; background-color: {latest_month_kpis[0]?.mer_ach >= 1 ? '#10b981' : '#ef4444'};"></div>
        </div>
    </div>
</Grid>

<div style="margin-top: 3rem;"></div>

## Performance Trends

<LineChart 
    data={kpis_monthly} 
    x=month_date 
    y={['total_net_sales', 'contribution_margin', 'total_ad_spend', 'mer_total_paid_ads']}
    title="Monthly Performance Trends"
/>

<div style="margin-top: 3rem;"></div>

<DataTable data={kpis_monthly}>
    <Column id=month_date title="Month" fmt="mmmm yyyy"/>
    <Column id=total_net_sales title="Net Sales" fmt=usd/>
    <Column id=total_ad_spend title="Ad Spend" fmt=usd/>
    <Column id=mer_total_paid_ads title="MER" fmt='0.0x'/>
    <Column id=nc_cpa title="Avg. ncCPA" fmt=usd/>
    <Column id=npoas title="Avg. NPOAS" fmt='0.0x'/>
    <Column id=ltv_cac_ratio title="Avg. LTV:CAC" fmt='0.0x'/>
</DataTable>
