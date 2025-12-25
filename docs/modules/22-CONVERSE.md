# SQL Converse

**Bidirectional AI Conversation Platform**

## Overview

SQL Converse creates a two-way conversation bridge between SQL Server/PostgreSQL and AI systems using LangChain, LangGraph, and LiteLLM. A database table acts as the middleware, allowing both database procedures and Python agents to communicate seamlessly while Presidio/Purview-style filtering ensures no PII or company secrets leak to AI systems.

## The Problem

### Current Database-AI Integration Challenges

| Challenge | Traditional Approach | Risk |
|-----------|---------------------|------|
| Async AI calls | HTTP from DB (complex) | Blocking, timeouts |
| Response handling | Manual parsing | Format errors |
| PII protection | None or manual | Data leaks to AI |
| Model flexibility | Hardcoded | Vendor lock-in |
| Conversation state | Stateless | Context lost |
| Error handling | Ad-hoc | Silent failures |

## SQL Converse Solution

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Stored Procedure / Application                            │ │
│  │         │                                                  │ │
│  │         ▼                                                  │ │
│  │  EXEC sql2ai.AskAI @prompt, @format, @max_tokens...       │ │
│  │         │                                                  │ │
│  │         ▼                                                  │ │
│  │  ┌─────────────────────────────────────────┐               │ │
│  │  │     sql2ai.ConversationQueue            │               │ │
│  │  │  (Request Table - the middleware)       │               │ │
│  │  └─────────────────────────────────────────┘               │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │ Poll / Subscribe
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQL CONVERSE AGENT (Python)                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    SECURITY LAYER                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │
│  │  │   Presidio   │  │   Purview    │  │   Custom     │     │ │
│  │  │  PII Filter  │  │   Classify   │  │   Filters    │     │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    AI ORCHESTRATION                        │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │
│  │  │  LangChain   │  │  LangGraph   │  │   LiteLLM    │     │ │
│  │  │   Chains     │  │   Agents     │  │   Router     │     │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │   OpenAI    │   │  Anthropic  │   │   Local     │
   │   GPT-4     │   │   Claude    │   │   Ollama    │
   └─────────────┘   └─────────────┘   └─────────────┘
```

## Conversation Queue Table

```sql
-- The middleware table for bidirectional communication
CREATE TABLE sql2ai.ConversationQueue (
    RequestId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    ConversationId UNIQUEIDENTIFIER,  -- For multi-turn conversations
    RequestedAt DATETIME2 DEFAULT GETUTCDATE(),
    RequestedBy NVARCHAR(200),  -- User/process identifier

    -- Request
    Prompt NVARCHAR(MAX) NOT NULL,
    SystemPrompt NVARCHAR(MAX),
    Model NVARCHAR(100) DEFAULT 'gpt-4',
    MaxTokens INT DEFAULT 1000,
    Temperature DECIMAL(3,2) DEFAULT 0.7,
    ResponseFormat NVARCHAR(50) DEFAULT 'text',  -- text, json, markdown
    JsonSchema NVARCHAR(MAX),  -- For structured output

    -- Security
    PIIFilteringApplied BIT DEFAULT 0,
    OriginalPromptHash VARBINARY(32),  -- To detect tampering

    -- Response
    Status NVARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, failed
    Response NVARCHAR(MAX),
    TokensUsed INT,
    ProcessingTimeMs INT,
    CompletedAt DATETIME2,

    -- Error handling
    ErrorMessage NVARCHAR(MAX),
    RetryCount INT DEFAULT 0,

    INDEX IX_Status_RequestedAt (Status, RequestedAt)
);
```

## Database Interface

### SQL Server

```sql
-- Simple AI query
DECLARE @Response NVARCHAR(MAX);

EXEC sql2ai.AskAI
    @Prompt = 'Summarize the sales trend for Q4',
    @Response = @Response OUTPUT;

SELECT @Response;

-- Structured JSON response
DECLARE @Analysis NVARCHAR(MAX);

EXEC sql2ai.AskAI
    @Prompt = 'Analyze this customer feedback and extract sentiment',
    @Context = @CustomerFeedback,
    @ResponseFormat = 'json',
    @JsonSchema = '{
        "sentiment": "positive|negative|neutral",
        "confidence": "number",
        "key_themes": ["string"],
        "recommended_action": "string"
    }',
    @Response = @Analysis OUTPUT;

-- Parse JSON response
SELECT
    JSON_VALUE(@Analysis, '$.sentiment') AS Sentiment,
    JSON_VALUE(@Analysis, '$.confidence') AS Confidence,
    JSON_VALUE(@Analysis, '$.recommended_action') AS Action;

-- Multi-turn conversation
DECLARE @ConversationId UNIQUEIDENTIFIER = NEWID();
DECLARE @Response1 NVARCHAR(MAX), @Response2 NVARCHAR(MAX);

-- First turn
EXEC sql2ai.AskAI
    @ConversationId = @ConversationId,
    @Prompt = 'What are the top 3 selling products?',
    @Response = @Response1 OUTPUT;

-- Follow-up (context preserved)
EXEC sql2ai.AskAI
    @ConversationId = @ConversationId,
    @Prompt = 'Why do you think they sell well?',
    @Response = @Response2 OUTPUT;
```

### PostgreSQL

```sql
-- Simple query
SELECT sql2ai.ask_ai('Summarize the sales trend for Q4');

-- With options
SELECT sql2ai.ask_ai(
    prompt := 'Analyze customer churn risk',
    context := (SELECT json_agg(c) FROM customers c WHERE last_order < NOW() - INTERVAL '90 days'),
    response_format := 'json',
    model := 'claude-3-sonnet'
);

-- Multi-turn
SELECT sql2ai.start_conversation() AS conversation_id;
-- Returns: 'abc-123-def'

SELECT sql2ai.continue_conversation(
    'abc-123-def',
    'What patterns do you see in the data?'
);
```

## Python Agent

```python
# sql2ai_converse/agent.py
import asyncio
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import litellm
import pyodbc

class SQLConverseAgent:
    def __init__(self, connection_string: str, config: dict):
        self.connection_string = connection_string
        self.config = config

        # PII Protection
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

        # Conversation memory (per conversation_id)
        self.conversations: dict[str, ConversationBufferMemory] = {}

        # LiteLLM for model flexibility
        litellm.set_verbose = False

    async def process_queue(self):
        """Main loop - poll queue and process requests."""
        while True:
            request = await self.get_next_request()
            if request:
                await self.process_request(request)
            else:
                await asyncio.sleep(0.1)  # Small delay when queue empty

    async def process_request(self, request: dict):
        """Process a single AI request with PII filtering."""
        try:
            # 1. Scan and filter PII from prompt
            filtered_prompt = self.filter_pii(request['prompt'])

            # 2. Check for company secrets
            if self.contains_secrets(filtered_prompt):
                raise SecurityException("Company secrets detected in prompt")

            # 3. Get or create conversation memory
            memory = self.get_conversation_memory(request.get('conversation_id'))

            # 4. Call AI model via LiteLLM
            response = await self.call_ai(
                prompt=filtered_prompt,
                system_prompt=request.get('system_prompt'),
                model=request.get('model', 'gpt-4'),
                max_tokens=request.get('max_tokens', 1000),
                response_format=request.get('response_format', 'text'),
                json_schema=request.get('json_schema'),
                memory=memory
            )

            # 5. Validate response format
            if request.get('response_format') == 'json':
                response = self.validate_json_response(
                    response,
                    request.get('json_schema')
                )

            # 6. Update queue with response
            await self.update_request(
                request['request_id'],
                status='completed',
                response=response
            )

        except Exception as e:
            await self.update_request(
                request['request_id'],
                status='failed',
                error=str(e)
            )

    def filter_pii(self, text: str) -> str:
        """Remove PII using Presidio."""
        results = self.analyzer.analyze(
            text=text,
            entities=[
                "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER",
                "US_SSN", "CREDIT_CARD", "US_BANK_NUMBER",
                "LOCATION", "DATE_TIME", "NRP", "MEDICAL_LICENSE"
            ],
            language="en"
        )

        if results:
            anonymized = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results,
                operators={
                    "DEFAULT": {"type": "replace", "new_value": "[REDACTED]"}
                }
            )
            return anonymized.text

        return text

    def contains_secrets(self, text: str) -> bool:
        """Check for company-specific secrets."""
        patterns = self.config.get('secret_patterns', [])
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    async def call_ai(
        self,
        prompt: str,
        system_prompt: str = None,
        model: str = "gpt-4",
        max_tokens: int = 1000,
        response_format: str = "text",
        json_schema: dict = None,
        memory: ConversationBufferMemory = None
    ) -> str:
        """Call AI model via LiteLLM for provider flexibility."""

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add conversation history if exists
        if memory:
            for msg in memory.chat_memory.messages:
                messages.append({
                    "role": "user" if msg.type == "human" else "assistant",
                    "content": msg.content
                })

        messages.append({"role": "user", "content": prompt})

        # Use LiteLLM for model-agnostic calls
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            response_format={"type": "json_object"} if response_format == "json" else None
        )

        return response.choices[0].message.content
```

## Configuration

```yaml
# sql2ai-converse.yaml
database:
  connection_string: ${DATABASE_CONNECTION}
  poll_interval: 100ms
  batch_size: 10

security:
  pii_filtering:
    enabled: true
    entities:
      - PERSON
      - EMAIL_ADDRESS
      - PHONE_NUMBER
      - US_SSN
      - CREDIT_CARD
      - LOCATION

  secret_patterns:
    - "API[_-]?KEY"
    - "PASSWORD"
    - "SECRET"
    - "INTERNAL[_-]?ONLY"
    - "CONFIDENTIAL"

  max_prompt_length: 10000
  audit_all_requests: true

models:
  default: gpt-4
  providers:
    openai:
      api_key: ${OPENAI_API_KEY}
      models: [gpt-4, gpt-4-turbo, gpt-3.5-turbo]

    anthropic:
      api_key: ${ANTHROPIC_API_KEY}
      models: [claude-3-opus, claude-3-sonnet]

    azure:
      api_key: ${AZURE_OPENAI_KEY}
      endpoint: ${AZURE_OPENAI_ENDPOINT}
      models: [gpt-4-azure]

    local:
      endpoint: http://localhost:11434
      models: [llama2, mistral, codellama]

  routing:
    - pattern: "code|sql|programming"
      model: codellama  # Route code questions to code model
    - pattern: "sensitive|confidential"
      model: local  # Keep sensitive queries local
    - default: gpt-4
```

## Response Format Enforcement

```sql
-- Ensure JSON response matches schema
EXEC sql2ai.AskAI
    @Prompt = 'Extract product information from this description',
    @Context = @ProductDescription,
    @ResponseFormat = 'json',
    @JsonSchema = '{
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "price": {"type": "number"},
            "category": {"type": "string", "enum": ["Electronics", "Clothing", "Food"]},
            "features": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["name", "price", "category"]
    }',
    @MaxRetries = 3,  -- Retry if format invalid
    @Response = @Response OUTPUT;
```

## Security Dashboard

```
╔══════════════════════════════════════════════════════════════════╗
║                    SQL CONVERSE SECURITY                         ║
╠══════════════════════════════════════════════════════════════════╣
║ REQUESTS TODAY: 4,721                                            ║
╠══════════════════════════════════════════════════════════════════╣
║ PII FILTERING                                                    ║
║ ─────────────────────────────────────────────────────────────── ║
║ Prompts scanned:      4,721                                      ║
║ PII detected:         847 (17.9%)                                ║
║ PII redacted:         847 ✓                                      ║
║ Types found:          Email (412), Phone (289), Name (146)       ║
╠══════════════════════════════════════════════════════════════════╣
║ SECRET DETECTION                                                 ║
║ ─────────────────────────────────────────────────────────────── ║
║ Blocked requests:     3                                          ║
║ Patterns matched:     API_KEY (2), CONFIDENTIAL (1)              ║
╠══════════════════════════════════════════════════════════════════╣
║ MODEL USAGE                                                      ║
║ ─────────────────────────────────────────────────────────────── ║
║ gpt-4:               2,847 requests                              ║
║ claude-3-sonnet:     1,204 requests                              ║
║ local/llama2:        670 requests (sensitive queries)            ║
╚══════════════════════════════════════════════════════════════════╝
```

## CLI Commands

```bash
# Initialize converse tables
sql2ai converse init --connection "..."

# Start Python agent
sql2ai converse start --config converse.yaml

# Test PII filtering
sql2ai converse test-filter "Contact John at john@email.com"

# View queue status
sql2ai converse status
```

## Integration Points

- **SQL Audit**: Log all AI interactions
- **SQL Comply**: Ensure AI usage compliance
- **SQL Encrypt**: Encrypt conversation history
- **SQL Monitor**: AI request dashboard
