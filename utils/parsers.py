import json
import re
from typing import Any, Dict, List


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
    return cleaned.strip()


def parse_analysis_response(response_text: str) -> Dict[str, Any]:
    cleaned = _strip_code_fences(response_text)
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    return {"executive_summary": cleaned}


def normalize_analysis(parsed: Dict[str, Any]) -> Dict[str, Any]:
    def as_list(value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    return {
        "one_sentence_summary": str(parsed.get("one_sentence_summary", "")).strip(),
        "executive_summary": str(parsed.get("executive_summary", "")).strip(),
        "market_opportunity": str(parsed.get("market_opportunity", "")).strip(),
        "competitive_landscape": str(parsed.get("competitive_landscape", "")).strip(),
        "competitive_advantages": as_list(parsed.get("competitive_advantages")),
        "strengths": as_list(parsed.get("strengths")),
        "weaknesses": as_list(parsed.get("weaknesses")),
        "risks": as_list(parsed.get("risks")),
        "opportunities": as_list(parsed.get("opportunities")),
    }
