-- data tables for nova initial setup

CREATE SCHEMA nova_raw;
SET search_path TO nova_raw;

CREATE TABLE users (
    hr_521 text,
    email_addr text,
    domain text,
    level integer,
    is_asker boolean
);

CREATE TABLE departments (
    department_name text,
    department_code text
);