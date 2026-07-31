-- Query 1: Total incidents in Querétaro by year
-- Business question: How has reported crime in Querétaro changed year over year?

SELECT
    i.year,
    SUM(i.incidents) AS total_incidents
FROM incidents i
INNER JOIN state_lookup s ON i.state_code = s.state_code
WHERE s.state_name = 'Querétaro'
GROUP BY i.year
ORDER BY i.year;


-- Query 2: Top 10 crime types in Querétaro (2015-2025)
-- Business question: Which crime categories drive the numbers?

SELECT
    i.crime_type,
    SUM(i.incidents) AS total_incidents
FROM incidents i
INNER JOIN state_lookup s ON i.state_code = s.state_code
WHERE s.state_name = 'Querétaro'
  AND i.year <= 2025                -- 2026 is a partial year (Jan-Feb only)
GROUP BY i.crime_type
ORDER BY total_incidents DESC
LIMIT 10;


-- Query 3: Seasonal patterns by month in Querétaro
-- Business question: Which months consistently have the most and least crime?
-- Compared per day, because February is shorter than the other months

SELECT
    i.month,
    SUM(i.incidents) AS total_incidents,
    ROUND(SUM(i.incidents) * 1.0 / CASE
        WHEN i.month = 2 THEN 311                 -- 11 Februaries, 3 of them leap years
        WHEN i.month IN (4, 6, 9, 11) THEN 330
        ELSE 341 END, 1) AS incidents_per_day
FROM incidents i
INNER JOIN state_lookup s ON i.state_code = s.state_code
WHERE s.state_name = 'Querétaro'
  AND i.year <= 2025                -- 2026 is a partial year (Jan-Feb only)
GROUP BY i.month
ORDER BY i.month;


-- Query 4: Querétaro vs national average by year
-- Business question: Is Querétaro above or below the national per-state average, and is that gap growing?

SELECT
    i.year,
    SUM(i.incidents) AS qro_total,
    ROUND(
        (SELECT SUM(incidents) / 32.0 FROM incidents WHERE year = i.year),
        2
    ) AS national_avg_per_state
FROM incidents i
INNER JOIN state_lookup s ON i.state_code = s.state_code
WHERE s.state_name = 'Querétaro'
GROUP BY i.year
ORDER BY i.year;


-- Query 5: Fastest rising crime types in Querétaro (2015 vs 2024)
-- Business question: Which crime categories have grown the most over the decade?
-- Uses INNER JOIN (via the incidents_2015 > 0 filter) because a % change needs a
-- nonzero 2015 baseline. Categories created after 2015 are excluded deliberately,
-- since "up infinity percent from zero" is not a meaningful comparison

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
    WHERE s.state_name = 'Querétaro' AND i.year = 2024
    GROUP BY i.crime_type
) a
LEFT JOIN (
    SELECT i.crime_type, SUM(i.incidents) AS incidents_2015
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    WHERE s.state_name = 'Querétaro' AND i.year = 2015
    GROUP BY i.crime_type
) b ON a.crime_type = b.crime_type
WHERE b.incidents_2015 > 0
ORDER BY pct_change DESC
LIMIT 10;


-- Query 6: Querétaro incidents per 100,000 inhabitants by year
-- Business question: Once population growth is stripped out, is crime actually rising?
-- Three-table JOIN: incidents need the state name (state_lookup) AND the matching
-- year's population (population). The rate is meaningless without both

SELECT
    i.year,
    SUM(i.incidents) AS total_incidents,
    p.population,
    ROUND(SUM(i.incidents) * 100000.0 / p.population, 1) AS rate_per_100k
FROM incidents i
INNER JOIN state_lookup s ON i.state_code = s.state_code
INNER JOIN population p ON i.state_code = p.state_code AND i.year = p.year  -- match state AND year
WHERE s.state_name = 'Querétaro'
  AND i.year <= 2025                -- 2026 is a partial year (Jan-Feb only)
GROUP BY i.year, p.population
ORDER BY i.year;


-- Query 7: Querétaro rate vs the true national rate, by year
-- Business question: Is Querétaro safer than the country as a whole, per capita?
-- The national rate here is population-weighted (all incidents / all people),
-- which fixes the earlier unweighted "average per state" comparison that
-- treated Colima (700k people) the same as Estado de México (17M)

SELECT
    q.year,
    q.rate_per_100k AS qro_rate,
    n.rate_per_100k AS national_rate
FROM (
    -- Querétaro's yearly rate
    SELECT i.year, ROUND(SUM(i.incidents) * 100000.0 / p.population, 1) AS rate_per_100k
    FROM incidents i
    INNER JOIN population p ON i.state_code = p.state_code AND i.year = p.year
    WHERE i.state_code = 22 AND i.year <= 2025
    GROUP BY i.year, p.population
) q
INNER JOIN (
    -- national yearly rate: total incidents over total population
    SELECT i.year, ROUND(SUM(i.incidents) * 100000.0 / MAX(t.national_pop), 1) AS rate_per_100k
    FROM incidents i
    INNER JOIN (
        SELECT year, SUM(population) AS national_pop
        FROM population
        GROUP BY year
    ) t ON i.year = t.year
    WHERE i.year <= 2025
    GROUP BY i.year
) n ON q.year = n.year
ORDER BY q.year;


-- Query 8: All 32 states ranked by incidents per 100,000 inhabitants (2025)
-- Business question: Where does Querétaro actually rank once state size is controlled for?

SELECT
    s.state_name,
    SUM(i.incidents) AS total_incidents,
    p.population,
    ROUND(SUM(i.incidents) * 100000.0 / p.population, 1) AS rate_per_100k
FROM incidents i
INNER JOIN state_lookup s ON i.state_code = s.state_code
INNER JOIN population p ON i.state_code = p.state_code AND i.year = p.year
WHERE i.year = 2025                 -- latest complete year
GROUP BY s.state_name, p.population
ORDER BY rate_per_100k DESC;


-- Query 9: Population growth vs change in crime rate, per state (2015 -> 2025)
-- Business question: Do fast-growing states pay for their growth with more crime per person?
-- Two subqueries build each state's 2015 and 2025 snapshots (incidents + population),
-- INNER JOINed on state_code because every state exists in both years

SELECT
    s.state_name,
    ROUND((b.population - a.population) * 100.0 / a.population, 1) AS pop_growth_pct,
    ROUND(a.rate_per_100k, 1) AS rate_2015,
    ROUND(b.rate_per_100k, 1) AS rate_2025,
    ROUND((b.rate_per_100k - a.rate_per_100k) * 100.0 / a.rate_per_100k, 1) AS rate_change_pct
FROM (
    -- 2015 snapshot: incidents, population, and rate per state
    SELECT i.state_code, p.population,
           SUM(i.incidents) * 100000.0 / p.population AS rate_per_100k
    FROM incidents i
    INNER JOIN population p ON i.state_code = p.state_code AND i.year = p.year
    WHERE i.year = 2015
    GROUP BY i.state_code, p.population
) a
INNER JOIN (
    -- 2025 snapshot: same shape as the 2015 subquery
    SELECT i.state_code, p.population,
           SUM(i.incidents) * 100000.0 / p.population AS rate_per_100k
    FROM incidents i
    INNER JOIN population p ON i.state_code = p.state_code AND i.year = p.year
    WHERE i.year = 2025
    GROUP BY i.state_code, p.population
) b ON a.state_code = b.state_code
INNER JOIN state_lookup s ON a.state_code = s.state_code
ORDER BY pop_growth_pct DESC;
