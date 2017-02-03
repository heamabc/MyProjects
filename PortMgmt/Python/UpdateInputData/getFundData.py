'''
Created on Jan 27, 2017

@author: ywang

Pull Fund Data To the 
'''

import pandas as pd
from pandas import DataFrame, Series

import sqlalchemy
from urllib.parse import quote_plus
from sqlalchemy.types import VARCHAR, FLOAT, DATETIME 

import pandas_datareader.data as web

from sys import exit

from UpdateInputData.processTransactionData import cleanColName

#===============================================================================
# Main Script
#===============================================================================

if __name__== "__main__":
    
    mf_list = pd.read_excel('Inputs\Mutual_Funds.xlsx', sheet='DFA', squeeze=True, header=None).tolist()
    
    panel = web.DataReader(mf_list, 'yahoo', '1980/1/1')
    
    df = panel.to_frame()
    df['Date'] = df.index.get_level_values(0)
    df['Ticker'] = df.index.get_level_values(1)
    df.index = range(0,df.shape[0])
    df = df[['Date', 'Ticker']+df.columns[:-2].tolist()]
    
    df.columns = cleanColName(df.columns)
    
    params = quote_plus("DRIVER={SQL Server}; SERVER=(local); DATABASE=PortMgmt; Trusted_Connection=yes")
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
    df.to_sql('DFA', engine, schema='MutualFundData', if_exists='append', index=False)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    