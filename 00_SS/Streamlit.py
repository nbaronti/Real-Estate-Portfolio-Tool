# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 11:44:21 2022
@author: dhubbard
"""
import timeit
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
import pyodbc
import datetime as dt
import streamlit as st
from datetime import date
from pathlib import Path
Server=''
Database='HOLDINGS'
Driver='ODBC Driver 13 for SQL Server'
Database_Con = f'mssql://@{Server}/{Database}?driver={Driver}'
engine=create_engine(Database_Con, echo=False)
con = engine.connect()
#@st.experimental_singleton
#create SQL connection
def LoadAllHoldings(filepath):
    start=timeit.default_timer()
    #load dataframe
    #holdingData = pd.DataFrame(pd.read_excel('data/Holdings_vs4_1.xlsx'))
    holdingData = pd.DataFrame(pd.read_excel(filepath))
    #format data for upload
    holdingData[['Units', 'AsofValue', 'AsofPrice', 'Weighting']] = holdingData[['Units', 'AsofValue', 'AsofPrice', 'Weighting']].astype(float)
    holdingData = holdingData.fillna('')
    #holdingData = holdingData.sort_values(by="SecurityName", key=lambda x: x.str.len(), ascending=False)
    holdingData['SecID'] = holdingData['SecID'].astype(str)
    #upload to SQL
    holdingData.to_sql('HoldingsHistoric', con, if_exists='replace', index=False)
    con.close()
    end=timeit.default_timer()
    print('The it took was : ',str(end-start))
def LoadCurrentMonthHoldings(filepath):
    start=timeit.default_timer()
    #load dataframe
    #holdingData = pd.DataFrame(pd.read_excel('data/Holdings_vs4_1.xlsx'))
    holdingData = pd.DataFrame(pd.read_excel(filepath))
    holdingData=holdingData.drop(['ModelGroupId','FromDT'],axis=1)
    #format data for upload
    holdingData[['Units', 'AsofValue', 'AsofPrice', 'Weighting']] = holdingData[['Units', 'AsofValue', 'AsofPrice', 'Weighting']].astype(float)
    holdingData = holdingData.fillna('')
    #holdingData = holdingData.sort_values(by="SecurityName", key=lambda x: x.str.len(), ascending=False)
    holdingData['SecID'] = holdingData['SecID'].astype(str)
    #upload to SQL
    holdingData.to_sql('HoldingsHistoric', con, if_exists='append', index=False)
    con.close()
    end=timeit.default_timer()
    print('The it took was : ',str(end-start))
def CleanHoldings(begdt,enddt,minweight,strategy):
    query=f'''select * from holdingshistoric where todt between '{begdt}' and '{enddt}' and groupname='{strategy}' '''
    #print(query)
    dfHoldings=pd.read_sql_query(query,engine)
    #dfHoldings=pd.read_excel(file,dtype={'GroupName':str,'Cusip':str}, parse_dates=['ToDt'])#,index_col=[1,3])
    #################################################################dfHoldings=dfHoldings.drop(['FromDT','ModelGroupId'],axis=1)
    #dfHoldings.index = dfHoldings['ToDt','GroupName']
    dfHoldings['Cusip']=dfHoldings['Cusip'].astype('str')
    di=dfHoldings.to_dict()
    del dfHoldings
    for value in di['Cusip']:
        strCusip=str(di['Cusip'][value])
        if len(strCusip)==6:
            di['Cusip'][value]="000"+strCusip
        elif len(strCusip)==7:
            di['Cusip'][value]="00"+strCusip
        elif len(strCusip)==8:
            di['Cusip'][value]="0"+strCusip
        elif len(strCusip)==10:
            di['Cusip'][value]=strCusip.replace(' ','')
        elif len(strCusip)>10 or len(strCusip)==0:
            di['Cusip'][value]="Lookup"
        #print(di['Cusip'][value])
    dfHoldings=pd.DataFrame(di)
    #dfHoldings['Cusip']=dfHoldings['Cusip'].astype('str')
    dfHoldings=dfHoldings[(dfHoldings['SecID']!='PerfConv')]
    dfHoldings[['Units', 'AsofValue', 'AsofPrice', 'Weighting']] = dfHoldings[['Units', 'AsofValue', 'AsofPrice', 'Weighting']].astype(float)
    #####################################################################3#Drop Garbage here
    #dfHoldings=dfHoldings[((dfHoldings['GroupName']=='AllCapCore') & (dfHoldings['Weighting']>=0.0015))] #| (dfHoldings['GroupName']!='Preferred')]
    dfHoldings=dfHoldings[((dfHoldings['GroupName']==strategy) & (dfHoldings['Weighting']>=minweight))] #| (dfHoldings['GroupName']!='Preferred')]
    #############################################################################################################
    dfHoldings['TotalWeight'] = dfHoldings.groupby(['GroupName','ToDt'], sort=False)["Weighting"].transform('sum')
    dfHoldings['RecalcWeight'] = dfHoldings['Weighting']/dfHoldings['TotalWeight']
    dfHoldings['Cusip']=dfHoldings['Cusip'].astype('str')
    #dfHoldings[dfHoldings['Cusip'].str.len==6]="000"+dfHoldings['Cusip']
    #
    #dfHoldings[dfHoldings['Cusip'].str.len==7]="00"+dfHoldings['Cusip']
    #
    #dfHoldings[dfHoldings['Cusip'].str.len==8]="0"+dfHoldings['Cusip']
    #dfSums=dfHoldings.drop(['SecTy','Cusip','SecID','Ticker','SecurityName','Units','AsofValue','AsofPrice'],axis=1)
    #dfSums=dfSums.groupby(['ToDt','GroupName']).sum()
    #dfSums.rename(columns = {'Weighting':'SumWeights'}, inplace = True)
    ######################dfHoldings=pd.concat([dfHoldings,dfSums],axis='columns',join='outer')
    #########################df_merged = dfHoldings.merge(dfSums, how='outer', left_index=True, right_index=True)
    #dfHoldings['ToDt'] = dfHoldings['ToDt'].dt.strftime('%Y/%m/%d')
    #dfAll['FundedDate'] = dfAll['FundedDate'].dt.strftime('%Y/%m/%d')
    #dfAll['InvestedDate'] = dfAll['InvestedDate'].dt.strftime('%Y/%m/%d')
    #dfAll['LiquidationDate'] = dfAll['LiquidationDate'].dt.strftime('%Y/%m/%d')
    #dfAll['MV Date or Run Date'] = dfAll['MV Date or Run Date'].dt.strftime('%Y/%m/%d')
    #dfAll['AcctNo']=dfAll['AcctNo'].astype('str')
    ###############################writer = pd.ExcelWriter('C:\\Users\\dhubbard\\Downloads\\AllCapHoldings_122820.xlsx', engine='xlsxwriter',date_format='mm/dd/yyyy')
    writer = pd.ExcelWriter(f'K:\General\DHubbard\Holdings\{strategy}Holdings.xlsx', engine='xlsxwriter',date_format='mm/dd/yyyy')
    dfHoldings.to_excel(writer,index=False,sheet_name=strategy)
    writer.save()
    writer.close()
#@st.cache(allow_output_mutation=True)
#=============================================================================
st.set_page_config(layout="wide")
st.title('ZIM Holdings Database')
st.write("Choose which operation below to do for holdings.")
dateToday = str(date.today())
col1, col2 = st.columns(2)
with col1:
    option = st.selectbox('Choose operation', ('Load Monthly Holdings','Reload All Holdings'))
with col2:
    st.write("")
st.write("")
if option == "Reload All Holdings":
    st.write("PLEASE READ:  \n 1.Source Files must be in .xlsx format.  \n 2.After you hit the submit button below, the program will run and give you a download button at the bottom upon completion.")
    col1, col2 = st.columns(2)
    with col1:
        first = st.file_uploader(label="Upload Source File")
    with col2:
        st.write("")
    if st.button('Submit'):
        LoadAllHoldings(first)
        st.write("Done!")
if option == "Load Monthly Holdings":
    st.write("PLEASE READ:  \n 1.Source Files must be in .xlsx format.  \n 2.After you hit the submit button below, the program will run and give you a download button at the bottom upon completion.")
    col1, col2 = st.columns(2)
    with col1:
        first = st.file_uploader(label="Upload Source File")
    with col2:
        st.write("")
    if st.button('Submit'):
        LoadCurrentMonthHoldings(first)
        st.write("Done!")
st.write('\n'*3)
st.write("Query for Strategy and TimeFrame")
beginDate = st.text_input("Begin Date")
endDate = st.text_input("End Date")
minweight=float(st.text_input("Min Weight",value=0.0015))
strategy=st.text_input("Strategy")
st.write('\n'*2)
if st.button('Run Strategy Holdings'):
    CleanHoldings(beginDate,endDate,minweight,strategy)
    print('Done.')
#=============================================================================
#LoadAllHoldings(1)