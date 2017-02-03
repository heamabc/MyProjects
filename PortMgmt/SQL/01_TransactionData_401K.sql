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
ON TransactionData.FourOhOneK (TradeDate, Ticker);
GO

-- Show Data
SELECT TOP 100 *
FROM TransactionData.FourOhOneK

-- Delete data
DELETE 
FROM TransactionData.FourOhOneK
*/
