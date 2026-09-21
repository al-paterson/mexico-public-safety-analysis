# Mexico Public Safety Analysis: Querétaro in National Context

Analysis of reported crime incidents across Mexico's 32 states from 2015 to 2025, using official federal data from the Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública (SESNSP), with population denominators from CONAPO.

Querétaro, my home state, has gone through unusually fast population and industrial growth over the past decade. I wanted to know whether crime kept pace with that growth, and how the state really compares to the rest of the country once you control for population size.

The answer surprised me, and it reversed my own first conclusion.

---

## Key Findings

- **My first version of this analysis got the headline wrong.** Comparing raw incident counts, Querétaro sits comfortably below the "average state" every year. But that comparison flatters small states. Measured per 100,000 inhabitants, **Querétaro has been above the national rate every single year since 2015**, on average 44% higher, and ranked **#9 of 32 states in 2025**.

  ![Querétaro vs national rate per 100k](output/charts/chart4_vs_national_rate.png)

- Raw incidents grew **+72.3%** (32,817 → 56,559) between 2015 and 2025, but the population grew **+26%** over the same window. The per-capita increase is **+36.8%** (1,558 → 2,131 per 100k). Roughly half the headline growth was just more people.
- **Most of that per-capita rise is one step in 2016.** Monthly reports went from about 2,800 (January to May 2016) to about 4,100 (June to December) and stayed there. A jump that sudden may be a change in how crimes were recorded rather than a crime wave; I can't tell which from this data. From 2017 to 2025 the rate fell 10.8%.
- **Fast growth did not go with rising rates.** Among the five fastest-growing states, three (Baja California, Baja California Sur, Nuevo León) had lower reported rates in 2025 than in 2015. Querétaro (+37%) and Quintana Roo (+27%) did not. Five states is a small sample, so this is a pattern, not proof.

  ![Population growth vs change in crime rate, 2015–2025](output/charts/chart7_growth_vs_crime.png)

- **Robo (theft)** is Querétaro's largest category: 252,721 reports from 2015 to 2025, more than the next four categories combined.
- Seasonality is mild: counted per day, October is highest and January lowest, about a 12% gap. The busiest month changes from year to year.
- Gender-based violence shows the largest proportional increase of any category (2015 vs 2024). The 2015 baseline was tiny, so this mostly reflects changes in legal classification and reporting practice. The trend is real and worth flagging, but the raw percentage by itself is misleading.
- The per-capita rate has **declined since 2023** even as the population keeps growing. That is the most positive trend in the data.

---

## Interactive Dashboard (Power BI)

A two-page dashboard that turns the analysis into something you can click through: the national picture first, then any single state against the country. Labels are in Spanish.

### Page 1: National overview (Resumen Nacional)
![Dashboard overview](powerbi/screenshots/page1_overview.png)

- 21.7M reported incidents from 2015 to 2025
- National rate: 1,512 per 100k in 2025, up 11.6% since 2015
- 15 of 32 states above the national average
- January–August 2026 is 1.2% below the same months of 2025

Below the numbers: crime types, a map shaded by rate, and each state's rate against how much it changed. Clicking a state on the map filters the page.

### Page 2: State detail (Detalle por Estado)
![State deep dive](powerbi/screenshots/page2_deep_dive.png)

Pick any state to see its rate against the national line, its crime types, its busiest months, and where it ranks among all 32. For Querétaro, the rate rose 36.8% over the decade against the national 11.6%, though most of that rise is the 2016 step described above.

### How it's built

- Star schema: one fact table (`fact_delitos`) with date, state and crime type dimensions. Population is a separate state × year table with no relationship; the rate measures bring it in with `TREATAS` on the selected states and years.
- Rates are DAX measures, so they follow the year and crime-type slicers. A locked filter keeps every chart on complete years (2015–2025). The partial 2026 data only feeds the year-to-date number.
- SESNSP changed its crime categories in 2026. I mapped the new ones back to the historical categories so 2026 can be compared with 2025. The mapping is done in the DuckDB build (not in this repo) and shows up as the `tipo_delito_hist` column.
- The panel frames and KPI cards are a custom visual. The source is in `custom-visual/`.
- It uses a later SESNSP release (data up to August 2026) than the analysis above, so a few numbers differ slightly.

---

## Questions Explored

1. How have reported crime incidents in Querétaro changed year over year?
2. Once population growth is stripped out, is crime actually rising?
3. Which crime categories drive the totals?
4. Are there seasonal patterns by month?
5. How does Querétaro compare to the national rate, per capita, and where does it rank among all 32 states?
6. Do fast-growing states pay for their growth with more crime per person?

---

## Data Cleaning Notes

The raw files needed real work before they were queryable:

- The SESNSP yearly format is **wide** (one column per month), so I reshaped it into long format (one row per state-category-month-year) to make SQL queries reasonable.
- The 2026 file ships separately from the 2015–2025 historical file; both are concatenated during cleaning, and 2026 (January–February only) is excluded from all trend analysis.
- Spanish column headers were translated and standardized to snake_case during cleaning.
- The CONAPO population file covers 1950–2070 with one row per year × state × single age × sex (~740k rows). I filtered to 2015–2026, summed over age and sex, and normalized accented column names (AÑO → ANO) so the script doesn't depend on encoding behavior.
- CONAPO and SESNSP both use INEGI state codes (1–32), which is what makes the population JOIN reliable. Names like "Ciudad de México" vs "CDMX" never have to match.

---

## Project Structure

```
mexico-public-safety-analysis/
├── data/
│   ├── raw/                  ← original files from datos.gob.mx and CONAPO (untouched)
│   ├── cleaned/              ← reshaped incidents + population tables
│   ├── parquet/              ← the 5 tables the Power BI dashboard loads
│   └── mexico_safety.db      ← SQLite database (incidents, population, state_lookup)
├── sql/
│   └── queries.sql           ← 9 analytical queries with business-question headers
├── postgres/                 ← same data in PostgreSQL: schema, load script, notes
├── powerbi/
│   ├── Mexico Crime Analytics.pbip   ← open this in Power BI Desktop
│   ├── Mexico Crime Analytics.SemanticModel/  ← tables, relationships, DAX measures
│   ├── Mexico Crime Analytics.Report/         ← pages and visuals
│   └── screenshots/          ← both dashboard pages
├── custom-visual/            ← source for the panel and KPI card visual (TypeScript)
├── output/
│   ├── charts/               ← the 2 charts used above (visualizations.py makes all 7)
│   └── report.md             ← the findings write-up; generate_report.py fills in the numbers
├── analysis.py               ← cleans and reshapes the SESNSP crime data
├── clean_population.py       ← cleans the CONAPO population file
├── load_db.py                ← loads cleaned CSVs into SQLite
├── visualizations.py         ← generates all charts
├── generate_report.py        ← builds output/report.md from query results
├── export_powerbi.py         ← exports star schema CSVs (not used by the current dashboard)
└── .gitignore
```

---

## Stack

Python (pandas) for loading and reshaping, SQLite for analytical queries, matplotlib for charts, Power BI for the dashboard. I went with SQLite instead of Postgres because the dataset fits comfortably in a single file and I wanted the repo to be self-contained. Anyone cloning it can run the whole pipeline without setting up a database server.

I later loaded the same data into PostgreSQL to work with a server-based database: declared column types, foreign keys, indexes and query plans. All nine queries return the same values on both. See `postgres/` for the schema and what was different. The Python scripts still use SQLite.

The per-capita queries are three-table JOINs: incidents need the state name from `state_lookup` **and** the matching year's population from `population`, joined on state code and year together.

---

## Data Sources

**Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública (SESNSP)**: [datos.gob.mx](https://datos.gob.mx), *Cifras de incidencia delictiva estatal*.

- `Estatal-Delitos-2015-2025_feb2026.csv`: historical data 2015–2025
- `RNID-Delitos_Estatal-2026-feb2026.csv`: 2026 partial data (Jan–Feb)

The dashboard uses the August 2026 release of the same two files (`…_ago2026.csv`), with 2026 data through August.

**CONAPO**: *Proyecciones de la Población de México 1950–2070*, mid-year population by state, age, and sex.

- `0_Pob_Mitad_1950_2070.xlsx`: estimates reconciled with the censuses up to 2019 (*conciliación demográfica*), projections from 2020

The analysis raw files are kept untouched in `data/raw/`.

---

## Limitations

- SESNSP figures reflect **reported** incidents only. Mexico has well-documented underreporting (the INEGI ENVIPE survey consistently estimates a "cifra negra" above 90% nationally), and reporting propensity varies enormously by state. The bottom of the per-capita ranking (Guerrero, Chiapas) is **not** a list of Mexico's safest states. It partly measures where people don't report. The ranking captures the interaction of crime and reporting behavior, not crime alone.
- Population figures for 2020 onward are CONAPO projections, not census counts. They are the standard denominators used in official rate calculations, but they carry projection uncertainty.
- Reporting standards and legal classifications changed during the analysis window; the gender-based violence category is the clearest example.
- 2025 data may still be revised in later SESNSP publications.
- Oaxaca (+348%) and Colima (+286%) have the biggest rate increases on the dashboard, but they are not real increases. Both states were still setting up how they record crimes in 2015–2017. Oaxaca went from 6,127 reports in 2015 to 31,607 in 2016, and Colima from 6,562 in 2015 to 24,425 in 2017. After that, both change much more slowly.
- Campeche normally has about 2,000 reports a year, but jumped to 25,536 in 2022 and 25,849 in 2023, then fell back to 5,581 by 2025. I haven't found the cause yet.

---

## How to Run

```bash
pip install -r requirements.txt

# 1. Clean and reshape the SESNSP crime data
py analysis.py

# 2. Clean the CONAPO population data (large file, takes a minute)
py clean_population.py

# 3. Load both into SQLite
py load_db.py

# 4. Generate charts
py visualizations.py

# 5. Generate report
py generate_report.py
```

Output appears in `output/charts/` and `output/report.md`.

The dashboard doesn't need these steps. It reads the parquet files in `data/parquet/`, which come from a separate DuckDB build of the same SESNSP and CONAPO data. To open it, open `powerbi/Mexico Crime Analytics.pbip` in Power BI Desktop, go to *Transform data → Edit parameters*, set `DataFolder` to the `data\parquet\` folder of your copy (keep the last backslash), then *Refresh*.

To use the PostgreSQL version instead of SQLite, see [postgres/README.md](postgres/README.md).
It loads the same cleaned CSVs, so run steps 1 and 2 first.
