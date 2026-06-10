"""Validation helpers for configuration and user input."""

from __future__ import annotations

from urllib.parse import urlparse

MIN_GEMINI_KEY_LENGTH = 20


def is_valid_gemini_api_key(api_key: str | None) -> bool:
    return bool(
        api_key and api_key.startswith("AIza") and len(api_key) >= MIN_GEMINI_KEY_LENGTH
    )


def is_valid_website_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_startup_inputs(startup_name: str, website: str, description: str) -> list[str]:
    errors: list[str] = []

    if not startup_name.strip():
        errors.append("Startup name is required.")

    if website.strip() and not is_valid_website_url(website.strip()):
        errors.append("Website URL must start with http:// or https://")

    cleaned_description = description.strip()
    if not cleaned_description:
        errors.append("Startup description is required.")
    elif len(cleaned_description) < 20:
        errors.append("Startup description should be at least 20 characters.")

    return errors
