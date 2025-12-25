using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RestSharp;
using Newtonsoft.Json;
using Polly;
using Polly.Retry;
using Serilog;
using SSMSAI.Core.AI;

namespace SSMSAI.AI.Providers
{
    /// <summary>
    /// OpenAI/ChatGPT provider implementation
    /// </summary>
    public class OpenAiProvider : IAiProvider
    {
        private static readonly ILogger Logger = Log.ForContext<OpenAiProvider>();
        private const string ApiUrl = "https://api.openai.com/v1/chat/completions";
        private string _apiKey;
        private string _model;
        private readonly RestClient _client;
        private readonly AsyncRetryPolicy<RestResponse> _retryPolicy;

        public string Name => "OpenAI";
        public bool IsConfigured => !string.IsNullOrEmpty(_apiKey);

        public OpenAiProvider()
        {
            _client = new RestClient();
            
            // Configure retry policy with Polly
            _retryPolicy = Policy
                .HandleResult<RestResponse>(r => !r.IsSuccessful && (int)r.StatusCode >= 500)
                .Or<TaskCanceledException>()
                .WaitAndRetryAsync(
                    3,
                    retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)),
                    onRetry: (outcome, timespan, retryCount, context) =>
                    {
                        Logger.Warning("Retry {RetryCount} after {Delay}ms", retryCount, timespan.TotalMilliseconds);
                    });
        }

        public void Configure(string apiKey, string model = null)
        {
            _apiKey = apiKey;
            _model = model ?? "gpt-3.5-turbo";
            Logger.Information("OpenAI provider configured with model: {Model}", _model);
        }

        public async Task<AiResponse> SendRequestAsync(AiRequest request, CancellationToken cancellationToken = default)
        {
            if (!IsConfigured)
            {
                Logger.Error("OpenAI provider not configured");
                return new AiResponse 
                { 
                    Success = false, 
                    ErrorMessage = "OpenAI provider not configured. Please set API key." 
                };
            }

            try
            {
                var restRequest = new RestRequest(ApiUrl, Method.Post);
                restRequest.AddHeader("Authorization", $"Bearer {_apiKey}");
                restRequest.AddHeader("Content-Type", "application/json");

                var requestBody = new
                {
                    model = request.Model ?? _model,
                    messages = new[]
                    {
                        new { role = "system", content = request.SystemPrompt ?? "You are a helpful SQL Server expert assistant." },
                        new { role = "user", content = request.Prompt }
                    },
                    temperature = request.Temperature,
                    max_tokens = request.MaxTokens
                };

                restRequest.AddJsonBody(requestBody);

                Logger.Debug("Sending request to OpenAI API");
                var response = await _retryPolicy.ExecuteAsync(async () => 
                    await _client.ExecuteAsync(restRequest, cancellationToken));

                if (response.IsSuccessful)
                {
                    var responseData = JsonConvert.DeserializeObject<OpenAiResponse>(response.Content);
                    var content = responseData?.Choices?.FirstOrDefault()?.Message?.Content;

                    if (!string.IsNullOrEmpty(content))
                    {
                        Logger.Information("Successfully received response from OpenAI");
                        return new AiResponse
                        {
                            Success = true,
                            Content = content,
                            TokensUsed = responseData.Usage?.TotalTokens ?? 0,
                            Model = responseData.Model
                        };
                    }
                }

                Logger.Error("Failed to get valid response from OpenAI. Status: {Status}, Content: {Content}", 
                    response.StatusCode, response.Content);
                
                return new AiResponse
                {
                    Success = false,
                    ErrorMessage = $"Failed to get response from OpenAI: {response.StatusDescription}"
                };
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Exception occurred while calling OpenAI API");
                return new AiResponse
                {
                    Success = false,
                    ErrorMessage = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<bool> TestConnectionAsync(CancellationToken cancellationToken = default)
        {
            var testRequest = new AiRequest
            {
                Prompt = "Hello, please respond with 'Connection successful'",
                MaxTokens = 50
            };

            var response = await SendRequestAsync(testRequest, cancellationToken);
            return response.Success;
        }

        // Response models
        private class OpenAiResponse
        {
            [JsonProperty("choices")]
            public Choice[] Choices { get; set; }

            [JsonProperty("usage")]
            public Usage Usage { get; set; }

            [JsonProperty("model")]
            public string Model { get; set; }
        }

        private class Choice
        {
            [JsonProperty("message")]
            public Message Message { get; set; }
        }

        private class Message
        {
            [JsonProperty("content")]
            public string Content { get; set; }
        }

        private class Usage
        {
            [JsonProperty("total_tokens")]
            public int TotalTokens { get; set; }
        }
    }
}
