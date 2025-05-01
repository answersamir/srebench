"""
This module provides a function to set up the LLM (Language Model) instance
using the Google Gemini API.
"""

import logging
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel
import config

logger = logging.getLogger(__name__)


# --- Configuration Function (Keep this) ---
def setup_llm() -> Optional[BaseChatModel]:
    """Initializes and returns the configured LLM instance."""
    gemini_api_key = config.get_gemini_api_key()
    llm_model_name = config.get_llm_model_name()
    llm_temperature = config.get_llm_temperature()

    if not gemini_api_key:
        logger.error(
            "Google API Key not configured correctly via config.py. Cannot setup LLM."
        )
        return None

    try:
        llm = ChatGoogleGenerativeAI(
            model=llm_model_name,
            temperature=llm_temperature,
            google_api_key=gemini_api_key,
            convert_system_message_to_human=True,
        )
        logger.info(
            "LLM instance created: Google Gemini (%s)", llm.model
        )  # Log instance creation
        return llm
    except Exception as e:
        logger.error("Failed to instantiate LLM in llm_provider: %s", e, exc_info=True)
        return None
