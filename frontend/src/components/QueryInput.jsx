import { useState } from 'react'
import useAgentStore from '../store/useAgentStore'
import { Send, RotateCcw } from 'lucide-react'

export default function QueryInput() {
  const {
    query,
    dataFiles,
    isExecuting,
    isConnected,
    setQuery,
    startExecution,
    cancelExecution,
    reset,
  } = useAgentStore()

  const canExecute = isConnected && !isExecuting && query.trim() && dataFiles.length > 0

  const handleSubmit = (e) => {
    e.preventDefault()
    if (canExecute) {
      startExecution()
    }
  }

  const handleReset = () => {
    setQuery('')
    reset()
  }

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Query</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
            What would you like to analyze?
          </label>
          <textarea
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., What product had made the most money for each country?"
            className="input min-h-[120px] resize-y"
            disabled={isExecuting}
          />
          <p className="mt-2 text-xs text-gray-500">
            Ask a data science question about your uploaded files
          </p>
        </div>

        <div className="flex gap-2">
          <button
            type="submit"
            disabled={!canExecute}
            className="btn btn-primary flex-1 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
            {isExecuting ? 'Executing...' : 'Execute Query'}
          </button>

          {isExecuting ? (
            <button
              type="button"
              onClick={cancelExecution}
              className="btn btn-danger"
            >
              Cancel
            </button>
          ) : (
            <button
              type="button"
              onClick={handleReset}
              className="btn btn-secondary"
              title="Reset"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          )}
        </div>

        {!isConnected && (
          <p className="text-sm text-red-600">
            Not connected to server. Please check your connection.
          </p>
        )}
      </form>
    </div>
  )
}
