---
title: Monthly Financial Overview
sidebar_label: Monthly Financial
sidebar_position: 3
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

    .pl-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        color: #f5f5f5;
    }

    .pl-row {
        display: flex;
        justify-content: space-between;
        padding: 0.25rem 0;
    }

    .pl-row.total {
        border-top: 1px solid #444;
        margin-top: 0.5rem;
        padding-top: 0.75rem;
        font-weight: bold;
    }

    .pl-row.subtotal {
        border-top: 1px dashed #333;
        margin-top: 0.25rem;
        padding-top: 0.5rem;
    }

    .pl-label {
        font-size: 0.85rem;
    }

    .pl-value {
        font-size: 0.85rem;
    }

    .metrics-layout {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 1.5rem;
    }

    .charts-column {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
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
        defaultValue={'last12months'}
    />
</div>

```sql filtered_kpis
  select * from ${kpis_raw}
  where date_day between '${inputs.date_filter.start}' and '${inputs.date_filter.end}'
```

```sql monthly_data
  WITH base AS (
    SELECT
      date_trunc('month', date_day)::DATE as month_date,
      sum(net_sales) as net_sales,
      sum(gross_margin) as gross_margin,
      sum(ad_spend) as ad_spend,
      avg(refund_rate) as refund_rate
    FROM ${filtered_kpis}
    GROUP BY 1
  ),
  calculated AS (
    SELECT
      *,
      -- Assumptions for mock data representation
      net_sales / (1 - refund_rate) * refund_rate as returns_val,
      net_sales / (1 - refund_rate) as gross_sales,
      net_sales - gross_margin as cogs_val,
      net_sales * 0.05 as shipping_val,
      gross_margin - ad_spend - (net_sales * 0.05) as contribution_margin_val,
      net_sales * 0.15 as fixed_opex_val,
      (gross_margin - ad_spend - (net_sales * 0.05) - (net_sales * 0.15)) as net_profit_val,
      net_sales * 0.65 as new_customer_rev,
      net_sales * 0.35 as returning_customer_rev,
      -- LTV/CAC simulation based on MER
      (net_sales / (ad_spend + 1)) * 1.2 as ltv_cac_val,
      ad_spend / (NULLIF(net_sales, 0) / 45 + 1) as cac_val,
      (net_sales / (NULLIF(net_sales, 0) / 45 + 1)) * 2.5 as ltv_val,
      LAG( (gross_margin - ad_spend - (net_sales * 0.05) - (net_sales * 0.15)) ) OVER (ORDER BY month_date) as prev_month_profit
    FROM base
  )
  SELECT
    *,
    (contribution_margin_val / gross_sales) as cm_pct,
    (net_profit_val / NULLIF(gross_sales, 0)) as net_margin_pct,
    (net_profit_val - prev_month_profit) / NULLIF(prev_month_profit, 0) as profit_growth_yoy,
    ltv_val / NULLIF(cac_val, 0) as ltv_to_cac
  FROM calculated
  ORDER BY month_date
```

```sql latest_month
  select * from ${monthly_data} order by month_date desc limit 1
```

<div class="card">
    <p class="card-title">Net Profit bars by month (% change vs last month)</p>
    <BarChart 
        data={monthly_data} 
        x=month_date 
        y=net_profit_val
        xFmt="mmm yyyy"
        yFmt=usd0k
        fillColor='#03c4a1'
        yGridlines=false
        xGridlines=false
        echartsOptions={{ backgroundColor: 'transparent' }}
    />
</div>

<div class="metrics-layout">
    <div class="card">
        <p class="card-title">P/L Balance (Latest Month)</p>
        <div class="pl-container">
            <div class="pl-row">
                <span class="pl-label">+ Gross sales</span>
                <span class="pl-value"><Value data={latest_month} column=gross_sales fmt=usd2k/></span>
            </div>
            <div class="pl-row">
                <span class="pl-label">- Returns</span>
                <span class="pl-value"><Value data={latest_month} column=returns_val fmt=usd2k/></span>
            </div>
            <div class="pl-row subtotal">
                <span class="pl-label">= Net sales</span>
                <span class="pl-value"><Value data={latest_month} column=net_sales fmt=usd2k/></span>
            </div>
            <div class="pl-row">
                <span class="pl-label">- COGS</span>
                <span class="pl-value"><Value data={latest_month} column=cogs_val fmt=usd2k/></span>
            </div>
            <div class="pl-row">
                <span class="pl-label">- ADS</span>
                <span class="pl-value"><Value data={latest_month} column=ad_spend fmt=usd2k/></span>
            </div>
            <div class="pl-row">
                <span class="pl-label">- Shipping</span>
                <span class="pl-value"><Value data={latest_month} column=shipping_val fmt=usd2k/></span>
            </div>
            <div class="pl-row subtotal">
                <span class="pl-label">= Contrib Margin</span>
                <span class="pl-value" style="color: #03c4a1"><Value data={latest_month} column=contribution_margin_val fmt=usd2k/></span>
            </div>
            <div class="pl-row">
                <span class="pl-label">- Fixed OPEX</span>
                <span class="pl-value"><Value data={latest_month} column=fixed_opex_val fmt=usd2k/></span>
            </div>
            <div class="pl-row total">
                <span class="pl-label">= Net Profit</span>
                <span class="pl-value" style="color: #03c4a1"><Value data={latest_month} column=net_profit_val fmt=usd2k/></span>
            </div>
        </div>
    </div>

    <div class="charts-column">
        <div class="card">
            <p class="card-title">Gross Revenue & Net Profit</p>
            <BarChart 
                data={monthly_data} 
                x=month_date 
                y={['gross_sales', 'net_profit_val']}
                type=grouped
                yFmt=usd0k
                y2=net_margin_pct
                y2SeriesType=line
                y2Fmt=pct0
                xFmt="mmm yyyy" 
                colorPalette={['#03c4a1', '#c52a87', '#947744']}
                yGridlines=false
                y2Gridlines=false
                xGridlines=false
                echartsOptions={{ backgroundColor: 'transparent' }}
            />
            <p style="font-size: 0.7rem; color: #666; margin-top: 0.5rem;">Profitability overview: gross sales vs net profit (bars) and net margin % (line)</p>
        </div>

        <div class="card">
            <p class="card-title">New vs Returning Customer Revenue</p>
            <BarChart 
                data={monthly_data} 
                x=month_date 
                y={['new_customer_rev', 'returning_customer_rev']}
                swapXY=false
                stacked=true
                xFmt="mmm yyyy"
                yFmt=usd0k
                colorPalette={['#03c4a1', '#c52a87']}
                yGridlines=false
                xGridlines=false
                echartsOptions={{ backgroundColor: 'transparent' }}
            />
            <p style="font-size: 0.7rem; color: #666; margin-top: 0.5rem;">Customer fidelity: stacked revenue by customer type</p>
        </div>

        <div class="card">
            <p class="card-title">LTV vs CAC & Ratio</p>
            <BarChart 
                data={monthly_data} 
                x=month_date 
                y={['ltv_val', 'cac_val']}
                type=grouped
                yFmt=usd0
                y2=ltv_to_cac
                y2SeriesType=line
                y2Fmt=num1
                colorPalette={['#03c4a1', '#c52a87', '#947744']}
                yGridlines=false
                y2Gridlines=false
                xGridlines=false
                echartsOptions={{ backgroundColor: 'transparent' }}
            />
            <p style="font-size: 0.7rem; color: #666; margin-top: 0.5rem;">Customer quality: LTV (green) and CAC (pink) bars vs LTV/CAC Ratio (line)</p>
        </div>
    </div>
</div>