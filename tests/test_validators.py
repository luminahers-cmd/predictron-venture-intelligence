import unittest

from utils.validators import is_valid_gemini_api_key, validate_startup_inputs


class ValidatorTests(unittest.TestCase):
    def test_valid_gemini_api_key_prefix(self):
        self.assertTrue(is_valid_gemini_api_key("AIza12345678901234567890"))
        self.assertFalse(is_valid_gemini_api_key("AQ.12345"))

    def test_startup_inputs_validation(self):
        errors = validate_startup_inputs("", "not-a-url", "short")
        self.assertGreaterEqual(len(errors), 2)


if __name__ == "__main__":
    unittest.main()
