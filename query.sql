-- Select all data from each table in the database
SELECT * FROM site;
SELECT * FROM site_actions;
SELECT * FROM scenario;
SELECT * FROM headcount;
SELECT * FROM market_costs;
SELECT * FROM sharing;
SELECT * FROM business_unit;
SELECT * FROM enterprise_distribution;
SELECT * FROM bu_distribution;
SELECT * FROM worker_distribution;

-- Create view to store detailed site-level data
CREATE VIEW detailed_site_view AS
SELECT s."Site_ID", s."Site_Name", s."Address", s."City", s."State_Province", s."Market", s."MSA", s."Country", s."Region", 
s."Latitude", s."Longitude", s."Tenure_Type", s."LED", s."Rentable_Square_Feet", s."Usable_Square_Feet", s."Seats", s."PNL_Rent", 
s."PNL_OpEx", s."Cash_Rent", s."Cash_OpEx", SUM(h."Headcount") AS "Headcount"
FROM site as s
INNER JOIN headcount as h
ON h."Site_ID" = s."Site_ID"
GROUP BY s."Site_ID";

SELECT * FROM detailed_site_view;

-- Create view to aggregate worker distribution detail for enterprise calculation
DROP VIEW IF EXISTS enterprise_workplace_calculations;

CREATE VIEW enterprise_workplace_calculations AS
SELECT sa."Scenario_ID", sa."Site_ID", sa."Site_Action",
	   ed."Work_Profile_ID", sh."Work_Profile_Description", 
	   sh."Sharing_Ratio", sh."Seat_Buffer", 
	   ed."Profile_Distribution", dsv."Headcount"
FROM scenario as s
INNER JOIN site_actions as sa
ON sa."Scenario_ID" = s."Scenario_ID"
INNER JOIN enterprise_distribution as ed
ON ed."Scenario_ID" = sa."Scenario_ID"
INNER JOIN detailed_site_view as dsv
ON dsv."Site_ID" = sa."Site_ID"
INNER JOIN sharing as sh
ON sh."Work_Profile_ID" = ed."Work_Profile_ID";

SELECT * FROM enterprise_workplace_calculations;


