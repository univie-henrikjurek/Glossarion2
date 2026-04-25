import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pipeline.heuristics import HeuristicsChecker, QualityCheckResult


class TestHeuristicsChecker:
    def setup_method(self):
        self.checker = HeuristicsChecker()

    def test_empty_output_detection(self):
        result = self.checker.check_quality(
            original="Hello world",
            translation="",
            source_lang="en",
            target_lang="de"
        )
        assert result.is_suspicious == True
        assert "empty_output" in result.issues

    def test_identical_source_detection(self):
        result = self.checker.check_quality(
            original="This is a longer sentence that should be translated",
            translation="This is a longer sentence that should be translated",
            source_lang="en",
            target_lang="de"
        )
        assert result.is_suspicious == True
        assert "identical_to_source" in result.issues

    def test_valid_translation(self):
        result = self.checker.check_quality(
            original="Hello",
            translation="Hallo",
            source_lang="en",
            target_lang="de"
        )
        assert result.is_suspicious == False

    def test_placeholder_remaining(self):
        result = self.checker.check_quality(
            original="Hello",
            translation="__PROTECTED_0__",
            source_lang="en",
            target_lang="de"
        )
        assert result.is_suspicious == True
        assert "placeholder_remaining" in result.issues

    def test_short_input_same_output(self):
        result = self.checker.check_quality(
            original="Hi",
            translation="Hi",
            source_lang="en",
            target_lang="de"
        )
        assert result.is_suspicious == False

    def test_excessive_repetition(self):
        result = self.checker.check_quality(
            original="This is a test",
            translation="This is a test test test test test test test test test test test test",
            source_lang="en",
            target_lang="de"
        )
        assert result.is_suspicious == True
        assert "excessive_repetition" in result.issues


class TestQualityCheckResult:
    def test_result_dataclass(self):
        result = QualityCheckResult(
            is_suspicious=True,
            issues=["empty_output", "placeholder_remaining"]
        )
        assert result.is_suspicious == True
        assert len(result.issues) == 2