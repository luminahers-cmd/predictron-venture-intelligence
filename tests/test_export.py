import unittest

from utils.export import PDF_MAX_LINES, generate_simple_pdf


class ExportTests(unittest.TestCase):
    def test_generate_simple_pdf_empty_text(self):
        pdf_bytes = generate_simple_pdf("")
        self.assertTrue(pdf_bytes.startswith(b"%PDF-1.4"))

    def test_generate_simple_pdf_with_long_text(self):
        long_text = "\n".join([f"line {i}" for i in range(PDF_MAX_LINES + 50)])
        pdf_bytes = generate_simple_pdf(long_text)
        self.assertIn(b"startxref", pdf_bytes)


if __name__ == "__main__":
    unittest.main()
