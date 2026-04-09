"""Concrete implementation of IBookingRepository using mock data generation."""
from __future__ import annotations

from app.application.interfaces import IBookingRepository
from app.domain.entities import Doctor
from app.shared.text_utils import normalize_text

DOCTOR_FIRST_NAMES = (
    "Đỗ Khánh Hà", "Trịnh Ngọc Phát", "Lê Minh An", "Nguyễn Thu Trang",
    "Trần Văn Sơn", "Phạm Hải Yến", "Vũ Đình Hiếu", "Hoàng Ngọc Mai",
    "Bùi Gia Khiêm", "Đặng Thùy Linh",
)


class MockBookingRepository(IBookingRepository):
    """Generates deterministic mock doctors and resolves doctor queries.

    No infrastructure coupling to other repositories; all data it needs
    is passed in as parameters (place_id, speciality_id, speciality_name).
    """

    def build_mock_doctors(
        self, place_id: int, speciality_id: int, speciality_name: str
    ) -> list[Doctor]:
        doctors: list[Doctor] = []
        base_id = place_id * 10_000 + speciality_id * 10
        norm_spec = normalize_text(speciality_name).replace(" ", "-")

        for i in range(3):
            name = f"Bác sĩ {DOCTOR_FIRST_NAMES[(base_id + i) % len(DOCTOR_FIRST_NAMES)]}"
            doc_id = base_id + i + 1
            doctors.append(
                Doctor(
                    doctor_id=doc_id,
                    professional_id=doc_id,
                    doctor_name=name,
                    doctor_ad=f"{norm_spec}-{place_id}-{i + 1}@vinmec.mock",
                    place_id=place_id,
                    speciality_id=speciality_id,
                    speciality_name=speciality_name,
                )
            )
        return doctors

    def find_doctor_by_name(self, doctors: list[Doctor], query: str) -> Doctor | None:
        return next(
            (d for d in doctors if d.doctor_name in query or query in d.doctor_name),
            None,
        )
