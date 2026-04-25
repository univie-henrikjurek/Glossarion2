from typing import Optional, List
from . import TranslationProvider, TranslationResult, ProviderFactory
from ..utils import logger


class LibreTranslateProvider(TranslationProvider):
    def __init__(self, url: str, api_key: Optional[str] = None):
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.logger = logger
        self.logger.info(f"LibreTranslateProvider initialized with URL: {self.url}")

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        hints: Optional[List[str]] = None
    ) -> TranslationResult:
        import httpx
        
        processed_text = text
        if hints:
            for hint in hints:
                if '=' in hint:
                    source_term, target_term = hint.split('=', 1)
                    processed_text = processed_text.replace(source_term, target_term)
                    self.logger.debug(f"Applied hint: {source_term} -> {target_term}")
        
        self.logger.info(f"Calling LibreTranslate: {self.url}/translate with text='{processed_text}'")
        
        try:
            async with httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=1, max_connections=1)
            ) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                self.logger.info(f"Making POST request to {self.url}/translate")
                
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
                
                self.logger.info(f"LibreTranslate response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    translated = data.get("translatedText", processed_text)
                    self.logger.info(f"Translation result: {translated}")
                    return TranslationResult(
                        text=translated,
                        provider="libretranslate",
                        confidence=data.get("confidence"),
                        hints_applied=hints
                    )
                else:
                    self.logger.error(f"LibreTranslate error: {response.status_code} - {response.text}")
                    return TranslationResult(
                        text=text,
                        provider="libretranslate",
                        confidence=0.0
                    )
        except Exception as e:
            self.logger.error(f"LibreTranslate request failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return TranslationResult(
                text=text,
                provider="libretranslate",
                confidence=0.0
            )


ProviderFactory.register("libretranslate", LibreTranslateProvider)


def create_libretranslate_provider(url: str, api_key: Optional[str] = None) -> LibreTranslateProvider:
    return LibreTranslateProvider(url, api_key)