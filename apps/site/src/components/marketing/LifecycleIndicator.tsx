'use client';

import { useState } from 'react';

type LifecycleStage = 'analyze' | 'optimize' | 'refactor' | 'index' | 'document' | 'version' | 'deploy';

interface StageInfo {
  id: LifecycleStage;
  name: string;
  description: string;
  icon: JSX.Element;
  features: string[];
}

const stages: StageInfo[] = [
  {
    id: 'analyze',
    name: 'Analyze',
    description: 'Deep schema analysis with AI-powered pattern detection',
    icon: <AnalyzeIcon />,
    features: ['Schema structure analysis', 'Dependency mapping', 'Anti-pattern detection', 'Compatibility checking'],
  },
  {
    id: 'optimize',
    name: 'Optimize',
    description: 'Query optimization with execution plan analysis',
    icon: <OptimizeIcon />,
    features: ['Execution plan interpretation', 'Query rewriting', 'Set-based conversion', 'Sargability analysis'],
  },
  {
    id: 'refactor',
    name: 'Refactor',
    description: 'Intelligent code refactoring suggestions',
    icon: <RefactorIcon />,
    features: ['Cursor to set-based', 'Procedure decomposition', 'Dead code detection', 'Normalization'],
  },
  {
    id: 'index',
    name: 'Index',
    description: 'Smart indexing recommendations',
    icon: <IndexIcon />,
    features: ['Missing indexes', 'Covering indexes', 'Unused detection', 'Consolidation'],
  },
  {
    id: 'document',
    name: 'Document',
    description: 'Auto-generated documentation',
    icon: <DocumentIcon />,
    features: ['ERD generation', 'Data dictionary', 'Change tracking', 'Intent documentation'],
  },
  {
    id: 'version',
    name: 'Version',
    description: 'Schema versioning and migration generation',
    icon: <VersionIcon />,
    features: ['Migration scripts', 'Rollback scripts', 'Drift detection', 'Breaking changes'],
  },
  {
    id: 'deploy',
    name: 'Deploy',
    description: 'Safe deployment with verification',
    icon: <DeployIcon />,
    features: ['Migration execution', 'Safety validation', 'Rollback automation', 'Verification'],
  },
];

interface LifecycleIndicatorProps {
  interactive?: boolean;
  highlightStage?: LifecycleStage;
}

export function LifecycleIndicator({
  interactive = true,
  highlightStage,
}: LifecycleIndicatorProps): JSX.Element {
  const [activeStage, setActiveStage] = useState<LifecycleStage>(highlightStage || 'analyze');
  const activeInfo = stages.find((s) => s.id === activeStage)!;

  return (
    <div className="w-full">
      {/* Lifecycle stages */}
      <div className="flex flex-wrap justify-center gap-2 md:gap-4 mb-8">
        {stages.map((stage) => (
          <button
            key={stage.id}
            onClick={() => interactive && setActiveStage(stage.id)}
            className={`
              flex flex-col items-center gap-2 p-4 rounded-xl transition-all
              ${interactive ? 'cursor-pointer hover:bg-bg-elevated' : 'cursor-default'}
              ${activeStage === stage.id ? 'bg-bg-elevated border border-primary' : 'border border-transparent'}
            `}
          >
            <div
              className={`
                w-12 h-12 rounded-lg flex items-center justify-center transition-colors
                ${activeStage === stage.id ? 'bg-primary text-white' : 'bg-bg-surface text-text-muted'}
              `}
            >
              {stage.icon}
            </div>
            <span
              className={`
                text-small font-medium transition-colors
                ${activeStage === stage.id ? 'text-text-primary' : 'text-text-muted'}
              `}
            >
              {stage.name}
            </span>
          </button>
        ))}
      </div>

      {/* Active stage details */}
      <div className="card p-6 md:p-8 animate-fade-in" key={activeStage}>
        <div className="flex flex-col md:flex-row md:items-start gap-6">
          <div
            className="w-16 h-16 rounded-xl flex items-center justify-center bg-primary text-white shrink-0"
          >
            {activeInfo.icon}
          </div>
          <div className="flex-1">
            <h3 className="text-h4 text-text-primary mb-2">{activeInfo.name}</h3>
            <p className="text-text-secondary mb-4">{activeInfo.description}</p>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {activeInfo.features.map((feature) => (
                <li key={feature} className="flex items-center gap-2 text-small text-text-secondary">
                  <svg className="w-4 h-4 text-success shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

// Icons
function AnalyzeIcon(): JSX.Element {
  return (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  );
}

function OptimizeIcon(): JSX.Element {
  return (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  );
}

function RefactorIcon(): JSX.Element {
  return (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>
  );
}

function IndexIcon(): JSX.Element {
  return (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
    </svg>
  );
}

function DocumentIcon(): JSX.Element {
  return (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  );
}

function VersionIcon(): JSX.Element {
  return (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
    </svg>
  );
}

function DeployIcon(): JSX.Element {
  return (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
    </svg>
  );
}
