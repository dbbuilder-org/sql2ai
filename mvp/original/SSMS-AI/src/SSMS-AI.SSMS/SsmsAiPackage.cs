using Microsoft.VisualStudio.Shell;
using System;
using System.Runtime.InteropServices;
using System.Threading;
using Task = System.Threading.Tasks.Task;
using Microsoft.VisualStudio.Shell.Interop;
using Serilog;
using System.IO;
using System.Reflection;
using System.ComponentModel.Composition;
using SSMSAI.SSMS.Extensions;
using SSMSAI.SSMS.Services;

namespace SSMSAI.SSMS
{
    /// <summary>
    /// This is the class that implements the package exposed by this assembly.
    /// </summary>
    [PackageRegistration(UseManagedResourcesOnly = true, AllowsBackgroundLoading = true)]
    [Guid(SsmsAiPackage.PackageGuidString)]
    [ProvideMenuResource("Menus.ctmenu", 1)]
    [ProvideAutoLoad(UIContextGuids80.NoSolution, PackageAutoLoadFlags.BackgroundLoad)]
    public sealed class SsmsAiPackage : AsyncPackage
    {
        /// <summary>
        /// SSMS-AI package GUID string.
        /// </summary>
        public const string PackageGuidString = "c3d4e5f6-a7b8-9012-cd34-567890123456";

        private ILogger _logger;
        private IAiCommandService _aiCommandService;
        private ObjectExplorerExtender _objectExplorerExtender;

        #region Package Members

        /// <summary>
        /// Initialization of the package; this method is called right after the package is sited, so this is the place
        /// where you can put all the initialization code that rely on services provided by VisualStudio.
        /// </summary>
        /// <param name="cancellationToken">A cancellation token to monitor for initialization cancellation, which can occur when VS is shutting down.</param>
        /// <param name="progress">A provider for progress updates.</param>
        /// <returns>A task representing the async work of package initialization, or an already completed task if there is none. Do not return null from this method.</returns>
        protected override async Task InitializeAsync(CancellationToken cancellationToken, IProgress<ServiceProgressData> progress)
        {
            try
            {
                // Initialize logging first
                InitializeLogging();
                _logger.Information("SSMS-AI Package initializing...");

                // When initialized asynchronously, the current thread may be a background thread at this point.
                // Do any initialization that requires the UI thread after switching to the UI thread.
                await this.JoinableTaskFactory.SwitchToMainThreadAsync(cancellationToken);

                // Initialize services and register MEF components
                InitializeServices();

                _logger.Information("SSMS-AI Package initialized successfully");
            }
            catch (Exception ex)
            {
                _logger?.Error(ex, "Failed to initialize SSMS-AI package");
                throw;
            }
        }

        private void InitializeLogging()
        {
            try
            {
                // Get the path to the extension's installation directory
                var assemblyLocation = Assembly.GetExecutingAssembly().Location;
                var extensionDir = Path.GetDirectoryName(assemblyLocation);
                var logDir = Path.Combine(extensionDir, "Logs");

                // Ensure log directory exists
                Directory.CreateDirectory(logDir);

                // Configure Serilog
                Log.Logger = new LoggerConfiguration()
                    .MinimumLevel.Debug()
                    .WriteTo.File(
                        Path.Combine(logDir, "ssms-ai-.log"),
                        rollingInterval: RollingInterval.Day,
                        retainedFileCountLimit: 7,
                        outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj}{NewLine}{Exception}")
                    .WriteTo.Console()
                    .CreateLogger();

                _logger = Log.Logger;
                _logger.Information("Logging initialized. Log directory: {LogDir}", logDir);
            }
            catch (Exception ex)
            {
                // Fallback to console only if file logging fails
                Log.Logger = new LoggerConfiguration()
                    .MinimumLevel.Debug()
                    .WriteTo.Console()
                    .CreateLogger();

                _logger = Log.Logger;
                _logger.Error(ex, "Failed to initialize file logging, using console only");
            }
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _logger?.Information("SSMS-AI Package disposing");
                Log.CloseAndFlush();
            }
            base.Dispose(disposing);
        }

        #endregion
    }
}

        /// <summary>
        /// Initialize services and MEF components
        /// </summary>
        private void InitializeServices()
        {
            try
            {
                _logger.Information("Initializing SSMS-AI services");

                // Initialize AI command service
                _aiCommandService = new AiCommandService();

                // Initialize Object Explorer extender
                _objectExplorerExtender = new ObjectExplorerExtender();
                _objectExplorerExtender.Initialize(_aiCommandService);

                _logger.Information("SSMS-AI services initialized successfully");
            }
            catch (Exception ex)
            {
                _logger.Error(ex, "Failed to initialize services");
                throw;
            }
        }
