from typing import Optional
from . import TranslationProvider, TranslationResult, ProviderFactory
from ..utils import logger


class LibreTranslateProvider(TranslationProvider):
    def __init__(self, url: str, api_key: Optional[str] = None):
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.logger = logger

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        hints: Optional[list[str]] = None
    ) -> TranslationResult:
        import httpx
        
        processed_text = text
        if hints:
            for hint in hints:
                if '=' in hint:
                    source_term, target_term = hint.split('=', 1)
                    processed_text = processed_text.replace(source_term, target_term)
                    self.logger.debug(f"Applied hint: {source_term} -> {target_term}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                response = await client.post(
                    f"{self.url}/translate",
                    json={
                        "q": processed_text,
                        "source": source_lang,
                        "target": target_lang,
                        "format": "text"
                    },
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return TranslationResult(
                        text=data.get("translatedText", processed_text),
                        provider="libretranslate",
                        confidence=data.get("confidence"),
                        hints_applied=hints
                    )
                else:
                    self.logger.error(f"LibreTranslate error: {response.status_code}")
                    return TranslationResult(
                        text=text,
                        provider="libretranslate",
                        confidence=0.0
                    )
        except Exception as e:
            self.logger.error(f"LibreTranslate request failed: {e}")
            return TranslationResult(
                text=text,
                provider="libretranslate",
                confidence=0.0
            )


ProviderFactory.register("libretranslate", LibreTranslateProvider)


def create_libretranslate_provider(url: str, api_key: Optional[str] = None) -> LibreTranslateProvider:
    return LibreTranslateProvider(url, api_key)