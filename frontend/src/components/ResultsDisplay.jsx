import { useState } from 'react'
import useAgentStore from '../store/useAgentStore'
import CodeViewer from './CodeViewer'
import { Sparkles, Code2, Terminal, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react'
import clsx from 'clsx'

export default function ResultsDisplay() {
  const { currentState, finalAnswer, isExecuting } = useAgentStore()
  const [expandedSections, setExpandedSections] = useState({
    code: true,
    output: true,
    answer: true,
  })
  const [copied, setCopied] = useState(false)

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }))
  }

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  if (!currentState && !finalAnswer) {
    return null
  }

  const latestResult = currentState?.execution_results?.[currentState.execution_results.length - 1]

  return (
    <div className="space-y-4">
      {/* Final Answer */}
      {finalAnswer && (
        <div className="card border-2 border-green-200 bg-green-50">
          <div
            className="flex items-center justify-between cursor-pointer"
            onClick={() => toggleSection('answer')}
          >
            <h2 className="text-lg font-semibold text-green-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5" />
              Final Answer
            </h2>
            {expandedSections.answer ? (
              <ChevronUp className="w-5 h-5 text-green-700" />
            ) : (
              <ChevronDown className="w-5 h-5 text-green-700" />
            )}
          </div>

          {expandedSections.answer && (
            <div className="mt-4">
              <div className="bg-white rounded-lg p-4 text-gray-900 whitespace-pre-wrap">
                {finalAnswer}
              </div>
              <button
                onClick={() => copyToClipboard(finalAnswer)}
                className="mt-3 btn btn-secondary text-sm flex items-center gap-2"
              >
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copied ? 'Copied!' : 'Copy Answer'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Generated Code */}
      {currentState?.current_code && (
        <div className="card">
          <div
            className="flex items-center justify-between cursor-pointer"
            onClick={() => toggleSection('code')}
          >
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Code2 className="w-5 h-5" />
              Generated Code
            </h2>
            {expandedSections.code ? (
              <ChevronUp className="w-5 h-5 text-gray-600" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-600" />
            )}
          </div>

          {expandedSections.code && (
            <div className="mt-4">
              <CodeViewer code={currentState.current_code} language="python" />
              <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
                <span className="badge badge-pending">
                  Steps: {currentState.steps?.length || 0}
                </span>
                {latestResult?.execution_time_ms && (
                  <span className="badge badge-pending">
                    Execution: {latestResult.execution_time_ms}ms
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Execution Output */}
      {latestResult && (
        <div className="card">
          <div
            className="flex items-center justify-between cursor-pointer"
            onClick={() => toggleSection('output')}
          >
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Terminal className="w-5 h-5" />
              Execution Output
            </h2>
            <div className="flex items-center gap-3">
              <span
                className={clsx(
                  'badge text-xs',
                  latestResult.success ? 'badge-completed' : 'badge-failed'
                )}
              >
                {latestResult.success ? 'Success' : 'Failed'}
              </span>
              {expandedSections.output ? (
                <ChevronUp className="w-5 h-5 text-gray-600" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-600" />
              )}
            </div>
          </div>

          {expandedSections.output && (
            <div className="mt-4 space-y-3">
              {/* Standard Output */}
              {latestResult.stdout && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">
                    Standard Output
                  </h3>
                  <pre className="bg-gray-900 text-green-400 rounded-lg p-4 text-sm overflow-x-auto">
                    {latestResult.stdout}
                  </pre>
                </div>
              )}

              {/* Standard Error */}
              {latestResult.stderr && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">
                    Standard Error
                  </h3>
                  <pre className="bg-gray-900 text-yellow-400 rounded-lg p-4 text-sm overflow-x-auto">
                    {latestResult.stderr}
                  </pre>
                </div>
              )}

              {/* Error Traceback */}
              {latestResult.error_traceback && (
                <div>
                  <h3 className="text-sm font-semibold text-red-700 mb-2">
                    Error Traceback
                  </h3>
                  <pre className="bg-red-50 text-red-900 border border-red-200 rounded-lg p-4 text-sm overflow-x-auto">
                    {latestResult.error_traceback}
                  </pre>
                </div>
              )}

              {/* Empty output indicator */}
              {!latestResult.stdout && !latestResult.stderr && !latestResult.error_traceback && (
                <p className="text-sm text-gray-500 italic">No output</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Execution indicator */}
      {isExecuting && !currentState?.current_code && (
        <div className="card text-center py-8">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 rounded-full mb-3">
            <Code2 className="w-6 h-6 text-primary-600 animate-pulse" />
          </div>
          <p className="text-sm text-gray-600">Generating code...</p>
        </div>
      )}
    </div>
  )
}
