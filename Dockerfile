# ============================================================
# Voicebox — Stateless TTS Server (Backend Only)
# ============================================================

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    gosu \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --no-deps chatterbox-tts
RUN pip install --no-cache-dir --no-deps hume-tada
RUN pip install --no-cache-dir git+https://github.com/QwenLM/Qwen3-TTS.git

# Copy backend application code
COPY backend/ /app/backend/

# Create data directories
RUN mkdir -p /app/data/generations /app/data/profiles /app/data/cache

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=60s \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Start the server
ENV PORT=17493
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port $PORT"]
