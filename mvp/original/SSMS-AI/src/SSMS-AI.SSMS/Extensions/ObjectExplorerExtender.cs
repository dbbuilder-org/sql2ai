using System;
using System.ComponentModel.Composition;
using System.Drawing;
using Microsoft.SqlServer.Management.UI.VSIntegration.ObjectExplorer;
using Microsoft.SqlServer.Management.Smo;
using Serilog;
using SSMSAI.SSMS.Services;

namespace SSMSAI.SSMS.Extensions
{
    /// <summary>
    /// Extends Object Explorer with AI context menu commands
    /// </summary>
    [Export(typeof(IObjectExplorerExtender))]
    public class ObjectExplorerExtender : IObjectExplorerExtender
    {
        private static readonly ILogger Logger = Log.ForContext<ObjectExplorerExtender>();
        private IAiCommandService _aiCommandService;

        /// <summary>
        /// Constructor with dependency injection
        /// </summary>
        public ObjectExplorerExtender()
        {
            Logger.Information("ObjectExplorerExtender initialized");
        }

        /// <summary>
        /// Initialize the extender with services
        /// </summary>
        public void Initialize(IAiCommandService aiCommandService)
        {
            _aiCommandService = aiCommandService ?? throw new ArgumentNullException(nameof(aiCommandService));
            Logger.Information("ObjectExplorerExtender services initialized");
        }

        /// <summary>
        /// Gets context menu items for the selected object
        /// </summary>
        public ObjectExplorerMenuItem[] GetContextMenuItems(INodeInformation nodeInfo)
        {
            try
            {
                if (nodeInfo?.Object == null)
                {
                    Logger.Debug("No object selected, returning empty menu");
                    return new ObjectExplorerMenuItem[0];
                }

                // Only show menu for stored procedures initially (Week 2 scope)
                if (nodeInfo.Object is StoredProcedure storedProcedure)
                {
                    Logger.Debug("Creating context menu for stored procedure: {ProcedureName}", storedProcedure.Name);
                    
                    return new ObjectExplorerMenuItem[]
                    {
                        new ObjectExplorerMenuItem("Explain with AI", new Bitmap(16, 16))
                        {
                            // Store object reference for later use
                            Tag = nodeInfo,
                            Enabled = true
                        }
                    };
                }

                // Future: Add support for other object types
                // Tables, Views, Functions, etc. will be added in Phase 2

                Logger.Debug("Object type {ObjectType} not supported yet", nodeInfo.Object.GetType().Name);
                return new ObjectExplorerMenuItem[0];
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Error creating context menu items");
                return new ObjectExplorerMenuItem[0];
            }
        }

        /// <summary>
        /// Handles menu item click events
        /// </summary>
        public void OnMenuItemClick(ObjectExplorerMenuItem menuItem, INodeInformation nodeInfo)
        {
            try
            {
                Logger.Information("Context menu item clicked: {MenuText}", menuItem.Text);

                if (_aiCommandService == null)
                {
                    Logger.Error("AI Command Service not initialized");
                    return;
                }

                if (menuItem.Text == "Explain with AI")
                {
                    // Execute the explain command asynchronously
                    _ = _aiCommandService.ExplainObjectAsync(nodeInfo);
                }
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Error handling menu item click");
                // Show user-friendly error message
                System.Windows.MessageBox.Show(
                    $"An error occurred: {ex.Message}", 
                    "SSMS-AI Error", 
                    System.Windows.MessageBoxButton.OK, 
                    System.Windows.MessageBoxImage.Error);
            }
        }
    }
}
