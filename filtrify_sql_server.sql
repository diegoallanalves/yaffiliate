IF DB_ID('FiltrifyAI') IS NULL
BEGIN
    CREATE DATABASE FiltrifyAI;
END;
GO

USE FiltrifyAI;
GO

-------------------------------------------------------

CREATE TABLE AffiliateNetworks (
    NetworkID INT IDENTITY(1,1) PRIMARY KEY,
    NetworkName NVARCHAR(100) NOT NULL UNIQUE,
    WebsiteURL NVARCHAR(500),
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

CREATE TABLE Products (
    ProductID INT IDENTITY(1,1) PRIMARY KEY,
    NetworkID INT NULL,

    ProductName NVARCHAR(250) NOT NULL,
    Category NVARCHAR(150),
    LanguageCode NVARCHAR(20),
    CountryCode NVARCHAR(10),

    Price DECIMAL(18,2) NOT NULL DEFAULT 0,
    CommissionAmount DECIMAL(18,2) NOT NULL DEFAULT 0,
    CommissionPercent DECIMAL(8,2) NOT NULL DEFAULT 0,

    SalesPageURL NVARCHAR(1000),
    AffiliateURL NVARCHAR(1000),

    Status NVARCHAR(30) NOT NULL DEFAULT 'Research',
    Notes NVARCHAR(MAX),

    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_Products_AffiliateNetworks
        FOREIGN KEY (NetworkID)
        REFERENCES AffiliateNetworks(NetworkID),

    CONSTRAINT CK_Products_Status
        CHECK (
            Status IN (
                'Research',
                'Shortlist',
                'Testing',
                'Active',
                'Paused',
                'Rejected',
                'Archived'
            )
        )
);
GO

--------------------------------------------------------

CREATE TABLE ProductMetrics (
    ProductMetricID BIGINT IDENTITY(1,1) PRIMARY KEY,
    ProductID INT NOT NULL,

    EPC DECIMAL(18,4),
    GravityScore DECIMAL(18,4),
    SearchVolume INT,
    CompetitionScore DECIMAL(8,2),
    EstimatedCPC DECIMAL(18,4),
    GoogleTrendScore DECIMAL(8,2),
    RefundRate DECIMAL(8,2),

    OpportunityScore DECIMAL(8,2),
    MetricDate DATE NOT NULL DEFAULT CAST(GETUTCDATE() AS DATE),
    DataSource NVARCHAR(100),

    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_ProductMetrics_Products
        FOREIGN KEY (ProductID)
        REFERENCES Products(ProductID)
        ON DELETE CASCADE
);
GO

----------------------------------------------------------------------------

CREATE TABLE Keywords (
    KeywordID BIGINT IDENTITY(1,1) PRIMARY KEY,
    KeywordText NVARCHAR(500) NOT NULL,
    LanguageCode NVARCHAR(20),
    CountryCode NVARCHAR(10),
    SearchIntent NVARCHAR(30),

    SearchVolume INT,
    EstimatedCPC DECIMAL(18,4),
    CompetitionScore DECIMAL(8,2),
    TrendScore DECIMAL(8,2),

    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT CK_Keywords_SearchIntent
        CHECK (
            SearchIntent IS NULL OR
            SearchIntent IN (
                'Informational',
                'Commercial',
                'Transactional',
                'Navigational'
            )
        )
);
GO

CREATE TABLE ProductKeywords (
    ProductID INT NOT NULL,
    KeywordID BIGINT NOT NULL,

    KeywordStatus NVARCHAR(30) NOT NULL DEFAULT 'Idea',
    RelevanceScore DECIMAL(8,2),
    IsNegative BIT NOT NULL DEFAULT 0,

    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT PK_ProductKeywords
        PRIMARY KEY (ProductID, KeywordID),

    CONSTRAINT FK_ProductKeywords_Products
        FOREIGN KEY (ProductID)
        REFERENCES Products(ProductID)
        ON DELETE CASCADE,

    CONSTRAINT FK_ProductKeywords_Keywords
        FOREIGN KEY (KeywordID)
        REFERENCES Keywords(KeywordID)
        ON DELETE CASCADE
);
GO

--------------------------------------------------------------

CREATE TABLE ContentAssets (
    ContentAssetID BIGINT IDENTITY(1,1) PRIMARY KEY,
    ProductID INT NOT NULL,

    AssetType NVARCHAR(50) NOT NULL,
    AssetTitle NVARCHAR(250),
    PromptText NVARCHAR(MAX),
    GeneratedContent NVARCHAR(MAX),

    AIProvider NVARCHAR(50),
    AIModel NVARCHAR(100),

    ApprovalStatus NVARCHAR(30) NOT NULL DEFAULT 'Draft',
    ApprovedAt DATETIME2,
    PublishedAt DATETIME2,

    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_ContentAssets_Products
        FOREIGN KEY (ProductID)
        REFERENCES Products(ProductID)
        ON DELETE CASCADE,

    CONSTRAINT CK_ContentAssets_AssetType
        CHECK (
            AssetType IN (
                'ProductAnalysis',
                'SEOArticle',
                'SEOBrief',
                'EmailSequence',
                'GoogleAd',
                'FacebookAd',
                'LandingPageCopy',
                'KeywordCluster'
            )
        ),

    CONSTRAINT CK_ContentAssets_ApprovalStatus
        CHECK (
            ApprovalStatus IN (
                'Draft',
                'Review',
                'Approved',
                'Rejected',
                'Published'
            )
        )
);
GO

--------------------------------------------------------------

CREATE TABLE LandingPages (
    LandingPageID BIGINT IDENTITY(1,1) PRIMARY KEY,
    ProductID INT NOT NULL,

    PageName NVARCHAR(250) NOT NULL,
    Slug NVARCHAR(250),
    PageURL NVARCHAR(1000),
    LocalFilePath NVARCHAR(1000),
    HTMLContent NVARCHAR(MAX),

    Status NVARCHAR(30) NOT NULL DEFAULT 'Draft',

    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_LandingPages_Products
        FOREIGN KEY (ProductID)
        REFERENCES Products(ProductID)
        ON DELETE CASCADE
);
GO

------------------------------------------------------------------------------

CREATE TABLE AdCampaigns (
    CampaignID BIGINT IDENTITY(1,1) PRIMARY KEY,
    ProductID INT NOT NULL,

    Platform NVARCHAR(30) NOT NULL,
    CampaignName NVARCHAR(250) NOT NULL,
    ExternalCampaignID NVARCHAR(250),

    Budget DECIMAL(18,2) NOT NULL DEFAULT 0,
    Spend DECIMAL(18,2) NOT NULL DEFAULT 0,
    Clicks INT NOT NULL DEFAULT 0,
    Conversions INT NOT NULL DEFAULT 0,
    Revenue DECIMAL(18,2) NOT NULL DEFAULT 0,

    Status NVARCHAR(30) NOT NULL DEFAULT 'Draft',

    StartDate DATE,
    EndDate DATE,

    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_AdCampaigns_Products
        FOREIGN KEY (ProductID)
        REFERENCES Products(ProductID)
        ON DELETE CASCADE,

    CONSTRAINT CK_AdCampaigns_Platform
        CHECK (
            Platform IN (
                'GoogleAds',
                'MetaAds',
                'TikTokAds',
                'MicrosoftAds'
            )
        )
);
GO

-------------------------------------------------------------------

CREATE TABLE TrackingPixels (
    TrackingPixelID BIGINT IDENTITY(1,1) PRIMARY KEY,
    ProductID INT NOT NULL,

    Platform NVARCHAR(50) NOT NULL,
    PixelName NVARCHAR(250),
    ExternalPixelID NVARCHAR(250),

    IsActive BIT NOT NULL DEFAULT 1,

    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_TrackingPixels_Products
        FOREIGN KEY (ProductID)
        REFERENCES Products(ProductID)
        ON DELETE CASCADE
);
GO

----------------------------------------------------------------------------------------------

CREATE TABLE CampaignScenarios (
    ScenarioID BIGINT IDENTITY(1,1) PRIMARY KEY,
    ProductID INT NULL,

    ScenarioName NVARCHAR(250),
    Budget DECIMAL(18,2) NOT NULL,
    CPC DECIMAL(18,4) NOT NULL,
    ConversionRate DECIMAL(10,6) NOT NULL,
    CommissionAmount DECIMAL(18,2) NOT NULL,

    EstimatedClicks DECIMAL(18,2),
    EstimatedSales DECIMAL(18,2),
    EstimatedRevenue DECIMAL(18,2),
    EstimatedProfit DECIMAL(18,2),
    ROAS DECIMAL(18,4),
    ROI DECIMAL(18,4),
    BreakEvenConversionRate DECIMAL(10,6),

    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_CampaignScenarios_Products
        FOREIGN KEY (ProductID)
        REFERENCES Products(ProductID)
        ON DELETE SET NULL
);
GO

---------------------------------------------------------------------------------------

INSERT INTO AffiliateNetworks (NetworkName, WebsiteURL)
VALUES
    ('Hotmart', 'https://www.hotmart.com'),
    ('Monetizze', 'https://www.monetizze.com.br'),
    ('Eduzz', 'https://www.eduzz.com'),
    ('ClickBank', 'https://www.clickbank.com'),
    ('Digistore24', 'https://www.digistore24.com'),
    ('Amazon Associates', 'https://affiliate-program.amazon.com');
GO

----------------------------------------------------------------------------------------------

SELECT *
FROM AffiliateNetworks;

--------------------------------------------------------------------------------------------

CREATE INDEX IX_Products_ProductName
ON Products(ProductName);

CREATE INDEX IX_Products_Status
ON Products(Status);

CREATE INDEX IX_ProductMetrics_ProductID_MetricDate
ON ProductMetrics(ProductID, MetricDate DESC);

CREATE INDEX IX_Keywords_KeywordText
ON Keywords(KeywordText);

CREATE INDEX IX_ContentAssets_ProductID_AssetType
ON ContentAssets(ProductID, AssetType);

CREATE INDEX IX_AdCampaigns_ProductID_Platform
ON AdCampaigns(ProductID, Platform);
GO

-------------------------------------------------------------------------------------------

CREATE VIEW vw_ProductOpportunitySummary
AS
SELECT
    p.ProductID,
    p.ProductName,
    n.NetworkName,
    p.Category,
    p.LanguageCode,
    p.CountryCode,
    p.Price,
    p.CommissionAmount,
    p.CommissionPercent,
    p.Status,

    metrics.EPC,
    metrics.GravityScore,
    metrics.SearchVolume,
    metrics.CompetitionScore,
    metrics.EstimatedCPC,
    metrics.GoogleTrendScore,
    metrics.RefundRate,
    metrics.OpportunityScore,
    metrics.MetricDate

FROM Products p

LEFT JOIN AffiliateNetworks n
    ON n.NetworkID = p.NetworkID

OUTER APPLY (
    SELECT TOP 1
        pm.EPC,
        pm.GravityScore,
        pm.SearchVolume,
        pm.CompetitionScore,
        pm.EstimatedCPC,
        pm.GoogleTrendScore,
        pm.RefundRate,
        pm.OpportunityScore,
        pm.MetricDate
    FROM ProductMetrics pm
    WHERE pm.ProductID = p.ProductID
    ORDER BY pm.MetricDate DESC, pm.ProductMetricID DESC
) metrics;
GO

-------------------------------------------------------------------------------------------

SELECT *
FROM vw_ProductOpportunitySummary;

-------------------------------------------------------------------------------------------

SELECT name
FROM sys.databases
WHERE name = 'FiltrifyAI';