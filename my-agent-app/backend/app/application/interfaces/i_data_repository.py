from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from app.domain.entities import Facility, Slot


class IDataRepository(ABC):
    """Port for data-loading operations (facilities, slots, mock verifications)."""

    @abstractmethod
    def get_facilities(self) -> list[Facility]:
        ...

    @abstractmethod
    def find_facility(self, query: str) -> Optional[Facility]:
        ...

    @abstractmethod
    def upcoming_booking_dates(self, days: int = 5) -> list[date]:
        ...

    @abstractmethod
    def build_mock_slots(self, selected_date: str) -> list[Slot]:
        ...

    @abstractmethod
    def generate_mock_verification(self, phone_number: str) -> tuple[str, str]:
        ...
