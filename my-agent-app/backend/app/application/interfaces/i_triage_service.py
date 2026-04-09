from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities import ClassificationResult


class ITriageService(ABC):
    """Port for symptom triage / specialty classification."""

    @abstractmethod
    def classify_symptoms(self, raw_text: str) -> ClassificationResult:
        ...
