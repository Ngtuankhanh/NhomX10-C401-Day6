from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal
from datetime import date, datetime

ConversationState = Literal[
    "GREETING",
    "COLLECTING_SYMPTOMS",
    "ASKING_FOLLOWUP",
    "SHOWING_SPECIALTY_RESULT",
    "COLLECTING_BOOKING_PREFS",
    "COLLECTING_PATIENT_INFO",
    "CONFIRMING_BOOKING",
    "WAITING_OTP",
    "BOOKING_COMPLETED",
    "FALLBACK_SUPPORT",
]

StatusCode = Literal[
    "typing",
    "analyzing_symptoms",
    "finding_doctors",
    "loading_slots",
    "submitting_booking",
    "waiting_for_otp",
    "confirming_booking",
    "recovering_from_error",
    "idle",
]

@dataclass
class ChatMessage:
    role: Literal["assistant", "user"]
    content: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z")

@dataclass
class Facility:
    place_id: int
    name: str
    geo_division: str
    city_hint: str

@dataclass
class Doctor:
    doctor_id: int
    professional_id: int
    doctor_name: str
    doctor_ad: str
    place_id: int
    speciality_id: int
    speciality_name: str

@dataclass
class Slot:
    label: str
    value: str

@dataclass
class SpecialtyDefinition:
    speciality_id: int
    speciality_name: str
    normalized_name: str
    diseases: tuple[str, ...]

@dataclass
class ClassificationResult:
    speciality_id: int | None
    speciality_name: str
    description: str
    confidence: float
    question: str | None
    matched_symptoms: tuple[str, ...]
    fallback_used: bool
    needs_more_info: bool = False
    warning_signs: tuple[str, ...] = ()

@dataclass
class BookingContext:
    place_id: int | None = None
    facility_name: str | None = None
    geo_division: str | None = None
    speciality_id: int | None = None
    speciality_name: str | None = None
    doctor_id: int | None = None
    professional_id: int | None = None
    doctor_name: str | None = None
    doctor_ad: str | None = None
    booking_date: str | None = None
    booking_time: str | None = None

@dataclass
class PatientInfo:
    name: str | None = None
    gender: int | None = None
    phone_number: str | None = None
    date_of_birth: str | None = None
    email: str | None = None
    inquiry_info: str | None = None

@dataclass
class SpecialtyAssessment:
    speciality_id: int | None = None
    speciality_name: str | None = None
    description: str | None = None
    confidence: float | None = None
    question: str | None = None
    matched_symptoms: list[str] = field(default_factory=list)
    needs_more_info: bool = False
    warning_signs: list[str] = field(default_factory=list)
    fallback_used: bool = False
    agent_b_status: str = "pending"

@dataclass
class BookingVerification:
    verif_id: str | None = None
    masked_username: str | None = None
    otp_required: bool = False
    otp_code: str | None = None
    booking_id: int | None = None

@dataclass
class FailureState:
    agent_b_failures: int = 0
    slot_lookup_failures: int = 0
    booking_failures: int = 0
    last_error_code: str | None = None

@dataclass
class SessionState:
    session_id: str
    conversation_state: ConversationState = "COLLECTING_SYMPTOMS"
    triage_attempt_count: int = 0
    symptom_messages: list[str] = field(default_factory=list)
    symptom_summary: str | None = None
    pending_field: str | None = None
    last_follow_up_question: str | None = None
    quick_replies: list[str] = field(default_factory=list)
    current_status: StatusCode = "idle"
    messages: list[ChatMessage] = field(default_factory=list)
    booking_context: BookingContext = field(default_factory=BookingContext)
    patient_info: PatientInfo = field(default_factory=PatientInfo)
    specialty_assessment: SpecialtyAssessment = field(default_factory=SpecialtyAssessment)
    booking_verification: BookingVerification = field(default_factory=BookingVerification)
    failure_state: FailureState = field(default_factory=FailureState)
    available_doctors: list[Doctor] = field(default_factory=list)
    available_slots: list[str] = field(default_factory=list)
