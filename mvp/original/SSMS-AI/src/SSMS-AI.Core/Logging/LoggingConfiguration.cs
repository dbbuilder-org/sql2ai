using Serilog;
using Serilog.Events;
using System;
using System.IO;

namespace SSMSAI.Core.Logging
{
    /// <summary>
    /// Centralized logging configuration for SSMS-AI
    /// </summary>
    public static class LoggingConfiguration
    {
        private static bool _isInitialized = false;

        /// <summary>
        /// Initializes the logging system
        /// </summary>
        public static void Initialize(string logPath = null)
        {
            if (_isInitialized)
                return;

            try
            {
                // Determine log path
                if (string.IsNullOrEmpty(logPath))
                {
                    var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
                    logPath = Path.Combine(appDataPath, "SSMS-AI", "Logs");
                }

                Directory.CreateDirectory(logPath);

                // Configure Serilog
                Log.Logger = new LoggerConfiguration()
                    .MinimumLevel.Debug()
                    .MinimumLevel.Override("Microsoft", LogEventLevel.Information)
                    .Enrich.FromLogContext()
                    .Enrich.WithThreadId()
                    .WriteTo.File(
                        Path.Combine(logPath, "ssms-ai-.log"),
                        rollingInterval: RollingInterval.Day,
                        retainedFileCountLimit: 7,
                        outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] [{ThreadId}] {SourceContext} - {Message:lj}{NewLine}{Exception}",
                        fileSizeLimitBytes: 10_485_760) // 10MB
                    .WriteTo.Console(
                        outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}")
                    .CreateLogger();

                _isInitialized = true;
                Log.Information("Logging system initialized. Log path: {LogPath}", logPath);
            }
            catch (Exception ex)
            {
                // Fallback to console only
                Log.Logger = new LoggerConfiguration()
                    .MinimumLevel.Debug()
                    .WriteTo.Console()
                    .CreateLogger();

                Log.Error(ex, "Failed to initialize file logging, using console only");
                _isInitialized = true;
            }
        }

        /// <summary>
        /// Ensures logging is properly shut down
        /// </summary>
        public static void Shutdown()
        {
            Log.Information("Shutting down logging system");
            Log.CloseAndFlush();
            _isInitialized = false;
        }
    }
}
