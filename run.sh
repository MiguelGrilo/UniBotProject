#!/bin/bash

#!/bin/bash

# Root path
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# Activate Virtual Environment
if [ -d "aiEngine/unibot-venv" ]; then
    source aiEngine/unibot-venv/bin/activate
    echo "Virtual Environment ready."
else
    echo "Virtual Environment not found."
    exit 1
fi

# Backend
cd aiEngine
uvicorn main:app --port 8000 --reload &
BACKEND_PID=$!

# Frontend
streamlit run gui.py --server.port 8501 &
STREAMLIT_PID=$!

# Kill function after Ctrl+C
trap "kill $BACKEND_PID $STREAMLIT_PID" SIGINT

echo "FastAPI: http://localhost:8000"
echo "Streamlit: http://localhost:8501"

# Keeps the script running so it doesn't close the background processes until the kill function activates
wait