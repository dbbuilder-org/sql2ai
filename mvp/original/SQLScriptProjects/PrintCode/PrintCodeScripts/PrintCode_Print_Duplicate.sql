CREATE OR ALTER PROCEDURE [dbo].[PrintCode_Print]
    @object_name NVARCHAR(261),
    @database_name SYSNAME = NULL,
    @PreviewMode BIT = 0,
    @ExecuteMode BIT = 1,
    @PrintOutCode BIT = 1,
    @sqlText NVARCHAR(MAX) = NULL OUTPUT
AS
BEGIN
    SET NOCOUNT ON
    
    DECLARE @WidthCheck VARCHAR(1000) = dbo.PrintWidthCheck()
    PRINT @WidthCheck
    
    -- Declare variables 
    DECLARE @sql NVARCHAR(MAX)
    DECLARE @error_message NVARCHAR(MAX) 
    DECLARE @Object_ID INT
    
    -- Default to the current database if no database is specified
    IF @database_name IS NULL
    BEGIN
        SET @database_name = DB_NAME()
        PRINT 'No database specified, using current database: ' + @database_name
    END    
    -- If object_name is unqualified (no schema), prefix with dbo.
    DECLARE @qualified_object_name NVARCHAR(261)
    
    IF @object_name NOT LIKE '%.%'
        SET @qualified_object_name = 'dbo.' + @object_name
    ELSE
        SET @qualified_object_name = @object_name
    
    -- Step 1: Get the object ID using simple dynamic SQL with fully qualified object name
    DECLARE @GetObjectSQL NVARCHAR(MAX) = N'
    USE [' + @database_name + ']
    SELECT OBJECT_ID(''' + @qualified_object_name + ''') as ObjectID'
    
    PRINT 'Getting object ID for ' + @qualified_object_name + ' in database ' + @database_name
    IF @PreviewMode = 1
        PRINT @GetObjectSQL
    
    DECLARE @ObjectIDTable TABLE (ObjectID INT)
    INSERT INTO @ObjectIDTable
    EXEC (@GetObjectSQL)
    
    SELECT @Object_ID = ObjectID FROM @ObjectIDTable
    
    IF @Object_ID IS NULL
    BEGIN
        PRINT 'Object not found.'
        RETURN
    END
    
    PRINT 'Object ID found: ' + CAST(@Object_ID AS VARCHAR(10))    
    -- Step 2: Get the object definition, creation date, and object details using simple dynamic SQL
    DECLARE @GetDefinitionSQL NVARCHAR(MAX) = N'
    USE [' + @database_name + ']
    SELECT 
        sm.definition,
        CONVERT(NVARCHAR(50), o.create_date, 120) as created_date,
        o.name as object_name,
        o.type_desc as object_type,
        s.name as schema_name
    FROM [' + @database_name + '].sys.sql_modules sm
    INNER JOIN [' + @database_name + '].sys.objects o ON sm.object_id = o.object_id
    INNER JOIN [' + @database_name + '].sys.schemas s ON o.schema_id = s.schema_id
    WHERE sm.object_id = ' + CAST(@Object_ID AS VARCHAR(10))
    
    PRINT 'Getting definition and creation date...'
    IF @PreviewMode = 1
        PRINT @GetDefinitionSQL
    
    DECLARE @DefinitionTable TABLE (
        Definition NVARCHAR(MAX),
        CreatedDate NVARCHAR(50),
        ObjectName NVARCHAR(128),
        ObjectType NVARCHAR(60),
        SchemaName NVARCHAR(128)
    )
    
    INSERT INTO @DefinitionTable
    EXEC (@GetDefinitionSQL)    
    -- Step 3: Get the extended properties using simple dynamic SQL
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
    
    DECLARE @PropertiesTable TABLE (
        PropertyName NVARCHAR(128),
        PropertyValue NVARCHAR(MAX)
    )
    
    INSERT INTO @PropertiesTable
    EXEC (@GetPropertiesSQL)
    
    -- Now process everything outside of dynamic SQL to avoid variable scoping issues
    DECLARE @CreatedDate NVARCHAR(50)
    DECLARE @Definition NVARCHAR(MAX)
    DECLARE @ActualObjectName NVARCHAR(128)
    DECLARE @ObjectType NVARCHAR(60)
    DECLARE @SchemaName NVARCHAR(128)    
    SELECT @Definition = Definition, @CreatedDate = CreatedDate, @ActualObjectName = ObjectName, @ObjectType = ObjectType, @SchemaName = SchemaName FROM @DefinitionTable
    
    IF @Definition IS NULL
    BEGIN
        PRINT 'Object definition not found.'
        RETURN
    END
    
    -- Define a table to store all change entries
    DECLARE @AllChanges TABLE (
        ChangeDate NVARCHAR(50),
        ChangeAuthor NVARCHAR(100),
        ChangeDescription NVARCHAR(MAX),
        SortOrder INT IDENTITY(1,1)
    )
    
    -- Define a table to store manual changes for preservation
    DECLARE @ManualChanges TABLE (
        ChangeText NVARCHAR(MAX),
        SortOrder INT IDENTITY(1,1)
    )
    
    -- Process the definition to extract headers and code
    DECLARE @ProcessedDefinition NVARCHAR(MAX) = @Definition
    
    -- Extract any manual changes from existing header comments
    -- Find all comment blocks and process them for changes
    DECLARE @CommentStart INT = 1
    DECLARE @CommentEnd INT = 1
    DECLARE @CommentBlock NVARCHAR(MAX)    
    -- Find all comment blocks and extract change information
    WHILE @CommentStart > 0
    BEGIN
        SET @CommentStart = CHARINDEX('/*', @ProcessedDefinition, @CommentEnd)
        
        -- If no more comments, exit loop
        IF @CommentStart = 0
            BREAK
            
        SET @CommentEnd = CHARINDEX('*/', @ProcessedDefinition, @CommentStart) + 2
        
        -- If can't find end comment, break
        IF CHARINDEX('*/', @ProcessedDefinition, @CommentStart) = 0
            BREAK
            
        -- Extract the comment block
        SET @CommentBlock = SUBSTRING(@ProcessedDefinition, @CommentStart, @CommentEnd - @CommentStart)
        
        -- Check if this is a header block (contains "Changes Made:")
        IF CHARINDEX('Changes Made:', @CommentBlock) > 0
        BEGIN
            -- Extract changes from this header
            DECLARE @ChangesStart INT = CHARINDEX('Changes Made:', @CommentBlock) + LEN('Changes Made:')
            DECLARE @ChangesEnd INT
            
            -- Look for the end of the Changes section
            SET @ChangesEnd = CHARINDEX('============', @CommentBlock, @ChangesStart)
            
            -- If we don't find the standard end, look for other potential section markers
            IF @ChangesEnd = 0
            BEGIN
                SET @ChangesEnd = CHARINDEX('------------', @CommentBlock, @ChangesStart)
                -- If still not found, use the end of the comment
                IF @ChangesEnd = 0
                    SET @ChangesEnd = CHARINDEX('*/', @CommentBlock, @ChangesStart)
            END            
            IF @ChangesEnd > 0
            BEGIN
                DECLARE @ChangesBlock NVARCHAR(MAX) = SUBSTRING(@CommentBlock, @ChangesStart, @ChangesEnd - @ChangesStart)
                
                -- Create a local table to temporarily store changes during parsing
                DECLARE @TempChanges TABLE (
                    ChangeDate NVARCHAR(50),
                    ChangeAuthor NVARCHAR(100),
                    ChangeDescription NVARCHAR(MAX),
                    LineNumber INT IDENTITY(1,1),
                    IsValid BIT DEFAULT 1
                )
                
                -- Process each line in the changes block
                DECLARE @LineStart INT = 1
                DECLARE @LineEnd INT
                DECLARE @Line NVARCHAR(1000)
                DECLARE @PrevDate NVARCHAR(50) = NULL -- Track previous date for fallback
                
                WHILE @LineStart < LEN(@ChangesBlock)
                BEGIN
                    SET @LineEnd = CHARINDEX(CHAR(13) + CHAR(10), @ChangesBlock + CHAR(13) + CHAR(10), @LineStart)
                    SET @Line = SUBSTRING(@ChangesBlock, @LineStart, @LineEnd - @LineStart)
                    
                    -- Trim and normalize the line to handle different formats
                    SET @Line = LTRIM(RTRIM(@Line))
                    
                    IF @Line LIKE '%-%' AND LEN(@Line) > 0
                    BEGIN
                        -- Skip entries containing "Code extracted with extended properties header"
                        -- or entries with no content after the colon
                        IF @Line LIKE '%Code extracted with extended properties header%'
                           OR @Line NOT LIKE '%:%'
                           OR LTRIM(RTRIM(SUBSTRING(@Line, CHARINDEX(':', @Line) + 1, LEN(@Line)))) = ''
                        BEGIN
                            -- Skip this line but still track it for context
                            INSERT INTO @TempChanges (ChangeDate, ChangeAuthor, ChangeDescription, IsValid)
                            VALUES (NULL, NULL, @Line, 0)
                        END                        ELSE
                        BEGIN
                            -- Extract dash position
                            DECLARE @DashPos INT = CHARINDEX('-', @Line)
                            DECLARE @AfterDash NVARCHAR(MAX) = LTRIM(SUBSTRING(@Line, @DashPos + 1, LEN(@Line)))
                            DECLARE @ColonPos INT = CHARINDEX(':', @AfterDash)
                            
                            -- Always ensure we have a colon to split author/description
                            IF @ColonPos > 0
                            BEGIN
                                DECLARE @BeforeColon NVARCHAR(MAX) = LTRIM(RTRIM(SUBSTRING(@AfterDash, 1, @ColonPos - 1)))
                                DECLARE @AfterColon NVARCHAR(MAX) = LTRIM(RTRIM(SUBSTRING(@AfterDash, @ColonPos + 1, LEN(@AfterDash))))
                                
                                -- Check if we have a date-like pattern at the beginning
                                DECLARE @HasDate BIT = 0
                                DECLARE @EntryDate NVARCHAR(50) = NULL
                                DECLARE @EntryAuthor NVARCHAR(100) = ''
                                DECLARE @EntryDesc NVARCHAR(MAX) = @AfterColon
                                
                                -- Look for date patterns in different formats
                                IF @BeforeColon LIKE '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]%' OR -- YYYY-MM-DD
                                   @BeforeColon LIKE '[0-9]/[0-9]/[0-9][0-9][0-9][0-9]%' OR           -- M/D/YYYY
                                   @BeforeColon LIKE '[0-9][0-9]/[0-9]/[0-9][0-9][0-9][0-9]%' OR      -- MM/D/YYYY
                                   @BeforeColon LIKE '[0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]%' OR      -- M/DD/YYYY
                                   @BeforeColon LIKE '[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]%'    -- MM/DD/YYYY
                                BEGIN
                                    SET @HasDate = 1
                                    
                                    -- Find the first space after a potential date
                                    DECLARE @FirstSpace INT = CHARINDEX(' ', @BeforeColon)                                    
                                    IF @FirstSpace > 0
                                    BEGIN
                                        -- We have both date and potentially author
                                        SET @EntryDate = LTRIM(RTRIM(SUBSTRING(@BeforeColon, 1, @FirstSpace - 1)))
                                        SET @EntryAuthor = LTRIM(RTRIM(SUBSTRING(@BeforeColon, @FirstSpace + 1, LEN(@BeforeColon) - @FirstSpace)))
                                    END
                                    ELSE
                                    BEGIN
                                        -- We only have a date
                                        SET @EntryDate = @BeforeColon
                                        SET @EntryAuthor = '' -- Empty author
                                    END
                                    
                                    -- Store the date for future reference
                                    SET @PrevDate = @EntryDate
                                END
                                ELSE
                                BEGIN
                                    -- No date pattern found, use fallbacks
                                    SET @EntryAuthor = @BeforeColon -- Assume everything before colon is author
                                    
                                    -- Use previous date if available
                                    IF @PrevDate IS NOT NULL
                                        SET @EntryDate = @PrevDate
                                    ELSE
                                        SET @EntryDate = NULL -- Will be resolved later
                                END
                                
                                -- Normalize date format if possible
                                IF @EntryDate IS NOT NULL AND (
                                   @EntryDate LIKE '[0-9]/[0-9]/[0-9][0-9][0-9][0-9]' OR 
                                   @EntryDate LIKE '[0-9][0-9]/[0-9]/[0-9][0-9][0-9][0-9]' OR
                                   @EntryDate LIKE '[0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]' OR
                                   @EntryDate LIKE '[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]')
                                BEGIN                                    DECLARE @Month NVARCHAR(2), @Day NVARCHAR(2), @Year NVARCHAR(4)
                                    
                                    -- Extract month, day, year from MM/DD/YYYY format
                                    DECLARE @FirstSlash INT = CHARINDEX('/', @EntryDate)
                                    DECLARE @SecondSlash INT = CHARINDEX('/', @EntryDate, @FirstSlash + 1)
                                    
                                    SET @Month = SUBSTRING(@EntryDate, 1, @FirstSlash - 1)
                                    SET @Day = SUBSTRING(@EntryDate, @FirstSlash + 1, @SecondSlash - @FirstSlash - 1)
                                    SET @Year = SUBSTRING(@EntryDate, @SecondSlash + 1, 4)
                                    
                                    -- Pad month and day with leading zeros if needed
                                    IF LEN(@Month) = 1 SET @Month = '0' + @Month
                                    IF LEN(@Day) = 1 SET @Day = '0' + @Day
                                    
                                    SET @EntryDate = @Year + '-' + @Month + '-' + @Day
                                END
                                
                                -- Store this entry with all information we have so far
                                INSERT INTO @TempChanges (ChangeDate, ChangeAuthor, ChangeDescription, IsValid)
                                VALUES (@EntryDate, @EntryAuthor, @EntryDesc, 1)
                            END
                            ELSE
                            BEGIN
                                -- No colon found, just store the whole line as a description
                                INSERT INTO @TempChanges (ChangeDate, ChangeAuthor, ChangeDescription, IsValid)
                                VALUES (NULL, '', LTRIM(RTRIM(SUBSTRING(@Line, @DashPos + 1, LEN(@Line)))), 1)
                            END
                        END
                    END
                    
                    SET @LineStart = @LineEnd + 2  -- Move past CRLF
                END                
                -- Post-processing to resolve missing dates
                DECLARE @ProcessCurrentDate NVARCHAR(50) = CONVERT(NVARCHAR(50), GETDATE(), 120)
                DECLARE @NextValidDate NVARCHAR(50) = NULL
                
                -- First pass: look forward to find next valid date for entries with NULL dates
                SELECT @NextValidDate = NULL
                DECLARE @MaxLine INT = (SELECT MAX(LineNumber) FROM @TempChanges)
                DECLARE @CurrentLine INT = @MaxLine
                
                WHILE @CurrentLine >= 1
                BEGIN
                    DECLARE @ThisDate NVARCHAR(50), @ThisValid BIT
                    
                    SELECT @ThisDate = ChangeDate, @ThisValid = IsValid 
                    FROM @TempChanges WHERE LineNumber = @CurrentLine
                    
                    IF @ThisValid = 1
                    BEGIN
                        IF @ThisDate IS NOT NULL
                            SET @NextValidDate = @ThisDate
                        ELSE IF @NextValidDate IS NOT NULL
                            UPDATE @TempChanges SET ChangeDate = @NextValidDate WHERE LineNumber = @CurrentLine
                    END
                    
                    SET @CurrentLine = @CurrentLine - 1
                END
                
                -- Second pass: look backward for any still-missing dates
                SELECT @PrevDate = NULL
                SET @CurrentLine = 1
                
                WHILE @CurrentLine <= @MaxLine
                BEGIN
                    SELECT @ThisDate = ChangeDate, @ThisValid = IsValid 
                    FROM @TempChanges WHERE LineNumber = @CurrentLine                    
                    IF @ThisValid = 1
                    BEGIN
                        IF @ThisDate IS NOT NULL
                            SET @PrevDate = @ThisDate
                        ELSE IF @PrevDate IS NOT NULL
                            UPDATE @TempChanges SET ChangeDate = @PrevDate WHERE LineNumber = @CurrentLine
                        ELSE
                            UPDATE @TempChanges SET ChangeDate = @ProcessCurrentDate WHERE LineNumber = @CurrentLine
                    END
                    
                    SET @CurrentLine = @CurrentLine + 1
                END
                
                -- Now insert all valid entries into the actual changes table
                INSERT INTO @AllChanges (ChangeDate, ChangeAuthor, ChangeDescription)
                SELECT ChangeDate, ChangeAuthor, ChangeDescription 
                FROM @TempChanges 
                WHERE IsValid = 1
                AND NOT EXISTS (
                    SELECT 1 FROM @AllChanges 
                    WHERE ChangeDescription = @TempChanges.ChangeDescription
                    AND ChangeAuthor = @TempChanges.ChangeAuthor
                )
            END
        END
    END    
    -- NEW APPROACH: Find the actual code portion by identifying the CREATE or ALTER statement
    -- outside of any comment blocks
    DECLARE @CodeStart INT = 1
    DECLARE @InComment BIT = 0
    DECLARE @CurrentPos INT = 1
    DECLARE @CurrentChar NCHAR(1)
    DECLARE @CodeStartFound BIT = 0
    
    -- First, find the position of CREATE outside of any comments
    WHILE @CurrentPos <= LEN(@ProcessedDefinition) AND @CodeStartFound = 0
    BEGIN
        SET @CurrentChar = SUBSTRING(@ProcessedDefinition, @CurrentPos, 1)
        
        -- Check for start of comment
        IF @CurrentPos < LEN(@ProcessedDefinition) - 1 AND 
           SUBSTRING(@ProcessedDefinition, @CurrentPos, 2) = '/*'
        BEGIN
            SET @InComment = 1
            SET @CurrentPos = @CurrentPos + 2
            CONTINUE
        END
        
        -- Check for end of comment
        IF @InComment = 1 AND 
           @CurrentPos < LEN(@ProcessedDefinition) - 1 AND 
           SUBSTRING(@ProcessedDefinition, @CurrentPos, 2) = '*/'
        BEGIN
            SET @InComment = 0
            SET @CurrentPos = @CurrentPos + 2
            CONTINUE
        END
        
        -- Skip anything inside comments
        IF @InComment = 1
        BEGIN
            SET @CurrentPos = @CurrentPos + 1
            CONTINUE
        END        
        -- Check for CREATE outside of comments
        IF UPPER(SUBSTRING(@ProcessedDefinition, @CurrentPos, 6)) = 'CREATE' AND
           (@CurrentPos = 1 OR SUBSTRING(@ProcessedDefinition, @CurrentPos - 1, 1) LIKE '[^A-Za-z0-9_]')
        BEGIN
            SET @CodeStart = @CurrentPos
            SET @CodeStartFound = 1
            BREAK
        END
        
        -- Check for ALTER as an alternative (for objects that might use ALTER instead of CREATE)
        IF @CodeStartFound = 0 AND 
           UPPER(SUBSTRING(@ProcessedDefinition, @CurrentPos, 5)) = 'ALTER' AND
           (@CurrentPos = 1 OR SUBSTRING(@ProcessedDefinition, @CurrentPos - 1, 1) LIKE '[^A-Za-z0-9_]')
        BEGIN
            SET @CodeStart = @CurrentPos
            SET @CodeStartFound = 1
            BREAK
        END
        
        SET @CurrentPos = @CurrentPos + 1
    END
    
    -- Extract the actual code starting from CREATE or ALTER
    DECLARE @ActualCode NVARCHAR(MAX)
    IF @CodeStartFound = 1
    BEGIN
        SET @ActualCode = SUBSTRING(@ProcessedDefinition, @CodeStart, LEN(@ProcessedDefinition) - @CodeStart + 1)
    END
    ELSE
    BEGIN
        -- If we couldn't find CREATE or ALTER, use the original definition (unlikely)
        SET @ActualCode = @ProcessedDefinition
        PRINT 'Warning: Could not find CREATE or ALTER statement in the code.'
    END
    
    PRINT 'Processing extended properties...'    
    -- Process the extended properties outside of dynamic SQL
    DECLARE @PropertyName NVARCHAR(128)
    DECLARE @PropertyValue NVARCHAR(MAX)
    DECLARE @FormattedName NVARCHAR(128)
    DECLARE @MetaSection NVARCHAR(MAX) = ''
    DECLARE @CodeReviewSection NVARCHAR(MAX) = ''
    DECLARE @VersionSection NVARCHAR(MAX) = ''
    DECLARE @ReleaseNotesSection NVARCHAR(MAX) = ''
    DECLARE @OtherSection NVARCHAR(MAX) = ''
    DECLARE @ExtendedPropertiesSection NVARCHAR(MAX) = ''
    DECLARE @CurrentDate NVARCHAR(50) = CONVERT(NVARCHAR(50), GETDATE(), 120)
    DECLARE @CurrentUser NVARCHAR(128) = SYSTEM_USER
    
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
        END        ELSE
        BEGIN
            -- Handle Changes-* properties
            IF LOWER(LEFT(@PropertyName, 8)) = 'changes-' AND LEN(@PropertyName) > 8
            BEGIN
                -- Extract the date part from the property name (after 'Changes-')
                DECLARE @ChangeDateStr NVARCHAR(50) = SUBSTRING(@PropertyName, 9, 100)
                
                -- If the property value doesn't contain "Code extracted with extended properties header"
                IF @PropertyValue NOT LIKE '%Code extracted with extended properties header%'
                BEGIN
                    -- Parse the change entry
                    DECLARE @ChangeValue NVARCHAR(MAX) = @PropertyValue
                    DECLARE @ChangeAuthor NVARCHAR(100) = ''
                    DECLARE @ChangeDesc NVARCHAR(MAX) = ''
                    
                    IF @ChangeValue LIKE '%:%'
                    BEGIN
                        DECLARE @PropColonPos INT = CHARINDEX(':', @ChangeValue)
                        
                        -- Check if there's a date part
                        IF CHARINDEX('-', @ChangeValue) > 0
                        BEGIN
                            DECLARE @PropDashPos INT = CHARINDEX('-', @ChangeValue)
                            DECLARE @PropAfterDash NVARCHAR(MAX) = LTRIM(SUBSTRING(@ChangeValue, @PropDashPos + 1, LEN(@ChangeValue)))
                            SET @PropColonPos = CHARINDEX(':', @PropAfterDash)
                            
                            IF @PropColonPos > 0
                            BEGIN
                                DECLARE @PropBeforeColon NVARCHAR(MAX) = LTRIM(RTRIM(SUBSTRING(@PropAfterDash, 1, @PropColonPos - 1)))
                                DECLARE @PropAfterColon NVARCHAR(MAX) = LTRIM(RTRIM(SUBSTRING(@PropAfterDash, @PropColonPos + 1, LEN(@PropAfterDash))))
                                
                                -- Check for space to separate date/author
                                DECLARE @PropSpacePos INT = CHARINDEX(' ', @PropBeforeColon)                                IF @PropSpacePos > 0
                                BEGIN
                                    -- We have both date and author
                                    SET @ChangeAuthor = LTRIM(RTRIM(SUBSTRING(@PropBeforeColon, @PropSpacePos + 1, LEN(@PropBeforeColon) - @PropSpacePos)))
                                END
                                ELSE
                                BEGIN
                                    -- We only have author (or just date, treated as author)
                                    SET @ChangeAuthor = @PropBeforeColon
                                END
                                
                                SET @ChangeDesc = @PropAfterColon
                            END
                            ELSE
                            BEGIN
                                -- No proper format, treat all as description
                                SET @ChangeDesc = LTRIM(RTRIM(SUBSTRING(@ChangeValue, @PropDashPos + 1, LEN(@ChangeValue))))
                            END
                        END
                        ELSE
                        BEGIN
                            -- No dash, try to parse author and description directly
                            SET @ChangeAuthor = LTRIM(RTRIM(SUBSTRING(@ChangeValue, 1, @PropColonPos - 1)))
                            SET @ChangeDesc = LTRIM(RTRIM(SUBSTRING(@ChangeValue, @PropColonPos + 1, LEN(@ChangeValue))))
                        END
                        
                        -- Add to changes table if not a duplicate
                        IF NOT EXISTS (
                            SELECT 1 FROM @AllChanges 
                            WHERE ChangeDescription = @ChangeDesc
                               AND ChangeAuthor = @ChangeAuthor
                        )
                        BEGIN
                            INSERT INTO @AllChanges (ChangeDate, ChangeAuthor, ChangeDescription)
                            VALUES (@ChangeDateStr, @ChangeAuthor, @ChangeDesc)
                        END
                    END
                END
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
    
    PRINT 'Building header comment...'
    
    -- Format the object type for human readability
    DECLARE @FormattedObjectType NVARCHAR(60)
    SET @FormattedObjectType = CASE 
        WHEN @ObjectType = 'SQL_STORED_PROCEDURE' THEN 'Stored Procedure'
        WHEN @ObjectType = 'SQL_SCALAR_FUNCTION' THEN 'Scalar Function'
        WHEN @ObjectType = 'SQL_TABLE_VALUED_FUNCTION' THEN 'Table Valued Function'
        WHEN @ObjectType = 'SQL_INLINE_TABLE_VALUED_FUNCTION' THEN 'Inline Table Valued Function'
        WHEN @ObjectType = 'VIEW' THEN 'View'
        WHEN @ObjectType = 'SQL_TRIGGER' THEN 'Trigger'
        WHEN @ObjectType = 'USER_TABLE' THEN 'Table'
        WHEN @ObjectType = 'SEQUENCE_OBJECT' THEN 'Sequence'
        ELSE REPLACE(REPLACE(@ObjectType, 'SQL_', ''), '_', ' ')
    END    
    -- Build the complete extended properties section with grouped categories
    IF LEN(@MetaSection) > 0
        SET @ExtendedPropertiesSection = @ExtendedPropertiesSection + 'Meta Information:' + CHAR(13) + CHAR(10) + @MetaSection + CHAR(13) + CHAR(10)
    
    IF LEN(@CodeReviewSection) > 0
        SET @ExtendedPropertiesSection = @ExtendedPropertiesSection + 'Code Review:' + CHAR(13) + CHAR(10) + @CodeReviewSection + CHAR(13) + CHAR(10)
    
    IF LEN(@VersionSection) > 0
        SET @ExtendedPropertiesSection = @ExtendedPropertiesSection + 'Version Information:' + CHAR(13) + CHAR(10) + @VersionSection + CHAR(13) + CHAR(10)
    
    IF LEN(@ReleaseNotesSection) > 0
        SET @ExtendedPropertiesSection = @ExtendedPropertiesSection + 'Release Notes:' + CHAR(13) + CHAR(10) + @ReleaseNotesSection + CHAR(13) + CHAR(10)
    
    IF LEN(@OtherSection) > 0
        SET @ExtendedPropertiesSection = @ExtendedPropertiesSection + 'Other Properties:' + CHAR(13) + CHAR(10) + @OtherSection + CHAR(13) + CHAR(10)
    
    -- Build changes section from all collected changes
    DECLARE @ChangesHeaderSection NVARCHAR(MAX) = ''
    DECLARE @CurrentChangeEntry NVARCHAR(MAX) = 
        '  - ' + @CurrentDate + ' ' + @CurrentUser + ': Code extracted with extended properties header' + CHAR(13) + CHAR(10)
    
    -- Add the current change entry first
    SET @ChangesHeaderSection = @CurrentChangeEntry
    
    -- Add all other changes, sorted by date (most recent first)
    DECLARE @ChangeEntryDate NVARCHAR(50), @ChangeEntryAuthor NVARCHAR(100), @ChangeEntryDesc NVARCHAR(MAX)
    
    DECLARE changes_cursor CURSOR FOR
    SELECT ChangeDate, ChangeAuthor, ChangeDescription FROM @AllChanges
    ORDER BY 
        -- Try to convert to datetime for proper sorting
        CASE 
            WHEN ISDATE(ChangeDate) = 1 THEN CONVERT(DATETIME, ChangeDate) 
            ELSE NULL 
        END DESC,
        SortOrder  -- Use the original order as fallback    
    OPEN changes_cursor
    FETCH NEXT FROM changes_cursor INTO @ChangeEntryDate, @ChangeEntryAuthor, @ChangeEntryDesc
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Add to changes section
        IF @ChangeEntryDate IS NOT NULL AND @ChangeEntryDesc IS NOT NULL
        BEGIN
            -- Format the change entry based on whether we have an author
            IF LEN(@ChangeEntryAuthor) > 0
                SET @ChangesHeaderSection = @ChangesHeaderSection + '  - ' + @ChangeEntryDate + ' ' + @ChangeEntryAuthor + ': ' + @ChangeEntryDesc + CHAR(13) + CHAR(10)
            ELSE
                SET @ChangesHeaderSection = @ChangesHeaderSection + '  - ' + @ChangeEntryDate + ' : ' + @ChangeEntryDesc + CHAR(13) + CHAR(10)
        END
        
        FETCH NEXT FROM changes_cursor INTO @ChangeEntryDate, @ChangeEntryAuthor, @ChangeEntryDesc
    END
    
    CLOSE changes_cursor
    DEALLOCATE changes_cursor
    
    -- Build the "Changes Previous" section from manual changes
    DECLARE @ChangesPreviousSection NVARCHAR(MAX) = ''
    
    -- First, check if there's an existing "Changes Previous" section in the source code
    DECLARE @ExistingPreviousChanges TABLE (
        ChangeText NVARCHAR(MAX),
        SortOrder INT IDENTITY(1,1)
    )
    
    -- IMPORTANT: Also check if there's an existing ChangesManual extended property
    -- and add those entries to our ExistingPreviousChanges table
    DECLARE @CheckManualChangesSQL NVARCHAR(MAX) = N'
    USE [' + @database_name + ']
    SELECT 
        CONVERT(NVARCHAR(MAX), ep.value) as PropertyValue
    FROM [' + @database_name + '].sys.extended_properties ep
    WHERE ep.major_id = ' + CAST(@Object_ID AS VARCHAR(10)) + '
        AND ep.minor_id = 0 
        AND ep.name = ''ChangesManual'''    
    DECLARE @ExistingManualChangesEP NVARCHAR(MAX) = NULL
    
    -- Execute the query to get existing manual changes from extended properties
    DECLARE @ManualChangesEPTable TABLE (PropertyValue NVARCHAR(MAX))
    INSERT INTO @ManualChangesEPTable
    EXEC (@CheckManualChangesSQL)
    
    SELECT @ExistingManualChangesEP = PropertyValue FROM @ManualChangesEPTable
    
    -- If we have existing manual changes in extended properties, add them to our tracking table
    IF @ExistingManualChangesEP IS NOT NULL
    BEGIN
        -- Process each line from the extended property
        DECLARE @EPLineStart INT = 1
        DECLARE @EPLineEnd INT
        DECLARE @EPLine NVARCHAR(1000)
        
        WHILE @EPLineStart <= LEN(@ExistingManualChangesEP)
        BEGIN
            SET @EPLineEnd = CHARINDEX(CHAR(13) + CHAR(10), @ExistingManualChangesEP + CHAR(13) + CHAR(10), @EPLineStart)
            SET @EPLine = SUBSTRING(@ExistingManualChangesEP, @EPLineStart, @EPLineEnd - @EPLineStart)
            
            -- Trim and check if the line has content
            SET @EPLine = LTRIM(RTRIM(@EPLine))
            
            IF LEN(@EPLine) > 0
            BEGIN
                -- Add to existing changes if not already there
                IF NOT EXISTS (
                    SELECT 1 FROM @ExistingPreviousChanges WHERE ChangeText = @EPLine
                )
                BEGIN
                    INSERT INTO @ExistingPreviousChanges (ChangeText)
                    VALUES (@EPLine)
                END
            END
            
            SET @EPLineStart = @EPLineEnd + 2  -- Move past CRLF
            IF @EPLineEnd = 0 OR @EPLineStart > LEN(@ExistingManualChangesEP)
                BREAK
        END
    END    
    -- Find any existing "Changes Previous" section in the source
    DECLARE @PrevChangesPos INT = 0
    DECLARE @PrevChangesEnd INT = 0
    DECLARE @CommentBlockStart INT = 1
    DECLARE @CommentBlockEnd INT = 1
    DECLARE @CommentBlockText NVARCHAR(MAX)
    
    -- Look for "Changes Previous" in any comment block
    WHILE @CommentBlockStart > 0
    BEGIN
        SET @CommentBlockStart = CHARINDEX('/*', @ProcessedDefinition, @CommentBlockEnd)
        
        IF @CommentBlockStart = 0
            BREAK
            
        SET @CommentBlockEnd = CHARINDEX('*/', @ProcessedDefinition, @CommentBlockStart) + 2
        
        IF CHARINDEX('*/', @ProcessedDefinition, @CommentBlockStart) = 0
            BREAK
            
        SET @CommentBlockText = SUBSTRING(@ProcessedDefinition, @CommentBlockStart, @CommentBlockEnd - @CommentBlockStart)
        
        SET @PrevChangesPos = CHARINDEX('Changes Previous:', @CommentBlockText)
        
        IF @PrevChangesPos > 0
        BEGIN
            -- Found a "Changes Previous" section, extract all entries
            DECLARE @PrevSectionStart INT = CHARINDEX('Changes Previous:', @CommentBlockText) + LEN('Changes Previous:')
            DECLARE @PrevSectionEnd INT
            
            -- Find the end of the section (next section marker or end of comment)
            SET @PrevSectionEnd = CHARINDEX('------------', @CommentBlockText, @PrevSectionStart)
            IF @PrevSectionEnd = 0
                SET @PrevSectionEnd = CHARINDEX('*/', @CommentBlockText, @PrevSectionStart)
            
            IF @PrevSectionEnd > 0
            BEGIN
                DECLARE @PrevSection NVARCHAR(MAX) = SUBSTRING(@CommentBlockText, @PrevSectionStart, @PrevSectionEnd - @PrevSectionStart)                
                -- Process each line
                DECLARE @PrevLineStart INT = 1
                DECLARE @PrevLineEnd INT
                DECLARE @PrevLine NVARCHAR(1000)
                
                WHILE @PrevLineStart < LEN(@PrevSection)
                BEGIN
                    SET @PrevLineEnd = CHARINDEX(CHAR(13) + CHAR(10), @PrevSection + CHAR(13) + CHAR(10), @PrevLineStart)
                    SET @PrevLine = SUBSTRING(@PrevSection, @PrevLineStart, @PrevLineEnd - @PrevLineStart)
                    
                    -- Trim and check if the line has content
                    SET @PrevLine = LTRIM(RTRIM(@PrevLine))
                    
                    IF LEN(@PrevLine) > 0 AND @PrevLine NOT LIKE '%<Add your change notes here>%'
                    BEGIN
                        -- Add to existing changes if not already there
                        IF NOT EXISTS (
                            SELECT 1 FROM @ExistingPreviousChanges WHERE ChangeText = @PrevLine
                        )
                        BEGIN
                            INSERT INTO @ExistingPreviousChanges (ChangeText)
                            VALUES (@PrevLine)
                        END
                    END
                    
                    SET @PrevLineStart = @PrevLineEnd + 2
                END
            END
        END
    END
    
    -- Now build the Changes Previous section, combining existing and new changes
    
    -- First add existing changes
    IF EXISTS (SELECT 1 FROM @ExistingPreviousChanges)
    BEGIN
        DECLARE @ExistingChangeText NVARCHAR(MAX)
        
        DECLARE existing_changes_cursor CURSOR FOR
        SELECT ChangeText FROM @ExistingPreviousChanges
        ORDER BY SortOrder        
        OPEN existing_changes_cursor
        FETCH NEXT FROM existing_changes_cursor INTO @ExistingChangeText
        
        WHILE @@FETCH_STATUS = 0
        BEGIN
            SET @ChangesPreviousSection = @ChangesPreviousSection + '  ' + @ExistingChangeText + CHAR(13) + CHAR(10)
            FETCH NEXT FROM existing_changes_cursor INTO @ExistingChangeText
        END
        
        CLOSE existing_changes_cursor
        DEALLOCATE existing_changes_cursor
    END
    
    -- Then add new manual changes found in this run
    IF EXISTS (SELECT 1 FROM @ManualChanges)
    BEGIN
        DECLARE @ManualChangeText NVARCHAR(MAX)
        
        DECLARE manual_changes_cursor CURSOR FOR
        SELECT ChangeText FROM @ManualChanges
        ORDER BY SortOrder
        
        OPEN manual_changes_cursor
        FETCH NEXT FROM manual_changes_cursor INTO @ManualChangeText
        
        WHILE @@FETCH_STATUS = 0
        BEGIN
            -- Only add if not already in the section
            IF @ChangesPreviousSection NOT LIKE '%' + @ManualChangeText + '%'
            BEGIN
                SET @ChangesPreviousSection = @ChangesPreviousSection + '  ' + @ManualChangeText + CHAR(13) + CHAR(10)
            END
            FETCH NEXT FROM manual_changes_cursor INTO @ManualChangeText
        END
        
        CLOSE manual_changes_cursor
        DEALLOCATE manual_changes_cursor
    END    
    -- Build the header comment with grouped extended properties
    DECLARE @HeaderComment NVARCHAR(MAX) = 
        '/*' + CHAR(13) + CHAR(10) +
        '============================================================================' + CHAR(13) + CHAR(10) +
        @FormattedObjectType + ': ' + @ActualObjectName + CHAR(13) + CHAR(10) +
        'Schema: ' + @SchemaName + CHAR(13) + CHAR(10) +
        'Database: ' + @database_name + CHAR(13) + CHAR(10) +
        '----------------------------------------------------------------------------' + CHAR(13) + CHAR(10) +
        'Date Created: ' + ISNULL(@CreatedDate, 'Not available') + CHAR(13) + CHAR(10) +
        'Date Modified: ' + @CurrentDate + CHAR(13) + CHAR(10) +
        'Current User: ' + @CurrentUser + CHAR(13) + CHAR(10) +
        CASE 
            WHEN LEN(@ExtendedPropertiesSection) > 0 THEN 
                '----------------------------------------------------------------------------' + CHAR(13) + CHAR(10) +
                @ExtendedPropertiesSection
            ELSE ''
        END +
        CASE 
            WHEN LEN(@ChangesPreviousSection) > 0 THEN 
                '----------------------------------------------------------------------------' + CHAR(13) + CHAR(10) +
                'Changes Previous: ' + CHAR(13) + CHAR(10) +
                @ChangesPreviousSection
            ELSE ''
        END +
        '----------------------------------------------------------------------------' + CHAR(13) + CHAR(10) +
        'Changes Made: ([Date] [Author]: [Description of changes])' + CHAR(13) + CHAR(10) +
        @ChangesHeaderSection +
        '============================================================================' + CHAR(13) + CHAR(10) +
        '*/' + CHAR(13) + CHAR(10) + CHAR(13) + CHAR(10)    
    -- Now transform the code to always use CREATE OR ALTER
    DECLARE @TransformedCode NVARCHAR(MAX) = @ActualCode
    
    -- Find the position of CREATE
    DECLARE @CreatePosition INT = PATINDEX('%CREATE%', UPPER(@ActualCode))
    
    IF @CreatePosition > 0
    BEGIN
        -- Find the position of the first non-whitespace character after CREATE
        DECLARE @AfterCreate NVARCHAR(MAX) = SUBSTRING(@ActualCode, @CreatePosition + 6, LEN(@ActualCode))
        DECLARE @FirstNonWhitespacePos INT = PATINDEX('%[^ \t\r\n]%', @AfterCreate)
        
        IF @FirstNonWhitespacePos > 0
        BEGIN
            -- Get the word after CREATE
            DECLARE @AfterCreateTrimmed NVARCHAR(MAX) = SUBSTRING(@AfterCreate, @FirstNonWhitespacePos, LEN(@AfterCreate))
            DECLARE @NextWordEndPos INT = PATINDEX('%[ \t\r\n]%', @AfterCreateTrimmed + ' ')
            DECLARE @NextWord NVARCHAR(100) = SUBSTRING(@AfterCreateTrimmed, 1, @NextWordEndPos - 1)
            
            -- Check if it's already "OR" (part of "CREATE OR ALTER")
            IF UPPER(@NextWord) = 'OR'
            BEGIN
                -- It's already "CREATE OR ALTER", no change needed
                SET @TransformedCode = @ActualCode
            END
            ELSE
            BEGIN
                -- It's just CREATE followed by object type - replace with CREATE OR ALTER
                DECLARE @PosAfterCreate INT = @CreatePosition + 6
                
                -- Calculate exact position to insert "OR ALTER "
                DECLARE @InsertPos INT = @PosAfterCreate + @FirstNonWhitespacePos - 1
                
                -- Insert "OR ALTER " right before the object type
                SET @TransformedCode = 
                    SUBSTRING(@ActualCode, 1, @InsertPos - 1) + 
                    'OR ALTER ' + 
                    SUBSTRING(@ActualCode, @InsertPos, LEN(@ActualCode))
            END
        END
    END    
    -- Create a new extended property for the current change
    -- This will be executed in the output if ExecuteMode is enabled
    DECLARE @AddChangePropertySQL NVARCHAR(MAX) = N'
    USE [' + @database_name + ']
    IF NOT EXISTS (
        SELECT 1 FROM sys.extended_properties 
        WHERE major_id = ' + CAST(@Object_ID AS VARCHAR(10)) + ' 
        AND minor_id = 0 
        AND name = ''Changes-' + @CurrentDate + '''
    )
    BEGIN
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
    -- Now add extended properties for all other changes we parsed that aren't 
    -- already present in the database
    DECLARE @OtherChangesSQL NVARCHAR(MAX) = ''
    
    -- Create a cursor to go through all changes in @AllChanges
    DECLARE change_props_cursor CURSOR FOR
    SELECT ChangeDate, ChangeAuthor, ChangeDescription FROM @AllChanges
    WHERE ChangeDescription NOT LIKE '%Code extracted with extended properties header%'
    
    OPEN change_props_cursor
    FETCH NEXT FROM change_props_cursor INTO @ChangeEntryDate, @ChangeEntryAuthor, @ChangeEntryDesc
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Formulate property value - maintain format even if author is blank
        DECLARE @PropValue NVARCHAR(MAX)
        
        IF LEN(@ChangeEntryAuthor) > 0
            SET @PropValue = N'  - ' + @ChangeEntryDate + ' ' + @ChangeEntryAuthor + ': ' + @ChangeEntryDesc
        ELSE
            SET @PropValue = N'  - ' + @ChangeEntryDate + ' : ' + @ChangeEntryDesc
        
        -- Add to SQL to create the extended property
        SET @OtherChangesSQL = @OtherChangesSQL + N'
        IF NOT EXISTS (
            SELECT 1 FROM sys.extended_properties 
            WHERE major_id = ' + CAST(@Object_ID AS VARCHAR(10)) + ' 
            AND minor_id = 0 
            AND name = ''Changes-' + @ChangeEntryDate + '-'' + CAST(NEWID() AS NVARCHAR(36))
        )
        BEGIN
            EXEC sys.sp_addextendedproperty 
                @name = N''Changes-' + @ChangeEntryDate + '-'' + CAST(NEWID() AS NVARCHAR(36)), 
                @value = N''' + REPLACE(@PropValue, '''', '''''') + ''', 
                @level0type = N''SCHEMA'', 
                @level0name = N''' + @SchemaName + ''', 
                @level1type = N''' +                     CASE 
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
        
        FETCH NEXT FROM change_props_cursor INTO @ChangeEntryDate, @ChangeEntryAuthor, @ChangeEntryDesc
    END
    
    CLOSE change_props_cursor
    DEALLOCATE change_props_cursor
    
    -- Store manual changes in extended properties too
    DECLARE @AddManualChangesSQL NVARCHAR(MAX) = ''
    
    -- Combine existing and new manual changes
    DECLARE @AllManualChanges NVARCHAR(MAX) = ''
    
    -- Build the combined manual changes list from the Changes Previous section
    IF LEN(@ChangesPreviousSection) > 0
    BEGIN
        SET @AllManualChanges = RTRIM(@ChangesPreviousSection)
    END    
    -- If we have manual changes to store
    IF LEN(@AllManualChanges) > 0
    BEGIN
        -- Generate a unique timestamp for this manual change
        DECLARE @CurrentDateNoSpace NVARCHAR(50) = REPLACE(@CurrentDate, ' ', '-')
        
        -- Add a new ChangePrevious-{timestamp} property
        SET @AddManualChangesSQL = N'
        USE [' + @database_name + ']
        DECLARE @ExistingChanges TABLE (
            PropertyName NVARCHAR(128)
        )
        
        -- Get existing ChangePrevious-* properties
        INSERT INTO @ExistingChanges
        SELECT name 
        FROM sys.extended_properties 
        WHERE major_id = ' + CAST(@Object_ID AS VARCHAR(10)) + '
          AND minor_id = 0
          AND name LIKE ''ChangePrevious-%''
        
        -- Add each manual change as a separate extended property
        '
        
        -- Process each manual change
        DECLARE @ManualChangeCounter INT = 1
        DECLARE @ManualLine NVARCHAR(MAX)
        DECLARE @ManualLineStart INT = 1
        DECLARE @ManualLineEnd INT
        
        WHILE @ManualLineStart <= LEN(@AllManualChanges)
        BEGIN
            SET @ManualLineEnd = CHARINDEX(CHAR(13) + CHAR(10), @AllManualChanges + CHAR(13) + CHAR(10), @ManualLineStart)
            SET @ManualLine = SUBSTRING(@AllManualChanges, @ManualLineStart, @ManualLineEnd - @ManualLineStart)
            
            -- Trim and check if the line has content
            SET @ManualLine = LTRIM(RTRIM(@ManualLine))            
            IF LEN(@ManualLine) > 0
            BEGIN
                -- Create a property for this change
                SET @AddManualChangesSQL = @AddManualChangesSQL + N'
                IF NOT EXISTS (
                    SELECT 1 FROM sys.extended_properties 
                    WHERE major_id = ' + CAST(@Object_ID AS VARCHAR(10)) + '
                      AND minor_id = 0
                      AND value = N''' + REPLACE(@ManualLine, '''', '''''') + '''
                      AND name LIKE ''ChangePrevious-%''
                )
                BEGIN
                    EXEC sys.sp_addextendedproperty 
                        @name = N''ChangePrevious-' + @CurrentDateNoSpace + '-' + CAST(@ManualChangeCounter AS NVARCHAR(10)) + ''', 
                        @value = N''' + REPLACE(@ManualLine, '''', '''''') + ''', 
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
                END
                '                
                SET @ManualChangeCounter = @ManualChangeCounter + 1
            END
            
            SET @ManualLineStart = @ManualLineEnd + 2  -- Move past CRLF
            IF @ManualLineEnd = 0 OR @ManualLineStart > LEN(@AllManualChanges)
                BREAK
        END
    END
    
    -- Building the final SQL string with USE statement, header comment, and GO statements
    SET @sqlText = 
        '--USE [' + @database_name + ']' + CHAR(13) + CHAR(10) + 
        'GO' + CHAR(13) + CHAR(10) + CHAR(13) + CHAR(10) +
        @HeaderComment +
        @TransformedCode
    
    -- Add the SQL to add the current change to extended properties if execute mode is enabled
    IF @ExecuteMode = 1
    BEGIN
        SET @sqlText = @sqlText + CHAR(13) + CHAR(10) + 
            'GO' + CHAR(13) + CHAR(10) + 
            '-- Add current change to extended properties' + CHAR(13) + CHAR(10) + 
            @AddChangePropertySQL + CHAR(13) + CHAR(10) +
            'GO' + CHAR(13) + CHAR(10)
            
        -- Add all other changes to extended properties if we have any
        IF LEN(@OtherChangesSQL) > 0
        BEGIN
            SET @sqlText = @sqlText + 
                '-- Add all parsed changes to extended properties' + CHAR(13) + CHAR(10) + 
                @OtherChangesSQL + CHAR(13) + CHAR(10) +
                'GO' + CHAR(13) + CHAR(10)
        END
            
        -- Add the manual changes to extended properties if we have any
        IF LEN(@AddManualChangesSQL) > 0
        BEGIN
            SET @sqlText = @sqlText + 
                '-- Store manual changes in extended properties' + CHAR(13) + CHAR(10) + 
                @AddManualChangesSQL + CHAR(13) + CHAR(10) +
                'GO' + CHAR(13) + CHAR(10)
        END
    END    
    PRINT 'Process completed successfully.'
    
    -- Output the code if requested
    IF @PrintOutCode = 1
        SELECT @sqlText AS ' '
END