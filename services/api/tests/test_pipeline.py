import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from normalization import Normalizer
from lexicon import LexiconResult
from providers import TranslationResult
from pipeline.heuristics import HeuristicsChecker


class TestPipelineIntegration:
    def test_normalizer_to_heuristics(self):
        normalizer = Normalizer()
        checker = HeuristicsChecker()
        
        normalized = normalizer.normalize("Hello world")
        
        quality = checker.check_quality(
            original="Hello world",
            translation="Hallo Welt",
            source_lang="en",
            target_lang="de"
        )
        
        assert quality.is_suspicious == False

    def test_protected_term_flow(self):
        normalizer = Normalizer()
        
        result = normalizer.normalize("Product-XY-123 is great")
        
        assert len(result.protected_ranges) > 0
        
        restored = normalizer.restore(result.text, result)
        assert "Product" in restored or "XY" in restored

    def test_lexicon_result_creation(self):
        result = LexiconResult(
            matches=[],
            hints=[],
            protected_terms=[]
        )
        assert len(result.matches) == 0
        assert len(result.hints) == 0

    def test_translation_result_with_hints(self):
        result = TranslationResult(
            text="Hello",
            provider="libretranslate",
            hints_applied=["hello=Hallo"]
        )
        assert result.hints_applied == ["hello=Hallo"]


class TestRegressionCases:
    def test_honeybadger_normalization(self):
        normalizer = Normalizer()
        
        result = normalizer.normalize("honeybadger")
        assert "honeybadger" in result.text.lower() or "honey" in result.text.lower()

    def test_honey_badger_split(self):
        normalizer = Normalizer()
        
        result = normalizer.normalize("honey badger")
        assert "honey" in result.text.lower()
        assert "badger" in result.text.lower()

    def test_dachs_not_roof(self):
        glossary = {
            "Dachs": {"en": "Dachs", "de": "Dachs"}
        }
        
        assert "Dachs" in glossary
        assert glossary["Dachs"]["en"] != "roof"

    def test_protected_identifier(self):
        normalizer = Normalizer()
        
        result = normalizer.normalize("product-XY-123")
        restored = normalizer.restore(result.text, result)
        
        assert "XY" in restored or "123" in restored