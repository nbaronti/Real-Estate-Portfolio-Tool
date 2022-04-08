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
SELECT * FROM worker_distribution;

-- Create view to store detailed site-level data
CREATE VIEW detailed_site_view AS
SELECT s."Site_ID", s."Site_Name", s."Address", s."City", s."State_Province", s."Market", s."MSA", s."Country", s."Region", 
s."Latitude", s."Longitude", s."Tenure_Type", s."LED", s."Rentable_Square_Feet", s."Usable_Square_Feet", s."Seats", s."PNL_Rent", 
s."PNL_OpEx", s."Cash_Rent", s."Cash_OpEx", a."S1_Action", a."S2_Action", a."S3_Action", a."S4_Action", a."S5_Action", h."Headcount",
h."BU_1_HC", h."BU_2_HC", h."BU_3_HC", h."BU_4_HC", h."BU_5_HC", h."BU_6_HC", h."BU_7_HC", h."BU_8_HC", h."BU_9_HC", h."BU_10_HC"
FROM site as s
INNER JOIN site_actions as a
ON s."Site_ID" = a."Site_ID"
INNER JOIN headcount as h
ON h."Site_ID" = a."Site_ID";

SELECT * FROM detailed_site_view;





