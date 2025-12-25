use SVDB_v2025_06_30_1

go
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