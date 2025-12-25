using System;
using System.Threading;
using System.Windows;
using Serilog;

namespace SSMSAI.SSMS.UI
{
    /// <summary>
    /// Progress dialog for long-running operations
    /// </summary>
    public partial class ProgressDialog : Window
    {
        private static readonly ILogger Logger = Log.ForContext<ProgressDialog>();
        private CancellationTokenSource _cancellationTokenSource;

        /// <summary>
        /// Gets the cancellation token for this operation
        /// </summary>
        public CancellationToken CancellationToken => _cancellationTokenSource?.Token ?? CancellationToken.None;

        /// <summary>
        /// Constructor
        /// </summary>
        public ProgressDialog(string message = "Processing...")
        {
            InitializeComponent();
            _cancellationTokenSource = new CancellationTokenSource();
            
            MessageTextBlock.Text = message;
            Logger.Information("Progress dialog created with message: {Message}", message);
        }

        /// <summary>
        /// Updates the progress message
        /// </summary>
        public void UpdateMessage(string message)
        {
            Dispatcher.BeginInvoke(new Action(() =>
            {
                MessageTextBlock.Text = message;
            }));
        }

        /// <summary>
        /// Handles Cancel button click
        /// </summary>
        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                Logger.Information("Progress dialog cancelled by user");
                _cancellationTokenSource?.Cancel();
                DialogResult = false;
                Close();
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Error handling cancel button click");
            }
        }

        /// <summary>
        /// Override close to handle cleanup
        /// </summary>
        protected override void OnClosed(EventArgs e)
        {
            _cancellationTokenSource?.Dispose();
            base.OnClosed(e);
        }
    }
}
