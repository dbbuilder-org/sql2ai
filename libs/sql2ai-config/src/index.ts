/**
 * SQL2AI Config Library
 *
 * Configuration management with validation,
 * environment variables, and secret handling.
 */

// Configuration provider interfaces
export interface IConfigProvider {
  load<T extends object>(path: string): Promise<T>;
  save<T extends object>(config: T, path: string): Promise<void>;
  merge<T extends object>(base: T, overrides: Partial<T>): T;
  validate<T extends object>(config: T, schema: ConfigSchema): ValidationResult;
}

// Configuration schema
export interface ConfigField {
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  required?: boolean;
  default?: unknown;
  secret?: boolean;
  description?: string;
  validator?: (value: unknown) => boolean;
}

export interface ConfigSchema {
  fields: Record<string, ConfigField>;
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
}

export interface ValidationError {
  field: string;
  message: string;
  value?: unknown;
}

// Configuration service interface
export interface IConfigurationService {
  get<T>(key: string): T | undefined;
  getRequired<T>(key: string): T;
  getSection<T extends object>(sectionName: string): T;
  getConnectionString(name: string): string | undefined;
  getSecret(key: string): string | undefined;
  reload(): Promise<void>;
}

// Environment configuration
export interface EnvironmentConfig {
  name: 'development' | 'staging' | 'production';
  variables: Record<string, string>;
}

// Database connection configuration
export interface DatabaseConfig {
  server: string;
  database: string;
  username?: string;
  password?: string;
  port?: number;
  encrypt?: boolean;
  trustServerCertificate?: boolean;
}

// AI configuration
export interface AiConfig {
  provider: 'openai' | 'claude' | 'local';
  apiKey?: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
  baseUrl?: string;
}

// Monitoring configuration
export interface MonitoringConfig {
  enabled: boolean;
  collectionIntervalSeconds: number;
  retentionDays: number;
  alerting: {
    enabled: boolean;
    channels: string[];
  };
}

// Application configuration
export interface AppConfig {
  environment: EnvironmentConfig;
  database: DatabaseConfig;
  ai: AiConfig;
  monitoring: MonitoringConfig;
  features: Record<string, boolean>;
}

// Helper functions
export function getEnv(key: string, defaultValue?: string): string | undefined {
  return process.env[key] ?? defaultValue;
}

export function getEnvRequired(key: string): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Required environment variable ${key} is not set`);
  }
  return value;
}

export function getEnvNumber(key: string, defaultValue?: number): number | undefined {
  const value = process.env[key];
  if (!value) return defaultValue;
  const parsed = parseInt(value, 10);
  return isNaN(parsed) ? defaultValue : parsed;
}

export function getEnvBoolean(key: string, defaultValue?: boolean): boolean | undefined {
  const value = process.env[key];
  if (!value) return defaultValue;
  return value.toLowerCase() === 'true' || value === '1';
}

// Re-export implementations (to be added)
// export { JsonConfigProvider } from './providers/JsonConfigProvider';
// export { YamlConfigProvider } from './providers/YamlConfigProvider';
// export { EnvironmentConfigProvider } from './providers/EnvironmentConfigProvider';
// export { ConfigurationService } from './services/ConfigurationService';
