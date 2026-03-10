"""
Configuration — edit .env before running
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ─── LLM Choice ───────────────────────────────────────────────────────────
    # "mistral" = your existing Mistral API key (recommended)
    # "ollama"  = runs fully local on your machine, no internet needed
    LLM_MODE = os.getenv("LLM_MODE", "mistral")

    # ─── Mistral API ──────────────────────────────────────────────────────────
    # Your existing key from https://console.mistral.ai
    # Recommended models (pick one):
    #   mistral-small-latest   → cheapest, fast, good enough
    #   mistral-large-latest   → most accurate, costs more
    #   open-mistral-nemo      → free tier friendly
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL   = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

    # ─── Ollama (Local fallback, no internet needed) ──────────────────────────
    # Install: https://ollama.com → run: ollama pull llama3.2
    OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

    # ─── ntfy.sh (Free Phone Notifications) ───────────────────────────────────
    # 1. Install 'ntfy' app on your phone (Android / iPhone)
    # 2. Tap '+' → pick a unique topic name → Subscribe
    # 3. Paste that same topic name below
    NTFY_TOPIC = os.getenv("NTFY_TOPIC", "")

    # ─── YouTube Channel Monitoring ───────────────────────────────────────────
    # Channel ID for @berich467 or any other stock YouTube channel
    # To find channel ID: View page source → search for "channelId"
    YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "")

    # ─── Agent Settings ───────────────────────────────────────────────────────
    CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "720"))  # 12 hours default
