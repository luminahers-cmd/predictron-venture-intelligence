"""Gemini service wrapper with robust error handling."""

from __future__ import annotations

import logging
from typing import Any

from google import genai

from utils.validators import is_valid_gemini_api_key

logger = logging.getLogger(__name__)


class GeminiServiceError(RuntimeError):
    """Base error for Gemini service failures."""


class GeminiConfigurationError(GeminiServiceError):
    """Raised when API key configuration is invalid."""


class GeminiAuthError(GeminiServiceError):
    """Raised when Gemini authentication fails."""


class GeminiResponseError(GeminiServiceError):
    """Raised when Gemini returns malformed or empty output."""


class GeminiService:
    MODEL = "gemini-2.5-flash"
    MIN_SCORE = 3
    BASE_SCORE = 4

    def __init__(self, api_key: str, client: Any | None = None) -> None:
        if not api_key:
            raise GeminiConfigurationError("Gemini API key is missing.")
        if not is_valid_gemini_api_key(api_key):
            raise GeminiConfigurationError(
                "Gemini API key must start with 'AIza'. "
                "Generate a new API key in Google AI Studio."
            )

        self.client = client or genai.Client(api_key=api_key)

    def analyze_startup(self, startup_name: str, website: str, description: str) -> str:
        prompt = self._build_analysis_prompt(startup_name, website, description)

        logger.info("Gemini analyze_startup request sent for '%s'", startup_name)
        try:
            response = self.client.models.generate_content(
                model=self.MODEL,
                contents=prompt,
            )
        except Exception as exc:
            logger.exception("Gemini generate_content failed")
            raise self._map_exception(exc) from exc

        text = getattr(response, "text", None)
        if not text or not text.strip():
            raise GeminiResponseError(
                "Gemini returned an empty response. Please retry the analysis."
            )

        return text.strip()

    def score_startup(self, description: str) -> dict[str, int]:
        lowered = description.lower()

        scoring_keywords = {
            "team_score": ["founder", "team", "experience", "operator", "expert"],
            "market_score": ["market", "tam", "growth", "demand", "industry"],
            "product_score": ["product", "platform", "technology", "solution", "features"],
            "moat_score": ["moat", "data", "network effects", "patent", "defensible"],
            "venture_potential_score": ["scale", "global", "recurring", "revenue", "enterprise"],
        }

        scores: dict[str, int] = {}
        for metric, keywords in scoring_keywords.items():
            hits = sum(1 for keyword in keywords if keyword in lowered)
            # Keyword hits add confidence above a conservative baseline (BASE_SCORE),
            # while MIN_SCORE prevents very sparse descriptions from collapsing to zero.
            scores[metric] = min(
                10, max(self.MIN_SCORE, self.BASE_SCORE + hits)
            )

        return scores

    def match_investors(self, description: str) -> list[dict[str, str]]:
        lowered = description.lower()

        investor_profiles = [
            {"name": "Sequoia Capital", "focus": ["enterprise", "ai", "saas"], "stage": "Series A-C"},
            {"name": "Andreessen Horowitz", "focus": ["ai", "consumer", "infrastructure"], "stage": "Seed-Growth"},
            {"name": "Accel", "focus": ["saas", "fintech", "marketplace"], "stage": "Seed-Series B"},
            {"name": "Lightspeed Venture Partners", "focus": ["enterprise", "cybersecurity", "ai"], "stage": "Seed-Series C"},
            {"name": "Tiger Global", "focus": ["growth", "fintech", "internet"], "stage": "Growth"},
            {"name": "General Catalyst", "focus": ["healthcare", "fintech", "ai"], "stage": "Seed-Growth"},
            {"name": "Bessemer Venture Partners", "focus": ["cloud", "developer tools", "saas"], "stage": "Series A-C"},
            {"name": "Y Combinator", "focus": ["b2b", "consumer", "deep tech"], "stage": "Pre-seed/Seed"},
        ]

        ranked: list[tuple[int, dict[str, str]]] = []
        for investor in investor_profiles:
            score = sum(1 for keyword in investor["focus"] if keyword in lowered)
            ranked.append((score, investor))

        ranked.sort(key=lambda item: item[0], reverse=True)
        selected = [investor for score, investor in ranked if score > 0][:5]

        if selected:
            return selected

        return investor_profiles[:5]

    def build_investment_memo(
        self,
        startup_name: str,
        website: str,
        analysis: str,
        scores: dict[str, int],
        investors: list[dict[str, str]],
    ) -> str:
        scores_text = "\n".join(
            [
                f"- Team Score: {scores['team_score']}/10",
                f"- Market Score: {scores['market_score']}/10",
                f"- Product Score: {scores['product_score']}/10",
                f"- Moat Score: {scores['moat_score']}/10",
                f"- Venture Potential Score: {scores['venture_potential_score']}/10",
            ]
        )

        investor_lines = "\n".join(
            [f"- {item['name']} ({item['stage']})" for item in investors]
        )

        return f"""# Predictron Investment Memo

## Startup
- Name: {startup_name}
- Website: {website or 'N/A'}

## Startup Scoring
{scores_text}

## Recommended Investors
{investor_lines}

## AI Analysis
{analysis}
"""

    @staticmethod
    def _build_analysis_prompt(startup_name: str, website: str, description: str) -> str:
        return f"""
You are an expert venture investor preparing a crisp investment memo.

Startup Name:
{startup_name}

Website:
{website or 'N/A'}

Startup Description:
{description}

Provide the response in markdown with these exact sections:
1. One-sentence summary
2. Market opportunity
3. Competitive advantages
4. Key risks
5. Venture-scale score (1-10 with one-line justification)
6. Suggested investors (5 names with short rationale)
7. Investment memo (3-6 concise paragraphs)
""".strip()

    @staticmethod
    def _map_exception(exc: Exception) -> GeminiServiceError:
        details = str(exc)
        normalized = details.upper()

        if (
            "UNAUTHENTICATED" in normalized
            or "ACCESS_TOKEN_TYPE_UNSUPPORTED" in normalized
            or "401" in normalized
        ):
            return GeminiAuthError(
                "Gemini authentication failed. Confirm you are using a Google AI Studio "
                "API key that starts with 'AIza'."
            )

        if "429" in normalized or "QUOTA" in normalized or "RATE" in normalized:
            return GeminiServiceError(
                "Gemini quota or rate limit reached. Please wait and retry."
            )

        if (
            "TIMEOUT" in normalized
            or "CONNECTION" in normalized
            or "NETWORK" in normalized
            or "503" in normalized
        ):
            return GeminiServiceError(
                "Network/service issue while contacting Gemini. Please retry shortly."
            )

        return GeminiServiceError(
            "Gemini request failed unexpectedly. Please retry or verify configuration."
        )
