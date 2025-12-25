using System;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using Serilog;
using SSMSAI.Core.Configuration;
using SSMSAI.AI.Providers;

namespace SSMSAI.SSMS.UI
{
    /// <summary>
    /// Configuration dialog for SSMS-AI settings
    /// </summary>
    public partial class ConfigurationDialog : Window
    {
        private static readonly ILogger Logger = Log.ForContext<ConfigurationDialog>();
        private readonly ConfigurationManager _configManager;
        private SsmsAiConfiguration _config;

        public ConfigurationDialog(ConfigurationManager configManager)
        {
            _configManager = configManager ?? throw new ArgumentNullException(nameof(configManager));
            InitializeComponent();
            LoadConfiguration();
        }

        /// <summary>
        /// Loads the current configuration into the dialog
        /// </summary>
        private void LoadConfiguration()
        {
            try
            {
                _config = _configManager.Load();
                
                // Set dialog values from configuration
                ApiKeyTextBox.Password = _config.ApiKey ?? string.Empty;
                ModelComboBox.Text = _config.Model ?? "gpt-3.5-turbo";
                TemperatureSlider.Value = _config.Temperature;
                MaxTokensTextBox.Text = _config.MaxTokens.ToString();
                TimeoutTextBox.Text = _config.TimeoutSeconds.ToString();
                
                UpdateTemperatureLabel();
                Logger.Information("Configuration loaded into dialog");
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Failed to load configuration");
                MessageBox.Show("Failed to load configuration: " + ex.Message, "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Saves the configuration and closes the dialog
        /// </summary>
        private async void SaveButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Validate inputs
                if (string.IsNullOrWhiteSpace(ApiKeyTextBox.Password))
                {
                    MessageBox.Show("API Key is required.", "Validation Error", MessageBoxButton.OK, MessageBoxImage.Warning);
                    ApiKeyTextBox.Focus();
                    return;
                }

                if (!int.TryParse(MaxTokensTextBox.Text, out int maxTokens) || maxTokens <= 0)
                {
                    MessageBox.Show("Max Tokens must be a positive integer.", "Validation Error", MessageBoxButton.OK, MessageBoxImage.Warning);
                    MaxTokensTextBox.Focus();
                    return;
                }

                if (!int.TryParse(TimeoutTextBox.Text, out int timeout) || timeout <= 0)
                {
                    MessageBox.Show("Timeout must be a positive integer.", "Validation Error", MessageBoxButton.OK, MessageBoxImage.Warning);
                    TimeoutTextBox.Focus();
                    return;
                }

                // Update configuration
                _config.ApiKey = ApiKeyTextBox.Password;
                _config.Model = ModelComboBox.Text;
                _config.Temperature = TemperatureSlider.Value;
                _config.MaxTokens = maxTokens;
                _config.TimeoutSeconds = timeout;

                // Test connection before saving
                if (TestConnectionCheckBox.IsChecked == true)
                {
                    var testResult = await TestConnectionAsync();
                    if (!testResult)
                    {
                        var result = MessageBox.Show(
                            "Connection test failed. Do you want to save the configuration anyway?",
                            "Connection Test Failed",
                            MessageBoxButton.YesNo,
                            MessageBoxImage.Warning);
                        
                        if (result == MessageBoxResult.No)
                        {
                            return;
                        }
                    }
                }

                // Save configuration
                _configManager.Save(_config);
                Logger.Information("Configuration saved successfully");
                
                DialogResult = true;
                Close();
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Failed to save configuration");
                MessageBox.Show("Failed to save configuration: " + ex.Message, "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Tests the connection to the AI provider
        /// </summary>
        private async Task<bool> TestConnectionAsync()
        {
            try
            {
                TestButton.IsEnabled = false;
                TestButton.Content = "Testing...";

                var provider = new OpenAiProvider();
                provider.Configure(ApiKeyTextBox.Password, ModelComboBox.Text);

                var success = await provider.TestConnectionAsync();
                
                if (success)
                {
                    MessageBox.Show("Connection test successful!", "Test Connection", MessageBoxButton.OK, MessageBoxImage.Information);
                    Logger.Information("Connection test successful");
                }
                else
                {
                    MessageBox.Show("Connection test failed. Please check your API key and settings.", "Test Connection", MessageBoxButton.OK, MessageBoxImage.Error);
                    Logger.Warning("Connection test failed");
                }

                return success;
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Exception during connection test");
                MessageBox.Show($"Connection test error: {ex.Message}", "Test Connection", MessageBoxButton.OK, MessageBoxImage.Error);
                return false;
            }
            finally
            {
                TestButton.IsEnabled = true;
                TestButton.Content = "Test Connection";
            }
        }

        /// <summary>
        /// Handles the Test Connection button click
        /// </summary>
        private async void TestButton_Click(object sender, RoutedEventArgs e)
        {
            await TestConnectionAsync();
        }

        /// <summary>
        /// Cancels the dialog without saving
        /// </summary>
        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }

        /// <summary>
        /// Updates the temperature label when slider value changes
        /// </summary>
        private void TemperatureSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            UpdateTemperatureLabel();
        }

        /// <summary>
        /// Updates the temperature display label
        /// </summary>
        private void UpdateTemperatureLabel()
        {
            if (TemperatureLabel != null)
            {
                TemperatureLabel.Content = $"Temperature: {TemperatureSlider.Value:F1}";
            }
        }

        /// <summary>
        /// Initializes the component (called by constructor)
        /// </summary>
        private void InitializeComponent()
        {
            Title = "SSMS-AI Configuration";
            Width = 450;
            Height = 400;
            WindowStartupLocation = WindowStartupLocation.CenterOwner;
            ResizeMode = ResizeMode.NoResize;

            // Create main grid
            var mainGrid = new Grid();
            mainGrid.Margin = new Thickness(20);
            
            // Define rows
            for (int i = 0; i < 7; i++)
            {
                mainGrid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            }
            mainGrid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            mainGrid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

            // API Key
            var apiKeyLabel = new Label { Content = "OpenAI API Key:", Margin = new Thickness(0, 0, 0, 5) };
            Grid.SetRow(apiKeyLabel, 0);
            mainGrid.Children.Add(apiKeyLabel);

            ApiKeyTextBox = new PasswordBox { Margin = new Thickness(0, 0, 0, 15) };
            Grid.SetRow(ApiKeyTextBox, 1);
            mainGrid.Children.Add(ApiKeyTextBox);

            // Model
            var modelLabel = new Label { Content = "Model:", Margin = new Thickness(0, 0, 0, 5) };
            Grid.SetRow(modelLabel, 2);
            mainGrid.Children.Add(modelLabel);

            ModelComboBox = new ComboBox { Margin = new Thickness(0, 0, 0, 15) };
            ModelComboBox.Items.Add("gpt-3.5-turbo");
            ModelComboBox.Items.Add("gpt-4");
            ModelComboBox.Items.Add("gpt-4-turbo-preview");
            ModelComboBox.SelectedIndex = 0;
            Grid.SetRow(ModelComboBox, 3);
            mainGrid.Children.Add(ModelComboBox);

            // Temperature
            TemperatureLabel = new Label { Content = "Temperature: 0.7", Margin = new Thickness(0, 0, 0, 5) };
            Grid.SetRow(TemperatureLabel, 4);
            mainGrid.Children.Add(TemperatureLabel);

            TemperatureSlider = new Slider 
            { 
                Minimum = 0, 
                Maximum = 2, 
                Value = 0.7, 
                TickFrequency = 0.1, 
                IsSnapToTickEnabled = true,
                Margin = new Thickness(0, 0, 0, 15)
            };
            TemperatureSlider.ValueChanged += TemperatureSlider_ValueChanged;
            Grid.SetRow(TemperatureSlider, 5);
            mainGrid.Children.Add(TemperatureSlider);

            // Advanced settings in a group box
            var advancedGroup = new GroupBox { Header = "Advanced Settings", Margin = new Thickness(0, 0, 0, 15) };
            var advancedGrid = new Grid();
            advancedGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            advancedGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            advancedGrid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            advancedGrid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

            var maxTokensLabel = new Label { Content = "Max Tokens:", Margin = new Thickness(5) };
            Grid.SetRow(maxTokensLabel, 0);
            Grid.SetColumn(maxTokensLabel, 0);
            advancedGrid.Children.Add(maxTokensLabel);

            MaxTokensTextBox = new TextBox { Text = "2000", Margin = new Thickness(5) };
            Grid.SetRow(MaxTokensTextBox, 0);
            Grid.SetColumn(MaxTokensTextBox, 1);
            advancedGrid.Children.Add(MaxTokensTextBox);

            var timeoutLabel = new Label { Content = "Timeout (seconds):", Margin = new Thickness(5) };
            Grid.SetRow(timeoutLabel, 1);
            Grid.SetColumn(timeoutLabel, 0);
            advancedGrid.Children.Add(timeoutLabel);

            TimeoutTextBox = new TextBox { Text = "30", Margin = new Thickness(5) };
            Grid.SetRow(TimeoutTextBox, 1);
            Grid.SetColumn(TimeoutTextBox, 1);
            advancedGrid.Children.Add(TimeoutTextBox);

            advancedGroup.Content = advancedGrid;
            Grid.SetRow(advancedGroup, 6);
            mainGrid.Children.Add(advancedGroup);

            // Test connection checkbox
            TestConnectionCheckBox = new CheckBox 
            { 
                Content = "Test connection before saving", 
                IsChecked = true,
                Margin = new Thickness(0, 0, 0, 15)
            };
            Grid.SetRow(TestConnectionCheckBox, 7);
            mainGrid.Children.Add(TestConnectionCheckBox);

            // Buttons
            var buttonPanel = new StackPanel 
            { 
                Orientation = Orientation.Horizontal, 
                HorizontalAlignment = HorizontalAlignment.Right,
                Margin = new Thickness(0, 15, 0, 0)
            };

            TestButton = new Button 
            { 
                Content = "Test Connection", 
                Width = 100, 
                Height = 30,
                Margin = new Thickness(0, 0, 10, 0)
            };
            TestButton.Click += TestButton_Click;
            buttonPanel.Children.Add(TestButton);

            var saveButton = new Button 
            { 
                Content = "Save", 
                Width = 75, 
                Height = 30,
                IsDefault = true,
                Margin = new Thickness(0, 0, 10, 0)
            };
            saveButton.Click += SaveButton_Click;
            buttonPanel.Children.Add(saveButton);

            var cancelButton = new Button 
            { 
                Content = "Cancel", 
                Width = 75, 
                Height = 30,
                IsCancel = true
            };
            cancelButton.Click += CancelButton_Click;
            buttonPanel.Children.Add(cancelButton);

            Grid.SetRow(buttonPanel, 8);
            mainGrid.Children.Add(buttonPanel);

            Content = mainGrid;
        }

        // UI Controls
        private PasswordBox ApiKeyTextBox;
        private ComboBox ModelComboBox;
        private Label TemperatureLabel;
        private Slider TemperatureSlider;
        private TextBox MaxTokensTextBox;
        private TextBox TimeoutTextBox;
        private CheckBox TestConnectionCheckBox;
        private Button TestButton;
    }
}