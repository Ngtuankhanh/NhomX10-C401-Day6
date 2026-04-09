# Prototype — AI Medical Triage & Booking

## 1. Mô tả sản phẩm
Đây là bản mẫu (prototype) của ứng dụng trợ lý y tế thông minh, tích hợp khả năng hội thoại tự nhiên để sàng lọc bệnh (triage) và quy trình đặt lịch khám thực tế tại các cơ sở bệnh viện. Hệ thống sử dụng kiến trúc đa tác nhân (Multi-agent) để đảm bảo độ chính xác và khả năng điều phối luồng công việc phức tạp.

## 2. Level: Working Prototype
- **Trạng thái:** Có AI chạy thật, tích hợp GPT-4o.
- **Tính năng:**
    - Nhận diện triệu chứng qua chat.
    - Gọi Specialist Agent để phân loại chuyên khoa.
    - Truy xuất dữ liệu bác sĩ/cơ sở từ API thật/mock data chuẩn.
    - Luồng đặt lịch 2 bước kèm OTP xác thực.

## 3. Links
- **GitHub Repository:** [Repo nhóm](https://github.com/Ngtuankhanh/NhomX10-C401-Day6)

## 4. Công nghệ & API
- **Frontend:** Next.js 14, Tailwind CSS, Lucide Icons.
- **Backend:** Python FastAPI, LangGraph (Orchestration Framework).
- **AI Model:** GPT-4o (Main Orchestrator), GPT-4o-mini (Specialist Agent).
- **Database/Storage:** In-memory session store (Local testing), CSV/JSON data files.

## 5. Phân công đóng góp (Team X10)

| Thành viên | Vai trò | Đóng góp chính | Output |
|-----------|---------|---------------|--------|
| **Nguyễn Tuấn Khanh** | Technical Leader | Setup project, thiết kế LangGraph orchestrator, UI/UX Design, Integrate API, design agent workflow, design evaluation LLM as a Judge and write spec final, viết kịch bản test | `backend/app/...`, `group/spec-final.md`, `frontend/app/...` |
| **Cao Chí Hải** | AI Engineering | Viết và tối ưu System Prompt, thiết kế Knowledge Graph, thiết kế code cho Specialist Agent | `backend/app/infrastructure/ai_services/agents/prompts.py` |