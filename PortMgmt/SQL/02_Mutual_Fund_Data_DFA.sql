-- Creat PortMgmt database

USE PortMgmt;
GO

/*
-- Create schema
CREATE SCHEMA MutualFundData;
GO
*/

/* -- Drop table
DROP TABLE MutualFundData.DFA_401K
GO
*/

/*
-- Create Table
CREATE TABLE MutualFundData.DFA_401K 
	(
	"Date" DATETIME,
    Ticker VARCHAR(20),
    "Open" float,
    High float,
    Low float,
	"Close" float,
	Volume float,
	AdjClose float
	)
*/


/*
--Create Index
CREATE INDEX idx_mf_dfa
ON MutualFundData.DFA_401K (Date, Ticker);
GO

-- Show Data
SELECT TOP 100 *
FROM MutualFundData.DFA_401K

-- Delete data
DELETE 
FROM MutualFundData.DFA_401K
*/
