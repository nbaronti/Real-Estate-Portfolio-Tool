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
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import plotly.graph_objects as go
from IPython.display import display
import panel as pn
from panel.interact import interact

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
    
def CurrentPortfolioMap():
    if p_or_m == "Portfolio":
        query = f'''SELECT * FROM detailed_site_view'''
    else:
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
    return site_level_map.show()

def CurrentPortfolioDF():
    if p_or_m == "Portfolio":
        query = f'''SELECT * FROM detailed_site_view'''
    else:
        query = f'''SELECT * FROM detailed_site_view WHERE detailed_site_view."Market" = '{Market}' '''
    detailed_site_DF = pd.read_sql_query(query,engine)
    return st.dataframe(detailed_site_DF)
    
def EnterpriseDistributionCalculations():
    scenario_input = scenario_selection
    if p_or_m == "Portfolio":
        query = f'''SELECT * FROM enterprise_distribution_calculations as edc WHERE edc."Scenario_ID" = '{scenario_input}' '''
    else: 
        query = f'''SELECT * FROM enterprise_distribution_calculations as edc WHERE edc."Scenario_ID" = '{scenario_input}' AND  edc."Market" = '{Market}' '''
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
    com_site_df = pd.concat([site_df,potential_seats_site_level], axis=1)
    com_site_df.rename(columns={'Potential Future Seats (With Buffer)' : 'Potential Seats'}, inplace=True)
    com_site_df["% Reduction Opportunity"] = 1 - (com_site_df["Potential Seats"] / com_site_df["Seats"])
    com_site_df["RSF Reduction Opportunity"] = com_site_df["Rentable_Square_Feet"] * com_site_df["% Reduction Opportunity"]
    com_site_df["P&L Cost Reduction Opportunity"] = (com_site_df["PNL_Rent"] + com_site_df["PNL_OpEx"]) * com_site_df["% Reduction Opportunity"]
    com_site_df['year'] = pd.DatetimeIndex(com_site_df['LED']).year
    com_site_df.sort_values(by=["year"], ascending=True, inplace=True)
    com_site_df.reset_index(inplace=True)
    savings_df = com_site_df[['year', 'P&L Cost Reduction Opportunity']].groupby('year').sum()
    savings_df.sort_index(ascending=True, inplace=True)
    savings_df["Cumulative P&L Savings"] = savings_df['P&L Cost Reduction Opportunity'].cumsum()
    com_site_df.set_index("Site_ID",inplace=True)
    return com_site_df, savings_df

def PNL_Chart(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["P&L Cost Reduction Opportunity"],
        name='Annual P&L Savings',
        marker_color='#7f7f7f'))
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["Cumulative P&L Savings"],
        name='Cumulative Annual P&L Savings',
        marker_color='#9467bd'))
    fig.update_layout(barmode='group', title="Annual & Cumulative P&L Savings by Year", xaxis_title='Year', yaxis_title='P&L Savings ($)', paper_bgcolor='rgba(245,245,245,1)', plot_bgcolor='rgba(245,245,245,1)')
    return fig.show()

# Work in process for beyond this class

def BusinessDistributionCalculations():
    scenario_input = scenario_selection
    query = f'''SELECT * FROM business_distribution_calculations as ewc WHERE ewc."Scenario_ID" = '{scenario_input}' '''
    portfolio_calculations = pd.read_sql_query(query,engine)
    return portfolio_calculations

# Work in process for beyond this class

def WorkerDistributionCalculations():
    scenario_input = scenario_selection
    query = f'''SELECT * FROM worker_workplace_calculations as ewc WHERE ewc."Scenario_ID" = '{scenario_input}' '''
    portfolio_calculations = pd.read_sql_query(query,engine)
    return portfolio_calculations

def to_excel(df, df2):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    df2.to_excel(writer, index=False, sheet_name='Sheet2')
    workbook = writer.book
    worksheet1 = writer.sheets['Sheet1']
    worksheet2 = writer.sheets['Sheet2']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet1.set_column('A:A', None, format1)
    worksheet2.set_column('A:A', None, format1) 
    writer.save()
    processed_data = output.getvalue()
    return processed_data


# @st.cache (allow_output_mutation=True)
# =============================================================================

st.set_page_config(layout="wide")

image = Image.open('04_Logo/Logo2.png')
st.sidebar.image(image)

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
p_or_m = st.sidebar.selectbox("Portfolio or Market Calculations?",["Portfolio","Market"])
if p_or_m == "Market":
    Market = st.sidebar.selectbox("Select Market",Market())
else:
    st.write("")  
st.sidebar.title("Generate & Visualize Site Map: ")
if st.sidebar.button('🌐 Generate Map'):
    map = CurrentPortfolioMap()
    df = CurrentPortfolioDF()
    print('Done.')

st.header("Run Calculations")

st.write('\n'*2)

calc_type = st.selectbox('Choose Calculation Type:', ('Enterprise Distribution Approach', 'Business Distribution Approach', 'Worker Distribution Approach'))
scenario_selection = st.selectbox('Choose Scenario:', Scenario())
start_date = st.date_input('Input Calculation Start Date', value=datetime.date(2022, 1, 1))
end_date = st.date_input('Input Calculation End Date', value=datetime.date(2031, 12, 31))

st.write('\n'*2)

st.markdown("#### Run Portfolio Calculations for Selected Scenario and Calculation Type:")
st.write('\n'*2)

df1, df2 = EnterpriseDistributionCalculations()

if st.button('⏳ Run Calculations'):
    st.dataframe(df1)
    st.dataframe(df2)
    print('Done.')
    
st.write('\n'*2)

st.sidebar.title("Visualize Annual & Cumulative P&L Savings: ")
if st.sidebar.button('📊 Generate Chart'):
    PNL_Chart(df2)
    print('Done.')

st.write('\n'*2)
    
df_xlsx = to_excel(df1, df2)

st.sidebar.title("Download Portfolio Output Reports: ")

st.sidebar.write('\n'*2)

st.sidebar.download_button(label='📥 Download Report Package',
                                data=df_xlsx ,
                                file_name= 'Portfolio_Calculations.xlsx')

