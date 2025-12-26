using System.Text;
using System.Threading.Tasks;
using Microsoft.VisualStudio.Shell;

namespace SQL2AI.SSMS.Commands
{
    /// <summary>
    /// Command to review SQL code for issues.
    /// </summary>
    public sealed class ReviewCodeCommand : BaseCommand
    {
        public const int CommandId = 0x0101;
        private static ReviewCodeCommand? _instance;

        private ReviewCodeCommand(SQL2AIPackage package) : base(package, CommandId) { }

        public static async Task InitializeAsync(SQL2AIPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
            _instance = new ReviewCodeCommand(package);
        }

        protected override async Task ExecuteAsync()
        {
            var code = await GetSelectedTextAsync();
            if (string.IsNullOrWhiteSpace(code))
            {
                await ShowMessageAsync("Please select SQL code to review.");
                return;
            }

            await WriteOutputAsync("Reviewing SQL code...");

            try
            {
                var result = await Package.ApiClient.ReviewCodeAsync(code);

                var message = new StringBuilder();
                message.AppendLine("=== Code Review Results ===\n");

                if (result.Passed)
                {
                    message.AppendLine("PASSED - No critical or high severity issues found.\n");
                }
                else
                {
                    message.AppendLine("FAILED - Issues found that should be addressed.\n");
                }

                message.AppendLine($"Summary:");
                message.AppendLine($"  Critical: {result.CriticalCount}");
                message.AppendLine($"  High: {result.HighCount}");
                message.AppendLine($"  Medium: {result.MediumCount}");
                message.AppendLine($"  Low: {result.LowCount}");
                message.AppendLine();

                if (result.Issues.Count > 0)
                {
                    message.AppendLine("Issues:");
                    message.AppendLine(new string('-', 50));

                    foreach (var issue in result.Issues)
                    {
                        var icon = issue.Severity switch
                        {
                            "critical" => "[!!!]",
                            "high" => "[!!]",
                            "medium" => "[!]",
                            _ => "[i]"
                        };

                        message.AppendLine($"\n{icon} {issue.RuleId}: {issue.Message}");
                        message.AppendLine($"    Category: {issue.Category}");

                        if (issue.LineNumber.HasValue)
                        {
                            message.AppendLine($"    Line: {issue.LineNumber}");
                        }

                        if (!string.IsNullOrEmpty(issue.Suggestion))
                        {
                            message.AppendLine($"    Suggestion: {issue.Suggestion}");
                        }

                        if (!string.IsNullOrEmpty(issue.CodeSnippet))
                        {
                            message.AppendLine($"    Code: {issue.CodeSnippet.Trim()}");
                        }
                    }
                }

                await WriteOutputAsync(message.ToString());

                // Show summary dialog
                var summary = result.Passed
                    ? "Code review passed! No critical issues found."
                    : $"Code review found {result.CriticalCount} critical and {result.HighCount} high severity issues. See Output window for details.";

                await ShowMessageAsync(summary);
            }
            catch (Services.ApiException ex)
            {
                await ShowErrorAsync($"API Error: {ex.Message}");
            }
        }
    }
}
