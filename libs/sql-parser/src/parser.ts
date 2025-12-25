/**
 * SQL Parser
 *
 * Main parser implementation that converts SQL text into an AST.
 */

import type { ParseOptions, ParseResult, SqlDialect } from './types';
import { Tokenizer } from './tokenizer';

export class SqlParser {
  private dialect: SqlDialect;
  private tokenizer: Tokenizer;

  constructor(options: ParseOptions) {
    this.dialect = options.dialect;
    this.tokenizer = new Tokenizer(options);
  }

  /**
   * Parse a SQL statement into an AST.
   */
  parse(sql: string): ParseResult {
    const tokens = this.tokenizer.tokenize(sql);

    // TODO: Implement full parser
    return {
      ast: {
        type: 'Program',
        start: { line: 1, column: 0, offset: 0 },
        end: { line: 1, column: sql.length, offset: sql.length },
        children: [],
      },
      tokens,
      errors: [],
      warnings: [],
    };
  }

  /**
   * Parse multiple SQL statements.
   */
  parseMultiple(sql: string): ParseResult[] {
    // Split by semicolon and parse each statement
    const statements = sql.split(';').filter((s) => s.trim().length > 0);
    return statements.map((statement) => this.parse(statement));
  }
}

/**
 * Convenience function to parse SQL.
 */
export function parse(sql: string, options: ParseOptions): ParseResult {
  const parser = new SqlParser(options);
  return parser.parse(sql);
}
