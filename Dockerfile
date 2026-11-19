FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies for common Telegram/media features (ffmpeg, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    ca-certificates \
    build-essential \
    libffi-dev \
    libssl-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY . /app

# Runtime data directories
RUN mkdir -p /app/downloads /app/temp

# Default command (can be overridden by platform configs)
CMD ["python3", "-m", "JoKeRUB"]
