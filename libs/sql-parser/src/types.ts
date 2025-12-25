/**
 * SQL Parser Types
 */

export type SqlDialect = 'postgresql' | 'sqlserver';

export interface ParseOptions {
  dialect: SqlDialect;
  preserveComments?: boolean;
  preserveWhitespace?: boolean;
}

export interface ParseResult {
  ast: AstNode;
  tokens: Token[];
  errors: ParseError[];
  warnings: ParseWarning[];
}

export interface Token {
  type: TokenType;
  value: string;
  start: Position;
  end: Position;
}

export interface Position {
  line: number;
  column: number;
  offset: number;
}

export type TokenType =
  | 'keyword'
  | 'identifier'
  | 'string'
  | 'number'
  | 'operator'
  | 'punctuation'
  | 'comment'
  | 'whitespace';

export interface AstNode {
  type: string;
  start: Position;
  end: Position;
  children?: AstNode[];
}

export interface ParseError {
  message: string;
  position: Position;
  code: string;
}

export interface ParseWarning {
  message: string;
  position: Position;
  code: string;
}

// Statement types
export interface SelectStatement extends AstNode {
  type: 'SelectStatement';
  columns: ColumnReference[];
  from?: TableReference[];
  where?: Expression;
  groupBy?: Expression[];
  having?: Expression;
  orderBy?: OrderByClause[];
  limit?: number;
  offset?: number;
}

export interface InsertStatement extends AstNode {
  type: 'InsertStatement';
  table: TableReference;
  columns?: string[];
  values?: Expression[][];
  select?: SelectStatement;
}

export interface UpdateStatement extends AstNode {
  type: 'UpdateStatement';
  table: TableReference;
  set: SetClause[];
  from?: TableReference[];
  where?: Expression;
}

export interface DeleteStatement extends AstNode {
  type: 'DeleteStatement';
  table: TableReference;
  where?: Expression;
}

export interface CreateTableStatement extends AstNode {
  type: 'CreateTableStatement';
  table: TableReference;
  columns: ColumnDefinition[];
  constraints?: TableConstraint[];
}

export interface ColumnReference extends AstNode {
  type: 'ColumnReference';
  table?: string;
  column: string;
  alias?: string;
}

export interface TableReference extends AstNode {
  type: 'TableReference';
  schema?: string;
  table: string;
  alias?: string;
}

export interface Expression extends AstNode {
  type: string;
}

export interface OrderByClause extends AstNode {
  type: 'OrderByClause';
  expression: Expression;
  direction: 'ASC' | 'DESC';
  nulls?: 'FIRST' | 'LAST';
}

export interface SetClause extends AstNode {
  type: 'SetClause';
  column: string;
  value: Expression;
}

export interface ColumnDefinition extends AstNode {
  type: 'ColumnDefinition';
  name: string;
  dataType: DataType;
  nullable?: boolean;
  defaultValue?: Expression;
  constraints?: ColumnConstraint[];
}

export interface DataType extends AstNode {
  type: 'DataType';
  name: string;
  precision?: number;
  scale?: number;
  length?: number;
}

export interface ColumnConstraint extends AstNode {
  type: 'ColumnConstraint';
  constraintType: 'PRIMARY_KEY' | 'UNIQUE' | 'NOT_NULL' | 'CHECK' | 'REFERENCES';
}

export interface TableConstraint extends AstNode {
  type: 'TableConstraint';
  constraintType: 'PRIMARY_KEY' | 'UNIQUE' | 'FOREIGN_KEY' | 'CHECK';
  columns: string[];
}
