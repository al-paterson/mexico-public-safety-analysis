import pandas as pd
import matplotlib.pyplot as plt

# Load the 2015-2025 historical data
# encoding="latin-1" handles Spanish characters like ñ and accents
df_hist = pd.read_csv(
    "data/raw/Estatal-Delitos-2015-2025_feb2026.csv",
    encoding="latin-1"
)

# Load the 2026 partial data (January-February only)
df_2026 = pd.read_csv(
    "data/raw/RNID-Delitos_Estatal-2026-feb2026.csv",
    encoding="latin-1"
)

# Verify how many rows and columns loaded
print("2015-2025 shape:", df_hist.shape)
print("2026 shape:", df_2026.shape)

# Show the column names to confirm the structure
print("\nColumns:", df_hist.columns.tolist())

# Stack both tables into one — same 19 columns, rows just pile on top
# ignore_index=True resets the row numbers so they run 0, 1, 2... continuously
# instead of 0-34495, then 0-3647 starting over
df = pd.concat([df_hist, df_2026], ignore_index=True)

print("Combined shape:", df.shape)
print("Years in data:", sorted(df['Año'].unique()))


# Rename columns from Spanish to English for analysis
df.columns = [
    'year', 'state_code', 'state', 'legal_category',
    'crime_type', 'crime_subtype', 'modality',
    'jan', 'feb', 'mar', 'apr', 'may', 'jun',
    'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
]

print(df.columns.tolist())

print(df[df['state'] == 'Querétaro'])


# Reshape from wide to long format
# id_vars: columns to keep as-is (the identifiers)
# value_vars: the columns to melt (our 12 month columns)
# var_name: what to call the new "month" column
# value_name: what to call the new "incidents" column
df_long = df.melt(
    id_vars=['year', 'state_code', 'state', 'legal_category', 'crime_type', 'crime_subtype', 'modality'],
    value_vars=['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'],
    var_name='month',
    value_name='incidents'
)

print("Long format shape:", df_long.shape)
print(df_long.head())

# Drop rows ever incidents are NaN
df_long = df_long.dropna(subset=['incidents'])
print("After dropna:", df_long.shape)


# Map month abbreviations to numbers for correct chronological sorting
month_map = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

# .map() replaces each value in the column using the dictionary above
df_long['month'] = df_long['month'].map(month_map)

print(df_long['month'].unique())


# Save cleaned long-format data to CSV
# index=False means don't write the row numbers as a column
df_long.to_csv("data/cleaned/incidents_long.csv", index=False)

print("Saved to data/cleaned/incidents_long.csv")
