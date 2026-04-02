-- Database: transit_tracker

-- DROP DATABASE IF EXISTS transit_tracker;

CREATE DATABASE transit_tracker
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_Antigua & Barbuda.1252'
    LC_CTYPE = 'English_Antigua & Barbuda.1252'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

COMMENT ON DATABASE transit_tracker
    IS 'postgres db for transit 268 app';

DROP TABLE vehicles;