from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities import Doctor


class IBookingRepository(ABC):
    """Port for doctor discovery and booking helpers."""

    @abstractmethod
    def find_doctor_by_name(self, doctors: list[Doctor], query: str) -> Optional[Doctor]:
        """Return the first Doctor whose name matches *query*, or None."""
        ...

    @abstractmethod
    def build_mock_doctors(
        self, place_id: int, speciality_id: int, speciality_name: str
    ) -> list[Doctor]:
        ...
