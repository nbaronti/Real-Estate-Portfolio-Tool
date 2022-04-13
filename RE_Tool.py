# import python packages

import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import plotly.express as px
import os
from pathlib import Path
from dotenv import load_dotenv
import timeit
import streamlit as st
from datetime import date
import datetime
from PIL import Image
import numpy as np

# create engine with postgres sql DB address

engine = create_engine("postgresql://postgres:postgres@localhost:5432/REAL")

# Set up API credentials, read the Mapbox API key, and set the token

load_dotenv()
map_box_api = os.getenv("mapbox")
px.set_mapbox_access_token(map_box_api)

# Define streamlit functions
    
def LoadPortfolioData(filepath):
    start = timeit.default_timer()
    data = pd.read_excel(filepath, sheet_name=None)  
    sheets = data.keys()
    for sheet_name in sheets:
        sheet = pd.read_excel(filepath, sheet_name=sheet_name)
        sheet.to_csv("02_CSV_Exports/%s.csv" % sheet_name, index=False)
    sheets_list = list(sheets)
    conn = psycopg2.connect(database="REAL", user='postgres', password='postgres', host='localhost', port='5432')
    conn.autocommit = True
    cursor = conn.cursor()
    schema_sql = open("03_SQL_Scripts/schema.sql", "r").read()
    cursor.execute(schema_sql)
    conn.commit()
    conn.close()
    for sheet in sheets_list:
        sheet_csv = sheet + ".csv"
        sheet_df = pd.read_csv(f"02_CSV_Exports/{sheet_csv}")
        sheet_df.to_sql(con=engine, index=False, name=sheet, if_exists='append')
    conn = psycopg2.connect(database="REAL", user='postgres', password='postgres', host='localhost', port='5432')
    conn.autocommit = True
    cursor = conn.cursor()
    query_sql = open("03_SQL_Scripts/query.sql", "r").read()
    cursor.execute(query_sql)
    conn.commit()
    conn.close()
    end = timeit.default_timer()
    return print('The time it took was : ',str(end-start))

def Market():
    query = f'''SELECT "Market" FROM market_costs'''
    market_df = pd.read_sql_query(query,engine)
    return market_df

def Scenario():
    query = f'''SELECT "Scenario_ID" FROM scenario'''
    scenario_df = pd.read_sql_query(query,engine)
    return scenario_df
    
def CurrentPortfolio():
    query = f'''SELECT * FROM detailed_site_view WHERE detailed_site_view."Market" = '{Market}' '''
    detailed_site_DF = pd.read_sql_query(query,engine)
    site_level_map = px.scatter_mapbox(
    detailed_site_DF,
    lat="Latitude",
    lon="Longitude",
    color="Site_Name",
    hover_data=["Address","City","Market","MSA"],
    width=700,
    height=700,
    text="Site_Name",
    title="Current Portfolio Map",
    size="Rentable_Square_Feet")
    site_level_map.show()
    
def EnterpriseDistributionCalculations():
    scenario_input = scenario_selection
    query = f'''SELECT * FROM enterprise_distribution_calculations as edc WHERE edc."Scenario_ID" = '{scenario_input}' '''
    enterprise_calculations = pd.read_sql_query(query,engine)
    enterprise_calculations["Allocable HC"] = enterprise_calculations["Headcount"] * enterprise_calculations["Profile_Distribution"]
    enterprise_calculations["Potential Future Seats (No Buffer)"] = enterprise_calculations["Allocable HC"] / enterprise_calculations["Sharing_Ratio"]
    enterprise_calculations["Buffer Seats"] = enterprise_calculations["Potential Future Seats (No Buffer)"] * enterprise_calculations["Seat_Buffer"]
    enterprise_calculations["Potential Future Seats (With Buffer)"] = enterprise_calculations["Potential Future Seats (No Buffer)"] + enterprise_calculations["Buffer Seats"]
    enterprise_calculations["Potential Future Seats (With Buffer)"].fillna(0, inplace=True)
    potential_seats_df = enterprise_calculations[["Site_ID","Potential Future Seats (With Buffer)"]]
    potential_seats_site_level = potential_seats_df.groupby(["Site_ID"]).sum().round({'Potential Future Seats (With Buffer)': 0}).astype(np.int64)
    query2 = f'''SELECT * FROM detailed_site_view as dsv'''
    site_df = pd.read_sql_query(query2,engine)
    site_df.set_index("Site_ID",inplace=True)
    combined_site_df_with_cals = pd.concat([site_df,potential_seats_site_level], axis=1)
    combined_site_df_with_cals.rename(columns={'Potential Future Seats (With Buffer)' : 'Potential Seats'}, inplace=True)
    combined_site_df_with_cals["Reduction Opportunity"] = 1 - (combined_site_df_with_cals["Potential Seats"] / combined_site_df_with_cals["Seats"])
    return combined_site_df_with_cals

def BusinessDistributionCalculations():
    scenario_input = scenario_selection
    query = f'''SELECT * FROM business_distribution_calculations as ewc WHERE ewc."Scenario_ID" = '{scenario_input}' '''
    portfolio_calculations = pd.read_sql_query(query,engine)
    
    return portfolio_calculations

def WorkerDistributionCalculations():
    scenario_input = scenario_selection
    query = f'''SELECT * FROM worker_workplace_calculations as ewc WHERE ewc."Scenario_ID" = '{scenario_input}' '''
    portfolio_calculations = pd.read_sql_query(query,engine)
    
    return portfolio_calculations


# @st.cache (allow_output_mutation=True)
# =============================================================================

st.set_page_config(layout="wide")

title = st.title('Real Estate Portfolio Tool') 

st.write('\n'*2)

st.header("Choose Operation & Load Portfolio Data")

dateToday = str(date.today())

option = st.selectbox('Choose Operation:', ('Load Portfolio Data', 'Other Operation'))
        
if option == "Load Portfolio Data":
    st.write("PLEASE READ:  \n 1) Source Files must be in .XLSX format.  \n 2) After you hit the submit button below, the file will load and then a message will appear saying the upload is complete.")

file = st.file_uploader(label="Upload Source File")
if st.button('Submit'):
    LoadPortfolioData(file)
    st.write("Upload Complete!")
        
st.write('\n'*2)

st.header("Display the Current Portfolio Map")
Market = st.selectbox("Select Market",Market())
st.write('\n'*2)
if st.button('Generate Current Portfolio Map'):
    CurrentPortfolio()
    print('Done.')

st.write('\n'*2)

st.header("Run Portfolio Calculations")

st.write('\n'*2)
calc_type = st.selectbox('Choose Calculation Type:', ('Enterprise Distribution Approach', 'Business Distribution Approach', 'Worker Distribution Approach'))
scenario_selection = st.selectbox('Choose Scenario:', Scenario())
start_date = st.date_input('Input Calculation Start Date', value=datetime.date(2022, 1, 1))
end_date = st.date_input('Input Calculation End Date', value=datetime.date(2031, 12, 31))

st.write('\n'*2)

st.write("Run Portfolio Analytics Calculations")
st.write('\n'*2)

if st.button('Run Calculations'):
    st.dataframe(EnterpriseDistributionCalculations())
    print('Done.')
