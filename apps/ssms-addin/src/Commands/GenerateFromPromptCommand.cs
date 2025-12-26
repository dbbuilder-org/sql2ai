using System.Threading.Tasks;
using Microsoft.VisualStudio.Shell;
using SQL2AI.SSMS.Models;
using SQL2AI.SSMS.UI;

namespace SQL2AI.SSMS.Commands
{
    /// <summary>
    /// Command to generate SQL from natural language prompt.
    /// </summary>
    public sealed class GenerateFromPromptCommand : BaseCommand
    {
        public const int CommandId = 0x0104;
        private static GenerateFromPromptCommand? _instance;

        private GenerateFromPromptCommand(SQL2AIPackage package) : base(package, CommandId) { }

        public static async Task InitializeAsync(SQL2AIPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
            _instance = new GenerateFromPromptCommand(package);
        }

        protected override async Task ExecuteAsync()
        {
            await Package.JoinableTaskFactory.SwitchToMainThreadAsync();

            // Show prompt dialog
            var dialog = new PromptDialog();
            if (dialog.ShowDialog() != true)
            {
                return;
            }

            var prompt = dialog.Prompt;
            var objectType = dialog.SelectedObjectType;

            if (string.IsNullOrWhiteSpace(prompt))
            {
                await ShowMessageAsync("Please enter a description of what you want to generate.");
                return;
            }

            await WriteOutputAsync($"Generating {objectType} from prompt...");

            try
            {
                var request = new DdlGenerationRequest
                {
                    Prompt = prompt,
                    ObjectType = objectType,
                    IncludeErrorHandling = true,
                    IncludeAuditLogging = dialog.IncludeAudit
                };

                var result = await Package.ApiClient.GenerateFromPromptAsync(request);

                await WriteOutputAsync($"Generated {result.ObjectType}: {result.ObjectName}");

                if (result.Warnings.Count > 0)
                {
                    await WriteOutputAsync("Warnings:");
                    foreach (var warning in result.Warnings)
                    {
                        await WriteOutputAsync($"  - {warning}");
                    }
                }

                if (result.SecurityNotes.Count > 0)
                {
                    await WriteOutputAsync("Security Notes:");
                    foreach (var note in result.SecurityNotes)
                    {
                        await WriteOutputAsync($"  - {note}");
                    }
                }

                // Insert generated code
                await InsertTextAsync("\n\n" + result.SqlScript);
                await WriteOutputAsync("SQL code inserted into editor.");

                if (!string.IsNullOrEmpty(result.RollbackScript))
                {
                    await WriteOutputAsync("\nRollback script available in Output window.");
                    await WriteOutputAsync("--- Rollback Script ---");
                    await WriteOutputAsync(result.RollbackScript);
                }
            }
            catch (Services.ApiException ex)
            {
                await ShowErrorAsync($"API Error: {ex.Message}");
            }
        }
    }
}
