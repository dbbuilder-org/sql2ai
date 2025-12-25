using System;
using System.ComponentModel.Design;
using System.Threading.Tasks;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Serilog;
using SSMSAI.Core.AI;
using SSMSAI.Core.Configuration;
using SSMSAI.AI.Providers;
using SSMSAI.SSMS.UI;
using System.Windows;

namespace SSMSAI.SSMS.Commands
{
    /// <summary>
    /// Command handler for "Explain with AI" context menu item
    /// </summary>
    internal sealed class ExplainWithAiCommand
    {
        private static readonly ILogger Logger = Log.ForContext<ExplainWithAiCommand>();

        /// <summary>
        /// Command ID for the Explain with AI command
        /// </summary>
        public const int CommandId = 0x0100;

        /// <summary>
        /// Command menu group (command set GUID)
        /// </summary>
        public static readonly Guid CommandSet = new Guid("c3d4e5f6-a7b8-9012-cd34-567890123457");

        /// <summary>
        /// VS Package that provides this command
        /// </summary>
        private readonly AsyncPackage _package;

        /// <summary>
        /// Configuration manager for accessing settings
        /// </summary>
        private readonly ConfigurationManager _configManager;

        /// <summary>
        /// AI provider for making requests
        /// </summary>
        private readonly IAiProvider _aiProvider;

        /// <summary>
        /// Initializes a new instance of the ExplainWithAiCommand class
        /// </summary>
        private ExplainWithAiCommand(AsyncPackage package, OleMenuCommandService commandService)
        {
            _package = package ?? throw new ArgumentNullException(nameof(package));
            commandService = commandService ?? throw new ArgumentNullException(nameof(commandService));

            _configManager = new ConfigurationManager();
            _aiProvider = new OpenAiProvider();

            // Load configuration and configure AI provider
            var config = _configManager.Load();
            if (!string.IsNullOrEmpty(config.ApiKey))
            {
                _aiProvider.Configure(config.ApiKey, config.Model);
            }

            var menuCommandID = new CommandID(CommandSet, CommandId);
            var menuItem = new OleMenuCommand(this.Execute, menuCommandID);
            
            // Set visibility based on context (only show for stored procedures)
            menuItem.BeforeQueryStatus += OnBeforeQueryStatus;
            
            commandService.AddCommand(menuItem);
            Logger.Information("ExplainWithAiCommand initialized");
        }

        /// <summary>
        /// Gets the instance of the command
        /// </summary>
        public static ExplainWithAiCommand Instance { get; private set; }

        /// <summary>
        /// Gets the service provider from the owner package
        /// </summary>
        private Microsoft.VisualStudio.Shell.IAsyncServiceProvider ServiceProvider => _package;

        /// <summary>
        /// Initializes the singleton instance of the command
        /// </summary>
        public static async Task InitializeAsync(AsyncPackage package)
        {
            // Switch to the main thread - the call to AddCommand in ExplainWithAiCommand's constructor requires
            // the UI thread.
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync(package.DisposalToken);

            OleMenuCommandService commandService = await package.GetServiceAsync((typeof(IMenuCommandService))) as OleMenuCommandService;
            Instance = new ExplainWithAiCommand(package, commandService);
        }

        /// <summary>
        /// Determines whether the command should be visible and enabled
        /// </summary>
        private void OnBeforeQueryStatus(object sender, EventArgs e)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            
            var command = sender as OleMenuCommand;
            if (command == null) return;

            try
            {
                // For now, always show the command - in a real implementation,
                // we would check if the selected item is a stored procedure
                // This requires accessing SSMS Object Explorer which is complex
                command.Visible = true;
                command.Enabled = true;
                
                // Check if AI provider is configured
                if (!_aiProvider.IsConfigured)
                {
                    command.Text = "Explain with AI (Not Configured)";
                }
                else
                {
                    command.Text = "Explain with AI";
                }

                Logger.Debug("Command visibility updated: Visible={Visible}, Enabled={Enabled}", 
                    command.Visible, command.Enabled);
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Error in OnBeforeQueryStatus");
                command.Visible = false;
                command.Enabled = false;
            }
        }

        /// <summary>
        /// Executes the command when user clicks "Explain with AI"
        /// </summary>
        private void Execute(object sender, EventArgs e)
        {
            ThreadHelper.ThrowIfNotOnUIThread();

            try
            {
                Logger.Information("ExplainWithAi command executed");

                // Check if AI provider is configured
                if (!_aiProvider.IsConfigured)
                {
                    ShowConfigurationDialog();
                    return;
                }

                // For MVP, use a hardcoded sample stored procedure
                // In a real implementation, we would extract the selected stored procedure from SSMS
                var sampleProcedure = @"
CREATE PROCEDURE GetCustomerOrders
    @CustomerId INT,
    @StartDate DATETIME = NULL,
    @EndDate DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        o.OrderId,
        o.OrderDate,
        o.TotalAmount,
        c.CustomerName
    FROM Orders o
    INNER JOIN Customers c ON o.CustomerId = c.CustomerId
    WHERE o.CustomerId = @CustomerId
        AND (@StartDate IS NULL OR o.OrderDate >= @StartDate)
        AND (@EndDate IS NULL OR o.OrderDate <= @EndDate)
    ORDER BY o.OrderDate DESC;
END";

                // Execute AI explanation asynchronously
                _ = Task.Run(async () => await ExplainProcedureAsync(sampleProcedure));
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Error executing ExplainWithAi command");
                ShowErrorMessage("An error occurred while executing the command.", ex.Message);
            }
        }

        /// <summary>
        /// Explains a stored procedure using AI
        /// </summary>
        private async Task ExplainProcedureAsync(string procedureText)
        {
            try
            {
                Logger.Information("Starting AI explanation for stored procedure");

                // Show progress dialog
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                
                var progressDialog = new ProgressDialog();
                progressDialog.Show();

                // Prepare AI request
                var prompt = $@"Please explain this SQL Server stored procedure in detail:

{procedureText}

Provide an explanation that covers:
1. Purpose and functionality
2. Parameters and their usage
3. Main logic and flow
4. Joins and relationships
5. Any potential improvements or observations

Please write in a clear, professional manner suitable for developers.";

                var request = new AiRequest
                {
                    Prompt = prompt,
                    SystemPrompt = "You are an expert SQL Server database developer and consultant. Provide clear, detailed explanations of database objects and code.",
                    Temperature = 0.3, // Lower temperature for more consistent technical explanations
                    MaxTokens = 1500
                };

                // Make AI request
                var response = await _aiProvider.SendRequestAsync(request);

                // Switch back to UI thread to update UI
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                progressDialog.Close();

                if (response.Success)
                {
                    Logger.Information("AI explanation completed successfully");
                    
                    // Show result dialog
                    var resultDialog = new AiResultDialog(response.Content, "Stored Procedure Explanation");
                    resultDialog.ShowDialog();
                }
                else
                {
                    Logger.Error("AI request failed: {ErrorMessage}", response.ErrorMessage);
                    ShowErrorMessage("AI Request Failed", response.ErrorMessage);
                }
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Exception in ExplainProcedureAsync");
                
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                ShowErrorMessage("An error occurred while processing the AI request.", ex.Message);
            }
        }

        /// <summary>
        /// Shows the configuration dialog
        /// </summary>
        private void ShowConfigurationDialog()
        {
            try
            {
                Logger.Information("Showing configuration dialog");
                
                var configDialog = new ConfigurationDialog(_configManager);
                var result = configDialog.ShowDialog();

                if (result == true)
                {
                    // Reload configuration and reconfigure AI provider
                    var config = _configManager.Load();
                    if (!string.IsNullOrEmpty(config.ApiKey))
                    {
                        _aiProvider.Configure(config.ApiKey, config.Model);
                        Logger.Information("AI provider reconfigured after settings change");
                    }
                }
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Error showing configuration dialog");
                ShowErrorMessage("Configuration Error", "Failed to open configuration dialog.");
            }
        }

        /// <summary>
        /// Shows an error message to the user
        /// </summary>
        private void ShowErrorMessage(string title, string message)
        {
            VsShellUtilities.ShowMessageBox(
                _package,
                message,
                title,
                OLEMSGICON.OLEMSGICON_CRITICAL,
                OLEMSGBUTTON.OLEMSGBUTTON_OK,
                OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);
        }
    }
}