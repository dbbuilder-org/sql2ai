/**
 * API Client for SQL2.AI Backend
 *
 * In production: Uses NEXT_PUBLIC_API_URL environment variable
 * In development: Uses /api/v1 proxy to localhost:8000
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL
  ? `${process.env.NEXT_PUBLIC_API_URL}/api`
  : '/api/v1';

interface ApiError {
  detail: string;
  status: number;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const config: RequestInit = {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      const error: ApiError = {
        detail: await response.text(),
        status: response.status,
      };
      throw error;
    }

    // Handle empty responses
    const text = await response.text();
    if (!text) return {} as T;

    return JSON.parse(text);
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const api = new ApiClient();

// =============================================================================
// Type Definitions
// =============================================================================

export interface Connection {
  id: string;
  name: string;
  dialect: 'sqlserver' | 'postgresql' | 'mysql' | 'mariadb';
  host: string;
  port: number;
  database: string;
  username: string;
  environment: 'development' | 'staging' | 'production';
  ssl_enabled: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_connected_at?: string;
}

export interface ConnectionCreate {
  name: string;
  dialect: string;
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  environment?: string;
  ssl_enabled?: boolean;
}

export interface Query {
  id: string;
  name: string;
  sql: string;
  description?: string;
  connection_id: string;
  is_favorite: boolean;
  execution_count: number;
  avg_execution_time_ms?: number;
  created_at: string;
  last_executed_at?: string;
}

export interface QueryExecution {
  id: string;
  query_id?: string;
  connection_id: string;
  sql: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  rows_affected?: number;
  execution_time_ms?: number;
  error_message?: string;
  result_data?: Record<string, unknown>[];
  created_at: string;
}

export interface SchemaTable {
  name: string;
  schema: string;
  row_count?: number;
  columns: SchemaColumn[];
}

export interface SchemaColumn {
  name: string;
  data_type: string;
  is_nullable: boolean;
  is_primary_key: boolean;
  is_foreign_key: boolean;
  default_value?: string;
}

export interface DashboardStats {
  total_connections: number;
  queries_today: number;
  ai_tokens_used: number;
  avg_response_time_ms: number;
}

export interface AIGenerateRequest {
  prompt: string;
  connection_id?: string;
  dialect?: string;
}

export interface AIGenerateResponse {
  sql: string;
  explanation?: string;
  tokens_used?: number;
}

// =============================================================================
// API Functions
// =============================================================================

// Connections
export const connections = {
  list: () => api.get<Connection[]>('/connections'),
  get: (id: string) => api.get<Connection>(`/connections/${id}`),
  create: (data: ConnectionCreate) => api.post<Connection>('/connections', data),
  update: (id: string, data: Partial<ConnectionCreate>) =>
    api.put<Connection>(`/connections/${id}`, data),
  delete: (id: string) => api.delete(`/connections/${id}`),
  test: (id: string) => api.post<{ success: boolean; message: string }>(
    `/connections/${id}/test`
  ),
};

// Queries
export const queries = {
  list: () => api.get<Query[]>('/queries'),
  get: (id: string) => api.get<Query>(`/queries/${id}`),
  create: (data: Partial<Query>) => api.post<Query>('/queries', data),
  execute: (connectionId: string, sql: string) =>
    api.post<QueryExecution>('/queries/execute', { connection_id: connectionId, sql }),
  history: (connectionId?: string) =>
    api.get<QueryExecution[]>(`/queries/history${connectionId ? `?connection_id=${connectionId}` : ''}`),
};

// Schema
export const schema = {
  get: (connectionId: string) =>
    api.get<{ tables: SchemaTable[] }>(`/schemas/${connectionId}`),
  extract: (connectionId: string) =>
    api.post<{ tables: SchemaTable[] }>(`/schemas/${connectionId}/extract`),
};

// AI
export const ai = {
  generate: (data: AIGenerateRequest) =>
    api.post<AIGenerateResponse>('/queries/generate', data),
  optimize: (sql: string, connectionId?: string) =>
    api.post<{ optimized_sql: string; suggestions: string[] }>('/queries/optimize', {
      sql,
      connection_id: connectionId
    }),
  explain: (sql: string) =>
    api.post<{ explanation: string }>('/queries/explain', { sql }),
};

// Dashboard
export const dashboard = {
  stats: () => api.get<DashboardStats>('/dashboard/stats'),
};

// Health
export const health = {
  check: () => api.get<{ status: string }>('/health'),
};
