# DS-STAR

**Data Science Agent via Iterative Planning and Verification**

DS-STAR is a Python implementation of the DS-STAR framework from the [research paper](https://arxiv.org/abs/2509.21825) by Google Cloud and KAIST. It's a data science agent that transforms raw data into actionable insights through iterative planning and verification.

## Features

- **Multi-format Data Support**: Automatically analyzes CSV, JSON, Excel, Parquet, Markdown, and text files
- **Iterative Planning**: Generates step-by-step analysis plans that are refined based on execution results
- **LLM-based Verification**: Uses an LLM judge to verify if the plan sufficiently answers the query
- **Self-debugging**: Automatically fixes code errors using traceback information
- **Backtracking**: Can identify and correct wrong steps in the plan
- **Real-time Progress**: Watch analysis steps as they happen
- **Code Viewer**: See the generated Python code

## Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# 1. Run the automated setup script
./setup_frontend.sh

# 2. Set your OpenAI API key
export OPENAI_API_KEY="sk-your-openai-api-key-here"
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key"
python server.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Option 3: Install as Package

```bash
pip install ds-star
```

Or install from source:

```bash
git clone https://github.com/your-repo/ds-star.git
cd ds-star
pip install -e .
```

## Running the Application

### Terminal 1: Start Backend

```bash
./start_backend.sh
```

You should see:
```
Starting DS-STAR Backend Server...
Server will run on http://localhost:8000

INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Start Frontend

```bash
./start_frontend.sh
```

You should see:
```
Starting DS-STAR Frontend...
Frontend will run on http://localhost:3000

  VITE v5.0.11  ready in 523 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### Open in Browser

Navigate to: **http://localhost:3000**

## Using the Application

### 1. Upload Files

- Click the upload area or drag files
- Supported: CSV, JSON, Excel, Parquet, etc.
- Example files: Use `data/transactions.csv` and `data/countries.json`

### 2. Enter Query

Type your question, for example:
```
What product had made the most money for each country?
```

### 3. Execute

- Click **"Execute Query"**
- Watch the real-time progress
- See the final answer when complete

## Example Queries

Try these with the sample data in `data/`:

```
1. What product had made the most money for each country?
2. What is the total revenue by product category?
3. Which country has the highest average transaction amount?
4. Show me the distribution of transactions across countries and products
```

## Programmatic Usage

```python
import asyncio
from ds_star import DSStarSession, OpenAIProvider, DSStarConfig

async def main():
    # Initialize the LLM provider
    provider = OpenAIProvider(
        api_key="sk-...",  # Or set OPENAI_API_KEY env var
        model="gpt-4-turbo-preview"
    )

    # Create a session with optional configuration
    config = DSStarConfig(
        max_iterations=20,
        max_debug_attempts=3,
    )
    session = DSStarSession(provider=provider, config=config)

    # Run DS-STAR on your data science task
    answer = await session.run(
        query="What is the average transaction amount by country?",
        data_files=["./data/transactions.csv", "./data/countries.json"]
    )

    print(f"Answer: {answer}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Architecture

DS-STAR uses a multi-agent architecture with 7 specialized agents:

| Agent | Purpose |
|-------|---------|
| **Analyzer** | Extracts metadata and schema from data files |
| **Planner** | Generates the next step in the analysis plan |
| **Coder** | Implements plan steps as executable Python code |
| **Verifier** | Checks if the current plan sufficiently answers the query |
| **Router** | Decides to add new steps or backtrack to fix errors |
| **Debugger** | Fixes code that failed during execution |
| **Finalizer** | Formats the final output |

### Algorithm

1. **Analyze Files**: Extract metadata from all data files
2. **Generate Initial Step**: Create the first plan step
3. **Iterative Loop** (up to `max_iterations`):
   - Generate code implementing all steps
   - Execute code (with automatic debugging on failure)
   - Verify if result is sufficient
   - If sufficient: return answer
   - If insufficient: route to add step or backtrack
4. **Finalize**: Format and return the final answer

## Configuration

```python
from ds_star import DSStarConfig

config = DSStarConfig(
    # Iteration limits
    max_iterations=20,        # Max planning iterations
    max_debug_attempts=3,     # Max debug attempts per execution

    # Execution settings
    execution_timeout_seconds=60.0,
    max_output_length=10000,

    # LLM settings
    temperature=0.0,
    max_tokens=4096,

    # Output formatting
    output_format="round to 2 decimal places",

    # Logging
    log_level="INFO",
)
```

## Advanced Usage

### Progress Callback

Monitor progress during execution:

```python
async def on_step(state):
    print(f"Iteration {state.iteration}: {len(state.current_plan)} steps")
    if state.last_execution_result:
        print(f"  Success: {state.last_execution_result.success}")

answer = await session.run(
    query="Analyze sales trends",
    data_files=["./sales.csv"],
    on_step=on_step
)
```

### Custom LLM Provider

Implement the `LLMProvider` protocol for other LLMs:

```python
from ds_star.providers.base import LLMProvider, Message, LLMResponse

class CustomProvider(LLMProvider):
    async def complete(
        self,
        messages: list[Message],
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        # Your implementation here
        ...

    async def complete_stream(self, messages, temperature=0.0, max_tokens=4096):
        # Optional streaming implementation
        ...

    async def embed(self, text: str) -> list[float]:
        # Optional embedding implementation
        ...
```

### Accessing Full State

Get complete execution state for debugging:

```python
state = await session.run_with_state(
    query="What patterns exist in the data?",
    data_files=["./data/"]
)

# Inspect all artifacts
print("File Descriptions:", state.file_descriptions)
print("Plan Steps:", state.current_plan)
print("Generated Code:", state.current_code)
print("Execution Results:", state.execution_results)
```

## Project Structure

```
google-ds-star/
├── backend/          # FastAPI server
│   ├── server.py
│   └── requirements.txt
├── frontend/         # React app
│   ├── src/
│   └── package.json
└── data/            # Sample data files
    ├── transactions.csv
    └── countries.json
```

## Supported File Formats

- **Tabular**: CSV, Excel (xlsx, xls), Parquet
- **Structured**: JSON, YAML, XML
- **Text**: Markdown, plain text

## Troubleshooting

### Backend won't start

**Problem**: `OPENAI_API_KEY environment variable not set`

**Solution**:
```bash
export OPENAI_API_KEY="sk-your-key"
```

### Frontend shows "Disconnected"

**Solution**:
1. Make sure backend is running on port 8000
2. Check backend terminal for errors
3. Refresh the browser page

### Port already in use

**Solution**:
```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

## Quick Commands Cheat Sheet

```bash
# Setup (one-time)
./setup_frontend.sh

# Set API key (each session)
export OPENAI_API_KEY="sk-your-key"

# Start backend
./start_backend.sh

# Start frontend (new terminal)
./start_frontend.sh

# Stop servers
Ctrl+C (in each terminal)

# Rebuild frontend
cd frontend && npm run build

# Run linter
cd frontend && npm run lint
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy ds_star

# Linting
ruff check ds_star
```

## Success Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Green "Connected to server" indicator visible
- [ ] Files upload successfully
- [ ] Query executes and shows progress
- [ ] Final answer appears

## Citation

If you use DS-STAR in your research, please cite the original paper:

```bibtex
@article{nam2025dsstar,
  title={DS-STAR: Data Science Agent via Iterative Planning and Verification},
  author={Nam, Jaehyun and Yoon, Jinsung and Chen, Jiefeng and Pfister, Tomas},
  journal={arXiv preprint arXiv:2509.21825},
  year={2025}
}
```

## License

MIT License
