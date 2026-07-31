-- Builds the Postgres database from the cleaned CSVs.
-- Run from the repo root so the relative paths work:
--   psql -U postgres -h localhost -d mexico_safety -f postgres/load.sql

\encoding UTF8

\i postgres/schema.sql
\i postgres/state_lookup.sql

-- \copy instead of COPY so psql reads the file, not the server
\copy population (year, state_code, population) FROM 'data/cleaned/population.csv' WITH (FORMAT csv, HEADER true)
\copy incidents (year, state_code, state, legal_category, crime_type, crime_subtype, modality, month, incidents) FROM 'data/cleaned/incidents_long.csv' WITH (FORMAT csv, HEADER true)

-- now the text is parsed, every value is whole, so integer is safe.
-- this also makes SUM() return bigint, which is what the ROUND() calls
-- in sql/queries.sql need. Postgres has no ROUND(double precision, integer).
ALTER TABLE incidents ALTER COLUMN incidents TYPE integer;

CREATE INDEX incidents_state_year_idx ON incidents (state_code, year);
CREATE INDEX incidents_year_idx       ON incidents (year);
CREATE INDEX incidents_crime_type_idx ON incidents (crime_type);

ANALYZE;

SELECT 'incidents' AS table_name, count(*) FROM incidents
UNION ALL SELECT 'population', count(*) FROM population
UNION ALL SELECT 'state_lookup', count(*) FROM state_lookup;
