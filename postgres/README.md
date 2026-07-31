# Postgres version of the database

I built this project on SQLite because the data is small and it needs no server.
Then I loaded the same data into Postgres to practise on a real database server.
The SQLite version still works. None of the Python scripts changed.

## Build it

From the repo root, with Postgres running locally:

```bash
createdb -U postgres -h localhost -E UTF8 mexico_safety
psql -U postgres -h localhost -d mexico_safety -f postgres/load.sql
```

It drops and recreates the tables, so it is safe to run again.

| File | What it does |
|---|---|
| `schema.sql` | Creates the tables with types, primary keys and foreign keys |
| `state_lookup.sql` | Inserts the 32 state codes with names and regions |
| `load.sql` | Runs the other two, copies both CSVs in, adds indexes |

Row counts after loading: 421,248 incidents, 384 population, 32 state_lookup.

## What was different from SQLite

In SQLite, pandas decided the column types. Here I declare them, which caught a
problem straight away: the cleaned CSV writes whole numbers as `3.0`, and Postgres
will not copy `"3.0"` into an integer column. I load it as `numeric` and narrow it
to `integer` afterwards.

That narrowing matters more than it looks. With `incidents` as an integer,
`SUM(incidents)` returns `bigint`, and multiplying by `100000.0` gives `numeric`,
so `ROUND(value, 1)` works. Loaded as a float instead, every `ROUND` in
`sql/queries.sql` fails. Postgres has no `ROUND(double precision, integer)`.
SQLite never complained because it does not check types this way.

Foreign keys are enforced now, so a bad state code is rejected at load time. I also
added indexes on the columns the queries filter and join by. The data is small
enough that SQLite did not need them.

## Checking the numbers

I ran all nine queries in `sql/queries.sql` against both databases and compared the
results row by row. All nine return the same values.

Query 9 returns its rows in a different order on each database. The values are the
same. `ORDER BY pop_growth_pct DESC` has no tie-breaker, and Chihuahua and Puebla
both grew 11.6%, so nothing decides which comes first. Adding `, s.state_name` to
the ORDER BY fixes it.
