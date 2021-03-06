
USE PortMgmt;
GO

/*
CREATE SCHEMA Portfolio;
GO

CREATE SCHEMA Position;
GO
*/

/*
DROP SCHEMA Portfolio;
GO

DROP SCHEMA Position;
GO

*/



DROP TABLE Portfolio.DFA_401K;
GO

DROP TABLE Position.DFA_401K;
GO


CREATE TABLE Portfolio.DFA_401K 
	(
	Date DATETIME,
    Balance float,
	Contribution float,
	Dividend float,
	"Return" float
	)

CREATE TABLE Position.DFA_401K
	(
	"Date" DATETIME,
	Ticker VARCHAR(20),
	CumShares float,
	"Close" float,
	AverageCost float,
	Amount float
	)




CREATE INDEX idx_port_dfa_dt
ON Portfolio.DFA_401K (Date);
GO


CREATE INDEX idx_position_dfa_dt_ticker
ON Position.DFA_401K (Date, Ticker);
GO


