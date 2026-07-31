# Public Safety Analysis: Querétaro, Mexico
**Data sources:** SESNSP reported incidents; CONAPO mid-year population
**Period:** 2015–2025
**Built by:** generate_report.py, July 04, 2026

---

## Executive Summary

Raw reported incidents in Querétaro grew **72.3%** between 2015 and 2025
(32,817 → 56,559). But the state's population grew **26.0%** over the
same window, so the per-capita picture is very different: incidents per 100,000
inhabitants rose **36.8%** (1,558 → 2,131). Roughly half
of the headline growth was simply more people.

Most of the per-capita rise is one step in 2016: monthly reports went from about
2,800 (January to May) to about 4,100 (June to December) and stayed
there. A jump that sudden may be a change in how crimes were recorded rather than a crime
wave; I can't tell which from this data. From 2017 to 2025 the rate fell **10.8%**.

The more uncomfortable finding: measured per capita, Querétaro has been **above the
national rate every single year**, on average 44.3% higher, and ranked
**#9 of 32 states** in reported incidents per 100k in 2025. An earlier version
of this analysis compared raw counts against a per-state average and concluded the
opposite; normalizing by population reverses the conclusion.

---

## 1. Year-over-Year Trend

| Year | Incidents | Qro per 100k | National per 100k |
|------|----------:|-------------:|------------------:|
| 2015 | 32,817 | 1,557.8 | 1,354.8 |
| 2016 | 42,900 | 1,978.0 | 1,427.5 |
| 2017 | 53,379 | 2,389.8 | 1,554.4 |
| 2018 | 57,809 | 2,514.5 | 1,579.4 |
| 2019 | 60,515 | 2,559.2 | 1,628.1 |
| 2020 | 52,026 | 2,150.0 | 1,436.1 |
| 2021 | 53,944 | 2,190.5 | 1,584.9 |
| 2022 | 58,676 | 2,339.4 | 1,648.2 |
| 2023 | 63,334 | 2,476.0 | 1,657.5 |
| 2024 | 59,371 | 2,277.6 | 1,581.7 |
| 2025 | 56,559 | 2,130.7 | 1,512.1 |

**Key observations:**
- Both raw counts and the per-capita rate peaked around 2019 and again in 2023.
- The 2020 drop (COVID-19 lockdowns) appears in both Querétaro and the national rate.
- The per-capita rate has declined since 2023 while population keeps growing. That is the
  most positive trend in the data.

---

## 2. Crime Type Breakdown

The top five crime categories account for the majority of all reported incidents:

| Crime Type | Total Incidents (2015–2025) |
|------------|----------------------------:|
| Robo | 252,721 |
| Lesiones | 60,764 |
| Otros delitos del Fuero Común | 44,544 |
| Amenazas | 38,363 |
| Violencia familiar | 36,720 |

**Robo** is the single largest category by a wide margin, followed by
**Lesiones**. These two categories together represent the bulk of reported crime
and should be the focus of any targeted intervention analysis.

---

## 3. Seasonal Patterns

| Month | Incidents per Day (2015–2025) |
|-------|------------------------------:|
| January | 137.6 |
| February | 143.6 |
| March | 147.8 |
| April | 144.8 |
| May | 148.8 |
| June | 149.7 |
| July | 149.5 |
| August | 151.0 |
| September | 150.7 |
| October | 153.6 |
| November | 146.7 |
| December | 141.9 |

**October** has the most incidents per day (153.6) and **January** the fewest
(137.6), counted per day because February is shorter than the other months.
The seasonal variation is moderate, a gap of about 11.6% between peak and trough,
suggesting crime in Querétaro is driven more by structural factors than seasonal ones.

---

## 4. Where Querétaro Ranks Nationally (2025, per 100k)

| Rank | State | Incidents per 100k |
|-----:|-------|-------------------:|
| 1 | Colima | 3,495.5 |
| 2 | Baja California Sur | 2,736.6 |
| 3 | Quintana Roo | 2,657.1 |
| 4 | Guanajuato | 2,546.5 |
| 5 | Aguascalientes | 2,536.3 |
| 6 | Ciudad de México | 2,290.8 |
| 7 | Baja California | 2,225.2 |
| 8 | Morelos | 2,210.5 |
| 9 | Querétaro | 2,130.7 | ←
| 10 | Coahuila | 2,033.6 |

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
| Violencia de género en todas sus modalidades distinta a la violencia familiar | 2 | 1,469 | +73,350.0% |
| Extorsión | 6 | 236 | +3,833.3% |
| Acoso sexual | 23 | 761 | +3,208.7% |
| Violación equiparada | 29 | 255 | +779.3% |
| Otros delitos que atentan contra la libertad personal | 33 | 277 | +739.4% |

The steepest rise is in **Violencia de género en todas sus modalidades distinta a la violencia familiar**, up 73,350% from
2 incidents in 2015 to 1,469 in 2024.
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
