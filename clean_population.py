import pandas as pd
import unicodedata
import os

# CONAPO mid-year population, one row per year x state x age x sex, 1950-2070
RAW_POP = "data/raw/conapo/ConDem50a19_ProyPob20a70/0_Pob_Mitad_1950_2070.xlsx"
CLEANED_OUT = "data/cleaned/population.csv"

YEAR_MIN, YEAR_MAX = 2015, 2026

os.makedirs("data/cleaned", exist_ok=True)

print("Reading CONAPO population file (large, takes a minute)...")
df = pd.read_excel(RAW_POP)


def strip_accents(text):
    return "".join(
        c for c in unicodedata.normalize("NFKD", str(text))
        if not unicodedata.combining(c)
    )


# AÑO -> ANO, so the column names are safe to reference
df.columns = [strip_accents(c).upper().strip() for c in df.columns]

df = df[(df["ANO"] >= YEAR_MIN) & (df["ANO"] <= YEAR_MAX)]

# CVE_GEO 0 is the national total. I drop it and sum the states instead,
# so there is only one source of truth in the table.
df = df[df["CVE_GEO"].between(1, 32)]

# collapse age and sex down to one row per state per year
population = (
    df.groupby(["ANO", "CVE_GEO"], as_index=False)["POBLACION"]
    .sum()
)

population.columns = ["year", "state_code", "population"]

expected = 32 * (YEAR_MAX - YEAR_MIN + 1)
assert len(population) == expected, f"expected {expected} rows, got {len(population)}"

population.to_csv(CLEANED_OUT, index=False)
print(f"Cleaned population saved: {len(population)} rows -> {CLEANED_OUT}")
