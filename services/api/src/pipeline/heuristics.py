import re
from dataclasses import dataclass
from typing import List
from ..utils import logger


@dataclass
class QualityCheckResult:
    is_suspicious: bool
    issues: List[str]


class HeuristicsChecker:
    EMPTY_THRESHOLD = 3
    REPETITION_PATTERN = re.compile(r'(.{10,})\1{3,}')
    PLACEHOLDER_PATTERN = re.compile(r'__[A-Z]+_\d+__')
    
    def __init__(self):
        self.logger = logger

    def check_quality(
        self,
        original: str,
        translation: str,
        source_lang: str,
        target_lang: str
    ) -> QualityCheckResult:
        issues: List[str] = []
        
        if len(translation.strip()) < self.EMPTY_THRESHOLD:
            issues.append("empty_output")
        
        if self.PLACEHOLDER_PATTERN.search(translation):
            issues.append("placeholder_remaining")
        
        if self.REPETITION_PATTERN.search(translation):
            issues.append("excessive_repetition")
        
        original_clean = re.sub(r'[^\w\s]', '', original.lower())
        translation_clean = re.sub(r'[^\w\s]', '', translation.lower())
        
        original_words = set(original_clean.split())
        translation_words = set(translation_clean.split())
        
        if original_clean.strip() == translation_clean.strip() and len(original) > 10:
            if source_lang != target_lang:
                issues.append("identical_to_source")
        elif len(original_words) > 0 and len(translation_words) > 0:
            overlap = original_words & translation_words
            overlap_ratio = len(overlap) / len(original_words)
            if overlap_ratio > 0.7:
                issues.append("excessive_word_overlap")
        
        if len(translation) > 10 * len(original):
            issues.append("unusually_long")
        
        if len(translation) < len(original) * 0.3 and len(original) > 10:
            issues.append("unusually_short")
        
        is_suspicious = len(issues) > 0
        if is_suspicious:
            self.logger.warning(f"Suspicious translation detected: {issues}")
        
        return QualityCheckResult(
            is_suspicious=is_suspicious,
            issues=issues
        )


def create_heuristics_checker() -> HeuristicsChecker:
    return HeuristicsChecker()