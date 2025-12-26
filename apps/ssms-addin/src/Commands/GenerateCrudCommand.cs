using System.Text;
using System.Threading.Tasks;
using Microsoft.VisualStudio.Shell;

namespace SQL2AI.SSMS.Commands
{
    /// <summary>
    /// Command to generate CRUD stored procedures for a table.
    /// </summary>
    public sealed class GenerateCrudCommand : BaseCommand
    {
        public const int CommandId = 0x0103;
        private static GenerateCrudCommand? _instance;

        private GenerateCrudCommand(SQL2AIPackage package) : base(package, CommandId) { }

        public static async Task InitializeAsync(SQL2AIPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
            _instance = new GenerateCrudCommand(package);
        }

        protected override async Task ExecuteAsync()
        {
            var selectedText = await GetSelectedTextAsync();

            // Try to extract table name from selected text or prompt user
            var tableName = ExtractTableName(selectedText);

            if (string.IsNullOrWhiteSpace(tableName))
            {
                await ShowMessageAsync(
                    "Please select a table name or position cursor on a table reference.\n\n" +
                    "Example: Right-click on 'Customers' to generate CRUD for that table.");
                return;
            }

            // Parse schema.table format
            var parts = tableName.Split('.');
            var schemaName = parts.Length > 1 ? parts[0].Trim('[', ']') : "dbo";
            var table = parts.Length > 1 ? parts[1].Trim('[', ']') : parts[0].Trim('[', ']');

            await WriteOutputAsync($"Generating CRUD procedures for {schemaName}.{table}...");

            try
            {
                var result = await Package.ApiClient.GenerateCrudAsync(table, schemaName);

                var message = new StringBuilder();
                message.AppendLine($"=== CRUD Procedures for {result.TableName} ===\n");

                message.AppendLine($"Generated {result.Procedures.Count} procedures:");
                foreach (var proc in result.Procedures)
                {
                    message.AppendLine($"  - {proc.Name} ({proc.Type})");
                }
                message.AppendLine();

                await WriteOutputAsync(message.ToString());

                // Ask if user wants to insert the generated code
                var insert = await ConfirmAsync(
                    $"Generated {result.Procedures.Count} CRUD procedures.\n\n" +
                    "Would you like to insert the SQL script into the editor?");

                if (insert)
                {
                    await InsertTextAsync("\n\n" + result.CombinedScript);
                    await WriteOutputAsync("CRUD procedures inserted into editor.");
                }
            }
            catch (Services.ApiException ex)
            {
                await ShowErrorAsync($"API Error: {ex.Message}");
            }
        }

        private static string? ExtractTableName(string text)
        {
            if (string.IsNullOrWhiteSpace(text))
                return null;

            text = text.Trim();

            // Handle simple table name
            if (!text.Contains(" ") && !text.Contains("\n"))
            {
                return text;
            }

            // Try to extract from FROM clause
            var fromIndex = text.IndexOf("FROM ", System.StringComparison.OrdinalIgnoreCase);
            if (fromIndex >= 0)
            {
                var afterFrom = text.Substring(fromIndex + 5).Trim();
                var endIndex = afterFrom.IndexOfAny(new[] { ' ', '\n', '\r', ',' });
                return endIndex > 0 ? afterFrom.Substring(0, endIndex) : afterFrom;
            }

            // Try to extract from INSERT INTO
            var insertIndex = text.IndexOf("INSERT INTO ", System.StringComparison.OrdinalIgnoreCase);
            if (insertIndex >= 0)
            {
                var afterInsert = text.Substring(insertIndex + 12).Trim();
                var endIndex = afterInsert.IndexOfAny(new[] { ' ', '\n', '\r', '(' });
                return endIndex > 0 ? afterInsert.Substring(0, endIndex) : afterInsert;
            }

            // Try to extract from UPDATE
            var updateIndex = text.IndexOf("UPDATE ", System.StringComparison.OrdinalIgnoreCase);
            if (updateIndex >= 0)
            {
                var afterUpdate = text.Substring(updateIndex + 7).Trim();
                var endIndex = afterUpdate.IndexOfAny(new[] { ' ', '\n', '\r' });
                return endIndex > 0 ? afterUpdate.Substring(0, endIndex) : afterUpdate;
            }

            return null;
        }
    }
}
