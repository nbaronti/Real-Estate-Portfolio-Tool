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
        sheet.to_csv("%s.csv" % sheet_name, index=False)
    sheets_list = list(sheets)
    conn = psycopg2.connect(database="REAL", user='postgres', password='postgres', host='localhost', port='5432')
    conn.autocommit = True
    cursor = conn.cursor()
    schema_sql = open("schema.sql", "r").read()
    cursor.execute(schema_sql)
    conn.commit()
    conn.close()
    for sheet in sheets_list:
        sheet_csv = sheet + ".csv"
        sheet_df = pd.read_csv(sheet_csv)
        sheet_df.to_sql(con=engine, index=False, name=sheet, if_exists='append')
    conn = psycopg2.connect(database="REAL", user='postgres', password='postgres', host='localhost', port='5432')
    conn.autocommit = True
    cursor = conn.cursor()
    query_sql = open("query.sql", "r").read()
    cursor.execute(query_sql)
    conn.commit()
    conn.close()
    end = timeit.default_timer()
    return print('The time it took was : ',str(end-start))
    
def CurrentPortfolio():
    query = f'''SELECT * FROM detailed_site_view'''
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
    
def EnterprisePortfolioCalculations():
    scenario_input = scenario_selection
    query = f'''SELECT * FROM enterprise_workplace_calculations as ewc WHERE ewc."Scenario_ID" = '{scenario_input}' '''
    portfolio_calculations = pd.read_sql_query(query,engine)
    return portfolio_calculations


# @st.cache (allow_output_mutation=True)
# =============================================================================

st.set_page_config(layout="wide")
st.title('Real Estate Portfolio Tool')
st.write("Choose the operation below to run the Real Estate Portfolio Tool")

dateToday = str(date.today())
col1, col2 = st.columns(2)

with col1:
    option = st.selectbox('Choose Operation:', ('Load Portfolio Data', 'Other'))
with col2:
    st.write("")

st.write("")
        
if option == "Load Portfolio Data":
    st.write("PLEASE READ:  \n 1. Source Files must be in .XLSX format.  \n 2. After you hit the submit button below, the program will run and give you a download button at the bottom upon completion.")
    col1, col2 = st.columns(2)
    with col1:
        file = st.file_uploader(label="Upload Source File")
    with col2:
        st.write("")
    if st.button('Submit'):
        LoadPortfolioData(file)
        st.write("Done!")
        
st.write('\n'*3)

st.write("Display the Current Portfolio Map")
Market = st.text_input("Enter Market for Map")
st.write('\n'*2)
if st.button('Generate Current Portfolio Map'):
    CurrentPortfolio()
    print('Done.')
    
st.write("Select Approach for Portfolio Calculations")

st.write('\n'*2)
calc_type = st.selectbox('Choose Calculation Type:', ('Enterprise Distribution Approach', 'Business Distribution Approach', 'Worker Distribution Approach'))
scenario_selection = st.selectbox('Choose Scenario:', ('Scenario_1', 'Scenario_2', 'Scenario_3', 'Scenario_4', 'Scenario_5'))

st.write('\n'*2)

st.write("Run Portfolio Analytics Calculations")
st.write('\n'*2)

if st.button('Run Calculations'):
    st.dataframe(EnterprisePortfolioCalculations())
    print('Done.')
