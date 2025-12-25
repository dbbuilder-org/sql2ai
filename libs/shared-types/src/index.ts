/**
 * Shared Types for SQL2.AI
 *
 * Common type definitions used across all SQL2.AI packages.
 */

// Database dialects
export type SqlDialect = 'postgresql' | 'sqlserver';

// User and authentication
export interface User {
  id: string;
  email: string;
  name: string;
  organization?: string;
  role: UserRole;
  createdAt: Date;
}

export type UserRole = 'admin' | 'developer' | 'viewer';

// Database connections
export interface DatabaseConnection {
  id: string;
  name: string;
  dialect: SqlDialect;
  host: string;
  port: number;
  database: string;
  username: string;
  ssl: boolean;
  createdAt: Date;
  lastUsedAt?: Date;
}

// API responses
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  meta?: ResponseMeta;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ResponseMeta {
  page?: number;
  pageSize?: number;
  total?: number;
  requestId?: string;
}

// Pagination
export interface PaginatedRequest {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

// Feature flags and configuration
export interface FeatureFlags {
  enableTelemetry: boolean;
  enableAIOptimization: boolean;
  enableMCPIntegration: boolean;
  maxConnectionsPerUser: number;
}

// Subscription and billing
export interface Subscription {
  id: string;
  userId: string;
  plan: SubscriptionPlan;
  status: 'active' | 'canceled' | 'past_due';
  currentPeriodEnd: Date;
}

export type SubscriptionPlan = 'free' | 'professional' | 'team' | 'enterprise';

// Job and task tracking
export interface Job {
  id: string;
  type: JobType;
  status: JobStatus;
  progress: number;
  result?: unknown;
  error?: string;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
}

export type JobType = 'schema_analysis' | 'migration' | 'optimization' | 'telemetry_sync';
export type JobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'canceled';

// Audit logging
export interface AuditLog {
  id: string;
  userId: string;
  action: string;
  resource: string;
  resourceId: string;
  details: Record<string, unknown>;
  timestamp: Date;
  ipAddress?: string;
}

// Zod schemas for runtime validation (to be used with @sql2ai/shared-types)
export const SQL_DIALECTS = ['postgresql', 'sqlserver'] as const;
export const USER_ROLES = ['admin', 'developer', 'viewer'] as const;
export const SUBSCRIPTION_PLANS = ['free', 'professional', 'team', 'enterprise'] as const;
