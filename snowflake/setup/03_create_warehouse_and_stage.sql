create warehouse if not exists RETAILIQ_XS
    warehouse_size = 'X-SMALL'
    auto_suspend = 60
    auto_resume = true
    initially_suspended = true
    comment = 'Small development warehouse for RetailIQ';

create file format if not exists RETAILIQ.RAW.RETAILIQ_CSV_FORMAT
    type = csv
    skip_header = 1
    field_optionally_enclosed_by = '"'
    null_if = ('', 'NULL', 'null')
    empty_field_as_null = true;

create stage if not exists RETAILIQ.RAW.RETAILIQ_STAGE
    file_format = RETAILIQ.RAW.RETAILIQ_CSV_FORMAT
    comment = 'Controlled landing stage for source transaction files';

