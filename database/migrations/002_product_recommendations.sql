USE FiltrifyAI;
GO

IF OBJECT_ID('ProductRecommendations', 'U') IS NULL
BEGIN
    CREATE TABLE ProductRecommendations (
        RecommendationID BIGINT IDENTITY(1,1) PRIMARY KEY,
        ProductID INT NOT NULL,

        OpportunityScore DECIMAL(8,2) NOT NULL,
        OpportunityLevel NVARCHAR(30) NOT NULL,
        RiskLevel NVARCHAR(30) NOT NULL,
        Difficulty NVARCHAR(30) NOT NULL,
        RecommendedChannel NVARCHAR(50) NOT NULL,
        ExpectedROI NVARCHAR(30) NOT NULL,
        RecommendedBudget DECIMAL(18,2) NOT NULL DEFAULT 0,

        Reasoning NVARCHAR(MAX),
        NextActions NVARCHAR(MAX),

        CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_ProductRecommendations_Products
            FOREIGN KEY (ProductID)
            REFERENCES Products(ProductID)
            ON DELETE CASCADE
    );
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'IX_ProductRecommendations_ProductID_CreatedAt'
      AND object_id = OBJECT_ID('ProductRecommendations')
)
BEGIN
    CREATE INDEX IX_ProductRecommendations_ProductID_CreatedAt
    ON ProductRecommendations(ProductID, CreatedAt DESC);
END;
GO