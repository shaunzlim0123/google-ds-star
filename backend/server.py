"""
FastAPI server for DS-STAR agent frontend.
Provides REST API and WebSocket endpoints for real-time communication.
"""
import asyncio
import json
import os
import shutil
import tempfile
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ds_star.config import DSStarConfig
from ds_star.core.session import DSStarSession
from ds_star.core.types import DSStarState
from ds_star.providers.openai_provider import OpenAIProvider


# Configuration
# Upload directory will be set during app startup
UPLOAD_DIR: Path = None

# Store active sessions
active_sessions = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global UPLOAD_DIR

    # Startup - create temp directory for uploads
    temp_dir = tempfile.mkdtemp(prefix="ds_star_uploads_")
    UPLOAD_DIR = Path(temp_dir)
    print(f"Starting DS-STAR backend server...")
    print(f"Uploads directory: {UPLOAD_DIR}")

    yield

    # Shutdown - clean up temp directory
    print("Shutting down DS-STAR backend server...")
    if UPLOAD_DIR and UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
        print(f"Cleaned up uploads directory: {UPLOAD_DIR}")


app = FastAPI(
    title="DS-STAR API",
    description="API for DS-STAR Data Science Agent",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    data_files: list[str]
    config: Optional[dict] = None


class ConfigRequest(BaseModel):
    max_iterations: int = 20
    max_debug_attempts: int = 3
    execution_timeout_seconds: float = 60.0
    temperature: float = 0.0
    max_tokens: int = 4096


class SessionResponse(BaseModel):
    session_id: str
    status: str


class FileInfo(BaseModel):
    filename: str
    path: str
    size: int


# Helper Functions
def state_to_dict(state: DSStarState) -> dict:
    """Convert DSStarState to JSON-serializable dict."""
    return {
        "query": state.query,
        "data_files": state.data_files,
        "file_descriptions": [
            {
                "path": fd.path,
                "file_type": fd.file_type,
                "description": fd.description,
                "schema": fd.schema,
                "sample_data": fd.sample_data,
                "row_count": fd.row_count,
                "size_bytes": fd.size_bytes
            } for fd in state.file_descriptions
        ] if state.file_descriptions else [],
        "steps": [
            {
                "index": step.index,
                "description": step.description,
                "status": step.status.name,
                "created_at": step.created_at.isoformat() if step.created_at else None
            } for step in state.steps
        ],
        "current_code": state.current_code.code if state.current_code else None,
        "execution_results": [
            {
                "success": result.success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error_traceback": result.error_traceback,
                "execution_time_ms": result.execution_time_ms
            } for result in state.execution_results
        ] if state.execution_results else [],
        "iteration": state.iteration,
        "is_complete": state.is_complete,
        "final_answer": state.final_answer
    }


# REST Endpoints
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "DS-STAR API",
        "version": "1.0.0"
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a data file for analysis."""
    if UPLOAD_DIR is None:
        raise HTTPException(status_code=503, detail="Server not fully initialized")

    try:
        # Create unique filename
        file_id = str(uuid.uuid4())[:8]
        safe_filename = f"{file_id}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename

        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        return FileInfo(
            filename=file.filename,
            path=str(file_path),
            size=len(content)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@app.get("/api/uploads")
async def list_uploads():
    """List all uploaded files."""
    if UPLOAD_DIR is None:
        raise HTTPException(status_code=503, detail="Server not fully initialized")

    files = []
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file():
            files.append(FileInfo(
                filename=file_path.name,
                path=str(file_path),
                size=file_path.stat().st_size
            ))
    return {"files": files}


@app.delete("/api/uploads/{filename}")
async def delete_upload(filename: str):
    """Delete an uploaded file."""
    if UPLOAD_DIR is None:
        raise HTTPException(status_code=503, detail="Server not fully initialized")

    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    file_path.unlink()
    return {"status": "deleted", "filename": filename}


# WebSocket Endpoint for Real-time Query Execution
@app.websocket("/ws/query")
async def websocket_query(websocket: WebSocket):
    """
    WebSocket endpoint for executing queries with real-time progress updates.

    Client sends:
    {
        "action": "start",
        "query": "What product had made the most money?",
        "data_files": ["/path/to/file.csv"],
        "config": {
            "max_iterations": 20,
            "max_debug_attempts": 3,
            ...
        }
    }

    Server sends:
    {
        "type": "progress",
        "state": {...},
        "iteration": 1
    }
    {
        "type": "complete",
        "state": {...},
        "final_answer": "..."
    }
    {
        "type": "error",
        "message": "..."
    }
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("action") == "start":
                query = message.get("query")
                data_files = message.get("data_files", [])
                config_dict = message.get("config", {})

                if not query or not data_files:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Query and data_files are required"
                    })
                    continue

                # Create configuration
                config = DSStarConfig(
                    max_iterations=config_dict.get("max_iterations", 20),
                    max_debug_attempts=config_dict.get("max_debug_attempts", 3),
                    execution_timeout_seconds=config_dict.get("execution_timeout_seconds", 60.0),
                    temperature=config_dict.get("temperature", 1.0),
                    max_tokens=config_dict.get("max_tokens", 4096),
                )

                # Create LLM provider
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    await websocket.send_json({
                        "type": "error",
                        "message": "OPENAI_API_KEY environment variable not set"
                    })
                    continue

                provider = OpenAIProvider(api_key=api_key)

                # Create session
                session = DSStarSession(provider=provider, config=config)
                active_sessions[session_id] = session

                # Progress callback
                async def on_step(state: DSStarState):
                    await websocket.send_json({
                        "type": "progress",
                        "state": state_to_dict(state),
                        "iteration": state.iteration
                    })

                # Send start notification
                await websocket.send_json({
                    "type": "start",
                    "session_id": session_id,
                    "message": "Query execution started"
                })

                # Run the query
                try:
                    final_state = await session.run_with_state(
                        query=query,
                        data_files=data_files,
                        on_step=on_step
                    )

                    # Send completion
                    await websocket.send_json({
                        "type": "complete",
                        "state": state_to_dict(final_state),
                        "final_answer": final_state.final_answer
                    })

                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Execution failed: {str(e)}",
                        "error_type": type(e).__name__
                    })

                finally:
                    # Clean up session
                    if session_id in active_sessions:
                        del active_sessions[session_id]

            elif message.get("action") == "cancel":
                # TODO: Implement cancellation logic
                await websocket.send_json({
                    "type": "cancelled",
                    "message": "Query execution cancelled"
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown action: {message.get('action')}"
                })

    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {session_id}")
        if session_id in active_sessions:
            del active_sessions[session_id]
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
