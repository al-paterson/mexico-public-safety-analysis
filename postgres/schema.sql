-- Tables for the Postgres version of the database.
-- Unlike SQLite, the column types are declared here instead of guessed by pandas.

DROP TABLE IF EXISTS incidents;
DROP TABLE IF EXISTS population;
DROP TABLE IF EXISTS state_lookup;

CREATE TABLE state_lookup (
    state_code  integer PRIMARY KEY,
    state_name  text NOT NULL,
    region      text NOT NULL
);

CREATE TABLE population (
    year        integer NOT NULL,
    state_code  integer NOT NULL REFERENCES state_lookup (state_code),
    population  integer NOT NULL,
    PRIMARY KEY (state_code, year)
);

-- incidents starts as numeric because the CSV writes whole numbers as "3.0",
-- which COPY will not load into an integer column. Narrowed in load.sql.
CREATE TABLE incidents (
    year            integer NOT NULL,
    state_code      integer NOT NULL REFERENCES state_lookup (state_code),
    state           text NOT NULL,
    legal_category  text,
    crime_type      text,
    crime_subtype   text,
    modality        text,
    month           integer NOT NULL,
    incidents       numeric
);
