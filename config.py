"""Application configuration and secrets handling."""

from __future__ import annotations

import os
from typing import Any, Mapping, Optional, Tuple

from utils.validators import is_valid_gemini_api_key


API_KEY_NAME = "GEMINI_API_KEY"
API_KEY_ENV_FALLBACK = "GOOGLE_API_KEY"


def _read_secret(secrets: Optional[Mapping[str, Any]], key: str) -> Optional[str]:
    if secrets is None:
        return None

    value: Any = None
    try:
        value = secrets.get(key)
    except AttributeError:
        try:
            value = secrets[key]
        except (KeyError, TypeError):
            value = None

    if isinstance(value, str):
        value = value.strip()
    return value or None


def mask_api_key(api_key: Optional[str]) -> str:
    """Mask an API key so logs never expose the full value."""
    if not api_key:
        return "not-set"
    if len(api_key) <= 8:
        return "****"
    return f"{api_key[:4]}...{api_key[-4:]}"


def resolve_api_key(
    secrets: Optional[Mapping[str, Any]] = None,
    environ: Optional[Mapping[str, str]] = None,
) -> Tuple[Optional[str], str]:
    """Resolve key from Streamlit secrets first, then env fallback."""
    secret_value = _read_secret(secrets, API_KEY_NAME)
    if secret_value:
        return secret_value, "streamlit_secrets"

    env_source = environ or os.environ
    env_value = (env_source.get(API_KEY_ENV_FALLBACK) or "").strip()
    if env_value:
        return env_value, "environment"

    return None, "none"


def get_api_key_status(
    secrets: Optional[Mapping[str, Any]] = None,
    environ: Optional[Mapping[str, str]] = None,
) -> dict[str, Any]:
    api_key, source = resolve_api_key(secrets=secrets, environ=environ)
    masked_key = mask_api_key(api_key)

    if not api_key:
        return {
            "api_key": None,
            "masked_key": masked_key,
            "source": source,
            "is_configured": False,
            "is_valid": False,
            "message": (
                "Gemini API key is missing. Configure GEMINI_API_KEY in Streamlit "
                "secrets or GOOGLE_API_KEY as an environment variable."
            ),
        }

    if not is_valid_gemini_api_key(api_key):
        return {
            "api_key": api_key,
            "masked_key": masked_key,
            "source": source,
            "is_configured": True,
            "is_valid": False,
            "message": (
                "Gemini API key format is invalid. Expected a Google AI Studio key "
                "starting with 'AIza'."
            ),
        }

    return {
        "api_key": api_key,
        "masked_key": masked_key,
        "source": source,
        "is_configured": True,
        "is_valid": True,
        "message": "Gemini API key loaded successfully.",
    }
