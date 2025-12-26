using System.Text;
using System.Threading.Tasks;
using Microsoft.VisualStudio.Shell;

namespace SQL2AI.SSMS.Commands
{
    /// <summary>
    /// Command to analyze an execution plan with AI.
    /// </summary>
    public sealed class AnalyzeExecutionPlanCommand : BaseCommand
    {
        public const int CommandId = 0x0105;
        private static AnalyzeExecutionPlanCommand? _instance;

        private AnalyzeExecutionPlanCommand(SQL2AIPackage package) : base(package, CommandId) { }

        public static async Task InitializeAsync(SQL2AIPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
            _instance = new AnalyzeExecutionPlanCommand(package);
        }

        protected override async Task ExecuteAsync()
        {
            var planXml = await GetSelectedTextAsync();

            // Check if it looks like an execution plan
            if (string.IsNullOrWhiteSpace(planXml) || !planXml.Contains("ShowPlanXML"))
            {
                await ShowMessageAsync(
                    "Please select an execution plan XML to analyze.\n\n" +
                    "To get the execution plan:\n" +
                    "1. Run your query with 'Include Actual Execution Plan' (Ctrl+M)\n" +
                    "2. Right-click the plan and select 'Show Execution Plan XML'\n" +
                    "3. Select all the XML and run this command");
                return;
            }

            await WriteOutputAsync("Analyzing execution plan...");

            try
            {
                var result = await Package.ApiClient.AnalyzeExecutionPlanAsync(planXml);

                var message = new StringBuilder();
                message.AppendLine("=== Execution Plan Analysis ===\n");

                message.AppendLine("Summary:");
                message.AppendLine(result.Summary);
                message.AppendLine();

                message.AppendLine($"Estimated Cost: {result.EstimatedCost:N2}");
                message.AppendLine();

                if (result.Issues.Count > 0)
                {
                    message.AppendLine($"Issues Found ({result.Issues.Count}):");
                    message.AppendLine(new string('-', 40));

                    foreach (var issue in result.Issues)
                    {
                        message.AppendLine($"\nOperator: {issue.Operator}");
                        message.AppendLine($"  Issue: {issue.Issue}");
                        message.AppendLine($"  Impact: {issue.Impact}");
                        if (!string.IsNullOrEmpty(issue.Fix))
                        {
                            message.AppendLine($"  Suggested Fix: {issue.Fix}");
                        }
                    }
                    message.AppendLine();
                }

                if (result.Recommendations.Count > 0)
                {
                    message.AppendLine("Recommendations:");
                    for (int i = 0; i < result.Recommendations.Count; i++)
                    {
                        message.AppendLine($"  {i + 1}. {result.Recommendations[i]}");
                    }
                }

                await WriteOutputAsync(message.ToString());

                // Show summary dialog
                var summaryMsg = result.Issues.Count > 0
                    ? $"Found {result.Issues.Count} issues in execution plan.\n\nSee Output window for details and recommendations."
                    : "Execution plan looks good! No significant issues found.";

                await ShowMessageAsync(summaryMsg);
            }
            catch (Services.ApiException ex)
            {
                await ShowErrorAsync($"API Error: {ex.Message}");
            }
        }
    }
}
