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
        private readonly SsmsAiConfiguration _configuration;
        private bool _isLoading = true;

        /// <summary>
        /// Constructor
        /// </summary>
        public ConfigurationDialog(SsmsAiConfiguration configuration)
        {
            InitializeComponent();
            _configuration = configuration ?? throw new ArgumentNullException(nameof(configuration));
            
            DataContext = _configuration;
            LoadConfiguration();
            _isLoading = false;
            
            Logger.Information("Configuration dialog opened");
        }

        /// <summary>
        /// Loads current configuration into UI controls
        /// </summary>
        private void LoadConfiguration()
        {
            try
            {
                // Set API key (if exists)
                if (!string.IsNullOrEmpty(_configuration.ApiKey))
                {
                    ApiKeyPasswordBox.Password = _configuration.ApiKey;
                }

                // Set provider selection
                foreach (ComboBoxItem item in ProviderComboBox.Items)
                {
                    if (item.Content.ToString() == _configuration.ApiProvider)
                    {
                        ProviderComboBox.SelectedItem = item;
                        break;
                    }
                }

                // Set model selection
                foreach (ComboBoxItem item in ModelComboBox.Items)
                {
                    if (item.Content.ToString() == _configuration.Model)
                    {
                        ModelComboBox.SelectedItem = item;
                        break;
                    }
                }

                Logger.Information("Configuration loaded into dialog");
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Error loading configuration into dialog");
            }
        }

        /// <summary>
        /// Handles provider selection change
        /// </summary>
        private void ProviderComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_isLoading || ProviderComboBox.SelectedItem == null) return;

            var selectedProvider = ((ComboBoxItem)ProviderComboBox.SelectedItem).Content.ToString();
            _configuration.ApiProvider = selectedProvider;

            // Update model options based on provider
            ModelComboBox.Items.Clear();
            if (selectedProvider == "OpenAI")
            {
                ModelComboBox.Items.Add(new ComboBoxItem { Content = "gpt-3.5-turbo" });
                ModelComboBox.Items.Add(new ComboBoxItem { Content = "gpt-4" });
                ModelComboBox.Items.Add(new ComboBoxItem { Content = "gpt-4-turbo" });
                ModelComboBox.SelectedIndex = 0;
            }

            Logger.Debug("Provider changed to: {Provider}", selectedProvider);
        }

        /// <summary>
        /// Handles API key password change
        /// </summary>
        private void ApiKeyPasswordBox_PasswordChanged(object sender, RoutedEventArgs e)
        {
            if (_isLoading) return;
            _configuration.ApiKey = ApiKeyPasswordBox.Password;
        }

        /// <summary>
        /// Tests the connection to the AI provider
        /// </summary>
        private async void TestConnectionButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                TestConnectionButton.IsEnabled = false;
                TestResultTextBlock.Text = "Testing...";
                TestResultTextBlock.Foreground = System.Windows.Media.Brushes.Blue;

                // Create provider and test connection
                var provider = new OpenAiProvider();
                provider.Configure(_configuration.ApiKey, _configuration.Model);

                var result = await provider.TestConnectionAsync();

                if (result)
                {
                    TestResultTextBlock.Text = "✓ Connection successful";
                    TestResultTextBlock.Foreground = System.Windows.Media.Brushes.Green;
                    Logger.Information("Connection test successful");
                }
                else
                {
                    TestResultTextBlock.Text = "✗ Connection failed";
                    TestResultTextBlock.Foreground = System.Windows.Media.Brushes.Red;
                    Logger.Warning("Connection test failed");
                }
            }
            catch (Exception ex)
            {
                TestResultTextBlock.Text = "✗ Error testing connection";
                TestResultTextBlock.Foreground = System.Windows.Media.Brushes.Red;
                Logger.Error(ex, "Error during connection test");
            }
            finally
            {
                TestConnectionButton.IsEnabled = true;
            }
        }

        /// <summary>
        /// Handles OK button click
        /// </summary>
        private void OkButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Validate configuration
                if (string.IsNullOrWhiteSpace(_configuration.ApiKey))
                {
                    MessageBox.Show("Please enter an API key.", "Validation Error", 
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                if (string.IsNullOrWhiteSpace(_configuration.Model))
                {
                    MessageBox.Show("Please select a model.", "Validation Error", 
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                // Set model from combo box selection
                if (ModelComboBox.SelectedItem != null)
                {
                    _configuration.Model = ((ComboBoxItem)ModelComboBox.SelectedItem).Content.ToString();
                }

                DialogResult = true;
                Logger.Information("Configuration dialog accepted");
                Close();
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Error handling OK button click");
                MessageBox.Show($"Error saving configuration: {ex.Message}", "Error", 
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Handles Cancel button click
        /// </summary>
        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Logger.Information("Configuration dialog cancelled");
            Close();
        }
    }
}
