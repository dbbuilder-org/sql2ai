-- First create the user-defined table type
CREATE TYPE dbo.ChangesTableType AS TABLE
(
    ChangeDate NVARCHAR(50),
    ChangeAuthor NVARCHAR(100),
    ChangeDescription NVARCHAR(MAX),
    SortOrder INT IDENTITY(1,1)
)
GO

-- Then modify the procedure to use the user-defined table type
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
            END
            -- Handle code-review* or code_review* properties  
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
                    END
                    ELSE
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
    -- Check if a property with this value already exists regardless of name
    IF NOT EXISTS (
        SELECT 1 FROM sys.extended_properties 
        WHERE major_id = ' + CAST(@Object_ID AS VARCHAR(10)) + ' 
        AND minor_id = 0 
        AND CONVERT(NVARCHAR(MAX), value) = N''  - ' + @CurrentDate + ' ' + @CurrentUser + ': Code extracted with extended properties header''
    )
    BEGIN
        -- Store the new UUID in a variable so it's consistent
        DECLARE @NewChangeID NVARCHAR(36) = CAST(NEWID() AS NVARCHAR(36))
        
        EXEC sys.sp_addextendedproperty 
            @name = N''Changes-' + @CurrentDate + '-'' + @NewChangeID, 
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