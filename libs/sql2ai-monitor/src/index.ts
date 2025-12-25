/**
 * SQL2AI Monitor Library
 *
 * Database monitoring and metrics collection
 * with alerting and anomaly detection.
 */

// Metric interfaces
export interface Metric {
  name: string;
  value: number;
  unit: MetricUnit;
  timestamp: Date;
  tags: Record<string, string>;
  metadata?: Record<string, unknown>;
}

export type MetricUnit =
  | 'count'
  | 'percent'
  | 'milliseconds'
  | 'seconds'
  | 'bytes'
  | 'kilobytes'
  | 'megabytes'
  | 'requests_per_second'
  | 'connections'
  | 'ratio';

export interface MetricSeries {
  name: string;
  dataPoints: Array<{ timestamp: Date; value: number }>;
  aggregation?: 'avg' | 'sum' | 'min' | 'max' | 'count';
}

// Collector interfaces
export interface IMetricCollector {
  collect(): Promise<Metric[]>;
  getName(): string;
  getInterval(): number;
}

export interface CollectorConfig {
  enabled: boolean;
  intervalSeconds: number;
  timeout?: number;
  retryCount?: number;
}

// SQL Server specific metrics
export interface SqlServerMetrics {
  performance: {
    batchRequestsPerSec: number;
    sqlCompilationsPerSec: number;
    sqlRecompilationsPerSec: number;
    pageLifeExpectancy: number;
    bufferCacheHitRatio: number;
    checkpointPagesPerSec: number;
  };
  memory: {
    totalServerMemoryKb: number;
    targetServerMemoryKb: number;
    memoryGrantsPending: number;
    memoryGrantsOutstanding: number;
  };
  io: {
    diskReadBytesPerSec: number;
    diskWriteBytesPerSec: number;
    ioStallReadMs: number;
    ioStallWriteMs: number;
  };
  connections: {
    userConnections: number;
    blockedProcesses: number;
    lockWaitsPerSec: number;
    deadlocksPerSec: number;
  };
}

// PostgreSQL specific metrics
export interface PostgreSqlMetrics {
  performance: {
    transactionsPerSec: number;
    activeConnections: number;
    idleConnections: number;
    waitingConnections: number;
    cacheHitRatio: number;
  };
  replication: {
    replicationLagBytes: number;
    replicationLagSeconds: number;
    walBytesPerSec: number;
  };
  vacuum: {
    deadTuples: number;
    lastAutovacuum: Date | null;
    vacuumRunning: boolean;
  };
  locks: {
    lockWaits: number;
    exclusiveLocks: number;
    deadlocks: number;
  };
}

// Alerting interfaces
export interface Alert {
  id: string;
  name: string;
  severity: AlertSeverity;
  message: string;
  metric: string;
  threshold: number;
  currentValue: number;
  triggeredAt: Date;
  resolvedAt?: Date;
  acknowledged?: boolean;
  metadata?: Record<string, unknown>;
}

export type AlertSeverity = 'info' | 'warning' | 'error' | 'critical';

export interface AlertRule {
  id: string;
  name: string;
  metric: string;
  condition: AlertCondition;
  threshold: number;
  duration: number;
  severity: AlertSeverity;
  channels: string[];
  enabled: boolean;
}

export type AlertCondition =
  | 'greater_than'
  | 'less_than'
  | 'equals'
  | 'not_equals'
  | 'rate_increase'
  | 'rate_decrease';

export interface IAlertEngine {
  evaluate(metrics: Metric[], rules: AlertRule[]): Alert[];
  acknowledge(alertId: string): Promise<void>;
  resolve(alertId: string): Promise<void>;
  getActiveAlerts(): Promise<Alert[]>;
}

// Baseline and anomaly detection
export interface Baseline {
  metric: string;
  period: BaselinePeriod;
  average: number;
  stdDev: number;
  min: number;
  max: number;
  percentiles: {
    p50: number;
    p90: number;
    p95: number;
    p99: number;
  };
  updatedAt: Date;
}

export type BaselinePeriod = 'hourly' | 'daily' | 'weekly';

export interface IAnomalyDetector {
  detect(metric: Metric, baseline: Baseline): AnomalyResult | null;
  updateBaseline(metrics: Metric[], period: BaselinePeriod): Baseline;
}

export interface AnomalyResult {
  metric: string;
  value: number;
  expectedRange: { min: number; max: number };
  deviationScore: number;
  timestamp: Date;
}

// Query analysis interfaces
export interface QueryInfo {
  queryHash: string;
  queryText: string;
  executionCount: number;
  totalDurationMs: number;
  avgDurationMs: number;
  totalCpuMs: number;
  avgCpuMs: number;
  totalLogicalReads: number;
  avgLogicalReads: number;
  lastExecutionTime: Date;
}

export interface QueryRegression {
  queryHash: string;
  queryText: string;
  previousAvgMs: number;
  currentAvgMs: number;
  regressionPercent: number;
  possibleCause: string;
  recommendation: string;
}

export interface IQueryAnalyzer {
  getTopQueries(limit: number, orderBy: 'duration' | 'cpu' | 'reads'): Promise<QueryInfo[]>;
  detectRegressions(lookbackHours: number): Promise<QueryRegression[]>;
  explainRegression(queryHash: string): Promise<string>;
}

// Re-export implementations (to be added)
// export { DmvCollector } from './collectors/DmvCollector';
// export { QueryStoreCollector } from './collectors/QueryStoreCollector';
// export { AlertEngine } from './alerting/AlertEngine';
// export { AnomalyDetector } from './analysis/AnomalyDetector';
// export { QueryAnalyzer } from './analysis/QueryAnalyzer';
