using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Windows;
using Microsoft.SqlServer.Management.UI.VSIntegration.ObjectExplorer;
using Microsoft.SqlServer.Management.Smo;
using Serilog;
using SSMSAI.Core.AI;
using SSMSAI.Core.Configuration;
using SSMSAI.AI.Providers;
using SSMSAI.SSMS.UI;

namespace SSMSAI.SSMS.Services
{
    /// <summary>
    /// Implementation of AI command operations
    /// </summary>
    public class AiCommandService : IAiCommandService
    {
        private static readonly ILogger Logger = Log.ForContext<AiCommandService>();
        
        private readonly ConfigurationManager _configManager;
        private IAiProvider _aiProvider;
        private SsmsAiConfiguration _configuration;

        /// <summary>
        /// Constructor
        /// </summary>
        public AiCommandService()
        {
            _configManager = new ConfigurationManager();
            LoadConfiguration();
            Logger.Information("AiCommandService initialized");
        }

        /// <summary>
        /// Loads configuration and initializes AI provider
        /// </summary>
        private void LoadConfiguration()
        {
            try
            {
                _configuration = _configManager.Load();
                
                // Initialize AI provider based on configuration
                if (_configuration.ApiProvider == "OpenAI")
                {
                    _aiProvider = new OpenAiProvider();
                    if (!string.IsNullOrEmpty(_configuration.ApiKey))
                    {
                        _aiProvider.Configure(_configuration.ApiKey, _configuration.Model);
                    }
                }
                
                Logger.Information("Configuration loaded. Provider: {Provider}, Configured: {IsConfigured}", 
                    _configuration.ApiProvider, _aiProvider?.IsConfigured ?? false);
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Failed to load configuration");
                _configuration = new SsmsAiConfiguration();
            }
        }

        /// <summary>
        /// Explains a database object using AI
        /// </summary>
        public async Task ExplainObjectAsync(INodeInformation nodeInfo)
        {
            try
            {
                Logger.Information("Starting explain operation for object: {ObjectType}", 
                    nodeInfo.Object?.GetType().Name);

                // Check if AI provider is configured
                if (_aiProvider == null || !_aiProvider.IsConfigured)
                {
                    Logger.Warning("AI provider not configured, showing configuration dialog");
                    ShowConfiguration();
                    return;
                }

                // Show progress dialog
                var progressDialog = new ProgressDialog("Analyzing object with AI...");
                progressDialog.Show();

                try
                {
                    // Extract object information
                    var objectInfo = ExtractObjectInformation(nodeInfo);
                    
                    // Create AI prompt
                    var prompt = CreateExplainPrompt(objectInfo);
                    
                    // Send request to AI provider
                    var request = new AiRequest
                    {
                        Prompt = prompt,
                        SystemPrompt = "You are an expert SQL Server database administrator. Explain database objects clearly and provide useful insights.",
                        Temperature = _configuration.Temperature,
                        MaxTokens = _configuration.MaxTokens,
                        Model = _configuration.Model
                    };

                    var response = await _aiProvider.SendRequestAsync(request);
                    
                    progressDialog.Close();

                    if (response.Success)
                    {
                        // Show results in a dialog
                        var resultDialog = new ResultDialog(objectInfo.Name, response.Content);
                        resultDialog.ShowDialog();
                    }
                    else
                    {
                        Logger.Error("AI request failed: {ErrorMessage}", response.ErrorMessage);
                        MessageBox.Show($"AI request failed: {response.ErrorMessage}", 
                            "SSMS-AI Error", MessageBoxButton.OK, MessageBoxImage.Error);
                    }
                }
                finally
                {
                    progressDialog?.Close();
                }
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Error in ExplainObjectAsync");
                MessageBox.Show($"An error occurred: {ex.Message}", 
                    "SSMS-AI Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Extracts relevant information from database object
        /// </summary>
        private ObjectInformation ExtractObjectInformation(INodeInformation nodeInfo)
        {
            var info = new ObjectInformation
            {
                Type = nodeInfo.Object.GetType().Name,
                Name = nodeInfo.UrnPath
            };

            // Handle stored procedures specifically
            if (nodeInfo.Object is StoredProcedure storedProcedure)
            {
                info.Name = storedProcedure.Name;
                info.Schema = storedProcedure.Schema;
                info.Definition = storedProcedure.TextBody;
                
                // Get parameters
                foreach (StoredProcedureParameter param in storedProcedure.Parameters)
                {
                    info.Parameters.Add($"{param.Name} {param.DataType} {(param.IsOutputParameter ? "OUTPUT" : "")}");
                }
            }

            return info;
        }

        /// <summary>
        /// Creates an explanation prompt for the object
        /// </summary>
        private string CreateExplainPrompt(ObjectInformation objectInfo)
        {
            var prompt = $@"Please explain this SQL Server {objectInfo.Type}:

Name: {objectInfo.Schema}.{objectInfo.Name}

Definition:
{objectInfo.Definition}

Please provide:
1. Purpose and functionality
2. Parameters explanation (if any)
3. Key logic and operations
4. Performance considerations
5. Potential improvements or best practices

Be clear and concise, suitable for a SQL developer.";

            return prompt;
        }

        /// <summary>
        /// Shows the configuration dialog
        /// </summary>
        public void ShowConfiguration()
        {
            try
            {
                var configDialog = new ConfigurationDialog(_configuration);
                if (configDialog.ShowDialog() == true)
                {
                    // Save updated configuration
                    _configManager.Save(_configuration);
                    
                    // Reload configuration and reinitialize provider
                    LoadConfiguration();
                    
                    Logger.Information("Configuration updated successfully");
                }
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Error showing configuration dialog");
                MessageBox.Show($"Error opening configuration: {ex.Message}", 
                    "SSMS-AI Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Tests the AI provider connection
        /// </summary>
        public async Task<bool> TestConnectionAsync()
        {
            try
            {
                if (_aiProvider == null || !_aiProvider.IsConfigured)
                {
                    Logger.Warning("AI provider not configured for connection test");
                    return false;
                }

                Logger.Information("Testing AI provider connection");
                var result = await _aiProvider.TestConnectionAsync();
                Logger.Information("Connection test result: {Result}", result);
                
                return result;
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Error testing AI provider connection");
                return false;
            }
        }
    }

    /// <summary>
    /// Represents extracted database object information
    /// </summary>
    public class ObjectInformation
    {
        public string Type { get; set; }
        public string Name { get; set; }
        public string Schema { get; set; }
        public string Definition { get; set; }
        public List<string> Parameters { get; set; } = new List<string>();
    }
}
