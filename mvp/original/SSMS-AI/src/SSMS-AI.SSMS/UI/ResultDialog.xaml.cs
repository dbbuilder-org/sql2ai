using System;
using System.Windows;
using Serilog;

namespace SSMSAI.SSMS.UI
{
    /// <summary>
    /// Dialog for displaying AI analysis results
    /// </summary>
    public partial class ResultDialog : Window
    {
        private static readonly ILogger Logger = Log.ForContext<ResultDialog>();
        private readonly string _content;

        /// <summary>
        /// Constructor
        /// </summary>
        public ResultDialog(string objectName, string content)
        {
            InitializeComponent();
            
            _content = content ?? string.Empty;
            TitleTextBlock.Text = $"Analysis: {objectName}";
            ContentTextBox.Text = _content;
            
            Logger.Information("Result dialog created for object: {ObjectName}", objectName);
        }

        /// <summary>
        /// Handles Copy button click
        /// </summary>
        private void CopyButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (!string.IsNullOrEmpty(_content))
                {
                    Clipboard.SetText(_content);
                    MessageBox.Show("Content copied to clipboard.", "SSMS-AI", 
                        MessageBoxButton.OK, MessageBoxImage.Information);
                    Logger.Information("Content copied to clipboard");
                }
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Error copying content to clipboard");
                MessageBox.Show($"Error copying to clipboard: {ex.Message}", "Error", 
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Handles Close button click
        /// </summary>
        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            Logger.Information("Result dialog closed");
            Close();
        }
    }
}
