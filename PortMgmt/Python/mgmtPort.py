'''
Manage Portfolio and update table PortPosition

Created on Feb 1, 2017

@author: ywang
'''

import pandas as pd
from pandas import DataFrame, Series

import sqlalchemy
from urllib.parse import quote_plus

SQL_PULL_HOLDING_POSITION = '''
SELECT [TradeDate] AS [Date], [Ticker], [Transaction], [Totalshares]
FROM TransactionData.FourOhOneK
ORDER BY TradeDate
'''

SQL_PULL_MF_PRICE = '''
SELECT [Date], [Ticker], [Close]
FROM MutualFundData.DFA
'''

def reindex_by_date(_df, dt):
    max_dt = _df.index.get_level_values(0).max()
    min_dt = _df.index.get_level_values(0).min()
    dates = dt[(dt>=min_dt) & (dt<=max_dt)]
    return _df.reindex(dates, method='ffill')


#===============================================================================
# Main Script
#===============================================================================

if __name__== "__main__":
    
    ################ Pull transaction data
    params = quote_plus("DRIVER={SQL Server}; SERVER=(local); DATABASE=PortMgmt; Trusted_Connection=yes")
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
    
    df_transaction = pd.read_sql(SQL_PULL_HOLDING_POSITION, engine, index_col='Date')
    df_transaction.sort_index(inplace=True)
    df_transaction['Date'] = df_transaction.index
    
    # There are multiple transaction type in a given day, must aggregate
    df_position = df_transaction.groupby(['Date','Ticker'])[['Totalshares']].sum()
    df_position.reset_index(1, inplace=True)
    
    # Get cumulative position
    df_position['CumShares'] = df_position.groupby('Ticker')['Totalshares'].cumsum()
    
    ################## Get Price
    start_dt = df_transaction.index.min()
    
    df_price = pd.read_sql(SQL_PULL_MF_PRICE+'WHERE [Date]>='+'\''+start_dt.strftime('%Y/%m/%d')+'\'', engine, index_col='Date') 
    df_price['Date'] = df_price.index
    
    busdate = df_price.index.unique()

    ################# Create daily position ##################
    df_pos_daily = df_position.groupby('Ticker').apply(reindex_by_date, dt=busdate)
    del df_position
    df_pos_daily.reset_index(0, drop=True, inplace=True)
    
    df_pos_daily['Date'] = df_pos_daily.index
    
    # add price
    df_pos_daily = df_pos_daily.merge(df_price, how='left', on=['Date','Ticker'])
    
    df_pos_daily = df_pos_daily[['Date', 'Ticker', 'CumShares', 'Close']]
    
    # Add value=$1 for VMMXX, GVMXX
    df_pos_daily.ix[df_pos_daily.Ticker.isin(['GVMXX', 'VMMXX']),'Close'] = 1 
    
    # Check if there is any date with missing price
    dt_price_missing = df_pos_daily[df_pos_daily.Close.isnull()].Date.unique()
    
    # Drop date with missing price 
    df_pos_daily = df_pos_daily[~df_pos_daily.Date.isin(dt_price_missing)]
    
    # Dollar position
    df_pos_daily['Amount'] = df_pos_daily['CumShares'] * df_pos_daily['Close']
    
    ################# Contribution ##################
    df_contrib = df_transaction.query('Transaction=="ACH Contribution"')
    df_contrib = df_contrib.groupby('Date')
    
    ################# Daily Table #######################
    
    df_daily = DataFrame(index=df_pos_daily.Date.unique(), columns=['Balance', 'Contribution', 'Dividend'])
    
    df_daily['Balance'] = df_pos_daily.groupby('Date')['Amount'].sum()
    
    
    
    
    
    
    
    
    
    
    
    
