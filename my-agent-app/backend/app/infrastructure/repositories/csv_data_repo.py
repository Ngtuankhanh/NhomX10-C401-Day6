from __future__ import annotations

import csv
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Optional
from uuid import uuid4

from app.application.interfaces import IDataRepository
from app.domain.entities import Facility, Slot, SpecialtyDefinition
from app.shared.text_utils import normalize_text

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"
FACILITIES_PATH = DATA_DIR / "facilities.csv"
SPECIALTIES_PATH = DATA_DIR / "specialties.csv"
KG_PATH = DATA_DIR / "kg_merged.json"


class DataLoader:
    @staticmethod
    @lru_cache(maxsize=1)
    def load_facilities() -> list[Facility]:
        facilities = []
        with open(FACILITIES_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                facilities.append(
                    Facility(
                        place_id=int(row["place_id"]),
                        name=row["name"],
                        geo_division=row["geo_division"],
                        city_hint=row["city_hint"],
                    )
                )
        return facilities

    @staticmethod
    @lru_cache(maxsize=1)
    def load_specialties() -> list[SpecialtyDefinition]:
        specialties = []
        with open(SPECIALTIES_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                specialties.append(
                    SpecialtyDefinition(
                        speciality_id=int(row["speciality_id"]),
                        speciality_name=row["speciality_name"],
                        normalized_name=normalize_text(row["speciality_name"]),
                        diseases=tuple(row["diseases"].split("|")),
                    )
                )
        return specialties


def get_facilities() -> list[Facility]:
    return DataLoader.load_facilities()


def find_facility(query: str) -> Facility | None:
    normalized_query = normalize_text(query)
    facilities = get_facilities()
    for f in facilities:
        if normalize_text(f.name) == normalized_query:
            return f
    for f in facilities:
        if (
            normalized_query in normalize_text(f.name)
            or f.city_hint in normalized_query
        ):
            return f
    return None


def upcoming_booking_dates(days: int = 5) -> list[date]:
    today = date.today()
    return [today + timedelta(days=offset) for offset in range(1, days + 1)]


def build_mock_slots(selected_date: str) -> list[Slot]:
    seed = sum(ord(char) for char in selected_date) % 3
    slot_sets = (
        ("09:00", "09:20", "10:40", "14:20", "15:00"),
        ("08:40", "10:20", "11:00", "13:40", "16:20"),
        ("09:40", "10:40", "14:00", "14:40", "16:00"),
    )
    return [Slot(label=slot, value=slot) for slot in slot_sets[seed]]


def generate_mock_verification(phone_number: str) -> tuple[str, str]:
    suffix = phone_number[-4:] if phone_number else "0000"
    return str(uuid4()), f"******{suffix}"


class CSVDataRepository(IDataRepository):
    """Concrete IDataRepository that reads facilities and specialties from CSV files."""

    def get_facilities(self) -> list[Facility]:
        return get_facilities()

    def find_facility(self, query: str) -> Optional[Facility]:
        return find_facility(query)

    def upcoming_booking_dates(self, days: int = 5) -> list[date]:
        return upcoming_booking_dates(days)

    def build_mock_slots(self, selected_date: str) -> list[Slot]:
        return build_mock_slots(selected_date)

    def generate_mock_verification(self, phone_number: str) -> tuple[str, str]:
        return generate_mock_verification(phone_number)
