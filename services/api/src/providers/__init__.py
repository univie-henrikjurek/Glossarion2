from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class TranslationResult:
    text: str
    provider: str
    confidence: Optional[float] = None
    hints_applied: Optional[list[str]] = None


class TranslationProvider(ABC):
    @abstractmethod
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        hints: Optional[list[str]] = None
    ) -> TranslationResult:
        pass


class ProviderFactory:
    _providers: dict[str, type[TranslationProvider]] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: type[TranslationProvider]) -> None:
        cls._providers[name] = provider_class
    
    @classmethod
    def create(cls, name: str, **kwargs) -> TranslationProvider:
        if name not in cls._providers:
            raise ValueError(f"Unknown provider: {name}")
        return cls._providers[name](**kwargs)
    
    @classmethod
    def available(cls) -> list[str]:
        return list(cls._providers.keys())