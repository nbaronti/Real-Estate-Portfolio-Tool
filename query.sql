-- Select all data from each table in the database
SELECT * FROM scenario;
SELECT * FROM site;
SELECT * FROM site_actions;
SELECT * FROM headcount;
SELECT * FROM market_costs;
SELECT * FROM sharing;
SELECT * FROM business_unit;
SELECT * FROM enterprise_distribution;
SELECT * FROM bu_distribution;
SELECT * FROM worker_distribution

-- Query to join site-level data
SELECT *
FROM site as s
INNER JOIN site_actions as a
ON s."Site_ID" = a."Site_ID"
INNER JOIN headcount as h
ON h."Site_ID" = a."Site_ID";






