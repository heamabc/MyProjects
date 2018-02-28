-- Creat YFin Database

USE YFinData;
GO

/*
-- Create schema
CREATE SCHEMA Holdings;
GO
*/

/* -- Drop table
DROP TABLE Holdings.ADR
GO
*/

/*
-- Create Table
CREATE TABLE Holdings.ADR
	(
	FundTicker VARCHAR(10),
	SecurityNum VARCHAR(20),
	Ticker VARCHAR(20),
	Weight float,
	"Name" VARCHAR(50), 
	Sector VARCHAR(30),
	"Date" DATETIME
	)
*/


/*
--Create Index
CREATE INDEX idx_hld_adr
ON Holdings.ADR (FundTicker, Date, Ticker);
GO
*/


-- Show Data
SELECT TOP 100 *
FROM Holdings.ADR
--WHERE Ticker = 'NYM'
ORDER BY [Date], [Weight] desc

SELECT [Date], COUNT(Ticker) AS NameCount
FROM Holdings.ADR
GROUP BY [Date], [FundTicker]
ORDER BY [Date], [FundTicker]

/*
-- Delete data
DELETE 
FROM Holdings.ADR
WHERE [Date] = '2017/12/29'
*/
