'''
Script to pull data

Created on Jan 10, 2018

@author: ywang
'''

sql_example = '''
    SELECT *
    FROM Stock.US
    WHERE Ticker = 'GSK'
    ORDER BY [Date]
    '''