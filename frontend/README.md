# DS-STAR Frontend

A modern React.js frontend for the DS-STAR (Data Science Agent via Iterative Planning and Verification) agent.

## Features

- **Real-time Query Execution**: Watch your data science queries being analyzed in real-time
- **File Upload & Management**: Drag-and-drop interface for uploading CSV, JSON, Excel, and other data files
- **Live Progress Monitoring**: Track the agent's progress through analysis phases and steps
- **Code Visualization**: View the generated Python code with syntax highlighting
- **Execution Results**: See stdout, stderr, and error tracebacks in real-time
- **Configurable Settings**: Customize max iterations, debug attempts, timeouts, and LLM parameters
- **Responsive Design**: Works seamlessly on desktop and tablet devices

## Technology Stack

- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Zustand**: Lightweight state management
- **WebSockets**: Real-time bidirectional communication
- **Axios**: HTTP client for file uploads
- **Prism React Renderer**: Syntax highlighting for code
- **Lucide React**: Beautiful icon library
- **React Dropzone**: File upload with drag-and-drop

## Prerequisites

- Node.js 18+ and npm
- DS-STAR backend server running on `localhost:8000`

## Installation

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000)

## Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

To preview the production build:

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx          # Main dashboard container
│   │   ├── Header.jsx              # App header
│   │   ├── QueryInput.jsx          # Query input form
│   │   ├── FileUpload.jsx          # File upload component
│   │   ├── ProgressMonitor.jsx     # Real-time progress tracker
│   │   ├── ResultsDisplay.jsx      # Results and final answer
│   │   ├── CodeViewer.jsx          # Syntax-highlighted code display
│   │   └── ConfigPanel.jsx         # Configuration settings
│   ├── store/
│   │   └── useAgentStore.js        # Zustand state management
│   ├── App.jsx                     # Root component
│   ├── main.jsx                    # Entry point
│   └── index.css                   # Global styles
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## Usage Guide

### 1. Upload Data Files

- Click the upload area or drag-and-drop your data files
- Supported formats: CSV, JSON, Excel, Parquet, Markdown, XML, YAML, TXT
- Files are uploaded to the backend server automatically

### 2. Enter Your Query

- Type your data science question in the query input
- Example: "What product had made the most money for each country?"
- Be specific about what insights you want from your data

### 3. Configure Settings (Optional)

- Expand the Configuration panel to adjust:
  - **Max Iterations**: Maximum planning iterations (default: 20)
  - **Max Debug Attempts**: How many times to retry failed code (default: 3)
  - **Execution Timeout**: Maximum code execution time in seconds (default: 60)
  - **Temperature**: LLM creativity (0.0 = deterministic, 1.0 = creative)
  - **Max Tokens**: Maximum LLM response length (default: 4096)

### 4. Execute Query

- Click "Execute Query" to start the analysis
- Watch the real-time progress in the Progress Monitor
- See the generated code and execution results as they happen

### 5. View Results

- The final answer appears when the analysis completes
- View the generated Python code with syntax highlighting
- Check execution output, errors, and tracebacks
- Copy the answer or code to clipboard

## State Management

The app uses Zustand for state management with the following key state:

- **Connection State**: WebSocket connection status
- **Query State**: Current query, data files, and configuration
- **Execution State**: Current iteration, steps, code, and results
- **History**: Past executions for reference

## WebSocket API

The frontend communicates with the backend via WebSocket at `ws://localhost:8000/ws/query`.

**Client Messages:**
```javascript
// Start execution
{
  "action": "start",
  "query": "Your query here",
  "data_files": ["/path/to/file.csv"],
  "config": {
    "max_iterations": 20,
    "max_debug_attempts": 3,
    ...
  }
}

// Cancel execution
{
  "action": "cancel"
}
```

**Server Messages:**
```javascript
// Execution started
{
  "type": "start",
  "session_id": "uuid",
  "message": "Query execution started"
}

// Progress update
{
  "type": "progress",
  "state": { /* DSStarState object */ },
  "iteration": 1
}

// Execution complete
{
  "type": "complete",
  "state": { /* Final DSStarState */ },
  "final_answer": "The answer..."
}

// Error occurred
{
  "type": "error",
  "message": "Error description"
}
```

## Styling

The app uses Tailwind CSS with a custom configuration:

- **Primary Color**: Blue (customizable in `tailwind.config.js`)
- **Custom Components**: Cards, buttons, badges, inputs defined in `index.css`
- **Status Colors**:
  - Pending: Gray
  - Executing: Yellow
  - Completed: Green
  - Failed: Red
  - Backtracked: Orange

## Development Tips

### Hot Module Replacement

Vite provides instant HMR. Changes to React components update immediately without full page reload.

### Proxy Configuration

The Vite dev server proxies API requests to the backend:

- `/api/*` → `http://localhost:8000/api/*`
- `/ws/*` → `ws://localhost:8000/ws/*`

### Adding New Components

1. Create component in `src/components/`
2. Import and use in `Dashboard.jsx` or other parent components
3. Access global state via `useAgentStore()` hook

### Updating State

```javascript
import useAgentStore from '../store/useAgentStore'

function MyComponent() {
  const { query, setQuery } = useAgentStore()

  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
    />
  )
}
```

## Troubleshooting

### WebSocket Connection Failed

- Ensure the backend server is running on `localhost:8000`
- Check backend logs for errors
- Verify CORS settings in backend allow `localhost:3000`

### Files Not Uploading

- Check backend `/api/upload` endpoint is accessible
- Verify file size and type are supported
- Check browser console for error messages

### Styles Not Applying

- Run `npm install` to ensure all dependencies are installed
- Check that Tailwind classes are being processed by PostCSS
- Clear browser cache and restart dev server

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation in `/docs`
- Review the backend API documentation
