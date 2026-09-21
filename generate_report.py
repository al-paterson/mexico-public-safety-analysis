import sqlite3
import pandas as pd
from datetime import date

conn = sqlite3.connect("data/mexico_safety.db")
QRO = "Querétaro"

# yearly totals and rate per 100k for Querétaro
yearly = pd.read_sql("""
    SELECT i.year,
           SUM(i.incidents) AS total_incidents,
           p.population,
           ROUND(SUM(i.incidents) * 100000.0 / p.population, 1) AS rate_per_100k
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    INNER JOIN population p ON i.state_code = p.state_code AND i.year = p.year
    WHERE s.state_name = ? AND i.year <= 2025
    GROUP BY i.year, p.population
    ORDER BY i.year
""", conn, params=[QRO])

# monthly totals for 2016, to show the jump in the middle of the year
months_2016 = pd.read_sql("""
    SELECT i.month, SUM(i.incidents) AS total_incidents
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    WHERE s.state_name = ? AND i.year = 2016
    GROUP BY i.month
""", conn, params=[QRO])

# national rate: all incidents over all people, not an average of the state rates
national = pd.read_sql("""
    SELECT i.year,
           ROUND(SUM(i.incidents) * 100000.0 / MAX(t.national_pop), 1) AS national_rate
    FROM incidents i
    INNER JOIN (
        SELECT year, SUM(population) AS national_pop FROM population GROUP BY year
    ) t ON i.year = t.year
    WHERE i.year <= 2025
    GROUP BY i.year
    ORDER BY i.year
""", conn)

# top crime categories, all years combined
top_crimes = pd.read_sql("""
    SELECT i.crime_type, SUM(i.incidents) AS total_incidents
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    WHERE s.state_name = ? AND i.year <= 2025
    GROUP BY i.crime_type
    ORDER BY total_incidents DESC
    LIMIT 5
""", conn, params=[QRO])

# incidents per day by month, 2015-2025 (per day because February is short)
monthly = pd.read_sql("""
    SELECT i.month,
           SUM(i.incidents) * 1.0 / CASE
               WHEN i.month = 2 THEN 311
               WHEN i.month IN (4, 6, 9, 11) THEN 330
               ELSE 341 END AS per_day
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    WHERE s.state_name = ? AND i.year <= 2025
    GROUP BY i.month
    ORDER BY i.month
""", conn, params=[QRO])

# all 32 states ranked by 2025 rate, used for Querétaro's national rank
ranking = pd.read_sql("""
    SELECT s.state_name,
           ROUND(SUM(i.incidents) * 100000.0 / p.population, 1) AS rate_per_100k
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    INNER JOIN population p ON i.state_code = p.state_code AND i.year = p.year
    WHERE i.year = 2025
    GROUP BY s.state_name, p.population
    ORDER BY rate_per_100k DESC
""", conn)

# fastest rising crime types (nonzero 2015 baseline required for a % change)
rising = pd.read_sql("""
    SELECT
        a.crime_type,
        COALESCE(b.incidents_2015, 0) AS incidents_2015,
        a.incidents_2024,
        ROUND(
            (a.incidents_2024 - COALESCE(b.incidents_2015, 0)) * 100.0
            / NULLIF(COALESCE(b.incidents_2015, 0), 0),
            1
        ) AS pct_change
    FROM (
        SELECT i.crime_type, SUM(i.incidents) AS incidents_2024
        FROM incidents i
        INNER JOIN state_lookup s ON i.state_code = s.state_code
        WHERE s.state_name = ? AND i.year = 2024
        GROUP BY i.crime_type
    ) a
    LEFT JOIN (
        SELECT i.crime_type, SUM(i.incidents) AS incidents_2015
        FROM incidents i
        INNER JOIN state_lookup s ON i.state_code = s.state_code
        WHERE s.state_name = ? AND i.year = 2015
        GROUP BY i.crime_type
    ) b ON a.crime_type = b.crime_type
    WHERE b.incidents_2015 > 0
    ORDER BY pct_change DESC
    LIMIT 5
""", conn, params=[QRO, QRO])

conn.close()

# derived stats

# one row per year with both rates
rates = yearly.merge(national, on="year")

peak_year = yearly.loc[yearly["total_incidents"].idxmax()]

# raw counts: 2015 vs 2025
inc_2015 = int(yearly[yearly["year"] == 2015]["total_incidents"].iloc[0])
inc_2025 = int(yearly[yearly["year"] == 2025]["total_incidents"].iloc[0])
pct_change_raw = round((inc_2025 - inc_2015) / inc_2015 * 100, 1)

# same comparison, per capita
rate_2015 = float(yearly[yearly["year"] == 2015]["rate_per_100k"].iloc[0])
rate_2025 = float(yearly[yearly["year"] == 2025]["rate_per_100k"].iloc[0])
pct_change_rate = round((rate_2025 - rate_2015) / rate_2015 * 100, 1)

# most of that rise is one step in mid-2016, so also measure from 2017
rate_2017 = float(yearly[yearly["year"] == 2017]["rate_per_100k"].iloc[0])
drop_since_2017 = round((rate_2017 - rate_2025) / rate_2017 * 100, 1)
before_step = months_2016[months_2016["month"] <= 5]["total_incidents"].mean()
after_step = months_2016[months_2016["month"] >= 6]["total_incidents"].mean()

# population growth over the same window
pop_2015 = int(yearly[yearly["year"] == 2015]["population"].iloc[0])
pop_2025 = int(yearly[yearly["year"] == 2025]["population"].iloc[0])
pop_growth = round((pop_2025 - pop_2015) / pop_2015 * 100, 1)

# Querétaro's national rank in 2025 (1 = highest rate)
qro_rank = int(ranking.reset_index(drop=True)
               .query("state_name == @QRO").index[0]) + 1

# how far above the national rate Querétaro sits, on average
avg_rate_gap_pct = round(((rates["rate_per_100k"] / rates["national_rate"]) - 1)
                         .mean() * 100, 1)

peak_month_row = monthly.loc[monthly["per_day"].idxmax()]
low_month_row  = monthly.loc[monthly["per_day"].idxmin()]
month_names = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
               7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}

peak_month = month_names[int(peak_month_row["month"])]
low_month  = month_names[int(low_month_row["month"])]

top1 = top_crimes.iloc[0]
top2 = top_crimes.iloc[1]

# build markdown

MONTH_TABLE = "\n".join(
    f"| {month_names[int(r.month)]} | {r.per_day:,.1f} |"
    for _, r in monthly.iterrows()
)

YEARLY_TABLE = "\n".join(
    f"| {int(r.year)} | {int(r.total_incidents):,} | {r.rate_per_100k:,.1f} | {r.national_rate:,.1f} |"
    for _, r in rates.iterrows()
)

RANKING_TABLE = "\n".join(
    f"| {i + 1} | {r.state_name} | {r.rate_per_100k:,.1f} |"
    + (" ←" if r.state_name == QRO else "")
    for i, r in ranking.reset_index(drop=True).iterrows()
    if i < 10 or r.state_name == QRO   # top 10 plus Querétaro's own row
)

report = f"""# Public Safety Analysis: Querétaro, Mexico
**Data sources:** SESNSP reported incidents; CONAPO mid-year population
**Period:** 2015–2025
**Built by:** generate_report.py, {date.today().strftime("%B %d, %Y")}

---

## Executive Summary

Raw reported incidents in Querétaro grew **{pct_change_raw}%** between 2015 and 2025
({inc_2015:,} → {inc_2025:,}). But the state's population grew **{pop_growth}%** over the
same window, so the per-capita picture is very different: incidents per 100,000
inhabitants rose **{pct_change_rate}%** ({rate_2015:,.0f} → {rate_2025:,.0f}). Roughly half
of the headline growth was simply more people.

Most of the per-capita rise is one step in 2016: monthly reports went from about
{round(before_step, -2):,.0f} (January to May) to about {round(after_step, -2):,.0f} (June to December) and stayed
there. A jump that sudden may be a change in how crimes were recorded rather than a crime
wave; I can't tell which from this data. From 2017 to 2025 the rate fell **{drop_since_2017}%**.

The more uncomfortable finding: measured per capita, Querétaro has been **above the
national rate every single year**, on average {avg_rate_gap_pct}% higher, and ranked
**#{qro_rank} of 32 states** in reported incidents per 100k in 2025. An earlier version
of this analysis compared raw counts against a per-state average and concluded the
opposite; normalizing by population reverses the conclusion.

---

## 1. Year-over-Year Trend

| Year | Incidents | Qro per 100k | National per 100k |
|------|----------:|-------------:|------------------:|
{YEARLY_TABLE}

**Key observations:**
- Both raw counts and the per-capita rate peaked around 2019 and again in 2023.
- The 2020 drop (COVID-19 lockdowns) appears in both Querétaro and the national rate.
- The per-capita rate has declined since 2023 while population keeps growing. That is the
  most positive trend in the data.

---

## 2. Crime Type Breakdown

| Crime Type | Total Incidents (2015–2025) |
|------------|----------------------------:|
{"".join(f"| {r.crime_type} | {int(r.total_incidents):,} |{chr(10)}" for _, r in top_crimes.iterrows())}
**{top1["crime_type"]}** is the single largest category by a wide margin, followed by
**{top2["crime_type"]}**. Together they are the bulk of all reported incidents.

---

## 3. Seasonal Patterns

| Month | Incidents per Day (2015–2025) |
|-------|------------------------------:|
{MONTH_TABLE}

**{peak_month}** has the most incidents per day ({peak_month_row["per_day"]:.1f}) and **{low_month}** the fewest
({low_month_row["per_day"]:.1f}), counted per day because February is shorter than the other months.
The seasonal variation is moderate, a gap of about {round((peak_month_row["per_day"] - low_month_row["per_day"]) / low_month_row["per_day"] * 100, 1)}% between peak and trough,
so seasonality is not a major driver here.

---

## 4. Where Querétaro Ranks Nationally (2025, per 100k)

| Rank | State | Incidents per 100k |
|-----:|-------|-------------------:|
{RANKING_TABLE}

Two caveats matter when reading this table. First, these are **reported** incidents:
states at the bottom of the ranking (Guerrero, Chiapas) are not a list of the safest
states in Mexico. Part of what the ranking measures is where people don't report.
Second, a state's rate can jump when it changes how it records crimes, not only when
crime changes. The ranking measures the interaction of crime and reporting behavior,
not crime alone.

---

## 5. Fastest Rising Crime Types (2015 vs 2024)

| Crime Type | 2015 | 2024 | % Change |
|------------|-----:|-----:|---------:|
{"".join(f"| {r['crime_type']} | {int(r['incidents_2015']):,} | {int(r['incidents_2024']):,} | +{float(r['pct_change']):,.1f}% |{chr(10)}" for _, r in rising.iterrows())}
The steepest rise is in **{rising.iloc[0]["crime_type"]}**, up {float(rising.iloc[0]["pct_change"]):,.0f}% from
{int(rising.iloc[0]["incidents_2015"]):,} incidents in 2015 to {int(rising.iloc[0]["incidents_2024"]):,} in 2024.
The 2015 baseline is tiny, so this percentage mostly reflects changes in legal
classification and reporting practice rather than an equivalent rise in actual events.

---

## Methodology

- Crime data downloaded from datos.gob.mx (SESNSP official release, February 2026)
- Population denominators from CONAPO mid-year population (estimates reconciled with the censuses to 2019, projections from 2020)
- Raw CSVs cleaned in Python/pandas: Spanish headers translated, wide format reshaped to long
- Analysis performed via SQLite; per-capita queries JOIN incidents to population on state AND year
- National rate is population-weighted: total national incidents ÷ total national population
- 2026 excluded from trend analysis (partial year: January–February only)
- Charts exported to `output/charts/` via matplotlib

*Source code available in this repository.*
"""

with open("output/report.md", "w", encoding="utf-8") as f:
    f.write(report)

print("Report saved to output/report.md")
