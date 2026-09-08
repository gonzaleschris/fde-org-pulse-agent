import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
DB_PATH = BASE_DIR / "data" / "fde_pulse_memory.db"

# Agent & Target Chat Group Info
TARGET_CHAT_GROUP = "AI GTM Tech - All Team"
ORG_NAME = "Forward Deployed Engineering (FDE)"

# Model Routing Configuration
ROUTING_MODELS = {
    "fast_worker": "gemini-2.0-flash",       # High-speed tool calling, classification, PII redaction
    "synthesis_lead": "gemini-2.0-pro-exp",   # Deep reasoning, multi-agent orchestration, executive briefs
    "fallback": "gemini-1.5-flash"
}

# Context Window & Compaction Thresholds
MAX_HISTORY_TOKENS = 8000
COMPACTED_SUMMARY_TARGET = 1000

# Secret Manager & GCP Configuration
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "fde-ai-agent-platform")
SECRET_NAME_GEMINI_KEY = os.getenv("SECRET_NAME_GEMINI_KEY", "gemini-api-key")
SECRET_NAME_CHAT_WEBHOOK = os.getenv("SECRET_NAME_CHAT_WEBHOOK", "google-chat-webhook-url")
