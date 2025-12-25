using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Media;
using Serilog;

namespace SSMSAI.SSMS.UI
{
    /// <summary>
    /// Dialog for displaying AI results with formatting and copy functionality
    /// </summary>
    public partial class AiResultDialog : Window
    {
        private static readonly ILogger Logger = Log.ForContext<AiResultDialog>();
        private readonly string _content;

        public AiResultDialog(string content, string title = "AI Result")
        {
            _content = content ?? throw new ArgumentNullException(nameof(content));
            InitializeComponent();
            Title = title;
            DisplayContent();
            Logger.Information("AiResultDialog created with title: {Title}", title);
        }

        /// <summary>
        /// Displays the AI response content
        /// </summary>
        private void DisplayContent()
        {
            try
            {
                ContentTextBox.Text = _content;
                ContentTextBox.ScrollToHome();
                Logger.Debug("Content displayed in result dialog");
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Failed to display content");
                ContentTextBox.Text = "Error displaying content: " + ex.Message;
            }
        }

        /// <summary>
        /// Copies the content to clipboard
        /// </summary>
        private void CopyButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                Clipboard.SetText(_content);
                CopyButton.Content = "Copied!";
                
                // Reset button text after 2 seconds
                var timer = new System.Windows.Threading.DispatcherTimer();
                timer.Interval = TimeSpan.FromSeconds(2);
                timer.Tick += (s, args) =>
                {
                    CopyButton.Content = "Copy to Clipboard";
                    timer.Stop();
                };
                timer.Start();
                
                Logger.Information("Content copied to clipboard");
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Failed to copy content to clipboard");
                MessageBox.Show("Failed to copy to clipboard: " + ex.Message, "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Closes the dialog
        /// </summary>
        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }

        /// <summary>
        /// Initializes the component (called by constructor)
        /// </summary>
        private void InitializeComponent()
        {
            Width = 700;
            Height = 500;
            WindowStartupLocation = WindowStartupLocation.CenterOwner;
            MinWidth = 400;
            MinHeight = 300;

            // Create main grid
            var mainGrid = new Grid();
            mainGrid.Margin = new Thickness(10);
            
            // Define rows
            mainGrid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            mainGrid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

            // Content display area
            var contentBorder = new Border
            {
                BorderBrush = Brushes.Gray,
                BorderThickness = new Thickness(1),
                Margin = new Thickness(0, 0, 0, 10)
            };

            ContentTextBox = new TextBox
            {
                IsReadOnly = true,
                TextWrapping = TextWrapping.Wrap,
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
                HorizontalScrollBarVisibility = ScrollBarVisibility.Auto,
                FontFamily = new FontFamily("Consolas"),
                FontSize = 12,
                Padding = new Thickness(10),
                Background = Brushes.White
            };

            contentBorder.Child = ContentTextBox;
            Grid.SetRow(contentBorder, 0);
            mainGrid.Children.Add(contentBorder);

            // Button panel
            var buttonPanel = new StackPanel 
            { 
                Orientation = Orientation.Horizontal, 
                HorizontalAlignment = HorizontalAlignment.Right,
                Margin = new Thickness(0, 10, 0, 0)
            };

            CopyButton = new Button 
            { 
                Content = "Copy to Clipboard", 
                Width = 120, 
                Height = 30,
                Margin = new Thickness(0, 0, 10, 0)
            };
            CopyButton.Click += CopyButton_Click;
            buttonPanel.Children.Add(CopyButton);

            var closeButton = new Button 
            { 
                Content = "Close", 
                Width = 75, 
                Height = 30,
                IsDefault = true,
                IsCancel = true
            };
            closeButton.Click += CloseButton_Click;
            buttonPanel.Children.Add(closeButton);

            Grid.SetRow(buttonPanel, 1);
            mainGrid.Children.Add(buttonPanel);

            Content = mainGrid;
        }

        // UI Controls
        private TextBox ContentTextBox;
        private Button CopyButton;
    }
}