using System.Threading;
using System.Threading.Tasks;

namespace SSMSAI.Core.AI
{
    /// <summary>
    /// Represents a request to an AI provider
    /// </summary>
    public class AiRequest
    {
        public string Prompt { get; set; }
        public string SystemPrompt { get; set; }
        public double Temperature { get; set; } = 0.7;
        public int MaxTokens { get; set; } = 2000;
        public string Model { get; set; }
    }

    /// <summary>
    /// Represents a response from an AI provider
    /// </summary>
    public class AiResponse
    {
        public string Content { get; set; }
        public int TokensUsed { get; set; }
        public string Model { get; set; }
        public bool Success { get; set; }
        public string ErrorMessage { get; set; }
    }

    /// <summary>
    /// Interface for AI providers (ChatGPT, Gemini, Claude)
    /// </summary>
    public interface IAiProvider
    {
        /// <summary>
        /// Gets the name of the AI provider
        /// </summary>
        string Name { get; }

        /// <summary>
        /// Gets whether the provider is configured and ready to use
        /// </summary>
        bool IsConfigured { get; }

        /// <summary>
        /// Sends a request to the AI provider
        /// </summary>
        Task<AiResponse> SendRequestAsync(AiRequest request, CancellationToken cancellationToken = default);

        /// <summary>
        /// Tests the connection to the AI provider
        /// </summary>
        Task<bool> TestConnectionAsync(CancellationToken cancellationToken = default);

        /// <summary>
        /// Configures the provider with necessary settings
        /// </summary>
        void Configure(string apiKey, string model = null);
    }
}
