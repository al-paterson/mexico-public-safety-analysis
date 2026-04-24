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
