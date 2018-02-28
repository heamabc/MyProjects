'''
Created on Jan 4, 2018

@author: ywang
'''

import pandas as pd
from pandas import DataFrame, Series
import pandas_datareader.data as web

import numpy as np

import sqlalchemy
from urllib.parse import quote_plus
from sqlalchemy.types import VARCHAR, FLOAT, DATETIME 

from datetime import datetime 

from sys import exit


d_ticker_correction = {
    'BRKB': 'BRK-B',
    'FCEA': 'FCE-A',
    'LGFA': 'LGF-A',
    'LGFB': 'LGF-B',
    'NYLDA': 'NYLD-A',
    'GEFB': 'GEF-B',
    'CRDB': 'CRD-B',
    'RDS/A': 'RDS-A',
    'RDS/B': 'RDS-B',
    'PBR/A': 'PBR-A'
    }


def correctTickers(x):
    if x in d_ticker_correction.keys():
        x_corrected = d_ticker_correction[x]
    else:
        x_corrected = x
    return x_corrected


def cleanColName(col):
    # clean up the whitespace in column names
    # col: data type Index
    for x in [' ', '-', '(', ')', '&', '\'']:
        col = col.str.replace(x, '')
    return col


def updateStockDataFromHoldings(region='US', updateDate=datetime.today().date()):
    # region = 'US', 'DevExUS', 'EM'
    
    params = quote_plus("DRIVER={SQL Server}; SERVER=ASTJ9K2Y52RESR\SYW_LOCAL_V2014; DATABASE=YFinData; Trusted_Connection=yes")
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
    
    # read holdings and holding info
    if region == 'US':
        input_file = 'Inputs\IWV_holdings_200612.csv'
        df_holdings = pd.read_csv(input_file, skiprows=10)
        df_holdings = df_holdings[df_holdings['Asset Class']=="Equity"]
        
        df_info = pd.read_csv(input_file, nrows=9)
        holdingsDate = pd.to_datetime(df_info.loc['Fund Holdings as of', :].values[0])
        
        df_holdings['Date'] = holdingsDate
        df_holdings.rename(columns={'Weight (%)': 'Weight'}, inplace=True)
        
        # ticker correction
        df_holdings['Ticker'] = df_holdings.Ticker.apply(correctTickers)
    elif region == 'ADR':
        df_holdings1 = pd.read_csv('Inputs\holdings_ADRD_201712.csv')
        df_holdings2 = pd.read_csv('Inputs\holdings_ADRE_201712.csv')
        
        df_holdings = pd.concat([df_holdings1, df_holdings2], ignore_index=True)
        df_holdings.rename(columns={'HoldingsTicker': 'Ticker'}, inplace=True)
        
        holdingsDate = pd.to_datetime(df_holdings.Date[0])
        
        df_holdings['Ticker'] = df_holdings.Ticker.str.strip()
        
        df_holdings['Ticker'] = df_holdings.Ticker.apply(correctTickers)
    else:
        exit('Region not implemented.')

    
    # Upload holding table to YH Database
    if region == 'US':
        col_hld_tbl = ['Date', 'Ticker', 'Name', 'Weight', 'Sector', 'SEDOL', 'ISIN', 'Exchange']
        temp = pd.read_sql('SELECT DISTINCT Date FROM Holdings.R3000_IWV', engine)
        if temp.shape[0] > 0:
            if holdingsDate not in pd.to_datetime(temp.Date.values):
                df_holdings[col_hld_tbl].to_sql('R3000_IWV', engine, schema='Holdings', if_exists='append', index=False)
                print('US stock holding table is appended')
        else:
            df_holdings[col_hld_tbl].to_sql('R3000_IWV', engine, schema='Holdings', if_exists='append', index=False)
            print('US stock holding table is created')
    elif region == 'ADR':
        col_hld_tbl = ['FundTicker', 'SecurityNum', 'Ticker', 'Weight', 'Name', 'Sector', 'Date']
        temp = pd.read_sql('SELECT DISTINCT Date FROM Holdings.ADR', engine)
        if temp.shape[0] > 0:
            if holdingsDate not in pd.to_datetime(temp.Date.values):
                df_holdings[col_hld_tbl].to_sql('ADR', engine, schema='Holdings', if_exists='append', index=False)
                print('ADR stock holding table is appended')
        else:
            df_holdings[col_hld_tbl].to_sql('ADR', engine, schema='Holdings', if_exists='append', index=False)
            print('ARD stock holding table is created')
 
    # Pull Data and Upload to YH Database
    error_ticker = []
    for ticker in df_holdings.Ticker:
        # Determine the last date in the database for each ticker
        temp = pd.read_sql('SELECT MAX(Date) FROM Stock.'+region + ' WHERE Ticker=\''+ticker+'\'', engine)
        if temp.notnull().iloc[0,0]:
            start_dt = temp.iloc[0,0]
        else:
            start_dt = pd.to_datetime('1980/1/1')
            
        if start_dt == pd.to_datetime(updateDate):
            continue
        else:
            df = DataFrame()
            print('Pulling: ', ticker)
            try: 
                df = web.DataReader(ticker, 'yahoo', start_dt, updateDate)
            except:
                print('Error Pulling ', ticker)
                error_ticker.append(ticker)
            
            if df.shape[0] > 1:
                if start_dt == pd.to_datetime('1980/1/1'):
                    df.to_excel('Outputs\\Stocks\\'+region+'\\'+ticker+'.xlsx')
                
                df['Ticker'] = ticker
                df['DailyTotalRet'] = df['Adj Close'].pct_change() 
                
                df.drop('Adj Close', axis=1, inplace=True)
                
                if start_dt == pd.to_datetime('1980/1/1'):
                    df.to_sql(region, engine, schema='Stock', if_exists='append')
                else:
                    df.iloc[1:,:].to_sql(region, engine, schema='Stock', if_exists='append')
                
                print(ticker, 'Uploaded: ', df.index.min(), df.index.max())
    
    # output error tickers
    DataFrame(index=error_ticker).to_excel('Outputs\\Stock_Error_Tickers_'+region+'.xlsx')

if __name__ == "__main__":
    # NEED to update data after market close
    
    ######################################################
    # Update US Stock Data
    ######################################################
    updateStockDataFromHoldings('US', '2018/2/2')
    
    # updateStockDataFromHoldings('US')
    
    
    
    ######################################################
    # Update ADR Stock Data
    ######################################################
    
    # updateStockDataFromHoldings('ADR', '2018/2/2')
    
    
    
    
    
    
    
    
    
    
    
    

