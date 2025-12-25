use SVDB_v2025_06_30_1

go
CREATE OR ALTER PROCEDURE [dbo].[PrintCode_Header]
    @FormattedObjectType NVARCHAR(60),
    @ActualObjectName NVARCHAR(128),
    @SchemaName NVARCHAR(128),
    @database_name SYSNAME,
    @CreatedDate NVARCHAR(50),
    @CurrentDate NVARCHAR(50),
    @CurrentUser NVARCHAR(128),
    @ExtendedPropertiesSection NVARCHAR(MAX),
    @ChangesPreviousSection NVARCHAR(MAX),
    @ChangesHeaderSection NVARCHAR(MAX),
    @HeaderComment NVARCHAR(MAX) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Build the header comment with grouped extended properties
    SET @HeaderComment = 
        '/*' + CHAR(13) + CHAR(10) +
        '============================================================================' + CHAR(13) + CHAR(10) +
        @FormattedObjectType + ': ' + @ActualObjectName + CHAR(13) + CHAR(10) +
        'Schema: ' + @SchemaName + CHAR(13) + CHAR(10) +
        'Database: ' + @database_name + CHAR(13) + CHAR(10) +
        '----------------------------------------------------------------------------' + CHAR(13) + CHAR(10) +
        'Date Created: ' + ISNULL(@CreatedDate, 'Not available') + CHAR(13) + CHAR(10) +
        'Date Modified: ' + @CurrentDate + CHAR(13) + CHAR(10) +
        'Current User: ' + @CurrentUser + CHAR(13) + CHAR(10)
    
    -- Add extended properties section if any
    IF LEN(@ExtendedPropertiesSection) > 0
        SET @HeaderComment = @HeaderComment + 
            '----------------------------------------------------------------------------' + CHAR(13) + CHAR(10) +
            @ExtendedPropertiesSection
    
    -- Add changes previous section if any
    IF LEN(@ChangesPreviousSection) > 0
        SET @HeaderComment = @HeaderComment + 
            '----------------------------------------------------------------------------' + CHAR(13) + CHAR(10) +
            'Changes Previous: ' + CHAR(13) + CHAR(10) +
            @ChangesPreviousSection
    
    -- Add changes made section
    SET @HeaderComment = @HeaderComment +
        '----------------------------------------------------------------------------' + CHAR(13) + CHAR(10) +
        'Changes Made: ([Date] [Author]: [Description of changes])' + CHAR(13) + CHAR(10) +
        @ChangesHeaderSection +
        '============================================================================' + CHAR(13) + CHAR(10) +
        '*/' + CHAR(13) + CHAR(10) + CHAR(13) + CHAR(10)
    
    RETURN 0
END