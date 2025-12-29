-- A singular test to check the logic of contribution margin.
-- Contribution margin should not be positive on days with zero or negative net sales,
-- unless there are returns that make other costs negative (not modeled here).

select
    date_day,
    contribution_margin,
    total_net_sales
from {{ ref('rpt_kpis') }}
where total_net_sales <= 0 and contribution_margin > 0
