import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Converse - Bidirectional AI Conversation | SQL2.AI',
  description:
    'Two-way conversation bridge between SQL databases and AI systems. LangChain, LangGraph, and LiteLLM integration with PII protection.',
};

export default function ConversePage(): JSX.Element {
  return (
    <>
      {/* Hero */}
      <section className="pt-32 pb-16 md:pt-40 md:pb-20">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <Link
              href="/features/"
              className="inline-flex items-center gap-2 text-small text-text-muted hover:text-text-secondary mb-6"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              All Modules
            </Link>

            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-2xl bg-[#8B5CF6]/10 flex items-center justify-center text-[#8B5CF6]">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Converse</h1>
                <p className="text-lg text-[#8B5CF6] font-medium">AI Conversation Bridge</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Bidirectional AI conversation platform for SQL Server and PostgreSQL. Database procedures
              and Python agents communicate seamlessly while Presidio-style filtering prevents data leaks.
            </p>
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">How It Works</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`┌─────────────────────────────────────────────────────────────────┐
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
│  ┌─────────────────────────────────────────────────────────────┐│
│  │   PII Filter  │   Purview Classify  │   Custom Filters     ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │   LangChain   │     LangGraph       │      LiteLLM         ││
│  └─────────────────────────────────────────────────────────────┘│
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │   OpenAI    │   │  Anthropic  │   │   Local     │
   │   GPT-4     │   │   Claude    │   │   Ollama    │
   └─────────────┘   └─────────────┘   └─────────────┘`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* SQL Interface */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Database Interface</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`-- Simple AI query from SQL Server
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

EXEC sql2ai.AskAI @ConversationId = @ConversationId,
    @Prompt = 'What are the top 3 selling products?',
    @Response = @Response1 OUTPUT;

EXEC sql2ai.AskAI @ConversationId = @ConversationId,
    @Prompt = 'Why do you think they sell well?',  -- Context preserved!
    @Response = @Response2 OUTPUT;`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Security Features */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Security & Privacy</h2>

          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">PII Detection</h3>
              <p className="text-sm text-text-muted mb-4">Presidio-powered scanning for:</p>
              <ul className="space-y-1 text-text-secondary text-sm">
                <li>• Names & Addresses</li>
                <li>• Email & Phone</li>
                <li>• SSN & Credit Cards</li>
                <li>• Medical Licenses</li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Secret Detection</h3>
              <p className="text-sm text-text-muted mb-4">Block prompts containing:</p>
              <ul className="space-y-1 text-text-secondary text-sm">
                <li>• API keys & passwords</li>
                <li>• Internal-only data</li>
                <li>• Confidential markers</li>
                <li>• Custom patterns</li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Model Routing</h3>
              <p className="text-sm text-text-muted mb-4">Route queries intelligently:</p>
              <ul className="space-y-1 text-text-secondary text-sm">
                <li>• Sensitive → Local LLM</li>
                <li>• Code → CodeLlama</li>
                <li>• General → GPT-4</li>
                <li>• Cost optimization</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* LiteLLM Integration */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 text-text-primary mb-4">Model Flexibility with LiteLLM</h2>
            <p className="text-text-secondary mb-12">
              One interface for all AI providers - switch models without code changes
            </p>

            <div className="flex flex-wrap justify-center gap-4">
              {['OpenAI', 'Anthropic', 'Azure OpenAI', 'AWS Bedrock', 'Ollama', 'Mistral', 'Cohere', 'Google AI'].map((provider) => (
                <div key={provider} className="px-4 py-2 rounded-lg bg-[#8B5CF6]/10 text-[#8B5CF6] text-sm font-medium">
                  {provider}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Response Format */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Guaranteed Response Formats</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`-- Ensure JSON response matches schema
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

-- Response is guaranteed to match schema or returns error`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Bridge Your Database to AI"
        description="Seamless, secure AI integration for SQL Server and PostgreSQL with full privacy protection."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
