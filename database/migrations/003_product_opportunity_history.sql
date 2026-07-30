USE FiltrifyAI;
GO

IF OBJECT_ID('ProductOpportunityHistory', 'U') IS NULL
BEGIN
    CREATE TABLE ProductOpportunityHistory (
        OpportunityHistoryID BIGINT IDENTITY(1,1) PRIMARY KEY,
        ProductID INT NOT NULL,

        OpportunityScore DECIMAL(8,2) NOT NULL,
        EPC DECIMAL(18,4) NULL,
        GravityScore DECIMAL(18,4) NULL,
        SearchVolume INT NULL,
        CompetitionScore DECIMAL(8,2) NULL,
        EstimatedCPC DECIMAL(18,4) NULL,
        GoogleTrendScore DECIMAL(8,2) NULL,
        RefundRate DECIMAL(8,2) NULL,

        RecordedAt DATETIME2 NOT NULL
            CONSTRAINT DF_ProductOpportunityHistory_RecordedAt
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_ProductOpportunityHistory_Products
            FOREIGN KEY (ProductID)
            REFERENCES Products(ProductID)
            ON DELETE CASCADE
    );
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'IX_ProductOpportunityHistory_ProductID_RecordedAt'
      AND object_id = OBJECT_ID('ProductOpportunityHistory')
)
BEGIN
    CREATE INDEX IX_ProductOpportunityHistory_ProductID_RecordedAt
    ON ProductOpportunityHistory (
        ProductID,
        RecordedAt DESC
    );
END;
GO