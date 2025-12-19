# DS-STAR Quick Start Guide

Get the DS-STAR frontend up and running in 5 minutes!

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed
- OpenAI API key

## Setup (One-Time)

```bash
# 1. Run the automated setup script
./setup_frontend.sh

# 2. Set your OpenAI API key
export OPENAI_API_KEY="sk-your-openai-api-key-here"
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

## Stopping the Application

Press `Ctrl+C` in both terminal windows to stop the servers.

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

## Manual Setup (Alternative)

If the automated script doesn't work:

### Backend
```bash
cd backend
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key"
python server.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
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

## Key Features

✅ **Real-time Progress**: Watch analysis steps as they happen
✅ **File Upload**: Drag-and-drop your data files
✅ **Code Viewer**: See the generated Python code
✅ **Results Display**: Get formatted answers
✅ **Configuration**: Adjust agent settings

## Next Steps

- Read [FRONTEND_OVERVIEW.md](FRONTEND_OVERVIEW.md) for detailed architecture
- Read [README_FRONTEND.md](README_FRONTEND.md) for complete setup guide
- Read [frontend/README.md](frontend/README.md) for frontend documentation

## Getting Help

- Check the browser console (F12) for errors
- Check backend terminal for error messages
- Review the detailed documentation files
- Ensure all prerequisites are installed

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

## Success Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Green "Connected to server" indicator visible
- [ ] Files upload successfully
- [ ] Query executes and shows progress
- [ ] Final answer appears

That's it! You're ready to analyze data with DS-STAR! 🚀
