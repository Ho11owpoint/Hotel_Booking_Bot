#!/usr/bin/env bash
# Aurora Grand Hotel — Booking Chatbot launcher (macOS / Linux)

set -e
cd "$(dirname "$0")"

echo
echo "  Aurora Grand Hotel -- Booking Chatbot"
echo "  --------------------------------------"
echo

# 1. Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] python3 not found. Install Python 3.10+ first."
    exit 1
fi

# 2. Virtual env
if [ ! -f ".venv/bin/python" ]; then
    echo "[SETUP] Creating virtual environment in .venv ..."
    python3 -m venv .venv
fi

# 3. Dependencies
if ! .venv/bin/python -c "import flask" >/dev/null 2>&1; then
    echo "[SETUP] Installing dependencies ..."
    .venv/bin/python -m pip install --upgrade pip >/dev/null
    .venv/bin/python -m pip install -r requirements.txt
fi

# 4. Open the browser after a brief delay (background)
(
    sleep 2
    if command -v open >/dev/null 2>&1; then open http://127.0.0.1:5000
    elif command -v xdg-open >/dev/null 2>&1; then xdg-open http://127.0.0.1:5000
    fi
) &

# 5. Start Flask (Ctrl+C to quit)
echo
echo "  Starting server at http://127.0.0.1:5000"
echo "  Press Ctrl+C to stop."
echo
cd src
exec ../.venv/bin/python app.py
