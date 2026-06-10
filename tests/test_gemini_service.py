import unittest

from services.gemini_service import GeminiAuthError, GeminiResponseError, GeminiService


class _FakeResponse:
    def __init__(self, text):
        self.text = text


class _FakeModels:
    def __init__(self, should_raise=False, text="analysis"):
        self.should_raise = should_raise
        self.text = text

    def generate_content(self, model, contents):
        if self.should_raise:
            raise RuntimeError("401 UNAUTHENTICATED ACCESS_TOKEN_TYPE_UNSUPPORTED")
        return _FakeResponse(self.text)


class _FakeClient:
    def __init__(self, should_raise=False, text="analysis"):
        self.models = _FakeModels(should_raise=should_raise, text=text)


class GeminiServiceTests(unittest.TestCase):
    def test_auth_error_mapped(self):
        service = GeminiService(
            api_key="AIza12345678901234567890",
            client=_FakeClient(should_raise=True),
        )
        with self.assertRaises(GeminiAuthError):
            service.analyze_startup("Acme", "https://acme.com", "An AI startup" * 5)

    def test_empty_response_rejected(self):
        service = GeminiService(
            api_key="AIza12345678901234567890",
            client=_FakeClient(text=" "),
        )
        with self.assertRaises(GeminiResponseError):
            service.analyze_startup("Acme", "https://acme.com", "An AI startup" * 5)

    def test_scoring_returns_expected_keys(self):
        service = GeminiService(
            api_key="AIza12345678901234567890",
            client=_FakeClient(text="ok"),
        )
        scores = service.score_startup(
            "Founder team building enterprise AI platform with recurring revenue"
        )
        self.assertEqual(
            set(scores.keys()),
            {
                "team_score",
                "market_score",
                "product_score",
                "moat_score",
                "venture_potential_score",
            },
        )
        for value in scores.values():
            self.assertGreaterEqual(value, 3)
            self.assertLessEqual(value, 10)

    def test_investor_matching_fallback_when_no_keywords(self):
        service = GeminiService(
            api_key="AIza12345678901234567890",
            client=_FakeClient(text="ok"),
        )
        investors = service.match_investors("")
        self.assertEqual(len(investors), 5)

    def test_build_investment_memo_contains_sections(self):
        service = GeminiService(
            api_key="AIza12345678901234567890",
            client=_FakeClient(text="ok"),
        )
        memo = service.build_investment_memo(
            startup_name="Acme",
            website="https://acme.com",
            analysis="Strong traction.",
            scores={
                "team_score": 7,
                "market_score": 8,
                "product_score": 7,
                "moat_score": 6,
                "venture_potential_score": 8,
            },
            investors=[{"name": "Accel", "focus": ["saas"], "stage": "Seed-Series B"}],
        )
        self.assertIn("## Startup", memo)
        self.assertIn("## Startup Scoring", memo)
        self.assertIn("## Recommended Investors", memo)


if __name__ == "__main__":
    unittest.main()
