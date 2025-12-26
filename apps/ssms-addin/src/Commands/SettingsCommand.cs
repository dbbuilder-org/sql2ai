using System.Threading.Tasks;
using Microsoft.VisualStudio.Shell;
using SQL2AI.SSMS.UI;

namespace SQL2AI.SSMS.Commands
{
    /// <summary>
    /// Command to open settings dialog.
    /// </summary>
    public sealed class SettingsCommand : BaseCommand
    {
        public const int CommandId = 0x0106;
        private static SettingsCommand? _instance;

        private SettingsCommand(SQL2AIPackage package) : base(package, CommandId) { }

        public static async Task InitializeAsync(SQL2AIPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
            _instance = new SettingsCommand(package);
        }

        protected override async Task ExecuteAsync()
        {
            await Package.JoinableTaskFactory.SwitchToMainThreadAsync();

            var settings = Package.SettingsService.GetSettings();
            var dialog = new SettingsDialog(settings);

            if (dialog.ShowDialog() == true)
            {
                Package.SettingsService.SaveSettings(dialog.Settings);
                Package.RefreshApiClient();

                await WriteOutputAsync("Settings saved successfully.");

                // Test connection if API key provided
                if (!string.IsNullOrEmpty(dialog.Settings.ApiKey))
                {
                    await WriteOutputAsync("Testing API connection...");
                    var connected = await Package.ApiClient.CheckConnectionAsync();
                    if (connected)
                    {
                        await WriteOutputAsync("API connection successful!");
                    }
                    else
                    {
                        await WriteOutputAsync("Warning: Could not connect to API. Please check your settings.");
                    }
                }
            }
        }
    }
}
