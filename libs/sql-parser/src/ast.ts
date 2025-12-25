/**
 * AST Utilities
 *
 * Helper functions for working with SQL ASTs.
 */

import type { AstNode, SelectStatement, TableReference, ColumnReference } from './types';

/**
 * Visit all nodes in an AST.
 */
export function visit(
  node: AstNode,
  visitor: (node: AstNode, parent?: AstNode) => void,
  parent?: AstNode
): void {
  visitor(node, parent);
  if (node.children) {
    for (const child of node.children) {
      visit(child, visitor, node);
    }
  }
}

/**
 * Find all nodes of a specific type.
 */
export function findAll<T extends AstNode>(
  node: AstNode,
  type: string
): T[] {
  const results: T[] = [];
  visit(node, (n) => {
    if (n.type === type) {
      results.push(n as T);
    }
  });
  return results;
}

/**
 * Extract all table references from a statement.
 */
export function extractTables(node: AstNode): TableReference[] {
  return findAll<TableReference>(node, 'TableReference');
}

/**
 * Extract all column references from a statement.
 */
export function extractColumns(node: AstNode): ColumnReference[] {
  return findAll<ColumnReference>(node, 'ColumnReference');
}

/**
 * Check if a statement is a SELECT query.
 */
export function isSelectStatement(node: AstNode): node is SelectStatement {
  return node.type === 'SelectStatement';
}

/**
 * Transform an AST node.
 */
export function transform(
  node: AstNode,
  transformer: (node: AstNode) => AstNode
): AstNode {
  const transformed = transformer(node);
  if (transformed.children) {
    transformed.children = transformed.children.map((child) =>
      transform(child, transformer)
    );
  }
  return transformed;
}

/**
 * Pretty print an AST node.
 */
export function prettyPrint(node: AstNode, indent: number = 0): string {
  const spaces = '  '.repeat(indent);
  let result = `${spaces}${node.type}`;

  if (node.children && node.children.length > 0) {
    result += ' {\n';
    for (const child of node.children) {
      result += prettyPrint(child, indent + 1) + '\n';
    }
    result += `${spaces}}`;
  }

  return result;
}
