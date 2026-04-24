# Mexico Public Safety Analysis — Querétaro

Analysis of reported crime incidents in Querétaro, Mexico from 2015 to 2025 using official federal data from the Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública (SESNSP).

---

## Business Questions

1. How have reported crime incidents in Querétaro changed year over year?
2. Which crime categories drive the numbers?
3. Are there seasonal patterns by month?
4. How does Querétaro compare to the national per-state average?

---

## Key Findings

- Incidents **grew 72.3%** from 2015 (32,817) to a peak of 63,334 in 2023, then declined to 56,559 by 2025
- **Robo (theft)** is the dominant crime type, accounting for 255,622 incidents over the decade
- **October** is the highest-crime month; **April** is the lowest — a moderate 9.6% seasonal gap
- Querétaro has remained **below the national per-state average every year**, averaging ~8,000 fewer incidents annually

---

## Project Structure

```
mexico-public-safety-analysis/
├── data/
│   ├── raw/                  ← original CSVs from datos.gob.mx (untouched)
│   ├── cleaned/              ← reshaped long-format CSV
│   └── mexico_safety.db      ← SQLite database
├── sql/
│   └── queries.sql           ← 4 analytical queries with comments
├── output/
│   ├── charts/               ← 4 exported PNG charts
│   └── report.md             ← generated markdown report
├── analysis.py               ← data loading and cleaning
├── load_db.py                ← loads cleaned CSV into SQLite
├── visualizations.py         ← generates all 4 charts
├── generate_report.py        ← builds output/report.md from query results
└── .gitignore
```

---

## Stack

| Tool | Purpose |
|------|---------|
| Python + pandas | Data loading, cleaning, reshaping |
| SQLite | Analytical queries with JOINs |
| matplotlib | Chart generation |

---

## Data Source

**Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública**
[datos.gob.mx](https://datos.gob.mx) — Cifras de incidencia delictiva estatal

- `Estatal-Delitos-2015-2025_feb2026.csv` — historical data 2015–2025
- `RNID-Delitos_Estatal-2026-feb2026.csv` — 2026 partial data (Jan–Feb)

Both files are kept untouched in `data/raw/`.

---

## How to Run

```bash
# 1. Clean and reshape raw data
py analysis.py

# 2. Load into SQLite
py load_db.py

# 3. Generate charts
py visualizations.py

# 4. Generate report
py generate_report.py
```

Output will appear in `output/charts/` and `output/report.md`.

---

## Charts

| File | Description |
|------|-------------|
| `chart1_yearly_trend.png` | Querétaro incidents by year (2015–2025) |
| `chart2_top_crimes.png` | Top 10 crime types, all years combined |
| `chart3_seasonal.png` | Incidents by month — seasonal pattern |
| `chart4_vs_national.png` | Querétaro vs national per-state average |
