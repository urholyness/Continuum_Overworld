-- Macro for incremental partition filtering
{% macro get_partition_filter(date_column, lookback_hours=2) %}
  {% if is_incremental() %}
    where {{ date_column }} >= current_timestamp - interval {{ lookback_hours }} hours
  {% endif %}
{% endmacro %}