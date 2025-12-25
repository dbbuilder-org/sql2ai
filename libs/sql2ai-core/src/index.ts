/**
 * SQL2AI Core Library
 *
 * Database connectivity and query execution abstraction
 * for SQL Server, PostgreSQL, and MySQL.
 */

// Connection interfaces
export interface DatabaseConnectionInfo {
  server: string;
  database: string;
  username?: string;
  password?: string;
  port?: number;
  encrypt?: boolean;
  trustServerCertificate?: boolean;
  connectionTimeout?: number;
  commandTimeout?: number;
}

export interface QueryMetrics {
  executionTimeMs: number;
  rowsAffected: number;
  cpuTimeMs?: number;
  logicalReads?: number;
  physicalReads?: number;
}

export interface IDatabaseConnection {
  query<T>(sql: string, parameters?: Record<string, unknown>): Promise<T[]>;
  querySingle<T>(sql: string, parameters?: Record<string, unknown>): Promise<T | null>;
  execute(sql: string, parameters?: Record<string, unknown>): Promise<number>;
  executeWithMetrics(
    sql: string,
    parameters?: Record<string, unknown>
  ): Promise<{ result: number; metrics: QueryMetrics }>;
  stream<T>(sql: string, parameters?: Record<string, unknown>): AsyncIterable<T>;
  close(): Promise<void>;
}

export interface IConnectionFactory {
  create(connectionInfo: DatabaseConnectionInfo): Promise<IDatabaseConnection>;
  testConnection(connectionInfo: DatabaseConnectionInfo): Promise<boolean>;
}

// Database types
export type DatabaseType = 'sqlserver' | 'postgresql' | 'mysql';

// Server and database info models
export interface ServerInfo {
  name: string;
  version: string;
  edition?: string;
  productLevel?: string;
  collation?: string;
}

export interface DatabaseInfo {
  name: string;
  state: string;
  recoveryModel?: string;
  compatibilityLevel?: number;
  sizeBytes?: number;
}

// Re-export implementations (to be added)
// export { SqlServerConnection } from './connections/SqlServerConnection';
// export { PostgresConnection } from './connections/PostgresConnection';
// export { ConnectionFactory } from './connections/ConnectionFactory';
