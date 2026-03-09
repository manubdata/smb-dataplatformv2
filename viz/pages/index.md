---
title: Welcome to SMB Data Platform
sidebar_label: Home
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
        margin-bottom: 1.5rem;
    }

    h2 {
        color: #f5f5f5;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    p, li {
        color: #b8b8b8;
        line-height: 1.6;
    }

    .guide-card {
        background-color: #1e1e1e;
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
    }

    .feature-list {
        list-style: none;
        padding: 0;
    }

    .feature-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 1.5rem;
    }

    .feature-icon {
        background-color: #333333;
        color: #03c4a1;
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        flex-shrink: 0;
        font-weight: bold;
    }

    .color-swatch {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 3px;
        margin-right: 8px;
    }
</style>

<div style="display: flex; align-items: center; margin-bottom: 2rem;">
    <img src="/logo.svg" alt="SMB Data Platform Logo" style="width: 64px; height: 64px; margin-right: 1.5rem;"/>
    <h1 style="margin-bottom: 0 !important;">SMB Data Platform</h1>
</div>

<div class="guide-card">
    <p>
        Welcome to the <strong>SMB Data Platform</strong>. This dashboard provides a comprehensive view of your business performance, 
        integrating data from Shopify, Meta Ads, and TikTok Ads.
    </p>
</div>

## Dashboard Guide

<div class="feature-list">
    <div class="feature-item">
        <div class="feature-icon">1</div>
        <div>
            <strong>Daily Health Check</strong>
            <p>Monitor your performance in real-time. This page compares daily results against specific business targets for Sales, Margin, Ad Spend, and Efficiency (MER).</p>
        </div>
    </div>

    <div class="feature-item">
        <div class="feature-icon">2</div>
        <div>
            <strong>Monthly Recap</strong>
            <p>Analyze long-term trends and monthly growth. Use this to identify seasonal patterns and the overall trajectory of your business.</p>
        </div>
    </div>

    <div class="feature-item">
        <div class="feature-icon">3</div>
        <div>
            <strong>Monthly Financial Overview</strong>
            <p>A detailed P&L view and unit economics analysis. Track gross sales, contribution margins, and LTV:CAC trends.</p>
        </div>
    </div>

    <div class="feature-item">
        <div class="feature-icon">4</div>
        <div>
            <strong>Weekly Tactical Allocation</strong>
            <p>Optimize your weekly budget. Compare platform performance (Meta vs TikTok), analyze the marketing funnel, and monitor product stock velocity.</p>
        </div>
    </div>

    <div class="feature-item">
        <div class="feature-icon">5</div>
        <div>
            <strong>Filters & Interactivity</strong>
            <p>Use the date range filters at the top of each page to zoom into specific periods. Most charts and tables update automatically based on your selection.</p>
        </div>
    </div>
</div>

## Performance Indicators

Understanding the color coding in our KPI cards:

*   <span class="color-swatch" style="background-color: #03c4a1;"></span> **Green (#03c4a1):** Target achieved or budget respected.
*   <span class="color-swatch" style="background-color: #c52a87;"></span> **Red (#c52a87):** Performance below target or budget exceeded.

## How Date Filters Work

The dashboard uses a reactive loop to ensure your view is always synchronized:

*   **Selection:** When you pick a range in the **Date Filter** component at the top of a page, it updates the global input variables for that session.
*   **Reactive SQL:** These variables are instantly injected into the underlying SQL queries (e.g., `WHERE date_day BETWEEN start AND end`).
*   **Most Recent Day Snapshot:** The **Metric Cards** specifically calculate values for the **most recent day** available within your selected period, giving you an "up-to-the-minute" snapshot relative to your filter.
*   **Automatic Refresh:** Because all metric cards, progress bars, and trend charts depend on these queries, they recalculate and refresh automatically without needing a page reload.

---

<p style="text-align: center; margin-top: 4rem; opacity: 0.5;">
    SMB Data Platform v2.0 • Data refreshed daily
</p>

