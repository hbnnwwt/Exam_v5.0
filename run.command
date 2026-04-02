#!/bin/bash
# Graduate Interview System - Startup (macOS)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "==================================="
echo "Graduate Interview System - Startup"
echo "==================================="
echo

# Find Python
PYTHON_EXE=""
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"
PYTHON_PORTABLE="$SCRIPT_DIR/python_portable/python3"

if [ -f "$PYTHON_PORTABLE" ]; then
    PYTHON_EXE="$PYTHON_PORTABLE"
elif [ -f "$VENV_PYTHON" ]; then
    PYTHON_EXE="$VENV_PYTHON"
elif command -v python3 &> /dev/null; then
    PYTHON_EXE="python3"
fi

if [ -z "$PYTHON_EXE" ]; then
    echo "[Error] Python not found."
    echo "[Info] Please run setup.command first to create the environment."
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "[Warning] Frontend dependencies not installed"
    echo "[Info] Please run build.command to build the frontend"
    echo
fi

# Check if frontend is built
if [ ! -f "backend/assets/frontend/index.html" ]; then
    echo "[Warning] Frontend not built!"
    echo "[Info] Please run: cd frontend && npm install && npm run build"
    echo "[Info] Starting development server..."
    echo
fi

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR/backend"
export FLASK_ENV=development

PORT=5001

# Start backend server
cd "$SCRIPT_DIR/backend"
echo "[Starting] Flask server..."
echo "[URL] http://localhost:$PORT"
echo

"$PYTHON_EXE" -u app.py $PORT &

# Wait a moment for server to start
sleep 2

# Open browser
open "http://localhost:$PORT"
