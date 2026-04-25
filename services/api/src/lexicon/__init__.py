import httpx
from dataclasses import dataclass
from typing import Optional, List, Dict
from ..utils import logger


@dataclass
class LexiconEntry:
    term: str
    translation: str
    source_lang: str
    target_lang: str
    is_protected: bool = False
    is_hint: bool = False


@dataclass
class LexiconResult:
    matches: List[LexiconEntry]
    hints: List[str]
    protected_terms: List[str]


class LexicalResolver:
    def __init__(self, dictionary_url: str, glossary_path: Optional[str] = None):
        self.dictionary_url = dictionary_url
        self.glossary_path = glossary_path
        self.logger = logger
        self._client: Optional[httpx.AsyncClient] = None
        self._glossary: Dict[str, Dict[str, str]] = {}
        
        if glossary_path:
            self._load_glossary()

    def _load_glossary(self) -> None:
        import json
        import os
        
        if not os.path.exists(self.glossary_path):
            self.logger.warning(f"Glossary file not found: {self.glossary_path}")
            return
        
        try:
            with open(self.glossary_path, 'r', encoding='utf-8') as f:
                self._glossary = json.load(f)
            self.logger.info(f"Loaded glossary with {len(self._glossary)} entries")
        except Exception as e:
            self.logger.error(f"Failed to load glossary: {e}")

    async def resolve(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> LexiconResult:
        self.logger.debug(f"Resolving lexicon for: {text[:50]}...")
        
        hints: List[str] = []
        protected_terms: List[str] = []
        matches: List[LexiconEntry] = []
        
        if self._glossary:
            for source_term, translations in self._glossary.items():
                if source_term.lower() in text.lower():
                    if target_lang in translations:
                        entry = LexiconEntry(
                            term=source_term,
                            translation=translations[target_lang],
                            source_lang=source_lang,
                            target_lang=target_lang,
                            is_protected=True,
                            is_hint=True
                        )
                        matches.append(entry)
                        protected_terms.append(source_term)
                        hints.append(f"{source_term}={translations[target_lang]}")

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.dictionary_url}/lookup",
                    params={"text": text, "source": source_lang, "target": target_lang}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("matches", []):
                        if item.get("term") not in protected_terms:
                            entry = LexiconEntry(
                                term=item["term"],
                                translation=item["translation"],
                                source_lang=source_lang,
                                target_lang=target_lang,
                                is_protected=item.get("protected", False),
                                is_hint=item.get("hint", False)
                            )
                            matches.append(entry)
                            if entry.is_protected:
                                protected_terms.append(entry.term)
        except Exception as e:
            self.logger.warning(f"Dictionary lookup failed: {e}")
        
        return LexiconResult(
            matches=matches,
            hints=hints,
            protected_terms=protected_terms
        )


def create_lexical_resolver(dictionary_url: str, glossary_path: Optional[str] = None) -> LexicalResolver:
    return LexicalResolver(dictionary_url, glossary_path)