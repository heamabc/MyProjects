'''
Update database and portfolio position

@author: ywang
'''

from UpdateInputData import getFundData
from UpdateInputData import processTransactionData


#===============================================================================
# Main Script
#===============================================================================

if __name__== "__main__":
    
    # update DFA transaction data
    processTransactionData.updateDatabase(account_name='DFA_401K', year_list=[2017])
    
    getFundData.updateDatabase(account_name='DFA_401K')


 