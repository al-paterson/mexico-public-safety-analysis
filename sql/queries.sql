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



SELECT 
    i.crime_type,
    SUM(i.incidents) as total_incidents
 FROM incidents i
 INNER JOIN state_lookup s ON i.state_code = s.state_code
 WHERE s.state_name = 'Querétaro'
 GROUP BY i.crime_type
 ORDER BY total_incidents DESC
 LIMIT 10