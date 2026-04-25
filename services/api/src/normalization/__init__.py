import re
from dataclasses import dataclass
from typing import Optional, List, Tuple
from ..utils import logger


@dataclass
class NormalizedText:
    original: str
    text: str
    protected_ranges: List[Tuple[int, int, str]]
    splits_applied: List[str]


class Normalizer:
    URL_PATTERN = re.compile(
        r'https?://[^\s<>"\']+|www\.[^\s<>"\']+'
    )
    FILE_PATH_PATTERN = re.compile(
        r'(?:/[a-zA-Z0-9_\-./]+)+|(?:[A-Za-z]:\\[a-zA-Z0-9_\-.]+[\\/]?)+'
    )
    EMAIL_PATTERN = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    )
    CODE_ID_PATTERN = re.compile(
        r'\b[a-zA-Z]+-[a-zA-Z0-9_-]+\b|\b[a-zA-Z0-9_-]+-[a-zA-Z]+\b'
    )
    CAMELCASE_PATTERN = re.compile(
        r'([a-z])([A-Z])|([a-zA-Z])([a-z])([A-Z])'
    )
    SNAKE_CASE_PATTERN = re.compile(r'_')
    NUMBER_PATTERN = re.compile(r'\b\d+\b')

    def __init__(self):
        self.logger = logger

    def normalize(self, text: str, source_lang: Optional[str] = None) -> NormalizedText:
        self.logger.debug(f"Normalizing text: {text[:50]}...")
        
        protected_ranges: List[Tuple[int, int, str]] = []
        working_text = text
        
        working_text, protected_ranges = self._protect_urls(working_text, protected_ranges)
        working_text, protected_ranges = self._protect_filepaths(working_text, protected_ranges)
        working_text, protected_ranges = self._protect_emails(working_text, protected_ranges)
        working_text, protected_ranges = self._protect_code_ids(working_text, protected_ranges)
        
        working_text = self._split_camelcase(working_text)
        working_text = self._split_snake_case(working_text)
        working_text = self._split_merged_compounds(working_text)
        
        working_text = working_text.strip()
        
        return NormalizedText(
            original=text,
            text=working_text,
            protected_ranges=protected_ranges,
            splits_applied=[]
        )

    def _protect_urls(self, text: str, protected: List) -> tuple[str, List]:
        for match in self.URL_PATTERN.finditer(text):
            protected.append((match.start(), match.end(), match.group()))
        result = self.URL_PATTERN.sub(lambda m: self._placeholder(len(protected)), text)
        return result, protected

    def _protect_filepaths(self, text: str, protected: List) -> tuple[str, List]:
        for match in self.FILE_PATH_PATTERN.finditer(text):
            protected.append((match.start(), match.end(), match.group()))
        result = self.FILE_PATH_PATTERN.sub(lambda m: self._placeholder(len(protected)), text)
        return result, protected

    def _protect_emails(self, text: str, protected: List) -> tuple[str, List]:
        for match in self.EMAIL_PATTERN.finditer(text):
            protected.append((match.start(), match.end(), match.group()))
        result = self.EMAIL_PATTERN.sub(lambda m: self._placeholder(len(protected)), text)
        return result, protected

    def _protect_code_ids(self, text: str, protected: List) -> tuple[str, List]:
        for match in self.CODE_ID_PATTERN.finditer(text):
            protected.append((match.start(), match.end(), match.group()))
        result = self.CODE_ID_PATTERN.sub(lambda m: self._placeholder(len(protected)), text)
        return result, protected

    def _split_camelcase(self, text: str) -> str:
        def replacer(match):
            if match.group(1) and match.group(2):
                return f"{match.group(1)} {match.group(2)}"
            elif match.group(3) and match.group(4) and match.group(5):
                return f"{match.group(3)} {match.group(4)}{match.group(5)}"
            return match.group(0)
        
        result = self.CAMELCASE_PATTERN.sub(replacer, text)
        return result

    def _split_snake_case(self, text: str) -> str:
        words = text.split()
        result = []
        for word in words:
            if self.SNAKE_CASE_PATTERN.search(word) and word.islower():
                result.append(word.replace('_', ' '))
            else:
                result.append(word)
        return ' '.join(result)

    def _split_merged_compounds(self, text: str) -> str:
        return text

    def _placeholder(self, index: int) -> str:
        return f"__PROTECTED_{index}__"

    def restore(self, text: str, normalized: NormalizedText) -> str:
        result = normalized.text
        
        for start, end, original in sorted(normalized.protected_ranges, key=lambda x: x[0], reverse=True):
            placeholder = f"__PROTECTED_{normalized.protected_ranges.index((start, end, original))}__"
            result = result.replace(placeholder, original)
        
        return result


def create_normalizer() -> Normalizer:
    return Normalizer()