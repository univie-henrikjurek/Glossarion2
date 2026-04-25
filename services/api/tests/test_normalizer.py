import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from normalization import Normalizer


class TestNormalizer:
    def setup_method(self):
        self.normalizer = Normalizer()

    def test_case_normalization(self):
        result = self.normalizer.normalize("HELLO World")
        assert result.text == "hello world"

    def test_camelcase_split(self):
        result = self.normalizer.normalize("camelCaseWord")
        assert "camel Case Word" in result.text or "camelCase" in result.original

    def test_snake_case_split(self):
        result = self.normalizer.normalize("snake_case_word")
        assert "snake case word" in result.text

    def test_url_preservation(self):
        result = self.normalizer.normalize("Visit https://example.com for info")
        assert len(result.protected_ranges) > 0
        restored = self.normalizer.restore(result.text, result)
        assert "https://example.com" in restored

    def test_email_preservation(self):
        result = self.normalizer.normalize("Contact test@example.com")
        assert len(result.protected_ranges) > 0
        restored = self.normalizer.restore(result.text, result)
        assert "test@example.com" in restored

    def test_code_id_preservation(self):
        result = self.normalizer.normalize("Product-XY-123 is great")
        assert len(result.protected_ranges) > 0

    def test_empty_input(self):
        result = self.normalizer.normalize("")
        assert result.text == ""

    def test_whitespace_trimming(self):
        result = self.normalizer.normalize("  hello world  ")
        assert result.text == "hello world"
        assert result.text == result.text.strip()


class TestNormalizationIntegration:
    def setup_method(self):
        self.normalizer = Normalizer()

    def test_mixed_case(self):
        text = "The URL https://test.com is important"
        result = self.normalizer.normalize(text)
        restored = self.normalizer.restore(result.text, result)
        assert "https://test.com" in restored

    def test_compound_preservation(self):
        text = "Dachs is a German word"
        result = self.normalizer.normalize(text)
        assert "dachs" in result.text.lower()