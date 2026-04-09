"""Booking tools for Agent A."""

from __future__ import annotations

import json
from typing import Any

import requests
from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime


def _tool_success(payload_key: str | None = None, payload: Any = None, **extra: Any) -> str:
    body: dict[str, Any] = {"status": "success"}
    if payload_key is not None:
        body[payload_key] = payload
    body.update(extra)
    return json.dumps(body, ensure_ascii=False)


def _tool_error(code: str, message: str, **extra: Any) -> str:
    body: dict[str, Any] = {
        "status": "error",
        "error": {"code": code, "message": message},
    }
    body.update(extra)
    return json.dumps(body, ensure_ascii=False)


def _resolve_thread_id(runtime: ToolRuntime | None) -> str:
    if runtime is None:
        return "default-thread"

    config = getattr(runtime, "config", None) or {}
    configurable = config.get("configurable", {}) if hasattr(config, "get") else {}
    thread_id = configurable.get("thread_id")
    return str(thread_id) if thread_id else "default-thread"


def _extract_response_value(payload: dict[str, Any], *keys: str) -> Any:
    containers = [payload]
    for container_key in ("data", "result"):
        nested = payload.get(container_key)
        if isinstance(nested, dict):
            containers.append(nested)

    for container in containers:
        for key in keys:
            value = container.get(key)
            if value not in (None, ""):
                return value
    return None


def _sync_session_after_booking_request(response_data: dict[str, Any], runtime: ToolRuntime) -> None:
    from app.presentation.api.dependencies import _session_repo

    session = _session_repo.get_session(_resolve_thread_id(runtime))
    if not session:
        return

    verif_id = _extract_response_value(response_data, "verif_id", "verification_id")
    masked_username = _extract_response_value(
        response_data,
        "masked_username",
        "maskedUsername",
        "masked_phone",
    )
    booking_id = _extract_response_value(response_data, "booking_id", "bookingId", "id")
    otp_required_raw = _extract_response_value(response_data, "otp_required", "otpRequired")
    otp_required = bool(otp_required_raw) if otp_required_raw is not None else bool(verif_id)

    session.booking_verification.verif_id = str(verif_id) if verif_id is not None else None
    session.booking_verification.masked_username = (
        str(masked_username) if masked_username is not None else None
    )
    session.booking_verification.otp_required = otp_required
    if booking_id is not None:
        try:
            session.booking_verification.booking_id = int(booking_id)
        except (TypeError, ValueError):
            session.booking_verification.booking_id = None

    if verif_id or otp_required:
        session.pending_field = "otp_code"
        session.conversation_state = "WAITING_OTP"

    _session_repo.save_session(session)


def _sync_session_after_booking_confirmation(
    response_data: dict[str, Any], runtime: ToolRuntime
) -> None:
    from app.presentation.api.dependencies import _session_repo

    session = _session_repo.get_session(_resolve_thread_id(runtime))
    if not session:
        return

    booking_id = _extract_response_value(response_data, "booking_id", "bookingId", "id")
    if booking_id is not None:
        try:
            session.booking_verification.booking_id = int(booking_id)
        except (TypeError, ValueError):
            session.booking_verification.booking_id = None

    session.pending_field = None
    session.conversation_state = "BOOKING_COMPLETED"
    _session_repo.save_session(session)


@tool
def list_facilities_tool() -> str:
    """Lấy danh sách các bệnh viện và phòng khám Vinmec.

    Hãy dùng tool này khi người dùng muốn chọn địa điểm khám hoặc hỏi về các cơ sở Vinmec.
    """

    url = "https://api2.vinmec.com/api/v1/auto-booking/vinmec/vinmec-place/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        compact_data = [
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "city": item.get("geo_division"),
                "site_uid": item.get("vinmec_site_uid"),
            }
            for item in data
        ]
        return _tool_success("facilities", compact_data)
    except Exception as exc:
        return _tool_error("FACILITY_LOOKUP_FAILED", str(exc))


@tool
def search_doctors_tool(speciality_id: int, place_id: int) -> str:
    """Tìm danh sách bác sĩ dựa trên chuyên khoa và cơ sở y tế.

    Args:
        speciality_id: ID của chuyên khoa (lấy từ kết quả của Specialist Agent).
        place_id: ID của cơ sở Vinmec (lấy từ list_facilities_tool).
    """

    url = (
        "https://api2.vinmec.com/api/v1/auto-booking/vinmec/ab-doctor/"
        f"?ab_doctor_speciality_id={speciality_id}&vinmec_place_id={place_id}"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        compact_data = [
            {
                "doctor_id": item.get("id"),
                "name": item.get("name"),
                "position": item.get("position"),
                "experience": item.get("degrees"),
                "speciality": item.get("speciality"),
                "price": item.get("price", {}).get("local"),
            }
            for item in data
        ]
        return _tool_success("doctors", compact_data)
    except Exception as exc:
        return _tool_error("DOCTOR_LOOKUP_FAILED", str(exc))


@tool
def get_doctor_slots_tool(doctor_id: int, speciality_id: int, place_id: int, date: str) -> str:
    """Lấy danh sách các giờ khám còn trống của một bác sĩ trong một ngày cụ thể.

    Args:
        doctor_id: ID của bác sĩ.
        speciality_id: ID chuyên khoa.
        place_id: ID cơ sở y tế.
        date: Ngày muốn khám (định dạng YYYY-MM-DD, ví dụ: 2026-04-21).
    """

    url = (
        "https://api2.vinmec.com/api/v1/auto-booking/vinmec/ab-time-slot/"
        f"?doctor_id={doctor_id}&doctor_speciality_id={speciality_id}"
        f"&vinmec_place_id={place_id}&date={date}"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        available_slots = [
            {
                "slot_id": item.get("id"),
                "time": item.get("start_time").split("T")[1][:5]
                if "T" in item.get("start_time", "")
                else "",
                "price": item.get("price"),
            }
            for item in data
            if item.get("is_avaiable") and not item.get("is_booked")
        ]
        return _tool_success("slots", available_slots)
    except Exception as exc:
        return _tool_error("SLOT_LOOKUP_FAILED", str(exc))


@tool
def get_specialties_tool(place_id: int) -> str:
    """Lấy danh sách các chuyên khoa chính thức của một cơ sở Vinmec.

    Args:
        place_id: ID của cơ sở Vinmec.
    """

    url = (
        "https://api2.vinmec.com/api/v1/auto-booking/vinmec/doctor-speciality/"
        f"?vinmec_place_id={place_id}"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        compact_data = [
            {
                "speciality_id": item.get("id"),
                "name": item.get("title"),
                "description": item.get("description"),
            }
            for item in data
            if item.get("ab_booking_enabled")
        ]
        return _tool_success("specialties", compact_data)
    except Exception as exc:
        return _tool_error("SPECIALTY_LOOKUP_FAILED", str(exc))


@tool
def suggest_hospital_by_location_tool(user_location: str) -> str:
    """Gợi ý bệnh viện Vinmec gần nhất dựa trên tỉnh thành hoặc địa chỉ của người dùng.

    Args:
        user_location: Tỉnh thành hoặc địa chỉ người dùng cung cấp (ví dụ: 'Hà Nội', 'HCM').
    """

    url = "https://api2.vinmec.com/api/v1/auto-booking/vinmec/vinmec-place/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        user_loc_lower = user_location.lower()
        matches = []

        for item in data:
            title = item.get("title", "").lower()
            city = item.get("geo_division", "").lower()
            if user_loc_lower in title or user_loc_lower in city or city in user_loc_lower:
                matches.append(
                    {
                        "id": item.get("id"),
                        "title": item.get("title"),
                        "city": item.get("geo_division"),
                    }
                )

        if not matches:
            preview = [
                {"id": item.get("id"), "title": item.get("title")}
                for item in data[:5]
            ]
            return _tool_success(
                "facilities",
                [],
                message=f"Không tìm thấy cơ sở phù hợp với '{user_location}'.",
                fallback_preview=preview,
            )

        return _tool_success("facilities", matches)
    except Exception as exc:
        return _tool_error("LOCATION_LOOKUP_FAILED", str(exc))


@tool
def create_booking_tool(
    name: str,
    phone_number: str,
    booking_date: str,
    place_id: int,
    speciality_id: int,
    proffesional_id: int,
    doctor_name: str,
    doctor_ad: str,
    speciality_name: str,
    geo_division: str,
    date_of_birth: str = "1990-01-01",
    email: str | None = None,
    gender: int = 1,
    runtime: ToolRuntime = None,
) -> str:
    """Tạo yêu cầu đặt lịch khám (Giai đoạn 1: Gửi mã OTP).

    Hãy dùng tool này khi đã có đủ thông tin khách hàng và lịch khám.

    Args:
        name: Họ và tên người khám.
        phone_number: Số điện thoại.
        booking_date: Ngày khám (YYYY-MM-DD).
        place_id: ID cơ sở khám (place_id).
        speciality_id: ID chuyên khoa.
        proffesional_id: ID bác sĩ (professional_id từ search_doctors_tool).
        doctor_name: Tên bác sĩ.
        doctor_ad: Username AD của bác sĩ (ad_username).
        speciality_name: Tên chuyên khoa.
        geo_division: Mã vùng/vị trí cơ sở (ví dụ: 'ha-noi', 'ocean-park-2').
        date_of_birth: Ngày sinh (YYYY-MM-DD).
        email: Email liên hệ (Không bắt buộc).
        gender: Giới tính (1: Nam, 2: Nữ).
    """

    url = "https://www.vinmec.com/api/v3/booking"
    payload = {
        "name": name,
        "phone_number": phone_number,
        "booking_date": booking_date,
        "booking_expected_time": None,
        "date_of_birth": date_of_birth,
        "doctor_ad": doctor_ad,
        "doctor_name": doctor_name,
        "email": email,
        "gender": gender,
        "geo_division": geo_division,
        "inquiry_info": "Yêu cầu đặt lịch từ trợ lý AI (Kiểm thử).",
        "is_foreigner": False,
        "language": "vi",
        "neededcaptcha": False,
        "place_id": place_id,
        "proffesional_id": proffesional_id,
        "source": "/vie/dang-ky-kham/",
        "speciality_id": speciality_id,
        "speciality_name": speciality_name,
        "type": 2,
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()

        if runtime is not None:
            _sync_session_after_booking_request(data, runtime)

        verif_id = _extract_response_value(data, "verif_id", "verification_id")
        otp_required_raw = _extract_response_value(data, "otp_required", "otpRequired")
        return _tool_success(
            "booking_request",
            data,
            verif_id=verif_id,
            masked_username=_extract_response_value(
                data,
                "masked_username",
                "maskedUsername",
                "masked_phone",
            ),
            otp_required=bool(otp_required_raw) if otp_required_raw is not None else bool(verif_id),
            booking_id=_extract_response_value(data, "booking_id", "bookingId", "id"),
        )
    except Exception as exc:
        return _tool_error("BOOKING_REQUEST_FAILED", str(exc))


@tool
def confirm_booking_tool(
    otp_code: str,
    verif_id: str,
    name: str,
    phone_number: str,
    booking_date: str,
    place_id: int,
    speciality_id: int,
    proffesional_id: int,
    doctor_name: str,
    doctor_ad: str,
    speciality_name: str,
    geo_division: str,
    date_of_birth: str = "1990-01-01",
    email: str | None = None,
    gender: int = 1,
    runtime: ToolRuntime = None,
) -> str:
    """Xác nhận đặt lịch khám bằng mã OTP (Giai đoạn 2: Hoàn tất).

    Hãy dùng tool này sau khi người dùng cung cấp mã OTP được gửi về điện thoại.

    Args:
        otp_code: Mã OTP khách hàng cung cấp.
        verif_id: Mã định danh xác thực (lấy từ kết quả tool create_booking_tool).
        email: Email liên hệ (Không bắt buộc).
        ... (các tham số khác giống tool create_booking_tool)
    """

    url = "https://www.vinmec.com/api/v2/booking"
    payload = {
        "opt_code": otp_code,
        "otp_code": otp_code,
        "verif_id": verif_id,
        "name": name,
        "phone_number": phone_number,
        "booking_date": booking_date,
        "booking_expected_time": None,
        "date_of_birth": date_of_birth,
        "doctor_ad": doctor_ad,
        "doctor_name": doctor_name,
        "email": email,
        "gender": gender,
        "geo_division": geo_division,
        "inquiry_info": "Xác nhận đặt lịch từ trợ lý AI (Kiểm thử).",
        "is_foreigner": False,
        "language": "vi",
        "neededcaptcha": False,
        "place_id": place_id,
        "proffesional_id": proffesional_id,
        "source": "/vie/dang-ky-kham/",
        "speciality_id": speciality_id,
        "speciality_name": speciality_name,
        "type": 2,
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()

        if runtime is not None:
            _sync_session_after_booking_confirmation(data, runtime)

        return _tool_success(
            "booking_confirmation",
            data,
            booking_id=_extract_response_value(data, "booking_id", "bookingId", "id"),
            verif_id=verif_id,
        )
    except Exception as exc:
        return _tool_error("BOOKING_CONFIRM_FAILED", str(exc))


@tool
def update_booking_field_tool(
    field_name: str,
    value: str | int | bool | None,
    category: str = "booking_context",
    runtime: ToolRuntime = None,
) -> str:
    """Cập nhật một trường thông tin vào bộ nhớ phiên khám (để hiển thị trên giao diện người dùng).

    Hãy dùng tool này ngay khi người dùng xác nhận một thông tin nào đó
    (ví dụ: chọn xong bác sĩ, nhập xong tên).

    Args:
        field_name: Tên trường cần cập nhật.
        value: Giá trị mới.
        category: Nhóm thông tin cần cập nhật.
    """

    from app.presentation.api.dependencies import _session_repo

    session = _session_repo.get_session(_resolve_thread_id(runtime))
    if not session:
        return _tool_error("SESSION_NOT_FOUND", "Không tìm thấy phiên để cập nhật.")

    targets = {
        "booking_context": session.booking_context,
        "patient_info": session.patient_info,
        "session": session,
        "booking_verification": session.booking_verification,
        "specialty_assessment": session.specialty_assessment,
        "failure_state": session.failure_state,
    }
    target = targets.get(category)

    if target is None:
        return _tool_error("INVALID_CATEGORY", f"Category không hợp lệ: {category}")
    if not hasattr(target, field_name):
        return _tool_error(
            "UNKNOWN_FIELD",
            f"Field '{field_name}' không tồn tại trong category '{category}'.",
        )

    setattr(target, field_name, value)
    _session_repo.save_session(session)
    return _tool_success(
        "updated_field",
        {"category": category, "field_name": field_name, "value": value},
    )
