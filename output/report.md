# Public Safety Analysis — Querétaro, Mexico
**Data source:** Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública (SESNSP)
**Period:** 2015–2025
**Generated:** April 24, 2026

---

## Executive Summary

Reported crime incidents in Querétaro increased **72.3%** between 2015 and 2025,
rising from 32,817 to 56,559 annual incidents. Despite this growth, Querétaro
has remained consistently **below the national per-state average** every year in the dataset,
with an average gap of 7,982 fewer incidents per year than the typical Mexican state.

The peak year was **2023** (63,334 incidents),
followed by a COVID-era dip in 2020 and a partial recovery through 2023 before declining again
toward 2025.

---

## 1. Year-over-Year Trend

| Year | Querétaro | National Avg per State |
|------|----------:|----------------------:|
| 2015 | 32,817 | 51,806 |
| 2016 | 42,900 | 55,130 |
| 2017 | 53,379 | 60,609 |
| 2018 | 57,809 | 62,185 |
| 2019 | 60,515 | 64,724 |
| 2020 | 52,026 | 57,537 |
| 2021 | 53,944 | 63,882 |
| 2022 | 58,676 | 66,937 |
| 2023 | 63,334 | 67,922 |
| 2024 | 59,371 | 65,380 |
| 2025 | 56,559 | 63,020 |

**Key observations:**
- Incidents grew steadily 2015–2019, peaking at 60,515 in 2019.
- A sharp drop in 2020 (–14.0%) aligns with COVID-19 lockdowns reducing activity and reporting.
- The state has trended downward since 2023, ending 2025 at 56,559 incidents.

---

## 2. Crime Type Breakdown

The top five crime categories account for the majority of all reported incidents:

| Crime Type | Total Incidents (2015–2025) |
|------------|----------------------------:|
| Robo | 255,622 |
| Lesiones | 61,576 |
| Otros delitos del Fuero Común | 45,525 |
| Amenazas | 38,962 |
| Violencia familiar | 37,419 |

**Robo** is the single largest category by a wide margin, followed by
**Lesiones**. These two categories together represent the bulk of reported crime
and should be the focus of any targeted intervention analysis.

---

## 3. Seasonal Patterns

| Month | Total Incidents (All Years) |
|-------|----------------------------:|
| January | 51,588 |
| February | 49,128 |
| March | 50,410 |
| April | 47,777 |
| May | 50,743 |
| June | 49,407 |
| July | 50,975 |
| August | 51,501 |
| September | 49,733 |
| October | 52,380 |
| November | 48,414 |
| December | 48,390 |

**October** is consistently the highest-crime month (52,380 total incidents
across all years), while **April** is the lowest (47,777).
The seasonal variation is moderate — roughly a 9.6% difference between peak and trough —
suggesting crime in Querétaro is driven more by structural factors than seasonal ones.

---

## 4. Querétaro vs National Average

Querétaro consistently reports **fewer incidents than the national per-state average**.
In 2025, the state recorded 56,559 incidents versus a national average of
63,020 — a gap of 6,461 incidents.

This gap has remained stable over the decade, suggesting Querétaro's relative safety
position has not deteriorated despite absolute growth in incident counts.

---

## Methodology

- Data downloaded directly from datos.gob.mx (SESNSP official release, February 2026)
- Raw CSVs cleaned in Python/pandas: Spanish headers translated, wide format reshaped to long
- Analysis performed via SQLite with INNER JOINs against a state lookup table
- National average calculated as total national incidents ÷ 32 states per year
- 2026 excluded from trend analysis (partial year: January–February only)
- Charts exported to `output/charts/` via matplotlib

*Source code available in this repository.*
