using System.Text;
using System.Threading.Tasks;
using Microsoft.VisualStudio.Shell;

namespace SQL2AI.SSMS.Commands
{
    /// <summary>
    /// Command to optimize the selected SQL query.
    /// </summary>
    public sealed class OptimizeQueryCommand : BaseCommand
    {
        public const int CommandId = 0x0100;
        private static OptimizeQueryCommand? _instance;

        private OptimizeQueryCommand(SQL2AIPackage package) : base(package, CommandId) { }

        public static async Task InitializeAsync(SQL2AIPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
            _instance = new OptimizeQueryCommand(package);
        }

        protected override async Task ExecuteAsync()
        {
            var query = await GetSelectedTextAsync();
            if (string.IsNullOrWhiteSpace(query))
            {
                await ShowMessageAsync("Please select a SQL query to optimize.");
                return;
            }

            await WriteOutputAsync("Analyzing query for optimization opportunities...");

            try
            {
                var result = await Package.ApiClient.OptimizeQueryAsync(query);

                var message = new StringBuilder();
                message.AppendLine("=== Query Optimization Results ===\n");

                if (result.Suggestions.Count > 0)
                {
                    message.AppendLine($"Found {result.Suggestions.Count} optimization suggestion(s):\n");

                    foreach (var suggestion in result.Suggestions)
                    {
                        message.AppendLine($"[{suggestion.Severity.ToUpper()}] {suggestion.Title}");
                        message.AppendLine($"  {suggestion.Description}");
                        if (!string.IsNullOrEmpty(suggestion.FixScript))
                        {
                            message.AppendLine($"  Fix: {suggestion.FixScript}");
                        }
                        message.AppendLine();
                    }

                    if (result.EstimatedImprovement > 0)
                    {
                        message.AppendLine($"Estimated improvement: {result.EstimatedImprovement:P0}");
                    }
                }
                else
                {
                    message.AppendLine("No optimization issues found. Query looks good!");
                }

                if (result.Warnings.Count > 0)
                {
                    message.AppendLine("\nWarnings:");
                    foreach (var warning in result.Warnings)
                    {
                        message.AppendLine($"  - {warning}");
                    }
                }

                await WriteOutputAsync(message.ToString());

                if (!string.IsNullOrEmpty(result.OptimizedQuery) &&
                    result.OptimizedQuery != query)
                {
                    var apply = await ConfirmAsync(
                        "An optimized query is available. Would you like to replace the current query?");

                    if (apply)
                    {
                        await ReplaceSelectedTextAsync(result.OptimizedQuery);
                        await WriteOutputAsync("Query replaced with optimized version.");
                    }
                }
            }
            catch (Services.ApiException ex)
            {
                await ShowErrorAsync($"API Error: {ex.Message}");
            }
        }
    }
}
