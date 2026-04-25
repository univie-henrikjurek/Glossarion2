import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from providers import TranslationProvider, ProviderFactory, TranslationResult


class TestProviderFactory:
    def test_register_provider(self):
        class MockProvider(TranslationProvider):
            async def translate(self, text, source_lang, target_lang, hints=None):
                return TranslationResult(text=text, provider="mock")
        
        ProviderFactory.register("mock", MockProvider)
        assert "mock" in ProviderFactory.available()

    def test_create_registered_provider(self):
        provider = ProviderFactory.create("libretranslate", url="http://localhost:5000")
        assert provider.url == "http://localhost:5000"


class TestTranslationProvider:
    def test_provider_interface(self):
        class TestProvider(TranslationProvider):
            async def translate(self, text, source_lang, target_lang, hints=None):
                return TranslationResult(
                    text=f"translated: {text}",
                    provider="test",
                    confidence=0.9
                )
        
        provider = TestProvider()


class TestTranslationResult:
    def test_result_creation(self):
        result = TranslationResult(
            text="Hello",
            provider="test",
            confidence=0.95,
            hints_applied=["hello=hola"]
        )
        
        assert result.text == "Hello"
        assert result.provider == "test"
        assert result.confidence == 0.95
        assert "hello=hola" in result.hints_applied