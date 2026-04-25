from dataclasses import dataclass
from typing import Optional
from .normalization import Normalizer, NormalizedText, create_normalizer
from .lexicon import LexicalResolver, LexiconResult, create_lexical_resolver
from .providers import TranslationProvider, ProviderFactory, TranslationResult
from .providers.libretranslate import create_libretranslate_provider
from .pipeline.heuristics import HeuristicsChecker, QualityCheckResult, create_heuristics_checker
from ..utils import logger


@dataclass
class PipelineConfig:
    libretranslate_url: str
    dictionary_url: str
    glossary_path: Optional[str] = None
    default_source_lang: str = "en"
    default_target_lang: str = "de"


@dataclass
class TranslateRequest:
    text: str
    source_lang: str
    target_lang: str
    glossary: Optional[dict[str, dict[str, str]]] = None


@dataclass
class TranslateResponse:
    translation: str
    original: str
    source_lang: str
    target_lang: str
    hints_applied: list[str]
    protected_terms: list[str]
    quality_issues: list[str]
    provider: str


class TranslationPipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = logger
        self.normalizer = create_normalizer()
        self.lexicon = create_lexical_resolver(config.dictionary_url, config.glossary_path)
        self.provider = create_libretranslate_provider(config.libretranslate_url)
        self.heuristics = create_heuristics_checker()

    async def translate(self, request: TranslateRequest) -> TranslateResponse:
        self.logger.info(f"Pipeline: {request.source_lang} -> {request.target_lang}: {request.text[:50]}...")
        
        combined_glossary = {}
        if request.glossary:
            combined_glossary = request.glossary
        elif self.config.glossary_path:
            combined_glossary = self._load_glossary()
        
        normalized = self.normalizer.normalize(request.text, request.source_lang)
        self.logger.debug(f"Normalized: {normalized.text[:50]}...")
        
        lexicon_result = await self.lexicon.resolve(
            normalized.text,
            request.source_lang,
            request.target_lang
        )
        self.logger.debug(f"Lexicon matches: {len(lexicon_result.matches)}")
        
        all_hints = list(lexicon_result.hints)
        if combined_glossary:
            for term, translations in combined_glossary.items():
                if term.lower() in normalized.text.lower():
                    if request.target_lang in translations:
                        all_hints.append(f"{term}={translations[request.target_lang]}")
        
        translation_result = await self.provider.translate(
            normalized.text,
            request.source_lang,
            request.target_lang,
            hints=all_hints
        )
        
        restored = self.normalizer.restore(translation_result.text, normalized)
        
        quality = self.heuristics.check_quality(
            request.text,
            restored,
            request.source_lang,
            request.target_lang
        )
        
        return TranslateResponse(
            translation=restored,
            original=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            hints_applied=all_hints,
            protected_terms=lexicon_result.protected_terms,
            quality_issues=quality.issues,
            provider=translation_result.provider
        )

    def _load_glossary(self) -> dict[str, dict[str, str]]:
        import json
        import os
        
        if not self.config.glossary_path or not os.path.exists(self.config.glossary_path):
            return {}
        
        try:
            with open(self.config.glossary_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load glossary: {e}")
            return {}


def create_pipeline(config: PipelineConfig) -> TranslationPipeline:
    return TranslationPipeline(config)