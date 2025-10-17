#!/bin/bash
# Railway Start Script - Handles PORT environment variable
PORT=${PORT:-8000}
echo "🚀 Starting server on port $PORT..."
exec uvicorn production_langgraph_orchestrator:app --host 0.0.0.0 --port "$PORT"
