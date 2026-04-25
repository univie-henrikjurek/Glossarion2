import json
import os
from typing import Optional
from .utils import logger


class DictionaryIndex:
    def __init__(self):
        self.logger = logger
        self.entries: dict[str, dict] = {}
        self.phrases: dict[int, list[dict]] = {}

    def add_entry(
        self,
        term: str,
        translation: str,
        source_lang: str,
        target_lang: str,
        is_protected: bool = False,
        is_hint: bool = False
    ) -> None:
        key = f"{source_lang}:{target_lang}:{term.lower()}"
        self.entries[key] = {
            "term": term,
            "translation": translation,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "is_protected": is_protected,
            "is_hint": is_hint,
            "priority": len(term.split())
        }

    def load_json(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            self.logger.warning(f"JSON file not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for term, translations in data.items():
                for lang_pair, translation in translations.items():
                    if ":" in lang_pair:
                        source, target = lang_pair.split(":")
                        self.add_entry(term, translation, source, target, is_protected=True, is_hint=True)
            
            self.logger.info(f"Loaded {len(self.entries)} entries from JSON")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load JSON: {e}")
            return False

    def lookup(self, text: str, source_lang: str, target_lang: str) -> list[dict]:
        text_lower = text.lower()
        text_words = text_lower.split()
        results = []
        matched_terms = set()
        
        phrases_sorted = sorted(
            [(k, v) for k, v in self.entries.items() if source_lang in k and target_lang in k],
            key=lambda x: x[1]["priority"],
            reverse=True
        )
        
        for key, entry in phrases_sorted:
            term_lower = entry["term"].lower()
            
            if term_lower == text_lower:
                if entry["term"] not in matched_terms:
                    results.insert(0, {
                        "term": entry["term"],
                        "translation": entry["translation"],
                        "source_lang": source_lang,
                        "target_lang": target_lang,
                        "match_type": "exact",
                        "is_protected": entry["is_protected"],
                        "is_hint": entry["is_hint"]
                    })
                    matched_terms.add(entry["term"])
            elif term_lower in text_lower:
                if entry["term"] not in matched_terms:
                    results.append({
                        "term": entry["term"],
                        "translation": entry["translation"],
                        "source_lang": source_lang,
                        "target_lang": target_lang,
                        "match_type": "contains",
                        "is_protected": entry["is_protected"],
                        "is_hint": entry["is_hint"]
                    })
                    matched_terms.add(entry["term"])
        
        return results[:20]

    def load_glossary(self, glossary_path: str) -> None:
        if os.path.exists(glossary_path):
            self.load_json(glossary_path)


def create_dictionary_index() -> DictionaryIndex:
    return DictionaryIndex()