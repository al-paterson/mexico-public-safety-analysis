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


-- Query 2: Top 10 crime types in Querétaro (all years combined)
-- Business question: Which crime categories drive the numbers?

SELECT
    i.crime_type,
    SUM(i.incidents) AS total_incidents
FROM incidents i
INNER JOIN state_lookup s ON i.state_code = s.state_code
WHERE s.state_name = 'Querétaro'
GROUP BY i.crime_type
ORDER BY total_incidents DESC
LIMIT 10;


-- Query 3: Seasonal patterns by month in Querétaro
-- Business question: Which months consistently have the most and least crime?

SELECT
    i.month,
    SUM(i.incidents) AS total_incidents
FROM incidents i
INNER JOIN state_lookup s ON i.state_code = s.state_code
WHERE s.state_name = 'Querétaro'
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
-- Uses LEFT JOIN so types that appeared after 2015 still surface (with 0 as baseline)

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
