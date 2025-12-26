using System;
using System.ComponentModel.Design;
using System.Threading.Tasks;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Task = System.Threading.Tasks.Task;

namespace SQL2AI.SSMS.Commands
{
    /// <summary>
    /// Base class for all SQL2.AI commands.
    /// </summary>
    public abstract class BaseCommand
    {
        /// <summary>
        /// Command menu group GUID.
        /// </summary>
        public static readonly Guid CommandSet = new Guid("B2C3D4E5-F6A7-8901-BCDE-F12345678901");

        /// <summary>
        /// Gets the package instance.
        /// </summary>
        protected SQL2AIPackage Package { get; }

        /// <summary>
        /// Gets the service provider.
        /// </summary>
        protected IAsyncServiceProvider ServiceProvider => Package;

        protected BaseCommand(SQL2AIPackage package, int commandId)
        {
            Package = package ?? throw new ArgumentNullException(nameof(package));

            if (package.GetService(typeof(IMenuCommandService)) is OleMenuCommandService commandService)
            {
                var menuCommandId = new CommandID(CommandSet, commandId);
                var menuItem = new OleMenuCommand(Execute, menuCommandId);
                menuItem.BeforeQueryStatus += BeforeQueryStatus;
                commandService.AddCommand(menuItem);
            }
        }

        /// <summary>
        /// Execute the command.
        /// </summary>
        private void Execute(object sender, EventArgs e)
        {
            ThreadHelper.ThrowIfNotOnUIThread();

            Package.JoinableTaskFactory.RunAsync(async () =>
            {
                try
                {
                    await ExecuteAsync();
                }
                catch (Exception ex)
                {
                    await ShowErrorAsync($"Error: {ex.Message}");
                }
            });
        }

        /// <summary>
        /// Override to implement command logic.
        /// </summary>
        protected abstract Task ExecuteAsync();

        /// <summary>
        /// Override to control command visibility.
        /// </summary>
        protected virtual void BeforeQueryStatus(object sender, EventArgs e)
        {
            // Default: always visible
        }

        /// <summary>
        /// Get the currently selected text in the editor.
        /// </summary>
        protected async Task<string> GetSelectedTextAsync()
        {
            await Package.JoinableTaskFactory.SwitchToMainThreadAsync();

            var dte = await Package.GetServiceAsync(typeof(EnvDTE.DTE)) as EnvDTE.DTE;
            if (dte?.ActiveDocument?.Selection is EnvDTE.TextSelection selection)
            {
                var text = selection.Text;
                if (!string.IsNullOrEmpty(text))
                {
                    return text;
                }

                // If no selection, get all text
                selection.SelectAll();
                text = selection.Text;
                selection.MoveToPoint(selection.ActivePoint);
                return text;
            }

            return string.Empty;
        }

        /// <summary>
        /// Insert text at current cursor position.
        /// </summary>
        protected async Task InsertTextAsync(string text)
        {
            await Package.JoinableTaskFactory.SwitchToMainThreadAsync();

            var dte = await Package.GetServiceAsync(typeof(EnvDTE.DTE)) as EnvDTE.DTE;
            if (dte?.ActiveDocument?.Selection is EnvDTE.TextSelection selection)
            {
                selection.Insert(text);
            }
        }

        /// <summary>
        /// Replace selected text.
        /// </summary>
        protected async Task ReplaceSelectedTextAsync(string text)
        {
            await Package.JoinableTaskFactory.SwitchToMainThreadAsync();

            var dte = await Package.GetServiceAsync(typeof(EnvDTE.DTE)) as EnvDTE.DTE;
            if (dte?.ActiveDocument?.Selection is EnvDTE.TextSelection selection)
            {
                selection.Delete();
                selection.Insert(text);
            }
        }

        /// <summary>
        /// Show an information message box.
        /// </summary>
        protected async Task ShowMessageAsync(string message, string title = "SQL2.AI")
        {
            await Package.JoinableTaskFactory.SwitchToMainThreadAsync();

            VsShellUtilities.ShowMessageBox(
                Package,
                message,
                title,
                OLEMSGICON.OLEMSGICON_INFO,
                OLEMSGBUTTON.OLEMSGBUTTON_OK,
                OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);
        }

        /// <summary>
        /// Show an error message box.
        /// </summary>
        protected async Task ShowErrorAsync(string message, string title = "SQL2.AI Error")
        {
            await Package.JoinableTaskFactory.SwitchToMainThreadAsync();

            VsShellUtilities.ShowMessageBox(
                Package,
                message,
                title,
                OLEMSGICON.OLEMSGICON_CRITICAL,
                OLEMSGBUTTON.OLEMSGBUTTON_OK,
                OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);
        }

        /// <summary>
        /// Show a Yes/No confirmation dialog.
        /// </summary>
        protected async Task<bool> ConfirmAsync(string message, string title = "SQL2.AI")
        {
            await Package.JoinableTaskFactory.SwitchToMainThreadAsync();

            var result = VsShellUtilities.ShowMessageBox(
                Package,
                message,
                title,
                OLEMSGICON.OLEMSGICON_QUERY,
                OLEMSGBUTTON.OLEMSGBUTTON_YESNO,
                OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);

            return result == (int)Microsoft.VisualStudio.VSConstants.MessageBoxResult.IDYES;
        }

        /// <summary>
        /// Write to output window.
        /// </summary>
        protected Task WriteOutputAsync(string message)
        {
            return Package.WriteToOutputAsync(message);
        }
    }
}
