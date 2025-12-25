/**
 * SQL2.AI UI Components
 *
 * Shared React components for the SQL2.AI platform.
 * Designed for distinctiveness - avoiding generic AI UI patterns.
 */

// Layout
export { Layout, type LayoutProps } from './components/Layout';
export { Card, type CardProps } from './components/Card';
export { Panel, type PanelProps } from './components/Panel';

// SQL-specific
export { SqlEditor, type SqlEditorProps } from './components/SqlEditor';
export { ExecutionPlan, type ExecutionPlanProps } from './components/ExecutionPlan';
export { SchemaTree, type SchemaTreeProps } from './components/SchemaTree';
export {
  QueryResults,
  type QueryResultsProps,
  MetricsChart,
  PerformanceGraph,
  ConnectionForm,
  QueryBuilder,
  Toast,
  Loading,
  ErrorBoundary,
} from './components/QueryResults';
