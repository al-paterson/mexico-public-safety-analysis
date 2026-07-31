import sqlite3
import pandas as pd
import os

# one fact table plus small lookup tables, so a slicer in Power BI
# filters everything through the relationships
OUT_DIR = "powerbi/data"
os.makedirs(OUT_DIR, exist_ok=True)

conn = sqlite3.connect("data/mexico_safety.db")

# 2026 is only January and February, so it would distort every year-level chart
fact = pd.read_sql("""
    SELECT year, month, state_code, crime_type, SUM(incidents) AS incidents
    FROM incidents
    WHERE year <= 2025
    GROUP BY year, month, state_code, crime_type
""", conn)
fact.to_csv(f"{OUT_DIR}/fact_incidents.csv", index=False)
print(f"fact_incidents.csv: {len(fact):,} rows")

# country column so the map puts Querétaro in Mexico, not Spain
dim_state = pd.read_sql("SELECT * FROM state_lookup", conn)
dim_state["country"] = "Mexico"
dim_state.to_csv(f"{OUT_DIR}/dim_state.csv", index=False)
print(f"dim_state.csv: {len(dim_state)} rows")

population = pd.read_sql("""
    SELECT state_code, year, population
    FROM population
    WHERE year <= 2025
""", conn)
population.to_csv(f"{OUT_DIR}/population.csv", index=False)
print(f"population.csv: {len(population)} rows")

# separate year table so one slicer filters incidents and population together
years = pd.DataFrame({"year": sorted(fact["year"].unique())})
years.to_csv(f"{OUT_DIR}/dim_year.csv", index=False)
print(f"dim_year.csv: {len(years)} rows")

conn.close()
print("Power BI exports ready in powerbi/data/")
