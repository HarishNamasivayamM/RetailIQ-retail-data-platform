{% macro retailiq_surrogate_key(fields) -%}
    md5(
      concat(
        {%- for field in fields -%}
          coalesce(cast({{ field }} as varchar), '__null__')
          {%- if not loop.last %}, '||', {% endif -%}
        {%- endfor -%}
      )
    )
{%- endmacro %}

