-- Creat YFin Database

USE YFinData;
GO

/*
-- Create schema
CREATE SCHEMA Stock;
GO
*/

/* -- Drop table
DROP TABLE Stock.ADR
GO
*/

/*
-- Create Table
CREATE TABLE Stock.ADR
	(
	"Date" DATETIME,
    Ticker VARCHAR(20),
    "Open" float,
    High float,
    Low float,
	"Close" float,
	Volume float,
	DailyTotalRet float
	)
*/


/*
--Create Index
CREATE INDEX idx_stk_adr
ON Stock.US (Date, Ticker);
GO
*/


-- Show Data
SELECT TOP 100 *
FROM Stock.ADR
ORDER BY [Date]

SELECT * 
FROM Stock.ADR
WHERE [Date] = '2018/1/8'
ORDER BY DailyTotalRet

SELECT *
FROM Stock.ADR
WHERE Ticker = 'WB'
ORDER BY [Date]

SELECT Ticker, MIN([Date]) AS StartDate, MAX([Date]) AS EndDate
FROM Stock.ADR
GROUP BY Ticker
ORDER BY Ticker

SELECT YEAR(Date), AVG(DailyTotalRet)*250 AS AnnualRet
FROM Stock.ADR
WHERE Ticker = 'WB'
GROUP BY YEAR(Date)
ORDER BY YEAR(Date)

/*
-- Delete data
DELETE 
FROM Stock.ADR
WHERE Ticker = 'BRKB'
*/
