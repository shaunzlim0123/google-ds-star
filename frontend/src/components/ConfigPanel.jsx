import { useState } from 'react'
import useAgentStore from '../store/useAgentStore'
import { Settings, ChevronDown, ChevronUp, RotateCcw } from 'lucide-react'

const DEFAULT_CONFIG = {
  max_iterations: 20,
  max_debug_attempts: 3,
  execution_timeout_seconds: 60.0,
  temperature: 0.0,
  max_tokens: 4096,
}

export default function ConfigPanel() {
  const { config, setConfig, isExecuting } = useAgentStore()
  const [isExpanded, setIsExpanded] = useState(false)

  const handleChange = (key, value) => {
    setConfig({ [key]: value })
  }

  const resetToDefaults = () => {
    setConfig(DEFAULT_CONFIG)
  }

  return (
    <div className="card">
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Settings className="w-5 h-5" />
          Configuration
        </h2>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-gray-600" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-600" />
        )}
      </div>

      {isExpanded && (
        <div className="mt-4 space-y-4">
          {/* Max Iterations */}
          <div>
            <label htmlFor="max_iterations" className="block text-sm font-medium text-gray-700 mb-1">
              Max Iterations
            </label>
            <input
              id="max_iterations"
              type="number"
              min="1"
              max="100"
              value={config.max_iterations}
              onChange={(e) => handleChange('max_iterations', parseInt(e.target.value))}
              disabled={isExecuting}
              className="input"
            />
            <p className="mt-1 text-xs text-gray-500">
              Maximum number of planning iterations (1-100)
            </p>
          </div>

          {/* Max Debug Attempts */}
          <div>
            <label htmlFor="max_debug_attempts" className="block text-sm font-medium text-gray-700 mb-1">
              Max Debug Attempts
            </label>
            <input
              id="max_debug_attempts"
              type="number"
              min="1"
              max="10"
              value={config.max_debug_attempts}
              onChange={(e) => handleChange('max_debug_attempts', parseInt(e.target.value))}
              disabled={isExecuting}
              className="input"
            />
            <p className="mt-1 text-xs text-gray-500">
              Maximum attempts to fix code errors (1-10)
            </p>
          </div>

          {/* Execution Timeout */}
          <div>
            <label htmlFor="execution_timeout" className="block text-sm font-medium text-gray-700 mb-1">
              Execution Timeout (seconds)
            </label>
            <input
              id="execution_timeout"
              type="number"
              min="10"
              max="600"
              step="10"
              value={config.execution_timeout_seconds}
              onChange={(e) => handleChange('execution_timeout_seconds', parseFloat(e.target.value))}
              disabled={isExecuting}
              className="input"
            />
            <p className="mt-1 text-xs text-gray-500">
              Maximum time for code execution (10-600 seconds)
            </p>
          </div>

          {/* Temperature */}
          <div>
            <label htmlFor="temperature" className="block text-sm font-medium text-gray-700 mb-1">
              Temperature
            </label>
            <div className="flex items-center gap-3">
              <input
                id="temperature"
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={config.temperature}
                onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
                disabled={isExecuting}
                className="flex-1"
              />
              <span className="text-sm font-medium text-gray-700 w-12 text-right">
                {config.temperature.toFixed(1)}
              </span>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              LLM creativity level (0.0 = deterministic, 1.0 = creative)
            </p>
          </div>

          {/* Max Tokens */}
          <div>
            <label htmlFor="max_tokens" className="block text-sm font-medium text-gray-700 mb-1">
              Max Tokens
            </label>
            <input
              id="max_tokens"
              type="number"
              min="1024"
              max="16384"
              step="512"
              value={config.max_tokens}
              onChange={(e) => handleChange('max_tokens', parseInt(e.target.value))}
              disabled={isExecuting}
              className="input"
            />
            <p className="mt-1 text-xs text-gray-500">
              Maximum LLM response length (1024-16384)
            </p>
          </div>

          {/* Reset Button */}
          <button
            onClick={resetToDefaults}
            disabled={isExecuting}
            className="btn btn-secondary w-full flex items-center justify-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Reset to Defaults
          </button>

          {/* Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-xs text-blue-900">
              <strong>Note:</strong> Configuration changes apply to the next execution.
              Advanced settings can affect analysis quality and performance.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
