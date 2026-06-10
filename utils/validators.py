from typing import List
from urllib.parse import urlparse


def _valid_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_startup_inputs(startup_name: str, website: str, description: str) -> List[str]:
    errors: List[str] = []

    if not startup_name or not startup_name.strip():
        errors.append("Startup name is required.")
    elif len(startup_name.strip()) < 2:
        errors.append("Startup name must be at least 2 characters.")

    if not website or not website.strip():
        errors.append("Website URL is required.")
    elif not _valid_url(website):
        errors.append("Website URL must start with http:// or https:// and include a valid domain.")

    if not description or not description.strip():
        errors.append("Startup description is required.")
    elif len(description.strip()) < 40:
        errors.append("Startup description must be at least 40 characters for meaningful analysis.")

    return errors
