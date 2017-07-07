'''
Created on Jan 27, 2017

@author: ywang

Goal: upload transcation data to database PortMgmt

20170511: Switch to SYW_LOCAL_V2014 instead of local

'''


import pandas as pd
from pandas import DataFrame, Series

import sqlalchemy
from urllib.parse import quote_plus
from datetime import datetime
from sqlalchemy.types import VARCHAR, FLOAT, DATETIME 

from sys import exit

DATA_TYPE_401K = {
    'TradeDate': DATETIME,
    'Investments': VARCHAR(100),
    'Ticker': VARCHAR(20),
    'Transaction': VARCHAR(100)
    }

# Set up data type for date and char columns; No need to set up the numeric columns
def getCleanData(file_name, num_col, date_col):
    #############################
    # clean up the data
    # num_col: numeric columns
    # date_col: date columns
    #############################
    df_temp = pd.read_csv(file_name, header=0, index_col=False, dtype='str')
    
    for col_name in num_col:
        df_temp[col_name] = df_temp[col_name].str.replace(',', '')
        df_temp[col_name] = df_temp[col_name].astype('float')
        
    for col_name in date_col:
        df_temp[col_name] = pd.to_datetime(df_temp[col_name], format='%m/%d/%Y')
        
    df_temp.columns = cleanColName(df_temp.columns)
            
    return df_temp
    
def cleanColName(col):
    # clean up the whitespace in column names
    # col: data type Index
    for x in [' ', '-', '(', ')', '&', '\'']:
        col = col.str.replace(x, '')
    return col


def resetDatabase():
    # TBI
    pass


def updateDatabase(account_name='DFA_401K', year_list=[2017]):
    # update the database TranscationData.DFA_401K
    
    directory='Inputs\\'+account_name+'\\'
    
    params = quote_plus("DRIVER={SQL Server}; SERVER=ASTJ9K2Y52RESR\SYW_LOCAL_V2014; DATABASE=PortMgmt; Trusted_Connection=yes")
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
    
    temp = pd.read_sql('SELECT MAX(TradeDate) FROM TransactionData.'+account_name, engine)
    if temp.notnull().iloc[0,0]:
        start_dt = temp.iloc[0,0]
    else:
        start_dt = '1900/1/1'
    
    for y in year_list:
        file_name = directory + str(y) + '.csv'
        num_col = ['Transaction Amount', 'Share Price', 'Total shares']
        date_col = ['Trade Date']
        
        df = getCleanData(file_name, num_col, date_col)
        df.query('TradeDate > @start_dt', inplace=True)
        
        if df.shape[0] > 0:
            df = df.groupby(['TradeDate', 'Investments', 'Ticker','Transaction','SharePrice'], as_index=False).sum()
            
            df.to_sql(account_name, engine, schema='TransactionData', if_exists='append', index=False, dtype=DATA_TYPE_401K)
            print('Data uploaded:', df.TradeDate.min(), df.TradeDate.max())      
        else:
            print('No New Data.')


#===============================================================================
# Main Script
#===============================================================================

if __name__== "__main__":
    
    pass
        

    
        
    