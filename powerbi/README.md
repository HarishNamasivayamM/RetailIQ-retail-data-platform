# Power BI handoff

There is no `.pbix` file in this repository. The project does not fabricate a
binary report that cannot be inspected or refreshed. Instead, this directory is
the implementation handoff for a Power BI Desktop report connected to the
Snowflake `RETAILIQ.ANALYTICS` schema.

Recommended connection mode is Import for a portfolio demo, with scheduled
refresh in the target environment. Use `fct_sales` as the central fact table,
the four dimensions for slicing, and the performance marts for focused tables.
The semantic model, DAX measures, and page-level design are documented here.

