using System;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.VisualStudio;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using SQL2AI.SSMS.Commands;
using SQL2AI.SSMS.Services;
using Task = System.Threading.Tasks.Task;

namespace SQL2AI.SSMS
{
    /// <summary>
    /// SQL2.AI SSMS Extension Package.
    /// </summary>
    [PackageRegistration(UseManagedResourcesOnly = true, AllowsBackgroundLoading = true)]
    [InstalledProductRegistration("#110", "#112", "1.0", IconResourceID = 400)]
    [ProvideMenuResource("Menus.ctmenu", 1)]
    [ProvideAutoLoad(VSConstants.UICONTEXT.NoSolution_string, PackageAutoLoadFlags.BackgroundLoad)]
    [ProvideAutoLoad(VSConstants.UICONTEXT.SolutionExists_string, PackageAutoLoadFlags.BackgroundLoad)]
    [Guid(PackageGuidString)]
    public sealed class SQL2AIPackage : AsyncPackage
    {
        public const string PackageGuidString = "A1B2C3D4-E5F6-7890-ABCD-EF1234567890";

        // Services
        private SettingsService? _settingsService;
        private Sql2AiApiClient? _apiClient;

        /// <summary>
        /// Gets the settings service.
        /// </summary>
        public SettingsService SettingsService => _settingsService ??= new SettingsService();

        /// <summary>
        /// Gets the API client.
        /// </summary>
        public Sql2AiApiClient ApiClient
        {
            get
            {
                if (_apiClient == null)
                {
                    var settings = SettingsService.GetSettings();
                    _apiClient = new Sql2AiApiClient(settings);
                }
                return _apiClient;
            }
        }

        /// <summary>
        /// Recreate API client with new settings.
        /// </summary>
        public void RefreshApiClient()
        {
            _apiClient?.Dispose();
            _apiClient = null;
        }

        /// <summary>
        /// Initialize the package.
        /// </summary>
        protected override async Task InitializeAsync(
            CancellationToken cancellationToken,
            IProgress<ServiceProgressData> progress)
        {
            await base.InitializeAsync(cancellationToken, progress);

            // Switch to UI thread for command registration
            await JoinableTaskFactory.SwitchToMainThreadAsync(cancellationToken);

            // Initialize commands
            await OptimizeQueryCommand.InitializeAsync(this);
            await ReviewCodeCommand.InitializeAsync(this);
            await ExplainQueryCommand.InitializeAsync(this);
            await GenerateCrudCommand.InitializeAsync(this);
            await GenerateFromPromptCommand.InitializeAsync(this);
            await AnalyzeExecutionPlanCommand.InitializeAsync(this);
            await SettingsCommand.InitializeAsync(this);

            // Show welcome message on first install
            await ShowWelcomeMessageAsync();
        }

        /// <summary>
        /// Show welcome message if API key not configured.
        /// </summary>
        private async Task ShowWelcomeMessageAsync()
        {
            var settings = SettingsService.GetSettings();
            if (string.IsNullOrEmpty(settings.ApiKey))
            {
                await JoinableTaskFactory.SwitchToMainThreadAsync();

                VsShellUtilities.ShowMessageBox(
                    this,
                    "Welcome to SQL2.AI for SSMS!\n\n" +
                    "To get started, configure your API key:\n" +
                    "Tools > SQL2.AI > Settings\n\n" +
                    "Get your API key at https://sql2.ai",
                    "SQL2.AI",
                    OLEMSGICON.OLEMSGICON_INFO,
                    OLEMSGBUTTON.OLEMSGBUTTON_OK,
                    OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);
            }
        }

        /// <summary>
        /// Write to output window.
        /// </summary>
        public async Task WriteToOutputAsync(string message)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();

            var outputWindow = await GetServiceAsync(typeof(SVsOutputWindow)) as IVsOutputWindow;
            if (outputWindow != null)
            {
                var paneGuid = new Guid("A1B2C3D4-E5F6-7890-ABCD-EF1234567891");
                outputWindow.CreatePane(ref paneGuid, "SQL2.AI", 1, 1);
                outputWindow.GetPane(ref paneGuid, out var pane);
                pane?.OutputStringThreadSafe($"[{DateTime.Now:HH:mm:ss}] {message}\n");
                pane?.Activate();
            }
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _apiClient?.Dispose();
            }
            base.Dispose(disposing);
        }
    }
}
