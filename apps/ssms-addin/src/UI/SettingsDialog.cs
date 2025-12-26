using System;
using System.Windows;
using System.Windows.Controls;
using SQL2AI.SSMS.Models;

namespace SQL2AI.SSMS.UI
{
    /// <summary>
    /// Settings dialog for SQL2.AI extension.
    /// </summary>
    public class SettingsDialog : Window
    {
        private readonly TextBox _apiKeyTextBox;
        private readonly TextBox _apiUrlTextBox;
        private readonly CheckBox _inlineCompletionCheckBox;
        private readonly CheckBox _notificationsCheckBox;
        private readonly TextBox _timeoutTextBox;
        private readonly CheckBox _localLlmCheckBox;
        private readonly TextBox _localLlmEndpointTextBox;

        public ExtensionSettings Settings { get; private set; }

        public SettingsDialog(ExtensionSettings settings)
        {
            Settings = settings ?? new ExtensionSettings();

            Title = "SQL2.AI Settings";
            Width = 450;
            Height = 400;
            WindowStartupLocation = WindowStartupLocation.CenterScreen;
            ResizeMode = ResizeMode.NoResize;

            var grid = new Grid();
            grid.Margin = new Thickness(15);
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

            // API Key
            var apiKeyLabel = new Label { Content = "API Key:", Margin = new Thickness(0, 5, 0, 0) };
            Grid.SetRow(apiKeyLabel, 0);
            grid.Children.Add(apiKeyLabel);

            _apiKeyTextBox = new TextBox
            {
                Text = Settings.ApiKey ?? string.Empty,
                Margin = new Thickness(0, 0, 0, 10)
            };
            Grid.SetRow(_apiKeyTextBox, 1);
            grid.Children.Add(_apiKeyTextBox);

            // API URL
            var apiUrlLabel = new Label { Content = "API URL:", Margin = new Thickness(0, 5, 0, 0) };
            Grid.SetRow(apiUrlLabel, 2);
            grid.Children.Add(apiUrlLabel);

            _apiUrlTextBox = new TextBox
            {
                Text = Settings.ApiBaseUrl,
                Margin = new Thickness(0, 0, 0, 10)
            };
            Grid.SetRow(_apiUrlTextBox, 3);
            grid.Children.Add(_apiUrlTextBox);

            // Timeout
            var timeoutPanel = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(0, 5, 0, 10) };
            timeoutPanel.Children.Add(new Label { Content = "Request Timeout (seconds):" });
            _timeoutTextBox = new TextBox
            {
                Text = Settings.RequestTimeoutSeconds.ToString(),
                Width = 50
            };
            timeoutPanel.Children.Add(_timeoutTextBox);
            Grid.SetRow(timeoutPanel, 4);
            grid.Children.Add(timeoutPanel);

            // Checkboxes
            _inlineCompletionCheckBox = new CheckBox
            {
                Content = "Enable inline completions",
                IsChecked = Settings.EnableInlineCompletion,
                Margin = new Thickness(0, 5, 0, 5)
            };
            Grid.SetRow(_inlineCompletionCheckBox, 5);
            grid.Children.Add(_inlineCompletionCheckBox);

            _notificationsCheckBox = new CheckBox
            {
                Content = "Show notifications",
                IsChecked = Settings.ShowNotifications,
                Margin = new Thickness(0, 5, 0, 10)
            };
            Grid.SetRow(_notificationsCheckBox, 6);
            grid.Children.Add(_notificationsCheckBox);

            // Local LLM section
            var localLlmPanel = new StackPanel { Margin = new Thickness(0, 10, 0, 10) };

            _localLlmCheckBox = new CheckBox
            {
                Content = "Use local LLM (for air-gapped environments)",
                IsChecked = Settings.UseLocalLlm,
                Margin = new Thickness(0, 0, 0, 5)
            };
            _localLlmCheckBox.Checked += (s, e) => _localLlmEndpointTextBox.IsEnabled = true;
            _localLlmCheckBox.Unchecked += (s, e) => _localLlmEndpointTextBox.IsEnabled = false;
            localLlmPanel.Children.Add(_localLlmCheckBox);

            var localEndpointLabel = new Label { Content = "Local LLM Endpoint:" };
            localLlmPanel.Children.Add(localEndpointLabel);

            _localLlmEndpointTextBox = new TextBox
            {
                Text = Settings.LocalLlmEndpoint ?? "http://localhost:11434",
                IsEnabled = Settings.UseLocalLlm
            };
            localLlmPanel.Children.Add(_localLlmEndpointTextBox);

            Grid.SetRow(localLlmPanel, 7);
            grid.Children.Add(localLlmPanel);

            // Buttons
            var buttonPanel = new StackPanel
            {
                Orientation = Orientation.Horizontal,
                HorizontalAlignment = HorizontalAlignment.Right,
                Margin = new Thickness(0, 10, 0, 0)
            };

            var saveButton = new Button
            {
                Content = "Save",
                Width = 80,
                Height = 25,
                Margin = new Thickness(0, 0, 10, 0),
                IsDefault = true
            };
            saveButton.Click += SaveButton_Click;
            buttonPanel.Children.Add(saveButton);

            var cancelButton = new Button
            {
                Content = "Cancel",
                Width = 80,
                Height = 25,
                IsCancel = true
            };
            cancelButton.Click += (s, e) => DialogResult = false;
            buttonPanel.Children.Add(cancelButton);

            Grid.SetRow(buttonPanel, 8);
            grid.Children.Add(buttonPanel);

            Content = grid;
        }

        private void SaveButton_Click(object sender, RoutedEventArgs e)
        {
            // Validate timeout
            if (!int.TryParse(_timeoutTextBox.Text, out var timeout) || timeout < 1 || timeout > 300)
            {
                MessageBox.Show("Timeout must be between 1 and 300 seconds.", "Validation Error",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            Settings = new ExtensionSettings
            {
                ApiKey = _apiKeyTextBox.Text.Trim(),
                ApiBaseUrl = _apiUrlTextBox.Text.Trim(),
                EnableInlineCompletion = _inlineCompletionCheckBox.IsChecked ?? true,
                ShowNotifications = _notificationsCheckBox.IsChecked ?? true,
                RequestTimeoutSeconds = timeout,
                UseLocalLlm = _localLlmCheckBox.IsChecked ?? false,
                LocalLlmEndpoint = _localLlmEndpointTextBox.Text.Trim()
            };

            DialogResult = true;
        }
    }
}
