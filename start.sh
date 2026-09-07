#!/bin/bash
set -e

# Change directory to project root
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo "🛑 Stopping existing processes on port 8000..."
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
pkill -f "telecom-ai-bot/main.py" 2>/dev/null || true
pkill -f "voiceconnect-ai" 2>/dev/null || true
sleep 1

export PYTHONUNBUFFERED=1

echo "🧠 Checking Ollama status..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Starting Ollama in the background..."
    ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
else
    echo "✅ Ollama is already running."
fi

echo "🤖 Starting TeleBot API..."
export PYTHONPATH="$PROJECT_ROOT/TTS:$PROJECT_ROOT/telecom-ai-bot:$PYTHONPATH"

# Detect Python in tts-env
if [ -f "/opt/homebrew/Caskroom/miniconda/base/envs/tts-env/bin/python" ]; then
    PYTHON_BIN="/opt/homebrew/Caskroom/miniconda/base/envs/tts-env/bin/python"
elif command -v conda >/dev/null 2>&1; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate tts-env
    PYTHON_BIN="python"
else
    PYTHON_BIN="python3"
fi

echo "Using Python: $PYTHON_BIN"
exec "$PYTHON_BIN" telecom-ai-bot/main.py

