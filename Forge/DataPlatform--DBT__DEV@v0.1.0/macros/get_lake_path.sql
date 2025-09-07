-- Macro for consistent lake path generation
{% macro get_lake_path(layer, topic_name=none, tenant_filter=none) %}
  {% set base_path = 's3://' ~ var('lake_bucket') ~ '/' ~ var(layer ~ '_path') %}
  
  {% if topic_name %}
    {% set topic_path = base_path ~ '/topic=' ~ topic_name %}
    
    {% if tenant_filter %}
      {{ topic_path ~ '/tenant_id=' ~ tenant_filter ~ '/**/*.parquet' }}
    {% else %}
      {{ topic_path ~ '/**/*.parquet' }}
    {% endif %}
  {% else %}
    {{ base_path ~ '/**/*.parquet' }}
  {% endif %}
{% endmacro %}