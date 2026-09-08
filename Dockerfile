# Production Dockerfile for FDE Org Pulse Agent
FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files & enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install -e .

RUN useradd -m fdeuser && chown -R fdeuser:fdeuser /app
USER fdeuser

ENTRYPOINT ["python", "-m", "fde_pulse.agent"]
CMD ["--input", "data/sample_chat_messages.json", "--week", "2026-W36", "--format", "all", "--export-telemetry"]
