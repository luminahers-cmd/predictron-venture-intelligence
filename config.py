import os
from dataclasses import dataclass
from typing import Optional, Tuple

import streamlit as st


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class AppConfig:
    api_key: str
    model: str = "gemini-2.5-flash"


def _secret_value(key: str) -> Optional[str]:
    try:
        value = st.secrets.get(key)
        if isinstance(value, str):
            return value.strip()
    except Exception:
        return None
    return None


def load_api_key_with_source() -> Tuple[Optional[str], str]:
    secret_key = _secret_value("GEMINI_API_KEY")
    if secret_key:
        return secret_key, "streamlit_secrets"

    env_key = (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()
    if env_key:
        return env_key, "environment"

    return None, "missing"


def get_config() -> AppConfig:
    api_key, _ = load_api_key_with_source()
    if not api_key:
        raise ConfigError(
            "Gemini API key is not configured. Add GEMINI_API_KEY in Streamlit secrets "
            "or set GOOGLE_API_KEY in environment variables."
        )
    return AppConfig(api_key=api_key)


def api_key_diagnostic(api_key: str) -> Optional[str]:
    if not api_key:
        return "API key is empty."
    if not api_key.startswith("AIza"):
        return (
            "API key format looks unusual. Gemini API keys from Google AI Studio usually "
            "start with 'AIza'."
        )
    return None
