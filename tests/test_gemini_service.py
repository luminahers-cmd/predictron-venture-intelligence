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


if __name__ == "__main__":
    unittest.main()
