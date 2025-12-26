using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;
using SQL2AI.SSMS.Models;

namespace SQL2AI.SSMS.Services
{
    /// <summary>
    /// HTTP client for SQL2.AI API.
    /// </summary>
    public class Sql2AiApiClient : IDisposable
    {
        private readonly HttpClient _httpClient;
        private readonly ExtensionSettings _settings;
        private bool _disposed;

        public Sql2AiApiClient(ExtensionSettings settings)
        {
            _settings = settings ?? throw new ArgumentNullException(nameof(settings));

            _httpClient = new HttpClient
            {
                BaseAddress = new Uri(_settings.ApiBaseUrl),
                Timeout = TimeSpan.FromSeconds(_settings.RequestTimeoutSeconds)
            };

            if (!string.IsNullOrEmpty(_settings.ApiKey))
            {
                _httpClient.DefaultRequestHeaders.Authorization =
                    new AuthenticationHeaderValue("Bearer", _settings.ApiKey);
            }

            _httpClient.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
            _httpClient.DefaultRequestHeaders.Add("User-Agent", "SQL2AI-SSMS/1.0");
        }

        /// <summary>
        /// Optimize a SQL query.
        /// </summary>
        public async Task<OptimizationResult> OptimizeQueryAsync(
            string query,
            string? connectionId = null,
            CancellationToken cancellationToken = default)
        {
            var request = new
            {
                query_text = query,
                connection_id = connectionId
            };

            return await PostAsync<OptimizationResult>(
                "/api/optimize/analyze-query",
                request,
                cancellationToken);
        }

        /// <summary>
        /// Review SQL code for issues.
        /// </summary>
        public async Task<CodeReviewResult> ReviewCodeAsync(
            string code,
            string? filePath = null,
            CancellationToken cancellationToken = default)
        {
            var request = new
            {
                code = code,
                file_path = filePath,
                min_severity = "info"
            };

            return await PostAsync<CodeReviewResult>(
                "/api/codereview/review",
                request,
                cancellationToken);
        }

        /// <summary>
        /// Explain a SQL query in natural language.
        /// </summary>
        public async Task<QueryExplanation> ExplainQueryAsync(
            string query,
            CancellationToken cancellationToken = default)
        {
            var request = new
            {
                query = query
            };

            return await PostAsync<QueryExplanation>(
                "/api/writer/explain",
                request,
                cancellationToken);
        }

        /// <summary>
        /// Generate CRUD procedures for a table.
        /// </summary>
        public async Task<CrudGenerationResult> GenerateCrudAsync(
            string tableName,
            string schemaName = "dbo",
            bool includeSoftDelete = false,
            CancellationToken cancellationToken = default)
        {
            var request = new
            {
                table_name = tableName,
                schema_name = schemaName,
                include_create = true,
                include_read = true,
                include_update = true,
                include_delete = true,
                include_list = true,
                include_search = true,
                soft_delete = includeSoftDelete
            };

            return await PostAsync<CrudGenerationResult>(
                "/api/writer/crud",
                request,
                cancellationToken);
        }

        /// <summary>
        /// Generate DDL from natural language prompt.
        /// </summary>
        public async Task<DdlGenerationResult> GenerateFromPromptAsync(
            DdlGenerationRequest request,
            CancellationToken cancellationToken = default)
        {
            return await PostAsync<DdlGenerationResult>(
                "/api/writer/from-prompt",
                request,
                cancellationToken);
        }

        /// <summary>
        /// Analyze an execution plan.
        /// </summary>
        public async Task<ExecutionPlanAnalysis> AnalyzeExecutionPlanAsync(
            string planXml,
            string? query = null,
            CancellationToken cancellationToken = default)
        {
            var request = new
            {
                plan_xml = planXml,
                query = query
            };

            return await PostAsync<ExecutionPlanAnalysis>(
                "/api/optimize/analyze-plan",
                request,
                cancellationToken);
        }

        /// <summary>
        /// Get inline completion suggestions.
        /// </summary>
        public async Task<string[]> GetCompletionsAsync(
            string partialQuery,
            int cursorPosition,
            CancellationToken cancellationToken = default)
        {
            var request = new
            {
                partial_query = partialQuery,
                cursor_position = cursorPosition
            };

            var result = await PostAsync<CompletionResult>(
                "/api/writer/complete",
                request,
                cancellationToken);

            return result?.Suggestions ?? Array.Empty<string>();
        }

        /// <summary>
        /// Check API connectivity.
        /// </summary>
        public async Task<bool> CheckConnectionAsync(CancellationToken cancellationToken = default)
        {
            try
            {
                var response = await _httpClient.GetAsync("/health", cancellationToken);
                return response.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }

        private async Task<T> PostAsync<T>(
            string endpoint,
            object request,
            CancellationToken cancellationToken) where T : new()
        {
            try
            {
                var json = JsonConvert.SerializeObject(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync(endpoint, content, cancellationToken);

                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    throw new ApiException(
                        $"API request failed: {response.StatusCode}",
                        (int)response.StatusCode,
                        errorContent);
                }

                var responseJson = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<T>(responseJson) ?? new T();
            }
            catch (TaskCanceledException) when (cancellationToken.IsCancellationRequested)
            {
                throw;
            }
            catch (TaskCanceledException)
            {
                throw new ApiException("Request timed out", 408, null);
            }
            catch (HttpRequestException ex)
            {
                throw new ApiException($"Network error: {ex.Message}", 0, null);
            }
        }

        public void Dispose()
        {
            if (!_disposed)
            {
                _httpClient?.Dispose();
                _disposed = true;
            }
        }

        private class CompletionResult
        {
            public string[]? Suggestions { get; set; }
        }
    }

    /// <summary>
    /// Exception for API errors.
    /// </summary>
    public class ApiException : Exception
    {
        public int StatusCode { get; }
        public string? ResponseContent { get; }

        public ApiException(string message, int statusCode, string? responseContent)
            : base(message)
        {
            StatusCode = statusCode;
            ResponseContent = responseContent;
        }
    }
}
