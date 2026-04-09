"""Test script for Agent A Full Orchestration Flow.
"""
import sys
from pathlib import Path

# Thêm root vào sys.path để import được app
sys.path.append(str(Path(__file__).parent.parent))

from app.presentation.api.dependencies import get_chat_service

def test_full_booking_flow():
    service = get_chat_service()
    
    # 1. Khởi tạo session
    print("--- [BƯỚC 1: KHỞI TẠO] ---")
    session_resp = service.create_session()
    session_id = session_resp["session_id"]
    print(f"Assistant: {session_resp['assistant_message']['content']}")
    
    # Kịch bản các câu thoại của người dùng
    user_inputs = [
        "Tôi bị đau đầu và chóng mặt từ sáng nay.",
        "Tôi ở khu vực Hai Bà Trưng, Hà Nội.",
        "Tôi muốn đặt lịch khám vào ngày 21/04/2026. Hãy tìm bác sĩ giúp tôi.",
        "Tôi chọn bác sĩ Nguyễn Mạnh Tường.",
        "Tôi chọn giờ 08:30.",
        "Tên tôi là Nguyễn Văn A, SĐT 0912345678, sinh ngày 11/02/1990."
    ]
    
    for i, user_msg in enumerate(user_inputs, 2):
        print(f"\n--- [BƯỚC {i}: NGƯỜI DÙNG GỬI TIN NHẮN] ---")
        print(f"User: {user_msg}")
        
        resp = service.send_user_message(session_id, user_msg)
        print(f"Assistant: {resp['assistant_message']['content']}")
        
        # In ra các tool call nếu có (nếu hệ thống log được)
        # Ở đây ta chỉ quan sát phản hồi text của Agent A.

if __name__ == "__main__":
    # Lưu ý: Cần set OPENAI_API_KEY trong môi trường trước khi chạy
    # export OPENAI_API_KEY=sk-...
    try:
        test_full_booking_flow()
    except Exception as e:
        print(f"Lỗi khi chạy test: {e}")
