-- Creat PortMgmt database

USE PortMgmt;
GO

/*
-- Create schema
CREATE SCHEMA TransactionData;
GO
*/

/* -- Drop table
DROP TABLE TransactionData.Four
GO
*/

/*
-- Create Table
CREATE TABLE TransactionData.FourOhOneK 
	(
	TradeDate DATETIME,
    Investments VARCHAR(100),
    Ticker VARCHAR(20),
    "Transaction" VARCHAR(100),
    TransactionAmount float,
    SharePrice float,
    Totalshares float
	)
*/


/*
--Create Index
CREATE INDEX idx_t401k
ON TransactionData.DFA_401K (TradeDate, Ticker);
GO

-- Show Data
SELECT TOP 100 *
FROM TransactionData.DFA_401K

-- Delete data
DELETE 
FROM TransactionData.DFA_401K
*/
