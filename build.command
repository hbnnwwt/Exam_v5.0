#!/bin/bash
# Graduate Interview System - Build Frontend (macOS)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "==================================="
echo "Graduate Interview System - Build"
echo "==================================="
echo

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "[Info] Node.js not found."
    echo "[Installing] Node.js LTS via Homebrew..."

    if ! command -v brew &> /dev/null; then
        echo "[Error] Homebrew not found. Please install Node.js from https://nodejs.org/"
        read -p "Press Enter to exit..."
        exit 1
    fi

    brew install node
    if [ $? -ne 0 ]; then
        echo "[Error] Failed to install Node.js."
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

NODE_EXE=$(command -v node)
NPM_EXE=$(command -v npm)

echo "[Info] Node.js found: $NODE_EXE"
node --version
echo

cd "$SCRIPT_DIR/frontend"

# Check node_modules
if [ ! -d "node_modules" ]; then
    echo "[Step 1] Installing frontend dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "[Error] Failed to install dependencies"
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo
fi

echo "[Step 2] Building frontend..."
npm run build
if [ $? -ne 0 ]; then
    echo "[Error] Build failed"
    read -p "Press Enter to exit..."
    exit 1
fi

echo
echo "==================================="
echo "[Success] Build completed!"
echo "[Output] backend/assets/frontend/"
echo "==================================="
echo
echo "Now you can run run.command to start the system"
read -p "Press Enter to exit..."
