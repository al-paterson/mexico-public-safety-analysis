import pandas as pd
import os

os.makedirs("data/cleaned", exist_ok=True)

df_hist = pd.read_csv(
    "data/raw/Estatal-Delitos-2015-2025_feb2026.csv",
    encoding="latin-1"
)
df_2026 = pd.read_csv(
    "data/raw/RNID-Delitos_Estatal-2026-feb2026.csv",
    encoding="latin-1"
)

df = pd.concat([df_hist, df_2026], ignore_index=True)

df.columns = [
    'year', 'state_code', 'state', 'legal_category',
    'crime_type', 'crime_subtype', 'modality',
    'jan', 'feb', 'mar', 'apr', 'may', 'jun',
    'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
]

df_long = df.melt(
    id_vars=['year', 'state_code', 'state', 'legal_category',
             'crime_type', 'crime_subtype', 'modality'],
    value_vars=['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                'jul', 'aug', 'sep', 'oct', 'nov', 'dec'],
    var_name='month',
    value_name='incidents'
)

df_long = df_long.dropna(subset=['incidents'])

month_map = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}
df_long['month'] = df_long['month'].map(month_map)

df_long.to_csv("data/cleaned/incidents_long.csv", index=False)
print(f"Cleaned data saved: {len(df_long):,} rows")
