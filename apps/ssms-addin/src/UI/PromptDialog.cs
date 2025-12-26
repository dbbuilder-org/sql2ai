using System.Windows;
using System.Windows.Controls;

namespace SQL2AI.SSMS.UI
{
    /// <summary>
    /// Dialog for entering natural language prompts for code generation.
    /// </summary>
    public class PromptDialog : Window
    {
        private readonly TextBox _promptTextBox;
        private readonly ComboBox _objectTypeComboBox;
        private readonly CheckBox _includeAuditCheckBox;

        public string Prompt { get; private set; } = string.Empty;
        public string SelectedObjectType { get; private set; } = "stored_procedure";
        public bool IncludeAudit { get; private set; }

        public PromptDialog()
        {
            Title = "SQL2.AI - Generate from Prompt";
            Width = 500;
            Height = 350;
            WindowStartupLocation = WindowStartupLocation.CenterScreen;
            ResizeMode = ResizeMode.NoResize;

            var grid = new Grid();
            grid.Margin = new Thickness(15);
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

            // Object type selection
            var typePanel = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(0, 0, 0, 10) };
            typePanel.Children.Add(new Label { Content = "Generate:", VerticalAlignment = VerticalAlignment.Center });

            _objectTypeComboBox = new ComboBox { Width = 200 };
            _objectTypeComboBox.Items.Add(new ComboBoxItem { Content = "Stored Procedure", Tag = "stored_procedure", IsSelected = true });
            _objectTypeComboBox.Items.Add(new ComboBoxItem { Content = "View", Tag = "view" });
            _objectTypeComboBox.Items.Add(new ComboBoxItem { Content = "Function", Tag = "function" });
            _objectTypeComboBox.Items.Add(new ComboBoxItem { Content = "Trigger", Tag = "trigger" });
            _objectTypeComboBox.Items.Add(new ComboBoxItem { Content = "Table", Tag = "table" });
            typePanel.Children.Add(_objectTypeComboBox);

            Grid.SetRow(typePanel, 0);
            grid.Children.Add(typePanel);

            // Prompt text box
            var promptLabel = new Label { Content = "Describe what you want to generate:", Margin = new Thickness(0, 0, 0, 5) };
            Grid.SetRow(promptLabel, 1);
            grid.Children.Add(promptLabel);

            _promptTextBox = new TextBox
            {
                TextWrapping = TextWrapping.Wrap,
                AcceptsReturn = true,
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
                Height = 120,
                Margin = new Thickness(0, 25, 0, 10)
            };
            Grid.SetRow(_promptTextBox, 1);
            grid.Children.Add(_promptTextBox);

            // Example text
            var exampleText = new TextBlock
            {
                Text = "Example: \"Create a stored procedure to transfer funds between accounts with proper locking, " +
                       "audit trail, and overdraft protection\"",
                TextWrapping = TextWrapping.Wrap,
                FontStyle = FontStyles.Italic,
                Foreground = System.Windows.Media.Brushes.Gray,
                Margin = new Thickness(0, 0, 0, 10)
            };
            Grid.SetRow(exampleText, 2);
            grid.Children.Add(exampleText);

            // Options
            _includeAuditCheckBox = new CheckBox
            {
                Content = "Include audit logging",
                Margin = new Thickness(0, 0, 0, 15)
            };
            Grid.SetRow(_includeAuditCheckBox, 3);
            grid.Children.Add(_includeAuditCheckBox);

            // Buttons
            var buttonPanel = new StackPanel
            {
                Orientation = Orientation.Horizontal,
                HorizontalAlignment = HorizontalAlignment.Right
            };

            var generateButton = new Button
            {
                Content = "Generate",
                Width = 100,
                Height = 30,
                Margin = new Thickness(0, 0, 10, 0),
                IsDefault = true
            };
            generateButton.Click += GenerateButton_Click;
            buttonPanel.Children.Add(generateButton);

            var cancelButton = new Button
            {
                Content = "Cancel",
                Width = 80,
                Height = 30,
                IsCancel = true
            };
            cancelButton.Click += (s, e) => DialogResult = false;
            buttonPanel.Children.Add(cancelButton);

            Grid.SetRow(buttonPanel, 4);
            grid.Children.Add(buttonPanel);

            Content = grid;

            // Focus prompt text box
            Loaded += (s, e) => _promptTextBox.Focus();
        }

        private void GenerateButton_Click(object sender, RoutedEventArgs e)
        {
            Prompt = _promptTextBox.Text.Trim();

            if (string.IsNullOrEmpty(Prompt))
            {
                MessageBox.Show("Please enter a description.", "Validation Error",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            var selectedItem = _objectTypeComboBox.SelectedItem as ComboBoxItem;
            SelectedObjectType = selectedItem?.Tag?.ToString() ?? "stored_procedure";
            IncludeAudit = _includeAuditCheckBox.IsChecked ?? false;

            DialogResult = true;
        }
    }
}
