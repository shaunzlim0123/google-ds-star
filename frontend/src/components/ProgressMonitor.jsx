import { useMemo } from 'react'
import useAgentStore from '../store/useAgentStore'
import {
  CheckCircle2,
  Circle,
  XCircle,
  AlertCircle,
  ArrowLeft,
  Loader2,
  FileSearch,
  Lightbulb,
  Code2,
  TestTube2,
  GitBranch,
  Bug,
  Sparkles
} from 'lucide-react'
import clsx from 'clsx'

const AGENT_ICONS = {
  analyzer: FileSearch,
  planner: Lightbulb,
  coder: Code2,
  verifier: TestTube2,
  router: GitBranch,
  debugger: Bug,
  finalizer: Sparkles,
}

const STATUS_CONFIG = {
  PENDING: {
    icon: Circle,
    className: 'text-gray-400',
    badgeClass: 'badge-pending',
    label: 'Pending'
  },
  EXECUTING: {
    icon: Loader2,
    className: 'text-yellow-500 animate-spin',
    badgeClass: 'badge-executing',
    label: 'Executing'
  },
  COMPLETED: {
    icon: CheckCircle2,
    className: 'text-green-500',
    badgeClass: 'badge-completed',
    label: 'Completed'
  },
  FAILED: {
    icon: XCircle,
    className: 'text-red-500',
    badgeClass: 'badge-failed',
    label: 'Failed'
  },
  BACKTRACKED: {
    icon: ArrowLeft,
    className: 'text-orange-500',
    badgeClass: 'badge-backtracked',
    label: 'Backtracked'
  },
}

export default function ProgressMonitor() {
  const { currentState, iteration, isExecuting } = useAgentStore()

  const currentPhase = useMemo(() => {
    if (!currentState) return 'idle'
    if (!currentState.file_descriptions || currentState.file_descriptions.length === 0) {
      return 'analyzing'
    }
    if (!currentState.is_complete) {
      return 'planning'
    }
    return 'finalizing'
  }, [currentState])

  if (!currentState && !isExecuting) {
    return (
      <div className="card">
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
            <Lightbulb className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Ready to analyze
          </h3>
          <p className="text-sm text-gray-600">
            Upload your data files and enter a query to get started
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Progress Monitor</h2>
        {iteration > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Iteration</span>
            <span className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-semibold">
              {iteration}
            </span>
          </div>
        )}
      </div>

      {/* Phase Indicator */}
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-3">
          <div className="flex items-center gap-2 flex-1">
            <div className={clsx(
              'w-full h-2 rounded-full bg-gray-200 overflow-hidden'
            )}>
              <div
                className={clsx(
                  'h-full bg-gradient-to-r from-primary-500 to-primary-600 transition-all duration-500',
                  currentPhase === 'analyzing' && 'w-1/3',
                  currentPhase === 'planning' && 'w-2/3',
                  currentPhase === 'finalizing' && 'w-full'
                )}
              />
            </div>
          </div>
        </div>
        <div className="flex justify-between text-xs text-gray-600">
          <span className={clsx(currentPhase === 'analyzing' && 'font-semibold text-primary-600')}>
            Analyzing Files
          </span>
          <span className={clsx(currentPhase === 'planning' && 'font-semibold text-primary-600')}>
            Planning & Executing
          </span>
          <span className={clsx(currentPhase === 'finalizing' && 'font-semibold text-primary-600')}>
            Finalizing
          </span>
        </div>
      </div>

      {/* File Descriptions */}
      {currentState?.file_descriptions && currentState.file_descriptions.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <FileSearch className="w-4 h-4" />
            Analyzed Files ({currentState.file_descriptions.length})
          </h3>
          <div className="space-y-2">
            {currentState.file_descriptions.map((file, idx) => (
              <div key={idx} className="bg-gray-50 rounded-lg p-3 text-sm">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">
                      {file.path.split('/').pop()}
                    </p>
                    <p className="text-gray-600 text-xs mt-1">{file.description}</p>
                  </div>
                  <span className="badge badge-pending text-xs">
                    {file.file_type}
                  </span>
                </div>
                {file.row_count && (
                  <p className="text-gray-500 text-xs mt-2">
                    {file.row_count.toLocaleString()} rows
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Steps */}
      {currentState?.steps && currentState.steps.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Lightbulb className="w-4 h-4" />
            Analysis Steps ({currentState.steps.length})
          </h3>
          <div className="space-y-2">
            {currentState.steps.map((step, idx) => {
              const statusConfig = STATUS_CONFIG[step.status] || STATUS_CONFIG.PENDING
              const StatusIcon = statusConfig.icon

              return (
                <div
                  key={idx}
                  className={clsx(
                    'flex items-start gap-3 p-3 rounded-lg border transition-all',
                    step.status === 'EXECUTING' && 'bg-yellow-50 border-yellow-200',
                    step.status === 'COMPLETED' && 'bg-green-50 border-green-200',
                    step.status === 'FAILED' && 'bg-red-50 border-red-200',
                    step.status === 'BACKTRACKED' && 'bg-orange-50 border-orange-200',
                    step.status === 'PENDING' && 'bg-gray-50 border-gray-200'
                  )}
                >
                  <StatusIcon className={clsx('w-5 h-5 flex-shrink-0 mt-0.5', statusConfig.className)} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm text-gray-900">
                        <span className="font-medium">Step {step.index + 1}:</span>{' '}
                        {step.description}
                      </p>
                      <span className={clsx('badge text-xs whitespace-nowrap', statusConfig.badgeClass)}>
                        {statusConfig.label}
                      </span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Execution in progress indicator */}
      {isExecuting && currentState?.steps && currentState.steps.length === 0 && (
        <div className="text-center py-8">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin mx-auto mb-3" />
          <p className="text-sm text-gray-600">Initializing analysis...</p>
        </div>
      )}
    </div>
  )
}
