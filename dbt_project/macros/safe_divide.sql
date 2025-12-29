{% macro safe_divide(numerator, denominator) %}
    coalesce({{ numerator }} / nullif({{ denominator }}, 0), 0)
{% endmacro %}
