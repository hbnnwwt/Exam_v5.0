#!/bin/bash
# Graduate Interview System - Python Environment Setup (macOS)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Python Environment Setup (macOS)"
echo "========================================"
echo

PYTHON_DIR="$SCRIPT_DIR/python_portable"
PYTHON_EXE="$PYTHON_DIR/python3"
VENV_DIR="$SCRIPT_DIR/venv"
VENV_PYTHON="$VENV_DIR/bin/python3"
USE_PORTABLE=0

# Check if portable Python already exists
if [ -f "$PYTHON_EXE" ]; then
    echo "[Info] Portable Python found."
    USE_PORTABLE=1
    PYTHON_TO_USE="$PYTHON_EXE"
    goto install_deps
fi

# Check if system Python is available
if command -v python3 &> /dev/null; then
    echo "[Info] System Python found:"
    python3 --version
    echo

    # Check if venv already exists
    if [ -f "$VENV_PYTHON" ]; then
        echo "[Info] Virtual environment already exists."
        PYTHON_TO_USE="$VENV_PYTHON"
    else
        # Create virtual environment
        echo "[Creating] Virtual environment..."
        python3 -m venv "$VENV_DIR"
        if [ $? -ne 0 ]; then
            echo "[Error] Failed to create virtual environment."
            read -p "Press Enter to exit..."
            exit 1
        fi
        PYTHON_TO_USE="$VENV_PYTHON"
    fi
else
    # No Python found - try to install via Homebrew
    echo "[Info] Python not found on this system."

    if command -v brew &> /dev/null; then
        echo "[Installing] Python 3 via Homebrew..."
        brew install python@3.12
        if [ $? -ne 0 ]; then
            echo "[Error] Failed to install Python via Homebrew."
            read -p "Press Enter to exit..."
            exit 1
        fi
        PYTHON_TO_USE="$(brew --prefix)/opt/python@3.12/bin/python3"
    else
        echo "[Error] Homebrew not found. Please install Python manually from https://www.python.org/downloads/"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

:install_deps
echo "[Installing] Dependencies..."

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR/backend"

# Upgrade pip and install dependencies
"$PYTHON_TO_USE" -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
if [ $? -ne 0 ]; then
    echo "[Error] Failed to upgrade pip."
    read -p "Press Enter to exit..."
    exit 1
fi

"$PYTHON_TO_USE" -m pip install -r "$SCRIPT_DIR/backend/requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
if [ $? -ne 0 ]; then
    echo "[Error] Failed to install dependencies."
    read -p "Press Enter to exit..."
    exit 1
fi

echo "[Creating] directories..."
mkdir -p "$SCRIPT_DIR/backend/assets/data"
mkdir -p "$SCRIPT_DIR/backend/assets/images"
mkdir -p "$SCRIPT_DIR/backend/assets/logos"
mkdir -p "$SCRIPT_DIR/backend/assets/uploads"
mkdir -p "$SCRIPT_DIR/backend/logs"

echo "[Initializing] database..."
"$PYTHON_TO_USE" "$SCRIPT_DIR/backend/init_db.py"
if [ $? -ne 0 ]; then
    echo "[Error] Database initialization failed."
    read -p "Press Enter to exit..."
    exit 1
fi

echo
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo
echo "Next steps:"
echo "  Double-click build.command  - Build frontend"
echo "  Double-click run.command    - Start the system"
echo

read -p "Press Enter to exit..."
