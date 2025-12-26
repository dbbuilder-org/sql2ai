using System;
using System.IO;
using Newtonsoft.Json;
using SQL2AI.SSMS.Models;

namespace SQL2AI.SSMS.Services
{
    /// <summary>
    /// Service for managing extension settings.
    /// </summary>
    public class SettingsService
    {
        private static readonly string SettingsPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "SQL2AI",
            "settings.json");

        private ExtensionSettings? _cachedSettings;

        /// <summary>
        /// Get current settings.
        /// </summary>
        public ExtensionSettings GetSettings()
        {
            if (_cachedSettings != null)
            {
                return _cachedSettings;
            }

            _cachedSettings = LoadSettings();
            return _cachedSettings;
        }

        /// <summary>
        /// Save settings.
        /// </summary>
        public void SaveSettings(ExtensionSettings settings)
        {
            try
            {
                var directory = Path.GetDirectoryName(SettingsPath);
                if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                var json = JsonConvert.SerializeObject(settings, Formatting.Indented);
                File.WriteAllText(SettingsPath, json);
                _cachedSettings = settings;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to save settings: {ex.Message}");
            }
        }

        /// <summary>
        /// Update API key.
        /// </summary>
        public void SetApiKey(string apiKey)
        {
            var settings = GetSettings();
            settings.ApiKey = apiKey;
            SaveSettings(settings);
        }

        /// <summary>
        /// Clear cached settings.
        /// </summary>
        public void ClearCache()
        {
            _cachedSettings = null;
        }

        private ExtensionSettings LoadSettings()
        {
            try
            {
                if (File.Exists(SettingsPath))
                {
                    var json = File.ReadAllText(SettingsPath);
                    return JsonConvert.DeserializeObject<ExtensionSettings>(json)
                           ?? new ExtensionSettings();
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to load settings: {ex.Message}");
            }

            return new ExtensionSettings();
        }
    }
}
