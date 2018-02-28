-- Creat YFin Database

USE YFinData;
GO

/*
-- Create schema
CREATE SCHEMA Stock;
GO
*/

/* -- Drop table
DROP TABLE Stock.US
GO
*/

/*
-- Create Table
CREATE TABLE Stock.US
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
CREATE INDEX idx_stk_us
ON Stock.US (Date, Ticker);
GO
*/


-- Show Data
SELECT TOP 100 *
FROM Stock.US
ORDER BY [Date]

SELECT * 
FROM Stock.US
WHERE [Date] = '2018/1/4'
ORDER BY DailyTotalRet

SELECT *
FROM Stock.US
WHERE Ticker = 'JNJ'
ORDER BY [Date]

SELECT Ticker, MIN([Date]) AS StartDate, MAX([Date]) AS EndDate
FROM Stock.US
GROUP BY Ticker
ORDER BY Ticker

/*
-- Delete data
DELETE 
FROM Stock.US
WHERE Ticker = 'BRKB'
*/
