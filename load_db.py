import pandas as pd
import sqlite3

# Connect to SQLite — creates the file if it doesn't exist
conn = sqlite3.connect("data/mexico_safety.db")

# Load the cleaned CSV
df = pd.read_csv("data/cleaned/incidents_long.csv")

# Write it to SQLite as a table called "incidents"
# if_exists="replace" means overwrite the table if it already exists
df.to_sql("incidents", conn, if_exists="replace", index=False)

print("Rows loaded:", conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0])


# Create a state lookup table with region groupings
state_lookup = pd.DataFrame([
    (1, 'Aguascalientes', 'North'), (2, 'Baja California', 'North'),
    (3, 'Baja California Sur', 'North'), (4, 'Campeche', 'South'),
    (5, 'Coahuila', 'North'), (6, 'Colima', 'West'),
    (7, 'Chiapas', 'South'), (8, 'Chihuahua', 'North'),
    (9, 'Ciudad de México', 'Central'), (10, 'Durango', 'North'),
    (11, 'Guanajuato', 'Central'), (12, 'Guerrero', 'South'),
    (13, 'Hidalgo', 'Central'), (14, 'Jalisco', 'West'),
    (15, 'Estado de México', 'Central'), (16, 'Michoacán', 'West'),
    (17, 'Morelos', 'Central'), (18, 'Nayarit', 'West'),
    (19, 'Nuevo León', 'North'), (20, 'Oaxaca', 'South'),
    (21, 'Puebla', 'Central'), (22, 'Querétaro', 'Central'),
    (23, 'Quintana Roo', 'South'), (24, 'San Luis Potosí', 'Central'),
    (25, 'Sinaloa', 'North'), (26, 'Sonora', 'North'),
    (27, 'Tabasco', 'South'), (28, 'Tamaulipas', 'North'),
    (29, 'Tlaxcala', 'Central'), (30, 'Veracruz', 'South'),
    (31, 'Yucatán', 'South'), (32, 'Zacatecas', 'North'),
], columns=['state_code', 'state_name', 'region'])

state_lookup.to_sql("state_lookup", conn, if_exists="replace", index=False)
print("State lookup rows:", conn.execute("SELECT COUNT(*) FROM state_lookup").fetchone()[0])


conn.close()

conn = sqlite3.connect("data/mexico_safety.db")

result1 = pd.read_sql("""
    SELECT i.year, SUM(i.incidents) AS total_incidents
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    WHERE s.state_name = 'Querétaro'
    GROUP BY i.year
    ORDER BY i.year
""", conn)
print("Query 1 - Incidents by year:")
print(result1)

result2 = pd.read_sql("""
    SELECT i.crime_type, SUM(i.incidents) AS total_incidents
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    WHERE s.state_name = 'Querétaro'
    GROUP BY i.crime_type
    ORDER BY total_incidents DESC
    LIMIT 10
""", conn)
print("\nQuery 2 - Top crime types:")
print(result2)

conn.close()

