-- Drop table if exists (once python scripts loads)
DROP VIEW IF EXISTS detailed_site_view;
DROP TABLE IF EXISTS bu_distribution;
DROP TABLE IF EXISTS scenario;
DROP TABLE IF EXISTS worker_distribution;
DROP TABLE IF EXISTS business_unit;
DROP TABLE IF EXISTS enterprise_distribution;
DROP TABLE IF EXISTS sharing;
DROP TABLE IF EXISTS headcount;
DROP TABLE IF EXISTS site_actions;
DROP TABLE IF EXISTS site;
DROP TABLE IF EXISTS market_costs;

-- Create new tables to import csv data
CREATE TABLE scenario (
  "Scenario_ID" VARCHAR PRIMARY KEY,
  "Scenario_Description" VARCHAR,
  "Calculation_Type" VARCHAR
);

CREATE TABLE market_costs (
  "Market" VARCHAR PRIMARY KEY,
  "MSA" VARCHAR,
  "Market_Asking_Rent" FLOAT,
  "Light_Renovation" FLOAT,
  "Moderate_Renovation" FLOAT,
  "Heavy_Renovation" FLOAT
);

CREATE TABLE site (
  "Site_ID" VARCHAR PRIMARY KEY,
  "Site_Name" VARCHAR,
  "Address" VARCHAR,
  "City" VARCHAR,
  "State_Province" VARCHAR,
  "Market" VARCHAR,
  "MSA" VARCHAR,
  "Country" VARCHAR,
  "Region" VARCHAR,
  "Latitude" DECIMAL(8,6),
  "Longitude" DECIMAL(9,6),
  "Tenure_Type" VARCHAR,
  "LED" DATE,
  "Rentable_Square_Feet" DECIMAL,
  "Usable_Square_Feet" DECIMAL,
  "Seats" INT,
  "PNL_Rent" FLOAT,
  "PNL_OpEx" FLOAT,
  "Cash_Rent" FLOAT,
  "Cash_OpEx" FLOAT,
  FOREIGN KEY ("Market") REFERENCES market_costs("Market")
);

CREATE TABLE site_actions (
  "Site_ID" VARCHAR,
  "S1_Action" VARCHAR,
  "S2_Action" VARCHAR,
  "S3_Action" VARCHAR,
  "S4_Action" VARCHAR,
  "S5_Action" VARCHAR,
  FOREIGN KEY ("Site_ID") REFERENCES site("Site_ID")
);

CREATE TABLE headcount (
  "Site_ID" VARCHAR,
  "Headcount" INT,
  "BU_1_HC" INT,
  "BU_2_HC" INT,
  "BU_3_HC" INT,
  "BU_4_HC" INT,
  "BU_5_HC" INT,
  "BU_6_HC" INT,
  "BU_7_HC" INT,
  "BU_8_HC" INT,
  "BU_9_HC" INT,
  "BU_10_HC" INT,
  FOREIGN KEY ("Site_ID") REFERENCES site("Site_ID")
);

CREATE TABLE business_unit (
  "Business_Unit_ID" VARCHAR PRIMARY KEY,
  "Business_Unit_Name" VARCHAR
);

CREATE TABLE sharing (
  "Work_Profile_ID" VARCHAR PRIMARY KEY,
  "Work_Profile_Description" VARCHAR,
  "Sharing_Ratio" FLOAT,
  "Seat_Buffer" FLOAT
);

CREATE TABLE bu_distribution (
  "Work_Profile_ID" VARCHAR,
  "Scenario_ID" VARCHAR,
  "BU_1_Distribution" FLOAT,
  "BU_2_Distribution" FLOAT,
  "BU_3_Distribution" FLOAT,
  "BU_4_Distribution" FLOAT,
  "BU_5_Distribution" FLOAT,
  "BU_6_Distribution" FLOAT,
  "BU_7_Distribution" FLOAT,
  "BU_8_Distribution" FLOAT,
  "BU_9_Distribution" FLOAT,
  "BU_10_Distribution" FLOAT,
  FOREIGN KEY ("Work_Profile_ID") REFERENCES sharing("Work_Profile_ID"),
  FOREIGN KEY ("Scenario_ID") REFERENCES scenario("Scenario_ID")
);

CREATE TABLE enterprise_distribution (
  "Work_Profile_ID" VARCHAR,
  "S1_Distribution" FLOAT,
  "S2_Distribution" FLOAT,
  "S3_Distribution" FLOAT,
  "S4_Distribution" FLOAT,
  "S5_Distribution" FLOAT,
  FOREIGN KEY ("Work_Profile_ID") REFERENCES sharing("Work_Profile_ID")
);

CREATE TABLE worker_distribution (
  "Worker_ID" VARCHAR PRIMARY KEY,
  "Worker_Description" VARCHAR,
  "Worker_Type" VARCHAR,
  "Site_ID" VARCHAR,
  "Business_Unit_ID" VARCHAR,
  "Work_Profile_ID" VARCHAR,
  FOREIGN KEY ("Site_ID") REFERENCES site("Site_ID"),
  FOREIGN KEY ("Business_Unit_ID") REFERENCES business_unit("Business_Unit_ID"),
  FOREIGN KEY ("Work_Profile_ID") REFERENCES sharing("Work_Profile_ID")
);





