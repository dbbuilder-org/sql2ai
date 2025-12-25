using System;
using System.Windows;
using System.Windows.Controls;
using Serilog;

namespace SSMSAI.SSMS.UI
{
    /// <summary>
    /// Simple progress dialog to show during AI requests
    /// </summary>
    public partial class ProgressDialog : Window
    {
        private static readonly ILogger Logger = Log.ForContext<ProgressDialog>();

        public ProgressDialog()
        {
            InitializeComponent();
            Logger.Information("ProgressDialog created");
        }

        /// <summary>
        /// Updates the progress message
        /// </summary>
        public void UpdateMessage(string message)
        {
            if (MessageLabel != null)
            {
                MessageLabel.Content = message;
                Logger.Debug("Progress message updated: {Message}", message);
            }
        }

        /// <summary>
        /// Initializes the component (called by constructor)
        /// </summary>
        private void InitializeComponent()
        {
            Title = "Processing...";
            Width = 300;
            Height = 120;
            WindowStartupLocation = WindowStartupLocation.CenterOwner;
            ResizeMode = ResizeMode.NoResize;
            WindowStyle = WindowStyle.ToolWindow;

            // Create main grid
            var mainGrid = new Grid();
            mainGrid.Margin = new Thickness(20);
            
            // Define rows
            mainGrid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            mainGrid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

            // Message label
            MessageLabel = new Label 
            { 
                Content = "Processing AI request...",
                HorizontalAlignment = HorizontalAlignment.Center,
                Margin = new Thickness(0, 0, 0, 10)
            };
            Grid.SetRow(MessageLabel, 0);
            mainGrid.Children.Add(MessageLabel);

            // Progress bar
            var progressBar = new ProgressBar
            {
                IsIndeterminate = true,
                Height = 20,
                Margin = new Thickness(0, 10, 0, 0)
            };
            Grid.SetRow(progressBar, 1);
            mainGrid.Children.Add(progressBar);

            Content = mainGrid;
        }

        // UI Controls
        private Label MessageLabel;
    }
}