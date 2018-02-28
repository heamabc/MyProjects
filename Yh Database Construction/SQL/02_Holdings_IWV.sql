-- Creat YFin Database

USE YFinData;
GO

/*
-- Create schema
CREATE SCHEMA Holdings;
GO
*/

/* -- Drop table
DROP TABLE Holdings.R3000_IWV
GO
*/

/*
-- Create Table
CREATE TABLE Holdings.R3000_IWV
	(
	"Date" DATETIME,
    Ticker VARCHAR(20),
    "Name" VARCHAR(50),
	Weight float,
	Sector VARCHAR(30),
	SEDOL VARCHAR(20),
	ISIN VARCHAR(20),
	Exchange VARCHAR(50)
	)
*/


/*
--Create Index
CREATE INDEX idx_hld_r3000_iwv
ON Holdings.R3000_IWV (Date, Ticker);
GO
*/


-- Show Data
SELECT TOP 100 *
FROM Holdings.R3000_IWV
WHERE Ticker = 'NYM'
ORDER BY [Date], [Weight] desc

SELECT [Date], COUNT(Ticker) AS NameCount
FROM Holdings.R3000_IWV
GROUP BY [Date]
ORDER BY [Date]

/*
-- Delete data
DELETE 
FROM Holdings.R3000_IWV
WHERE [Date] = '2017/12/29'
*/
