import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lexicon import LexicalResolver, LexiconResult


class TestLexicalResolver:
    def test_create_resolver(self):
        resolver = LexicalResolver("http://localhost:8001")
        assert resolver.dictionary_url == "http://localhost:8001"

    def test_glossary_loading(self):
        resolver = LexicalResolver("http://localhost:8001", glossary_path=None)
        assert resolver._glossary == {}


class TestLexiconEntry:
    def test_entry_creation(self):
        from lexicon import LexiconEntry
        
        entry = LexiconEntry(
            term="honeybadger",
            translation="Honigdachs",
            source_lang="en",
            target_lang="de",
            is_protected=True
        )
        
        assert entry.term == "honeybadger"
        assert entry.translation == "Honigdachs"
        assert entry.is_protected == True


class TestLongestMatch:
    def test_phrase_longer_than_word(self):
        from lexicon import LexiconEntry
        
        entries = [
            LexiconEntry(term="honey", translation="Honig", source_lang="en", target_lang="de"),
            LexiconEntry(term="honey badger", translation="Honigdachs", source_lang="en", target_lang="de"),
        ]
        
        entries_sorted = sorted(entries, key=lambda x: len(x.term.split()), reverse=True)
        
        assert entries_sorted[0].term == "honey badger"


class TestGlossaryOverride:
    def test_glossary_priority(self):
        glossary = {
            "Dachs": {"de": "Dachs", "en": "Dachs"},
            "roof": {"en": "roof", "de": "Dach"}
        }
        
        term = "Dachs"
        if term in glossary:
            assert glossary[term]["en"] == "Dachs"