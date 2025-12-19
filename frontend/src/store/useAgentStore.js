import { create } from 'zustand'

const useAgentStore = create((set, get) => ({
  // Connection state
  ws: null,
  isConnected: false,
  isExecuting: false,

  // Query state
  query: '',
  dataFiles: [],
  config: {
    max_iterations: 20,
    max_debug_attempts: 3,
    execution_timeout_seconds: 60.0,
    temperature: 0.0,
    max_tokens: 4096,
  },

  // Execution state
  sessionId: null,
  currentState: null,
  iteration: 0,
  finalAnswer: null,
  error: null,

  // History
  executionHistory: [],

  // Actions
  setQuery: (query) => set({ query }),

  setDataFiles: (files) => set({ dataFiles: files }),

  setConfig: (config) => set((state) => ({
    config: { ...state.config, ...config }
  })),

  connectWebSocket: () => {
    // Use relative URL to leverage Vite's WebSocket proxy
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/query`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('WebSocket connected')
      set({ isConnected: true, ws, error: null })
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      set({ isConnected: false, ws: null })
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      set({ error: 'WebSocket connection failed' })
    }

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      const { handleMessage } = get()
      handleMessage(message)
    }

    set({ ws })
  },

  disconnectWebSocket: () => {
    const { ws } = get()
    if (ws) {
      ws.close()
      set({ ws: null, isConnected: false })
    }
  },

  handleMessage: (message) => {
    console.log('Received message:', message)

    switch (message.type) {
      case 'start':
        set({
          sessionId: message.session_id,
          isExecuting: true,
          error: null,
          finalAnswer: null,
          currentState: null,
          iteration: 0,
        })
        break

      case 'progress':
        set({
          currentState: message.state,
          iteration: message.iteration,
        })
        break

      case 'complete':
        set({
          currentState: message.state,
          finalAnswer: message.final_answer,
          isExecuting: false,
        })
        // Add to history
        const { query, dataFiles, currentState } = get()
        set((state) => ({
          executionHistory: [
            {
              id: Date.now(),
              query,
              dataFiles,
              state: currentState,
              finalAnswer: message.final_answer,
              timestamp: new Date().toISOString(),
            },
            ...state.executionHistory,
          ],
        }))
        break

      case 'error':
        set({
          error: message.message,
          isExecuting: false,
        })
        break

      case 'cancelled':
        set({
          isExecuting: false,
          error: 'Execution cancelled',
        })
        break

      default:
        console.warn('Unknown message type:', message.type)
    }
  },

  startExecution: () => {
    const { ws, query, dataFiles, config } = get()

    if (!ws || !ws.readyState === WebSocket.OPEN) {
      set({ error: 'WebSocket not connected' })
      return
    }

    if (!query || dataFiles.length === 0) {
      set({ error: 'Query and data files are required' })
      return
    }

    const message = {
      action: 'start',
      query,
      data_files: dataFiles,
      config,
    }

    ws.send(JSON.stringify(message))
  },

  cancelExecution: () => {
    const { ws } = get()
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: 'cancel' }))
    }
  },

  clearError: () => set({ error: null }),

  reset: () => set({
    sessionId: null,
    currentState: null,
    iteration: 0,
    finalAnswer: null,
    error: null,
  }),
}))

export default useAgentStore
