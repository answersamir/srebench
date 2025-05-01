"""Configuration module for loading environment variables and providing defaults."""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file located in the project root (adjust path if needed)
# Assumes .env is in the parent directory of src/
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=dotenv_path)
logger.info("Attempting to load .env file from: %s", dotenv_path)


def get_env_variable(var_name: str, default: Optional[str] = None) -> Optional[str]:
    """Gets an environment variable, logging a warning if not found (unless default is set)."""
    value = os.getenv(var_name)
    if value is None:
        if default is None:
            logger.warning(
                "Environment variable '%s' not found and no default value provided.",
                var_name,
            )
        return default
    return value


# --- Helper Functions for Configuration Values ---


def get_gemini_api_key() -> Optional[str]:
    """Retrieves the Gemini API key from environment variables."""
    return get_env_variable("GEMINI_API_KEY")


def get_llm_model_name() -> str:
    """Retrieves the LLM model name from environment variables, with a default."""
    # Ensure a default is always returned if the env var is missing
    return get_env_variable("LLM_MODEL_NAME", default="gemini-1.5-flash")


def get_llm_temperature() -> float:
    """Retrieves the LLM temperature from environment variables, with a default."""
    temp_str = get_env_variable("LLM_TEMPERATURE", default="0.5")
    try:
        return float(temp_str)
    except (ValueError, TypeError):
        logger.warning(
            "Invalid value '%s' for LLM_TEMPERATURE. Using default 0.5.", temp_str
        )
        return 0.5
