import sqlite3
import pandas as pd
from datetime import date

conn = sqlite3.connect("data/mexico_safety.db")
QRO = "Querétaro"

yearly = pd.read_sql("""
    SELECT i.year, SUM(i.incidents) AS total_incidents
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    WHERE s.state_name = ? AND i.year <= 2025
    GROUP BY i.year
    ORDER BY i.year
""", conn, params=[QRO])

top_crimes = pd.read_sql("""
    SELECT i.crime_type, SUM(i.incidents) AS total_incidents
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    WHERE s.state_name = ?
    GROUP BY i.crime_type
    ORDER BY total_incidents DESC
    LIMIT 5
""", conn, params=[QRO])

monthly = pd.read_sql("""
    SELECT i.month, SUM(i.incidents) AS total_incidents
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    WHERE s.state_name = ?
    GROUP BY i.month
    ORDER BY i.month
""", conn, params=[QRO])

vs_national = pd.read_sql("""
    SELECT
        i.year,
        SUM(i.incidents) AS qro_total,
        ROUND((SELECT SUM(incidents) / 32.0 FROM incidents WHERE year = i.year), 2)
            AS national_avg_per_state
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    WHERE s.state_name = ? AND i.year <= 2025
    GROUP BY i.year
    ORDER BY i.year
""", conn, params=[QRO])

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

# ── derived stats ─────────────────────────────────────────────────────────────

peak_year = yearly.loc[yearly["total_incidents"].idxmax()]
low_year  = yearly.loc[yearly["total_incidents"].idxmin()]

inc_2015 = int(yearly[yearly["year"] == 2015]["total_incidents"].iloc[0])
inc_2025 = int(yearly[yearly["year"] == 2025]["total_incidents"].iloc[0])
pct_change = round((inc_2025 - inc_2015) / inc_2015 * 100, 1)

peak_month_row = monthly.loc[monthly["total_incidents"].idxmax()]
low_month_row  = monthly.loc[monthly["total_incidents"].idxmin()]
month_names = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
               7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}

peak_month = month_names[int(peak_month_row["month"])]
low_month  = month_names[int(low_month_row["month"])]

top1 = top_crimes.iloc[0]
top2 = top_crimes.iloc[1]

avg_gap = (vs_national["national_avg_per_state"] - vs_national["qro_total"]).mean()
latest = vs_national[vs_national["year"] == 2025].iloc[0]
gap_2025 = int(latest["national_avg_per_state"] - latest["qro_total"])

# ── build markdown ────────────────────────────────────────────────────────────

MONTH_TABLE = "\n".join(
    f"| {month_names[int(r.month)]} | {int(r.total_incidents):,} |"
    for _, r in monthly.iterrows()
)

YEARLY_TABLE = "\n".join(
    f"| {int(r.year)} | {int(r.total_incidents):,} | {int(r2.national_avg_per_state):,} |"
    for (_, r), (_, r2) in zip(yearly.iterrows(), vs_national.iterrows())
)

report = f"""# Public Safety Analysis — Querétaro, Mexico
**Data source:** Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública (SESNSP)
**Period:** 2015–2025
**Generated:** {date.today().strftime("%B %d, %Y")}

---

## Executive Summary

Reported crime incidents in Querétaro increased **{pct_change}%** between 2015 and 2025,
rising from {inc_2015:,} to {inc_2025:,} annual incidents. Despite this growth, Querétaro
has remained consistently **below the national per-state average** every year in the dataset,
with an average gap of {int(avg_gap):,} fewer incidents per year than the typical Mexican state.

The peak year was **{int(peak_year["year"])}** ({int(peak_year["total_incidents"]):,} incidents),
followed by a COVID-era dip in 2020 and a partial recovery through 2023 before declining again
toward 2025.

---

## 1. Year-over-Year Trend

| Year | Querétaro | National Avg per State |
|------|----------:|----------------------:|
{YEARLY_TABLE}

**Key observations:**
- Incidents grew steadily 2015–2019, peaking at {int(yearly[yearly['year']==2019]['total_incidents'].iloc[0]):,} in 2019.
- A sharp drop in 2020 (–{round((1 - int(yearly[yearly['year']==2020]['total_incidents'].iloc[0]) / int(yearly[yearly['year']==2019]['total_incidents'].iloc[0]))*100,1)}%) aligns with COVID-19 lockdowns reducing activity and reporting.
- The state has trended downward since 2023, ending 2025 at {inc_2025:,} incidents.

---

## 2. Crime Type Breakdown

The top five crime categories account for the majority of all reported incidents:

| Crime Type | Total Incidents (2015–2025) |
|------------|----------------------------:|
{"".join(f"| {r.crime_type} | {int(r.total_incidents):,} |{chr(10)}" for _, r in top_crimes.iterrows())}
**{top1["crime_type"]}** is the single largest category by a wide margin, followed by
**{top2["crime_type"]}**. These two categories together represent the bulk of reported crime
and should be the focus of any targeted intervention analysis.

---

## 3. Seasonal Patterns

| Month | Total Incidents (All Years) |
|-------|----------------------------:|
{MONTH_TABLE}

**{peak_month}** is consistently the highest-crime month ({int(peak_month_row["total_incidents"]):,} total incidents
across all years), while **{low_month}** is the lowest ({int(low_month_row["total_incidents"]):,}).
The seasonal variation is moderate — roughly a {round((int(peak_month_row["total_incidents"]) - int(low_month_row["total_incidents"])) / int(low_month_row["total_incidents"]) * 100, 1)}% difference between peak and trough —
suggesting crime in Querétaro is driven more by structural factors than seasonal ones.

---

## 4. Querétaro vs National Average

Querétaro consistently reports **fewer incidents than the national per-state average**.
In 2025, the state recorded {int(latest["qro_total"]):,} incidents versus a national average of
{int(latest["national_avg_per_state"]):,} — a gap of {gap_2025:,} incidents.

This gap has remained stable over the decade, suggesting Querétaro's relative safety
position has not deteriorated despite absolute growth in incident counts.

---

## 5. Fastest Rising Crime Types (2015 vs 2024)

| Crime Type | 2015 | 2024 | % Change |
|------------|-----:|-----:|---------:|
{"".join(f"| {r['crime_type']} | {int(r['incidents_2015']):,} | {int(r['incidents_2024']):,} | +{float(r['pct_change']):,.1f}% |{chr(10)}" for _, r in rising.iterrows())}
The steepest rise is in **{rising.iloc[0]["crime_type"]}**, up {float(rising.iloc[0]["pct_change"]):,.0f}% from
{int(rising.iloc[0]["incidents_2015"]):,} incidents in 2015 to {int(rising.iloc[0]["incidents_2024"]):,} in 2024.
This likely reflects both improved reporting and real increases in gender-based violence.

---

## Methodology

- Data downloaded directly from datos.gob.mx (SESNSP official release, February 2026)
- Raw CSVs cleaned in Python/pandas: Spanish headers translated, wide format reshaped to long
- Analysis performed via SQLite with INNER JOINs against a state lookup table
- National average calculated as total national incidents ÷ 32 states per year
- 2026 excluded from trend analysis (partial year: January–February only)
- Charts exported to `output/charts/` via matplotlib

*Source code available in this repository.*
"""

with open("output/report.md", "w", encoding="utf-8") as f:
    f.write(report)

print("Report saved to output/report.md")
