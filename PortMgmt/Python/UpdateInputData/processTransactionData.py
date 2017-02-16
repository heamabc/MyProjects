'''
Created on Jan 27, 2017

@author: ywang

Goal: upload transcation data to database PortMgmt
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
    pass


def updateDatabase():
    # 
    pass


#===============================================================================
# Main Script
#===============================================================================

if __name__== "__main__":
    
    # Read csv files, clean the data and import it to sql database    
    directory = 'Inputs\\401K\\'
    skema_name = 'TransactionData'
      
    # Check
    print('Importing: ', skema_name)
    append_check = input('Are you sure to append the database? Type Yes or No: ')
    if append_check != 'Yes':
        exit()
        
    params = quote_plus("DRIVER={SQL Server}; SERVER=(local); DATABASE=PortMgmt; Trusted_Connection=yes")
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
    
    for y in range(2013, 2018):
        
        file_name = directory + str(y) + '.csv'
        num_col = ['Transaction Amount', 'Share Price', 'Total shares']
        date_col = ['Trade Date']
        
        df = getCleanData(file_name, num_col, date_col)
        df = df.groupby(['TradeDate', 'Investments', 'Ticker','Transaction','SharePrice'], as_index=False).sum()

        df.to_sql('FourOhOneK', engine, schema=skema_name, if_exists='append', index=False, dtype=DATA_TYPE_401K)

        print(y, ':Data uploaded:', df.shape)        
        

    
        
    