create schema if not exists RETAILIQ.RAW comment = 'Source-preserving ingestion layer';
create schema if not exists RETAILIQ.STAGING comment = 'dbt standardized source models';
create schema if not exists RETAILIQ.INTERMEDIATE comment = 'Reusable transaction calculations';
create schema if not exists RETAILIQ.ANALYTICS comment = 'Dimensional and reporting models';

