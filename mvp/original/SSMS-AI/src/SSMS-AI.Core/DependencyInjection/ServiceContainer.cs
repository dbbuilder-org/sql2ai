using Microsoft.Extensions.DependencyInjection;
using SSMSAI.Core.AI;
using SSMSAI.Core.Configuration;
using System;

namespace SSMSAI.Core.DependencyInjection
{
    /// <summary>
    /// Service container for dependency injection
    /// </summary>
    public class ServiceContainer
    {
        private static readonly Lazy<ServiceContainer> _instance = new Lazy<ServiceContainer>(() => new ServiceContainer());
        private readonly ServiceProvider _serviceProvider;
        private readonly ServiceCollection _services;

        private ServiceContainer()
        {
            _services = new ServiceCollection();
            ConfigureServices();
            _serviceProvider = _services.BuildServiceProvider();
        }

        public static ServiceContainer Instance => _instance.Value;

        /// <summary>
        /// Gets a service from the container
        /// </summary>
        public T GetService<T>() where T : class
        {
            return _serviceProvider.GetService<T>();
        }

        /// <summary>
        /// Gets a required service from the container
        /// </summary>
        public T GetRequiredService<T>() where T : class
        {
            return _serviceProvider.GetRequiredService<T>();
        }

        /// <summary>
        /// Configures all services
        /// </summary>
        private void ConfigureServices()
        {
            // Core services
            _services.AddSingleton<ConfigurationManager>();
            
            // AI providers will be registered in the AI project
            // For now, we just define the interface
        }

        /// <summary>
        /// Registers an AI provider
        /// </summary>
        public void RegisterAiProvider<T>() where T : class, IAiProvider
        {
            _services.AddTransient<IAiProvider, T>();
        }
    }
}
