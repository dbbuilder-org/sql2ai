using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using Newtonsoft.Json;
using Serilog;

namespace SSMSAI.Core.Configuration
{
    /// <summary>
    /// Configuration settings for SSMS-AI
    /// </summary>
    public class SsmsAiConfiguration
    {
        public string ApiProvider { get; set; } = "OpenAI";
        public string ApiKey { get; set; }
        public string Model { get; set; } = "gpt-3.5-turbo";
        public double Temperature { get; set; } = 0.7;
        public int MaxTokens { get; set; } = 2000;
        public int TimeoutSeconds { get; set; } = 30;
        public int RetryCount { get; set; } = 3;
    }

    /// <summary>
    /// Manages configuration persistence with encryption
    /// </summary>
    public class ConfigurationManager
    {
        private static readonly ILogger Logger = Log.ForContext<ConfigurationManager>();
        private readonly string _configPath;
        private readonly byte[] _entropy = Encoding.UTF8.GetBytes("SSMS-AI-Config-Entropy");

        public ConfigurationManager()
        {
            // Store config in user's AppData folder
            var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            var configDir = Path.Combine(appDataPath, "SSMS-AI");
            Directory.CreateDirectory(configDir);
            _configPath = Path.Combine(configDir, "config.json");
            
            Logger.Information("Configuration path: {ConfigPath}", _configPath);
        }

        /// <summary>
        /// Loads configuration from disk
        /// </summary>
        public SsmsAiConfiguration Load()
        {
            try
            {
                if (!File.Exists(_configPath))
                {
                    Logger.Information("No configuration file found, returning defaults");
                    return new SsmsAiConfiguration();
                }

                var encryptedData = File.ReadAllText(_configPath);
                var jsonData = Decrypt(encryptedData);
                var config = JsonConvert.DeserializeObject<SsmsAiConfiguration>(jsonData);
                
                Logger.Information("Configuration loaded successfully");
                return config ?? new SsmsAiConfiguration();
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Failed to load configuration");
                return new SsmsAiConfiguration();
            }
        }

        /// <summary>
        /// Saves configuration to disk
        /// </summary>
        public void Save(SsmsAiConfiguration config)
        {
            try
            {
                var jsonData = JsonConvert.SerializeObject(config, Formatting.Indented);
                var encryptedData = Encrypt(jsonData);
                File.WriteAllText(_configPath, encryptedData);
                
                Logger.Information("Configuration saved successfully");
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Failed to save configuration");
                throw;
            }
        }

        /// <summary>
        /// Encrypts sensitive data using DPAPI
        /// </summary>
        private string Encrypt(string data)
        {
            try
            {
                var dataBytes = Encoding.UTF8.GetBytes(data);
                var encryptedBytes = ProtectedData.Protect(dataBytes, _entropy, DataProtectionScope.CurrentUser);
                return Convert.ToBase64String(encryptedBytes);
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Failed to encrypt data");
                throw;
            }
        }

        /// <summary>
        /// Decrypts sensitive data using DPAPI
        /// </summary>
        private string Decrypt(string encryptedData)
        {
            try
            {
                var encryptedBytes = Convert.FromBase64String(encryptedData);
                var decryptedBytes = ProtectedData.Unprotect(encryptedBytes, _entropy, DataProtectionScope.CurrentUser);
                return Encoding.UTF8.GetString(decryptedBytes);
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Failed to decrypt data");
                throw;
            }
        }
    }
}
