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