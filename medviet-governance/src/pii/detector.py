import re
from typing import Iterable

from presidio_analyzer import RecognizerResult


CCCD_PATTERN = re.compile(r"(?<!\d)\d{10,12}(?!\d)")
VN_PHONE_PATTERN = re.compile(r"(?<!\d)(?:0?(?:3|5|7|8|9)\d{8})(?!\d)")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
LETTER_PATTERN = re.compile(r"[^\W\d_]+", re.UNICODE)


class VietnamesePIIAnalyzer:
    """Small local analyzer compatible with the Presidio analyze() interface."""

    def analyze(
        self,
        text: str,
        language: str = "vi",
        entities: Iterable[str] | None = None,
        **_: object,
    ) -> list[RecognizerResult]:
        if language != "vi":
            return []

        text = "" if text is None else str(text)
        entity_filter = set(entities or ["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"])
        results: list[RecognizerResult] = []

        if "EMAIL_ADDRESS" in entity_filter:
            results.extend(
                RecognizerResult("EMAIL_ADDRESS", match.start(), match.end(), 0.95)
                for match in EMAIL_PATTERN.finditer(text)
            )

        if "VN_CCCD" in entity_filter:
            results.extend(
                RecognizerResult("VN_CCCD", match.start(), match.end(), 0.90)
                for match in CCCD_PATTERN.finditer(text)
            )

        if "VN_PHONE" in entity_filter:
            results.extend(
                RecognizerResult("VN_PHONE", match.start(), match.end(), 0.90)
                for match in VN_PHONE_PATTERN.finditer(text)
            )

        if "PERSON" in entity_filter and self._looks_like_person_name(text):
            results.append(RecognizerResult("PERSON", 0, len(text), 0.75))

        return sorted(results, key=lambda result: (result.start, result.end))

    @staticmethod
    def _looks_like_person_name(text: str) -> bool:
        if not text or "@" in text:
            return False
        if CCCD_PATTERN.fullmatch(text.strip()) or VN_PHONE_PATTERN.fullmatch(text.strip()):
            return False

        tokens = LETTER_PATTERN.findall(text)
        if len(tokens) < 2 or len(tokens) > 8:
            return False

        return sum(len(token) >= 2 for token in tokens) >= 2


def build_vietnamese_analyzer() -> VietnamesePIIAnalyzer:
    return VietnamesePIIAnalyzer()


def detect_pii(text: str, analyzer: VietnamesePIIAnalyzer) -> list[RecognizerResult]:
    return analyzer.analyze(
        text=text,
        language="vi",
        entities=["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"],
    )
