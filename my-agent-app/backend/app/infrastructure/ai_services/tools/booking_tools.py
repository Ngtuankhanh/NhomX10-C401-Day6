"""Booking tools for Agent A.
"""
from __future__ import annotations
import requests
import json
from langchain_core.tools import tool

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
        
        # Chỉ trả về các thông tin cần thiết để tiết kiệm token
        compact_data = [
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "city": item.get("geo_division"),
                "site_uid": item.get("vinmec_site_uid")
            }
            for item in data
        ]
        return json.dumps(compact_data, ensure_ascii=False)
    except Exception as e:
        return f"Lỗi khi lấy danh sách bệnh viện: {str(e)}"

@tool
def search_doctors_tool(speciality_id: int, place_id: int) -> str:
    """Tìm danh sách bác sĩ dựa trên chuyên khoa và cơ sở y tế.
    
    Args:
        speciality_id: ID của chuyên khoa (lấy từ kết quả của Specialist Agent).
        place_id: ID của cơ sở Vinmec (lấy từ list_facilities_tool).
    """
    url = f"https://api2.vinmec.com/api/v1/auto-booking/vinmec/ab-doctor/?ab_doctor_speciality_id={speciality_id}&vinmec_place_id={place_id}"
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
                "price": item.get("price", {}).get("local")
            }
            for item in data
        ]
        return json.dumps(compact_data, ensure_ascii=False)
    except Exception as e:
        return f"Lỗi khi tìm bác sĩ: {str(e)}"

@tool
def get_doctor_slots_tool(doctor_id: int, speciality_id: int, place_id: int, date: str) -> str:
    """Lấy danh sách các giờ khám còn trống của một bác sĩ trong một ngày cụ thể.
    
    Args:
        doctor_id: ID của bác sĩ.
        speciality_id: ID chuyên khoa.
        place_id: ID cơ sở y tế.
        date: Ngày muốn khám (định dạng YYYY-MM-DD, ví dụ: 2026-04-21).
    """
    url = f"https://api2.vinmec.com/api/v1/auto-booking/vinmec/ab-time-slot/?doctor_id={doctor_id}&doctor_speciality_id={speciality_id}&vinmec_place_id={place_id}&date={date}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        available_slots = [
            {
                "slot_id": item.get("id"),
                "time": item.get("start_time").split("T")[1][:5] if "T" in item.get("start_time", "") else "",
                "price": item.get("price")
            }
            # Chỉ lấy các slot còn khả dụng
            for item in data if item.get("is_avaiable") and not item.get("is_booked")
        ]
        return json.dumps(available_slots, ensure_ascii=False)
    except Exception as e:
        return f"Lỗi khi lấy lịch bác sĩ: {str(e)}"

@tool
def get_specialties_tool(place_id: int) -> str:
    """Lấy danh sách các chuyên khoa chính thức của một cơ sở Vinmec.
    
    Args:
        place_id: ID của cơ sở Vinmec.
    """
    url = f"https://api2.vinmec.com/api/v1/auto-booking/vinmec/doctor-speciality/?vinmec_place_id={place_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        compact_data = [
            {
                "speciality_id": item.get("id"),
                "name": item.get("title"),
                "description": item.get("description")
            }
            for item in data if item.get("ab_booking_enabled")
        ]
        return json.dumps(compact_data, ensure_ascii=False)
    except Exception as e:
        return f"Lỗi khi lấy danh sách chuyên khoa: {str(e)}"

@tool
def suggest_hospital_by_location_tool(user_location: str) -> str:
    """Gợi ý bệnh viện Vinmec gần nhất dựa trên tỉnh thành hoặc địa chỉ của người dùng.
    
    Args:
        user_location: Tỉnh thành hoặc địa chỉ người dùng cung cấp (ví dụ: 'Hà Nội', 'HCM').
    """
    # Lấy danh sách gốc từ tool sẵn có
    try:
        url = "https://api2.vinmec.com/api/v1/auto-booking/vinmec/vinmec-place/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        user_loc_lower = user_location.lower()
        matches = []
        
        for item in data:
            title = item.get("title", "").lower()
            city = item.get("geo_division", "").lower()
            
            # Simple keyword matching
            if user_loc_lower in title or user_loc_lower in city or city in user_loc_lower:
                matches.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "city": item.get("geo_division")
                })
        
        if not matches:
            return f"Không tìm thấy bệnh viện nào tại '{user_location}'. Bạn hãy xem danh sách toàn bộ các cơ sở: {json.dumps([{'id': x.get('id'), 'title': x.get('title')} for x in data[:5]], ensure_ascii=False)}"
            
        return json.dumps(matches, ensure_ascii=False)
    except Exception as e:
        return f"Lỗi khi tìm kiếm bệnh viện theo vị trí: {str(e)}"

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
    gender: int = 1
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
        "type": 2
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False)
    except Exception as e:
        return f"Lỗi khi gửi yêu cầu đặt lịch: {str(e)}"

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
    gender: int = 1
) -> str:
    """Xác nhận đặt lịch khám bằng mã OTP (Giai đoạn 2: Hoàn tất).
    
    Hãy dùng tool này sau khi người dùng cung cấp mã OTP được gửi về điện thoại.
    
    Args:
        otp_code: Mã OTP khách hàng cung cấp.
        verif_id: Mã định danh xác thực (lấy từ kết quả tool create_booking_tool).
        email: Email liên hệ (Không bắt buộc).
        ... (các tham số khác giống tool create_booking_tool)
    """
    url = "https://www.vinmec.com/api/v2/booking" # Sửa lại URL chuẩn cho OTP nếu cần
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
        "type": 2
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False)
    except Exception as e:
        return f"Lỗi khi xác nhận OTP: {str(e)}"

@tool
def update_booking_field_tool(
    field_name: str, 
    value: str | int | None, 
    category: str = "booking_context",
    thread_id: str = "default-thread"
) -> str:
    """Cập nhật một trường thông tin vào bộ nhớ phiên khám (để hiển thị trên giao diện người dùng).
    
    Hãy dùng tool này ngay khi người dùng xác nhận một thông tin nào đó (ví dụ: chọn xong bác sĩ, nhập xong tên).
    
    Args:
        field_name: Tên trường cần cập nhật (ví dụ: 'facility_name', 'doctor_name', 'name', 'phone_number', 'booking_date').
        value: Giá trị mới.
        category: Nhóm thông tin ('booking_context' hoặc 'patient_info').
        thread_id: ID phiên chat.
    """
    from app.presentation.api.dependencies import _session_repo
    
    session = _session_repo.get_session(thread_id)
    if not session:
        return "Không tìm thấy phiên để cập nhật."
        
    if category == "booking_context":
        setattr(session.booking_context, field_name, value)
    elif category == "patient_info":
        setattr(session.patient_info, field_name, value)
    elif category == "session":
        setattr(session, field_name, value)
        
    _session_repo.save_session(session)
    return f"Đã cập nhật {field_name} thành {value}."





