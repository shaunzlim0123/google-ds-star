import { useEffect } from 'react'
import useAgentStore from '../store/useAgentStore'
import QueryInput from './QueryInput'
import FileUpload from './FileUpload'
import ProgressMonitor from './ProgressMonitor'
import ResultsDisplay from './ResultsDisplay'
import ConfigPanel from './ConfigPanel'
import { AlertCircle } from 'lucide-react'

export default function Dashboard() {
  const {
    isConnected,
    isExecuting,
    error,
    clearError,
    connectWebSocket,
    disconnectWebSocket,
  } = useAgentStore()

  useEffect(() => {
    connectWebSocket()
    return () => disconnectWebSocket()
  }, [connectWebSocket, disconnectWebSocket])

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`}
          />
          <span className="text-sm text-gray-600">
            {isConnected ? 'Connected to server' : 'Disconnected'}
          </span>
        </div>
        {isExecuting && (
          <div className="flex items-center gap-2 px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
            <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
            Executing query...
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-red-900">Error</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
          <button
            onClick={clearError}
            className="text-red-600 hover:text-red-800 text-sm font-medium"
          >
            Dismiss
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Input & Config */}
        <div className="lg:col-span-1 space-y-6">
          <QueryInput />
          <FileUpload />
          <ConfigPanel />
        </div>

        {/* Right Column: Progress & Results */}
        <div className="lg:col-span-2 space-y-6">
          <ProgressMonitor />
          <ResultsDisplay />
        </div>
      </div>
    </div>
  )
}
