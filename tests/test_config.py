import unittest

from config import get_api_key_status, resolve_api_key


class ConfigTests(unittest.TestCase):
    def test_resolve_api_key_prefers_streamlit_secret(self):
        key, source = resolve_api_key(
            secrets={"GEMINI_API_KEY": "AIzaSecretFromStreamlit"},
            environ={"GOOGLE_API_KEY": "AIzaFromEnv"},
        )
        self.assertEqual(key, "AIzaSecretFromStreamlit")
        self.assertEqual(source, "streamlit_secrets")

    def test_get_api_key_status_invalid_format(self):
        status = get_api_key_status(secrets={"GEMINI_API_KEY": "AQ.invalid"})
        self.assertTrue(status["is_configured"])
        self.assertFalse(status["is_valid"])
        self.assertIn("invalid", status["message"].lower())


if __name__ == "__main__":
    unittest.main()
