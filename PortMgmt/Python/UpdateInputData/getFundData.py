'''
Created on Jan 27, 2017

@author: ywang

Pull Fund Data To the 
'''

import pandas as pd
from pandas import DataFrame, Series
from pandas.tseries.offsets import DateOffset

import sqlalchemy
from urllib.parse import quote_plus
from sqlalchemy.types import VARCHAR, FLOAT, DATETIME 

import pandas_datareader.data as web

from sys import exit

from UpdateInputData.processTransactionData import cleanColName


def resetDatabase():
    pass


def updateDatabase(account_name='DFA_401K'):
    
    mf_list = pd.read_excel('Inputs\Mutual_Funds.xlsx', sheet=account_name, squeeze=True, header=None).tolist()
    
    params = quote_plus("DRIVER={SQL Server}; SERVER=(local); DATABASE=PortMgmt; Trusted_Connection=yes")
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
    
    temp = pd.read_sql('SELECT MAX(Date) FROM MutualFundData.'+account_name, engine)
    if temp.notnull().iloc[0,0]:
        start_dt = temp.iloc[0,0]
    else:
        start_dt = '1980/1/1' 
 
    panel = web.DataReader(mf_list, 'yahoo', start_dt)
    
    df = panel.to_frame()
    df['Date'] = df.index.get_level_values(0)
    df['Ticker'] = df.index.get_level_values(1)
    df.index = range(0,df.shape[0])
    df = df[['Date', 'Ticker']+df.columns[:-2].tolist()]
    
    df.columns = cleanColName(df.columns)
    
    # convert AdjClose to Total Return
    df['TotalDailyReturn'] = df.groupby('Ticker')['AdjClose'].pct_change().round(8)
    df.drop('AdjClose', axis=1, inplace=True)
    df.query('Date > @start_dt', inplace=True)
    
    if df.shape[0] > 0:
        df.to_sql(account_name, engine, schema='MutualFundData', if_exists='append', index=False)
        print('Fund Data Upload:', df.Date.min(), df.Date.max())




#===============================================================================
# Main Script
#===============================================================================

if __name__== "__main__":
    pass
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    