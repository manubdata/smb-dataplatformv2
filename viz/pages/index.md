---
title: Daily Health Check
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

```sql kpis_all
  select * from metrics.rpt_kpis order by date_day desc
```

<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
    <div></div>
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
    -- Achievement logic (Current / Target)
    total_net_sales / 5000.0 as sales_ach,
    contribution_margin / 2500.0 as margin_ach,
    total_ad_spend / 1000.0 as spend_ach, -- Lower is better usually, but here we check budget
    mer_total_paid_ads / 8.0 as mer_ach
  from metrics.rpt_kpis
  where date_day between '${inputs.date_filter.start}' and '${inputs.date_filter.end}'
  order by date_day desc
```

```sql latest_kpis
  select * from ${kpis} limit 1
```

<Grid columns=4 gap=4>
    <!-- Net Sales -->
    <div class="health-card">
        <h3>Net Sales</h3>
        <div class="value" style="color: {latest_kpis[0]?.sales_ach >= 1 ? '#10b981' : '#ef4444'}">
            <Value data={latest_kpis} column=total_net_sales fmt='usd0k'/>
        </div>
        <div class="target">
            <Value data={latest_kpis} column=sales_ach fmt='0.0%'/> of target (5.0K)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_kpis[0]?.sales_ach * 100, 100)}%; background-color: {latest_kpis[0]?.sales_ach >= 1 ? '#10b981' : '#ef4444'};"></div>
        </div>
    </div>

    <!-- Margin -->
    <div class="health-card">
        <h3>Contribution Margin</h3>
        <div class="value" style="color: {latest_kpis[0]?.margin_ach >= 1 ? '#10b981' : '#ef4444'}">
            <Value data={latest_kpis} column=contribution_margin fmt='usd0k'/>
        </div>
        <div class="target">
            <Value data={latest_kpis} column=margin_ach fmt='0.0%'/> of target (2.5K)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_kpis[0]?.margin_ach * 100, 100)}%; background-color: {latest_kpis[0]?.margin_ach >= 1 ? '#10b981' : '#ef4444'};"></div>
        </div>
    </div>

    <!-- Ad Spend -->
    <div class="health-card">
        <h3>Ad Spend</h3>
        <div class="value" style="color: {latest_kpis[0]?.spend_ach <= 1 ? '#10b981' : '#ef4444'}">
            <Value data={latest_kpis} column=total_ad_spend fmt='usd0k'/>
        </div>
        <div class="target">
            <Value data={latest_kpis} column=spend_ach fmt='0.0%'/> of budget (1.0K)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_kpis[0]?.spend_ach * 100, 100)}%; background-color: {latest_kpis[0]?.spend_ach <= 1 ? '#10b981' : '#ef4444'};"></div>
        </div>
    </div>

    <!-- MER -->
    <div class="health-card">
        <h3>Marketing Efficiency</h3>
        <div class="value" style="color: {latest_kpis[0]?.mer_ach >= 1 ? '#10b981' : '#ef4444'}">
            <Value data={latest_kpis} column=mer_total_paid_ads fmt='0.1x'/>
        </div>
        <div class="target">
            <Value data={latest_kpis} column=mer_ach fmt='0.0%'/> of target (8.0x)
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {Math.min(latest_kpis[0]?.mer_ach * 100, 100)}%; background-color: {latest_kpis[0]?.mer_ach >= 1 ? '#10b981' : '#ef4444'};"></div>
        </div>
    </div>
</Grid>

<div style="margin-top: 3rem;"></div>

## Performance Trends

<LineChart 
    data={kpis} 
    x=date_day 
    y={['total_net_sales', 'contribution_margin', 'total_ad_spend', 'mer_total_paid_ads']}
    title="Performance Trends"
/>

<div style="margin-top: 3rem;"></div>

<DataTable data={kpis}>
    <Column id=date_day title="Date"/>
    <Column id=total_net_sales title="Net Sales" fmt=usd/>
    <Column id=total_ad_spend title="Ad Spend" fmt=usd/>
    <Column id=mer_total_paid_ads title="MER" fmt='0.0x'/>
    <Column id=nc_cpa title="ncCPA" fmt=usd/>
    <Column id=npoas title="NPOAS" fmt='0.0x'/>
    <Column id=ltv_cac_ratio title="LTV:CAC" fmt='0.0x'/>
</DataTable>
