/**
 * SQL Tokenizer
 *
 * Converts SQL text into a stream of tokens.
 */

import type { ParseOptions, Token, TokenType, Position } from './types';

export class Tokenizer {
  private dialect: ParseOptions['dialect'];
  private preserveComments: boolean;
  private preserveWhitespace: boolean;

  constructor(options: ParseOptions) {
    this.dialect = options.dialect;
    this.preserveComments = options.preserveComments ?? false;
    this.preserveWhitespace = options.preserveWhitespace ?? false;
  }

  /**
   * Tokenize a SQL string.
   */
  tokenize(sql: string): Token[] {
    const tokens: Token[] = [];
    let pos = 0;
    let line = 1;
    let column = 0;

    while (pos < sql.length) {
      const char = sql[pos];
      const startPos: Position = { line, column, offset: pos };

      // Handle whitespace
      if (/\s/.test(char)) {
        const match = sql.slice(pos).match(/^\s+/);
        if (match) {
          if (this.preserveWhitespace) {
            tokens.push(this.createToken('whitespace', match[0], startPos));
          }
          this.advancePosition(match[0], pos, line, column);
          pos += match[0].length;
          continue;
        }
      }

      // Handle single-line comments
      if (sql.slice(pos, pos + 2) === '--') {
        const endOfLine = sql.indexOf('\n', pos);
        const end = endOfLine === -1 ? sql.length : endOfLine;
        const comment = sql.slice(pos, end);
        if (this.preserveComments) {
          tokens.push(this.createToken('comment', comment, startPos));
        }
        pos = end;
        continue;
      }

      // Handle multi-line comments
      if (sql.slice(pos, pos + 2) === '/*') {
        const end = sql.indexOf('*/', pos + 2);
        const comment = end === -1 ? sql.slice(pos) : sql.slice(pos, end + 2);
        if (this.preserveComments) {
          tokens.push(this.createToken('comment', comment, startPos));
        }
        pos += comment.length;
        continue;
      }

      // Handle strings
      if (char === "'" || char === '"') {
        const quote = char;
        let end = pos + 1;
        while (end < sql.length) {
          if (sql[end] === quote) {
            if (sql[end + 1] === quote) {
              end += 2; // Escaped quote
            } else {
              break;
            }
          } else {
            end++;
          }
        }
        const value = sql.slice(pos, end + 1);
        tokens.push(this.createToken('string', value, startPos));
        pos = end + 1;
        continue;
      }

      // Handle numbers
      if (/\d/.test(char)) {
        const match = sql.slice(pos).match(/^\d+(\.\d+)?/);
        if (match) {
          tokens.push(this.createToken('number', match[0], startPos));
          pos += match[0].length;
          continue;
        }
      }

      // Handle identifiers and keywords
      if (/[a-zA-Z_]/.test(char)) {
        const match = sql.slice(pos).match(/^[a-zA-Z_][a-zA-Z0-9_]*/);
        if (match) {
          const value = match[0];
          const type = this.isKeyword(value) ? 'keyword' : 'identifier';
          tokens.push(this.createToken(type, value, startPos));
          pos += value.length;
          continue;
        }
      }

      // Handle operators and punctuation
      const operators = ['<=>', '<>', '!=', '>=', '<=', '::', '||', '&&'];
      const foundOp = operators.find((op) => sql.slice(pos, pos + op.length) === op);
      if (foundOp) {
        tokens.push(this.createToken('operator', foundOp, startPos));
        pos += foundOp.length;
        continue;
      }

      if (/[<>=!+\-*/%&|^~]/.test(char)) {
        tokens.push(this.createToken('operator', char, startPos));
        pos++;
        continue;
      }

      if (/[(),;.\[\]{}]/.test(char)) {
        tokens.push(this.createToken('punctuation', char, startPos));
        pos++;
        continue;
      }

      // Unknown character - skip
      pos++;
    }

    return tokens;
  }

  private createToken(type: TokenType, value: string, start: Position): Token {
    return {
      type,
      value,
      start,
      end: {
        line: start.line,
        column: start.column + value.length,
        offset: start.offset + value.length,
      },
    };
  }

  private advancePosition(
    text: string,
    _pos: number,
    _line: number,
    _column: number
  ): { line: number; column: number } {
    let line = _line;
    let column = _column;
    for (const char of text) {
      if (char === '\n') {
        line++;
        column = 0;
      } else {
        column++;
      }
    }
    return { line, column };
  }

  private isKeyword(word: string): boolean {
    const keywords = new Set([
      'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'EXISTS',
      'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE',
      'CREATE', 'TABLE', 'INDEX', 'VIEW', 'PROCEDURE', 'FUNCTION',
      'ALTER', 'DROP', 'TRUNCATE',
      'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'CROSS', 'ON',
      'GROUP', 'BY', 'HAVING', 'ORDER', 'ASC', 'DESC',
      'LIMIT', 'OFFSET', 'TOP', 'DISTINCT',
      'UNION', 'INTERSECT', 'EXCEPT', 'ALL',
      'AS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
      'NULL', 'IS', 'LIKE', 'BETWEEN', 'CAST',
      'BEGIN', 'COMMIT', 'ROLLBACK', 'TRANSACTION',
      'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'UNIQUE', 'CHECK',
      'CONSTRAINT', 'DEFAULT', 'IDENTITY', 'SERIAL',
      'INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT',
      'VARCHAR', 'CHAR', 'TEXT', 'NVARCHAR', 'NCHAR',
      'DECIMAL', 'NUMERIC', 'FLOAT', 'REAL', 'DOUBLE',
      'DATE', 'TIME', 'TIMESTAMP', 'DATETIME', 'DATETIME2',
      'BOOLEAN', 'BIT', 'BLOB', 'BINARY', 'VARBINARY',
      'UUID', 'UNIQUEIDENTIFIER', 'JSON', 'JSONB', 'XML',
    ]);
    return keywords.has(word.toUpperCase());
  }
}
