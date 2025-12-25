/**
 * SQL2AI Files Library
 *
 * File parsing and transformation pipeline
 * for CSV, Excel, JSON, XML, and log files.
 */

// File processor interfaces
export interface FileOptions {
  encoding?: string;
  delimiter?: string;
  hasHeader?: boolean;
  skipRows?: number;
  maxRows?: number;
  sheetName?: string;
  dateFormats?: string[];
}

export interface ColumnInfo {
  name: string;
  detectedType: DataType;
  nullable: boolean;
  sampleValues: unknown[];
  uniqueCount?: number;
  nullCount?: number;
  minLength?: number;
  maxLength?: number;
}

export type DataType =
  | 'string'
  | 'integer'
  | 'decimal'
  | 'boolean'
  | 'date'
  | 'datetime'
  | 'time'
  | 'binary'
  | 'json'
  | 'unknown';

export interface FileAnalysisResult {
  detectedFormat: FileFormat;
  detectedEncoding: string;
  estimatedRowCount: number;
  columns: ColumnInfo[];
  metadata: Record<string, unknown>;
  warnings: string[];
}

export type FileFormat = 'csv' | 'tsv' | 'excel' | 'json' | 'jsonl' | 'xml' | 'parquet' | 'log';

export interface IFileProcessor {
  analyze(input: Buffer | string, options?: FileOptions): Promise<FileAnalysisResult>;
  streamRows(
    input: Buffer | string,
    options?: FileOptions
  ): AsyncIterable<Record<string, unknown>>;
  readAll(input: Buffer | string, options?: FileOptions): Promise<Record<string, unknown>[]>;
}

// Transformation interfaces
export interface TransformRule {
  column: string;
  operation: TransformOperation;
  parameters?: Record<string, unknown>;
}

export type TransformOperation =
  | 'trim'
  | 'uppercase'
  | 'lowercase'
  | 'titlecase'
  | 'replace'
  | 'regex_replace'
  | 'parse_date'
  | 'parse_number'
  | 'map_values'
  | 'default_value'
  | 'concat'
  | 'split'
  | 'substring';

export interface ITransformer {
  apply(row: Record<string, unknown>, rules: TransformRule[]): Record<string, unknown>;
  applyBatch(
    rows: Record<string, unknown>[],
    rules: TransformRule[]
  ): Record<string, unknown>[];
}

// Validation interfaces
export interface ValidationRule {
  column: string;
  validator: ValidatorType;
  parameters?: Record<string, unknown>;
  message?: string;
}

export type ValidatorType =
  | 'required'
  | 'type'
  | 'min_length'
  | 'max_length'
  | 'range'
  | 'pattern'
  | 'enum'
  | 'email'
  | 'url'
  | 'phone'
  | 'date'
  | 'custom';

export interface ValidationError {
  row: number;
  column: string;
  value: unknown;
  rule: string;
  message: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  rowsValidated: number;
  rowsFailed: number;
}

export interface IDataValidator {
  validate(rows: Record<string, unknown>[], rules: ValidationRule[]): ValidationResult;
  validateRow(row: Record<string, unknown>, rules: ValidationRule[]): ValidationError[];
}

// Schema detection
export interface ISchemaDetector {
  detect(rows: Record<string, unknown>[], sampleSize?: number): ColumnInfo[];
  inferType(values: unknown[]): DataType;
  suggestSqlType(columnInfo: ColumnInfo, dialect: 'sqlserver' | 'postgresql'): string;
}

// Re-export implementations (to be added)
// export { CsvProcessor } from './processors/CsvProcessor';
// export { ExcelProcessor } from './processors/ExcelProcessor';
// export { JsonProcessor } from './processors/JsonProcessor';
// export { SchemaDetector } from './analysis/SchemaDetector';
// export { DataTransformer } from './transform/DataTransformer';
// export { DataValidator } from './validation/DataValidator';
