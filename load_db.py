import pandas as pd
import sqlite3

conn = sqlite3.connect("data/mexico_safety.db")

df = pd.read_csv("data/cleaned/incidents_long.csv")
df.to_sql("incidents", conn, if_exists="replace", index=False)

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

conn.close()
print("Database loaded.")
