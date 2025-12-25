/**
 * SQL2AI AI Library
 *
 * AI/LLM provider abstraction with multi-provider support
 * for OpenAI, Claude, and local models.
 */

// AI Provider interfaces
export interface AiOptions {
  model?: string;
  temperature?: number;
  maxTokens?: number;
  systemPrompt?: string;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  stopSequences?: string[];
  metadata?: Record<string, string>;
}

export interface AiResponse {
  content: string;
  model: string;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  finishReason: 'stop' | 'length' | 'content_filter' | 'tool_calls';
  metadata?: Record<string, unknown>;
}

export interface EmbeddingResult {
  embedding: number[];
  model: string;
  dimensions: number;
}

export type AnalysisType =
  | 'code_review'
  | 'performance'
  | 'security'
  | 'documentation'
  | 'optimization'
  | 'explanation';

export interface IAiProvider {
  complete(prompt: string, options?: AiOptions): Promise<AiResponse>;
  stream(prompt: string, options?: AiOptions): AsyncIterable<string>;
  embed(text: string): Promise<EmbeddingResult>;
  embedBatch(texts: string[]): Promise<EmbeddingResult[]>;
  analyze(content: string, type: AnalysisType, options?: AiOptions): Promise<AiResponse>;
}

// Conversation interfaces
export interface ConversationMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
  timestamp?: Date;
}

export interface ConversationContext {
  messages: ConversationMessage[];
  metadata?: Record<string, unknown>;
}

export interface IConversationService {
  startConversation(systemPrompt?: string): ConversationContext;
  addMessage(context: ConversationContext, role: 'user' | 'assistant', content: string): void;
  complete(context: ConversationContext, options?: AiOptions): Promise<AiResponse>;
  stream(context: ConversationContext, options?: AiOptions): AsyncIterable<string>;
}

// Prompt template interfaces
export interface PromptTemplate {
  name: string;
  template: string;
  variables: string[];
  defaultOptions?: Partial<AiOptions>;
}

export interface IPromptTemplateService {
  register(template: PromptTemplate): void;
  get(name: string): PromptTemplate | undefined;
  render(name: string, variables: Record<string, string>): string;
}

// Provider types
export type AiProviderType = 'openai' | 'claude' | 'local' | 'azure';

// Default options
export const defaultAiOptions: AiOptions = {
  model: 'gpt-4-turbo',
  temperature: 0.7,
  maxTokens: 4096,
  topP: 1,
  frequencyPenalty: 0,
  presencePenalty: 0,
};

// Re-export implementations (to be added)
// export { OpenAiProvider } from './providers/OpenAiProvider';
// export { ClaudeProvider } from './providers/ClaudeProvider';
// export { LocalProvider } from './providers/LocalProvider';
// export { PromptTemplateService } from './services/PromptTemplateService';
// export { ConversationService } from './services/ConversationService';
