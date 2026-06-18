"""
Global configuration for Personal Thinker.
All paths and settings in one place.
Reads from config/user_config.yaml.
"""
from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

load_dotenv()

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent.resolve()
CONFIG_DIR = BASE_DIR / "config"
MEMORY_DIR = BASE_DIR / "memory"
USER_DATA_DIR = MEMORY_DIR / "user_data"
GLOBAL_DATA_DIR = USER_DATA_DIR / "_global"
TEMPLATES_DIR = MEMORY_DIR / "templates"
PROMPTS_DIR = BASE_DIR / "prompts"

# ─── User Config (YAML) ──────────────────────────────────────────────────────
USER_CONFIG_PATH = CONFIG_DIR / "user_config.yaml"

def load_user_config() -> dict:
    """Load configuration from YAML."""
    if USER_CONFIG_PATH.exists():
        with open(USER_CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

USER_CONFIG = load_user_config()

# ─── Onboarding config ────────────────────────────────────────────────────────
FIRE_OPTIONS = USER_CONFIG.get("onboarding", {}).get("fire_options", [
    "calm", "impulsiv", "analitic", "emotiv", "rezervat",
    "direct", "optimist", "pesimist", "adaptiv", "rigid"
])
MAX_FOLLOW_UP = USER_CONFIG.get("onboarding", {}).get("max_follow_up", 3)

# ─── Folder config ─────────────────────────────────────────────────────────────
DEFAULT_FOLDERS = USER_CONFIG.get("folders", {}).get("default", [
    "Muncă", "Familie", "Relații"
])

# ─── LLM Config ──────────────────────────────────────────────────────────────
LLM_CONFIG = {
    "base_url": os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1"),
    "api_key": os.getenv("MINIMAX_API_KEY", ""),
    "model": "MiniMax-M2.7",
    "temperature": 0.3,
    "max_tokens": 4000,
}

# ─── Agent Config ─────────────────────────────────────────────────────────────
AGENT_CONFIG = {
    "min_data_points_for_discovery": 3,
    "discovery_confidence_threshold": 0.75,
    "max_context_messages": 20,
}

# ─── Special folders ───────────────────────────────────────────────────────────
GLOBAL_FOLDER_NAME = "_global"
