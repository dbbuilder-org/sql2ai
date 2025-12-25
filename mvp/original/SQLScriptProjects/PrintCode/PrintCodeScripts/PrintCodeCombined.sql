use SVDB_v2025_06_30_1

go

-- PrintCode combined script
-- Contains the following stored procedures:
-- 1. PrintCode_Print - Main procedure that handles the object code extraction and formatting
-- 2. PrintCode_ExtendedProperties - Handles extended properties extraction and processing
-- 3. PrintCode_Header - Handles header comment creation
-- 4. PrintCode - Wrapper procedure that chooses the appropriate implementation
-- 5. PrintCodeVersion - Reports the current version number

-- First, create the user-defined table type for changes
CREATE TYPE dbo.ChangesTableType AS TABLE
(
    ChangeDate NVARCHAR(50),
    ChangeAuthor NVARCHAR(100),
    ChangeDescription NVARCHAR(MAX),
    SortOrder INT IDENTITY(1,1)
)
GO

-- Next, create the PrintCodeVersion procedure

CREATE OR ALTER PROCEDURE [dbo].[PrintCodeVersion]
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Define the current version
    DECLARE @MajorVersion INT = 1
    DECLARE @MinorVersion INT = 0
    DECLARE @PatchVersion INT = 0
    DECLARE @VersionString NVARCHAR(50)
    
    -- Build the version string
    SET @VersionString = CAST(@MajorVersion AS NVARCHAR(10)) + '.' + 
                         CAST(@MinorVersion AS NVARCHAR(10)) + '.' + 
                         CAST(@PatchVersion AS NVARCHAR(10))
    
    -- Print the version information
    PRINT '--------------------------------------------------------'
    PRINT 'PrintCode System Version: ' + @VersionString
    PRINT 'Release Date: 2025-05-31'
    PRINT '--------------------------------------------------------'
    
    RETURN 0
END
GO-- Next, create the PrintCode_ExtendedProperties procedure

CREATE OR ALTER PROCEDURE [dbo].[PrintCode_ExtendedProperties]
    @Object_ID INT,
    @database_name SYSNAME,
    @SchemaName SYSNAME,
    @ActualObjectName SYSNAME,
    @ObjectType NVARCHAR(60),
    @PreviewMode BIT = 0,
    @MetaSection NVARCHAR(MAX) OUTPUT,
    @CodeReviewSection NVARCHAR(MAX) OUTPUT,
    @VersionSection NVARCHAR(MAX) OUTPUT,
    @ReleaseNotesSection NVARCHAR(MAX) OUTPUT,
    @OtherSection NVARCHAR(MAX) OUTPUT,
    @AllChanges dbo.ChangesTableType READONLY
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Initialize output variables
    SET @MetaSection = ''
    SET @CodeReviewSection = ''
    SET @VersionSection = ''
    SET @ReleaseNotesSection = ''
    SET @OtherSection = ''
    
    -- Step 1: Get the extended properties using simple dynamic SQL
    DECLARE @GetPropertiesSQL NVARCHAR(MAX) = N'
    USE [' + @database_name + ']
    SELECT 
        ep.name as PropertyName,
        CONVERT(NVARCHAR(MAX), ep.value) as PropertyValue
    FROM [' + @database_name + '].sys.extended_properties ep
    WHERE ep.major_id = ' + CAST(@Object_ID AS VARCHAR(10)) + '
        AND ep.minor_id = 0
    ORDER BY ep.name'
    
    PRINT 'Getting extended properties...'
    IF @PreviewMode = 1
        PRINT @GetPropertiesSQL
    
    -- Temp table to store properties
    DECLARE @PropertiesTable TABLE (
        PropertyName NVARCHAR(128),
        PropertyValue NVARCHAR(MAX)
    )
    
    -- Execute the query
    INSERT INTO @PropertiesTable
    EXEC (@GetPropertiesSQL)    
    -- Process the extended properties
    DECLARE @PropertyName NVARCHAR(128)
    DECLARE @PropertyValue NVARCHAR(MAX)
    DECLARE @FormattedName NVARCHAR(128)
    
    -- Create a table to store changes to be added to the database
    DECLARE @ChangesToAdd TABLE (
        ChangeName NVARCHAR(128),
        ChangeValue NVARCHAR(MAX)
    )
    
    -- Process each extended property using a cursor
    DECLARE property_cursor CURSOR FOR
    SELECT PropertyName, PropertyValue FROM @PropertiesTable
    
    OPEN property_cursor
    FETCH NEXT FROM property_cursor INTO @PropertyName, @PropertyValue
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        SET @FormattedName = @PropertyName
        
        -- Handle meta* properties
        IF LOWER(LEFT(@PropertyName, 4)) = 'meta' AND LEN(@PropertyName) > 4
        BEGIN
            SET @FormattedName = SUBSTRING(@PropertyName, 5, 100)
            SET @FormattedName = REPLACE(REPLACE(@FormattedName, '_', ' '), '-', ' ')
            IF LEN(@FormattedName) > 0
                SET @FormattedName = UPPER(LEFT(@FormattedName, 1)) + LOWER(SUBSTRING(@FormattedName, 2, 100))
            SET @MetaSection = @MetaSection + '  ' + @FormattedName + ': ' + ISNULL(@PropertyValue, '(null)') + CHAR(13) + CHAR(10)
        END
        ELSE
        BEGIN
            -- Handle Changes-* properties
            IF LOWER(LEFT(@PropertyName, 8)) = 'changes-' AND LEN(@PropertyName) > 8
            BEGIN
                -- We don't process these here - they are handled by the calling procedure
                -- Just store the property in the output table
                INSERT INTO @ChangesToAdd (ChangeName, ChangeValue)
                VALUES (@PropertyName, @PropertyValue)
            END            -- Handle code-review* or code_review* properties  
            ELSE IF (LOWER(LEFT(@PropertyName, 11)) = 'code-review' OR LOWER(LEFT(@PropertyName, 11)) = 'code_review') AND LEN(@PropertyName) > 11
            BEGIN
                SET @FormattedName = SUBSTRING(@PropertyName, 12, 100)
                SET @FormattedName = REPLACE(REPLACE(@FormattedName, '_', ' '), '-', ' ')
                IF LEN(@FormattedName) > 0
                    SET @FormattedName = UPPER(LEFT(@FormattedName, 1)) + LOWER(SUBSTRING(@FormattedName, 2, 100))
                SET @CodeReviewSection = @CodeReviewSection + '  ' + @FormattedName + ': ' + ISNULL(@PropertyValue, '(null)') + CHAR(13) + CHAR(10)
            END
            ELSE
            BEGIN
                -- Handle version* properties
                IF LOWER(LEFT(@PropertyName, 7)) = 'version' AND LEN(@PropertyName) > 7
                BEGIN
                    SET @FormattedName = SUBSTRING(@PropertyName, 8, 100)

                    SET @FormattedName = REPLACE(REPLACE(@FormattedName, '_', ' '), '-', ' ')
                    IF LEN(@FormattedName) > 0
                        SET @FormattedName = UPPER(LEFT(@FormattedName, 1)) + LOWER(SUBSTRING(@FormattedName, 2, 100))
                    SET @VersionSection = @VersionSection + '  ' + @FormattedName + ': ' + ISNULL(@PropertyValue, '(null)') + CHAR(13) + CHAR(10)
                END
                ELSE
                BEGIN
                    -- Handle RELEASE_NOTES* properties
                    IF UPPER(LEFT(@PropertyName, 13)) = 'RELEASE_NOTES' AND LEN(@PropertyName) > 13
                    BEGIN
                        SET @FormattedName = SUBSTRING(@PropertyName, 14, 100)
                        SET @FormattedName = REPLACE(REPLACE(@FormattedName, '_', ' '), '-', ' ')
                        IF LEN(@FormattedName) > 0
                            SET @FormattedName = UPPER(LEFT(@FormattedName, 1)) + LOWER(SUBSTRING(@FormattedName, 2, 100))
                        SET @ReleaseNotesSection = @ReleaseNotesSection + '  ' + @FormattedName + ': ' + ISNULL(@PropertyValue, '(null)') + CHAR(13) + CHAR(10)
                    END                    ELSE
                    BEGIN
                        -- Handle all other properties
                        SET @FormattedName = REPLACE(REPLACE(@PropertyName, '_', ' '), '-', ' ')
                        IF LEN(@FormattedName) > 0
                            SET @FormattedName = UPPER(LEFT(@FormattedName, 1)) + LOWER(SUBSTRING(@FormattedName, 2, 100))
                        SET @OtherSection = @OtherSection + '  ' + @FormattedName + ': ' + ISNULL(@PropertyValue, '(null)') + CHAR(13) + CHAR(10)
                    END
                END
            END
        END
        
        FETCH NEXT FROM property_cursor INTO @PropertyName, @PropertyValue
    END
    
    CLOSE property_cursor
    DEALLOCATE property_cursor
    
    -- Return the generated SQL for adding new properties
    DECLARE @AddChangesSQL NVARCHAR(MAX) = ''
    DECLARE @CurrentDate NVARCHAR(50) = CONVERT(NVARCHAR(50), GETDATE(), 120)
    DECLARE @CurrentUser NVARCHAR(128) = SYSTEM_USER
    
    -- Create a new extended property for the current change
    -- This will be executed in the output if ExecuteMode is enabled
    SET @AddChangesSQL = N'
    USE [' + @database_name + ']
    IF NOT EXISTS (
        SELECT 1 FROM sys.extended_properties 
        WHERE major_id = ' + CAST(@Object_ID AS VARCHAR(10)) + ' 
        AND minor_id = 0 
        AND name = ''Changes-' + @CurrentDate + '''
    )    BEGIN
        EXEC sys.sp_addextendedproperty 
            @name = N''Changes-' + @CurrentDate + ''', 
            @value = N''  - ' + @CurrentDate + ' ' + @CurrentUser + ': Code extracted with extended properties header'', 
            @level0type = N''SCHEMA'', 
            @level0name = N''' + @SchemaName + ''', 
            @level1type = N''' + 
                CASE 
                    WHEN @ObjectType = 'SQL_STORED_PROCEDURE' THEN 'PROCEDURE'
                    WHEN @ObjectType = 'SQL_SCALAR_FUNCTION' OR 
                         @ObjectType = 'SQL_TABLE_VALUED_FUNCTION' OR
                         @ObjectType = 'SQL_INLINE_TABLE_VALUED_FUNCTION' THEN 'FUNCTION'
                    WHEN @ObjectType = 'VIEW' THEN 'VIEW'
                    WHEN @ObjectType = 'SQL_TRIGGER' THEN 'TRIGGER'
                    WHEN @ObjectType = 'USER_TABLE' THEN 'TABLE'
                    WHEN @ObjectType = 'SEQUENCE_OBJECT' THEN 'SEQUENCE'
                    ELSE ''
                END + ''', 
            @level1name = N''' + @ActualObjectName + '''
    END'
    
    -- Return the SQL for adding the current change
    RETURN 0
END
GO

-- Next, create the PrintCode_Header procedure
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
GO
 
-- Finally, create the PrintCode wrapper procedure

CREATE OR ALTER PROCEDURE [dbo].[PrintCode]
    @object_name NVARCHAR(261),
    @database_name SYSNAME = NULL,
    @PreviewMode BIT = 0,
    @ExecuteMode BIT = 1,
    @PrintOutCode BIT = 1,
    @sqlText NVARCHAR(MAX) = NULL OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    
    PRINT 'PrintCode wrapper procedure executing...'
    
    -- Call the version procedure to display current version
    EXEC [dbo].[PrintCodeVersion]
    
    -- Call the main implementation procedure
    EXEC [dbo].[PrintCode_Print]
        @object_name = @object_name,
        @database_name = @database_name,
        @PreviewMode = @PreviewMode,
        @ExecuteMode = @ExecuteMode,
        @PrintOutCode = @PrintOutCode,
        @sqlText = @sqlText OUTPUT
    
    RETURN 0
END
GO

go 

[PrintCode] 'GenerateUserKey'