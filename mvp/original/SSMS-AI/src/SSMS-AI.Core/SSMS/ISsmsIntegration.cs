namespace SSMSAI.Core.SSMS
{
    /// <summary>
    /// Represents a SQL Server object (table, view, stored procedure, etc.)
    /// </summary>
    public class SqlObject
    {
        public string Name { get; set; }
        public string Schema { get; set; }
        public string Database { get; set; }
        public SqlObjectType Type { get; set; }
        public string FullName => $"[{Database}].[{Schema}].[{Name}]";
        public string Definition { get; set; }
    }

    /// <summary>
    /// Types of SQL Server objects
    /// </summary>
    public enum SqlObjectType
    {
        Table,
        View,
        StoredProcedure,
        Function,
        Trigger,
        Index,
        Unknown
    }

    /// <summary>
    /// Interface for SSMS integration operations
    /// </summary>
    public interface ISsmsIntegration
    {
        /// <summary>
        /// Gets the definition of a SQL object
        /// </summary>
        string GetObjectDefinition(SqlObject sqlObject);

        /// <summary>
        /// Gets the current connection string
        /// </summary>
        string GetConnectionString();

        /// <summary>
        /// Shows a message to the user
        /// </summary>
        void ShowMessage(string message, string title = "SSMS-AI");

        /// <summary>
        /// Shows an error message to the user
        /// </summary>
        void ShowError(string message, string title = "SSMS-AI Error");
    }
}
