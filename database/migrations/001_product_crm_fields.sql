USE FiltrifyAI;
GO

IF COL_LENGTH('Products', 'FacebookAdsLibraryURL') IS NULL
BEGIN
    ALTER TABLE Products
    ADD FacebookAdsLibraryURL NVARCHAR(1000) NULL;
END;
GO

IF COL_LENGTH('Products', 'GoogleAdsTransparencyURL') IS NULL
BEGIN
    ALTER TABLE Products
    ADD GoogleAdsTransparencyURL NVARCHAR(1000) NULL;
END;
GO

IF COL_LENGTH('Products', 'TargetAudience') IS NULL
BEGIN
    ALTER TABLE Products
    ADD TargetAudience NVARCHAR(MAX) NULL;
END;
GO

IF COL_LENGTH('Products', 'MainBenefits') IS NULL
BEGIN
    ALTER TABLE Products
    ADD MainBenefits NVARCHAR(MAX) NULL;
END;
GO