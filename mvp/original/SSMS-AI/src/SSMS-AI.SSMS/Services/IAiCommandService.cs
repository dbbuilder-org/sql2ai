using System.Threading.Tasks;
using Microsoft.SqlServer.Management.UI.VSIntegration.ObjectExplorer;

namespace SSMSAI.SSMS.Services
{
    /// <summary>
    /// Interface for AI command operations
    /// </summary>
    public interface IAiCommandService
    {
        /// <summary>
        /// Explains a database object using AI
        /// </summary>
        Task ExplainObjectAsync(INodeInformation nodeInfo);

        /// <summary>
        /// Shows the configuration dialog
        /// </summary>
        void ShowConfiguration();

        /// <summary>
        /// Tests the AI provider connection
        /// </summary>
        Task<bool> TestConnectionAsync();
    }
}
