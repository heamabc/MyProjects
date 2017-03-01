'''
Manage Portfolio and update table PortPosition

Created on Feb 1, 2017

@author: ywang
'''

import pandas as pd
from pandas import DataFrame, Series

import sqlalchemy
from urllib.parse import quote_plus

import numpy as np
from numpy import datetime64

SQL_PULL_HOLDING_POSITION = '''
SELECT [TradeDate] AS [Date], [Ticker], [Transaction], [Totalshares], [SharePrice]
FROM TransactionData.DFA_401K
ORDER BY TradeDate
'''

SQL_PULL_MF_PRICE = '''
SELECT [Date], [Ticker], [Close]
FROM MutualFundData.DFA_401K
'''

def reindex_by_date(g, dt):
    _df = g[['CumShares', 'AverageCost']].copy()
    _df.index = g.Date
    max_dt = max(datetime64(_df.index.max()), dt.max())
    min_dt = datetime64(_df.index.min())
    dates = dt[(dt>=min_dt) & (dt<=max_dt)]
    return _df.reindex(dates, method='ffill')


def get_cumsum_adj_and_cost(_df):
    # cumulative sum of shares, reset the CumShares to 0, if it's too small
    # get average cost over time
    df_adj = _df.copy()
    df_adj['CumShares'] = _df['Totalshares']
    df_adj['AverageCost'] = _df['SharePrice']
    
    N = df_adj.index.size    
    for k in range(1,N):
        temp = df_adj.CumShares[df_adj.index[k-1]] + df_adj.Totalshares[df_adj.index[k]]
        if np.abs(temp) < 0.01:
            temp = 0
        df_adj.ix[df_adj.index[k], 'CumShares'] = temp
    
    for k in range(1,N):
        transaction_amount = df_adj.ix[df_adj.index[k],'SharePrice'] * df_adj.ix[df_adj.index[k],'Totalshares']
        if transaction_amount > 0:
            total_cost_prev = df_adj.ix[df_adj.index[k-1], 'AverageCost'] * df_adj.ix[df_adj.index[k-1], 'CumShares']
            df_adj.ix[df_adj.index[k], 'AverageCost'] = (total_cost_prev +  transaction_amount) / df_adj.ix[df_adj.index[k], 'CumShares']
        else:
            df_adj.ix[df_adj.index[k], 'AverageCost'] = df_adj.ix[df_adj.index[k-1], 'AverageCost']
        
    return df_adj[['Date', 'Ticker', 'CumShares', 'AverageCost']].reset_index(drop=True)
        

def resetPort():
    pass


def updatePort():
    pass


#===============================================================================
# Main Script
#===============================================================================

if __name__== "__main__":
    
    account_name = 'DFA_401K'
    
    ################ Pull transaction data
    params = quote_plus("DRIVER={SQL Server}; SERVER=(local); DATABASE=PortMgmt; Trusted_Connection=yes")
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
    
    df_transaction = pd.read_sql(SQL_PULL_HOLDING_POSITION, engine)
    df_transaction.sort_values(by='Date', inplace=True)
    
    # There are multiple transaction type in a given day, must aggregate
    df_position = df_transaction.groupby(['Date','Ticker','SharePrice'])[['Totalshares']].sum()
    df_position.reset_index(inplace=True)
    
    # Get cumulative position
    cum_position_adj = df_position.groupby('Ticker').apply(get_cumsum_adj_and_cost)
    
    df_position = df_position.merge(cum_position_adj, how='left', on=['Date', 'Ticker']) 
    
    ################## Get Price
    start_dt = df_transaction.Date.min()
    
    df_price = pd.read_sql(SQL_PULL_MF_PRICE+'WHERE [Date]>='+'\''+start_dt.strftime('%Y/%m/%d')+'\'', engine) 
    
    busdate = df_price.Date.unique()

    ################# Create daily position ##################
    df_pos_daily = df_position.groupby('Ticker').apply(reindex_by_date, dt=busdate)
    # sdel df_position
    df_pos_daily.reset_index(inplace=True)
    df_pos_daily.sort_values(by=['Date','Ticker'], inplace=True)
    
    # add price
    df_pos_daily = df_pos_daily.merge(df_price, how='left', on=['Date','Ticker'])
    
    df_pos_daily = df_pos_daily[['Date', 'Ticker', 'CumShares', 'Close', 'AverageCost']]
    
    # Add value=$1 for VMMXX, GVMXX
    df_pos_daily.ix[df_pos_daily.Ticker.isin(['GVMXX', 'VMMXX']),'Close'] = 1 
    
    # Check if there is any date with missing price
    date_price_missing = df_pos_daily[df_pos_daily.Close.isnull()].Date.unique()
    
    # Drop date with missing price 
    df_pos_daily = df_pos_daily[~df_pos_daily.Date.isin(date_price_missing)]
    
    # Dollar position
    df_pos_daily['Amount'] = df_pos_daily['CumShares'] * df_pos_daily['Close']
    
    df_pos_daily.query('CumShares!=0', inplace=True)
    
    ################# Contribution ##################
    df_contrib = df_transaction.query('Transaction=="ACH Contribution"')
    df_contrib = df_contrib.groupby(['Date', 'Ticker']).sum()
    
    df_contrib.reset_index(1, inplace=True) 
    
    df_contrib['Date'] = df_contrib.index
    
    df_contrib = df_contrib.merge(df_price, how='left', on=['Date', 'Ticker'])
    
    df_contrib.ix[df_contrib.Ticker.isin(['GVMXX', 'VMMXX']),'Close'] = 1 
    
    df_contrib['Amount'] = df_contrib['Totalshares'] * df_contrib['Close']
    
    df_contrib = df_contrib.groupby('Date')[['Amount']].sum()
    
    ################# Dividend ##########################
    DIV_LIST = ['Ordinary Dividend Reinvestment Increase', 
                'Daily Accrual Dividend Reinvestment Incr',
                'Long Term Capital Gain Reinvestment',
                'Short Term Capital Gain Reinvestment',
                'Earnings Allocation',
                'Increase Earnings']
                
                
    df_dividend = df_transaction.query('Transaction==@DIV_LIST')
    
    df_dividend = df_dividend.groupby(['Date', 'Ticker'])[['Totalshares']].sum()
    
    df_dividend.reset_index(1, inplace=True)
    df_dividend['Date'] = df_dividend.index
    
    df_dividend = df_dividend.merge(df_price, how='left', on=['Date', 'Ticker'])
    
    df_dividend.ix[df_dividend.Ticker.isin(['GVMXX', 'VMMXX']),'Close'] = 1 
    
    df_dividend['Amount'] = df_dividend['Totalshares'] * df_dividend['Close']
    
    df_dividend = df_dividend.groupby('Date')[['Amount']].sum()
    
    
    ################# Daily Table #######################
    
    df_portfolio = DataFrame(index=df_pos_daily.Date.unique(), columns=['Balance', 'Contribution', 'Dividend'])
    
    df_portfolio['Balance'] = df_pos_daily.groupby('Date')['Amount'].sum()
    
    df_portfolio['Contribution'] = df_contrib['Amount']
    df_portfolio.ix[df_portfolio.Contribution.isnull(), 'Contribution'] = 0
    
    df_portfolio['Dividend'] = df_dividend['Amount']
    df_portfolio.ix[df_portfolio.Dividend.isnull(), 'Dividend'] = 0
    
    bal_less_contribution = (df_portfolio['Balance'] - df_portfolio['Contribution']).values 
    bal_initial = df_portfolio.Balance.values
    df_portfolio['Return'] = np.nan
    df_portfolio.ix[1:, 'Return'] = bal_less_contribution[1:] / bal_initial[:-1] - 1
    
    
    ################ Commit to database
    df_portfolio.to_sql(account_name, engine, schema='Portfolio', if_exists='replace', index_label='Date')
    
    df_pos_daily.index = df_pos_daily.Date
    df_pos_daily.drop('Date', axis=1, inplace=True)
    df_pos_daily.to_sql(account_name, engine, schema='Position', if_exists='replace', index_label='Date')
    
    
    
    
    
    
    
    
    
    
    
    
