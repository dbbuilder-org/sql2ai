using System.Text;
using System.Threading.Tasks;
using Microsoft.VisualStudio.Shell;

namespace SQL2AI.SSMS.Commands
{
    /// <summary>
    /// Command to explain a SQL query in natural language.
    /// </summary>
    public sealed class ExplainQueryCommand : BaseCommand
    {
        public const int CommandId = 0x0102;
        private static ExplainQueryCommand? _instance;

        private ExplainQueryCommand(SQL2AIPackage package) : base(package, CommandId) { }

        public static async Task InitializeAsync(SQL2AIPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
            _instance = new ExplainQueryCommand(package);
        }

        protected override async Task ExecuteAsync()
        {
            var query = await GetSelectedTextAsync();
            if (string.IsNullOrWhiteSpace(query))
            {
                await ShowMessageAsync("Please select a SQL query to explain.");
                return;
            }

            await WriteOutputAsync("Analyzing query...");

            try
            {
                var result = await Package.ApiClient.ExplainQueryAsync(query);

                var message = new StringBuilder();
                message.AppendLine("=== Query Explanation ===\n");

                message.AppendLine("Summary:");
                message.AppendLine(result.Summary);
                message.AppendLine();

                if (result.Steps.Count > 0)
                {
                    message.AppendLine("Execution Steps:");
                    for (int i = 0; i < result.Steps.Count; i++)
                    {
                        message.AppendLine($"  {i + 1}. {result.Steps[i]}");
                    }
                    message.AppendLine();
                }

                if (result.TablesInvolved.Count > 0)
                {
                    message.AppendLine($"Tables Involved: {string.Join(", ", result.TablesInvolved)}");
                    message.AppendLine();
                }

                if (!string.IsNullOrEmpty(result.PerformanceNotes))
                {
                    message.AppendLine("Performance Notes:");
                    message.AppendLine($"  {result.PerformanceNotes}");
                }

                await WriteOutputAsync(message.ToString());
                await ShowMessageAsync($"Query Explanation:\n\n{result.Summary}\n\nSee Output window for details.");
            }
            catch (Services.ApiException ex)
            {
                await ShowErrorAsync($"API Error: {ex.Message}");
            }
        }
    }
}
