# Reflection Cá Nhân — Hackathon Day 06

**Họ và Tên:** Nguyễn Tuấn Khanh
**Mã Học Viên:** 2A202600409

---

## 1. Role cụ thể trong nhóm

Technical Leader kiêm Full-stack Developer. Phụ trách toàn bộ kiến trúc kỹ thuật của hệ thống: từ thiết kế LangGraph orchestrator cho Agent Orchestrator, tích hợp các booking tools với API Vinmec thật, xây dựng pipeline đánh giá chất lượng AI (LLM-as-a-Judge), thiết kế UI/UX frontend và viết bản SPEC final cho nhóm.

---

## 2. Phần phụ trách cụ thể (Có output rõ ràng)

- **Output 1:** Thiết kế và implement toàn bộ kiến trúc backend theo Clean Architecture (Domain / Application / Infrastructure / Presentation). Cụ thể: `backend/app/domain/entities.py`, `backend/app/application/use_cases/chat_handler.py`, `backend/app/infrastructure/ai_services/agents/agent.py`. Agent A sử dụng LangGraph `create_react_agent` với `MemorySaver` để duy trì lịch sử hội thoại theo `thread_id`.

- **Output 2:** Viết và tích hợp toàn bộ 8 tools cho Agent A, bao gồm `specialist_agent_tool`, `list_facilities_tool`, `search_doctors_tool`, `get_doctor_slots_tool`, `create_booking_tool`, `confirm_booking_tool`, `update_booking_field_tool` — tất cả trong `backend/app/infrastructure/ai_services/tools/booking_tools.py`. Đặc biệt, luồng đặt lịch 2 bước (Draft + OTP) với Vinmec API được tôi thiết kế và implement hoàn toàn.

- **Output 3:** Xây dựng pipeline observability và evaluation (LLM-as-a-Judge) tại `backend/app/observability/`. Mỗi request của user đều được ghi lại dưới dạng `AIRequestTrace` với đầy đủ thông tin về conversation state, tool calls, và kết quả trả về. Judge Agent sau đó chấm điểm từng trace theo các tiêu chí như `correctness`, `safety`, `relevance` — giúp nhóm có dữ liệu khách quan để cải thiện system prompt.

---

## 3. Đánh giá phần SPEC

- **Mạnh nhất:** Phần **Top 3 Failure Modes** và **Emergency Guardrail**. Đây là phần tôi dành nhiều thời gian nhất để suy nghĩ vì trong lĩnh vực y tế, failure không phải lỗi kỹ thuật mà còn là rủi ro sức khoẻ thật sự. Việc xác định rõ "Hallucination thông tin bác sĩ" và có giải pháp "Strict API Mapping" là quyết định thiết kế đúng đắn và có thể triển khai ngay được, không mang tính lý thuyết.

- **Yếu nhất:** Phần **ROI 3 kịch bản**. Các con số được đưa ra (50/200/1000 user/ngày) thiếu cơ sở benchmark thực tế. Lý tưởng nhất nên tham khảo số liệu thực tế về lưu lượng đặt lịch qua tổng đài/website của Vinmec, từ đó tính ROI tốt hơn. Hiện tại phần này thiên về ước tính cảm tính.

---

## 4. Các đóng góp cụ thể khác

- Thiết kế và viết `group/spec-final.md` — bao gồm cả 6 phần bắt buộc của Hackathon (AI Canvas, User Stories 4 paths, Eval Metrics, Failure Modes, ROI, Mini Spec) và toàn bộ phần kỹ thuật phía sau (Agent contracts, State machine, Tool definitions).

- Debug lỗi import pipeline trong kiến trúc Clean Architecture khi các module ở tầng Infrastructure cố gắng import trực tiếp từ Application layer. Tìm ra nguyên nhân là circular dependency và giải quyết bằng cách tạo `interfaces/__init__.py` đúng cách để expose các abstract interfaces.

- Test end-to-end 3 luồng chính: Happy path (triệu chứng rõ -> khoa -> đặt lịch thành công), Uncertain path (Agent B hỏi lại thêm 1 câu -> chốt khoa), và Emergency path (phát hiện từ khoá cấp cứu -> dừng flow booking, hiển thị cảnh báo 115).

---

## 5. Một điều học được mới

Trước hackathon tôi nghĩ LangGraph chỉ là một layer bọc thêm lên LangChain, không có gì đặc biệt. Sau khi implement mới hiểu: điểm mạnh thật sự của LangGraph là **stateful checkpointing** — nó tự động lưu và phục hồi toàn bộ message history và tool state giữa các lượt gọi mà không cần tôi tự viết logic session management. `MemorySaver` + `thread_id` giải quyết hoàn toàn bài toán multi-turn conversation mà trước đây tôi luôn phải tự làm bằng Redis hoặc database. Đây là kiến thức tôi sẽ áp dụng ngay vào các dự án thực tế sau này.

---

## 6. Nếu làm lại, bạn sẽ thay đổi điều gì?

Tôi sẽ **chốt contract JSON giữa Agent A và Agent B từ ngày đầu** thay vì để hai người làm song song và sync với nhau vào giữa chừng. Trong hackathon này, tôi phải điều chỉnh input/output schema của `specialist_agent_tool` 3 lần vì thành viên làm Agent B thay đổi format output. Nếu chốt cứng schema như `SpecialistAgentInput` và `SpecialistAgentOutput` bằng Pydantic model ngay từ 9h sáng, cả hai người có thể làm hoàn toàn độc lập và ghép vào nhau dễ dàng — tiết kiệm ít nhất 2 tiếng debug.

---

## 7. AI giúp gì và AI "sai" ở đâu?

- **AI giúp:** Tôi dùng Antigravity/Claude để generate scaffold cho toàn bộ cấu trúc Clean Architecture (Domain/Application/Infrastructure/Presentation layers) — công việc thường mất vài giờ nếu làm tay, nay chỉ mất khoảng 20 phút để review và điều chỉnh. Ngoài ra Claude rất hiệu quả trong việc viết docstring, Pydantic schema, và gợi ý edge case cho failure handling mà tôi chưa nghĩ tới (ví dụ case OTP hết hạn cần re-trigger booking step 1, không chỉ re-send OTP).

- **AI sai/nhiễu:** Khi tôi hỏi Claude về cách thiết kế LangGraph multi-agent với `create_react_agent`, nó gợi ý dùng `StateGraph` và `add_conditional_edges` phức tạp không cần thiết. Nếu áp dụng ngay sẽ mất rất nhiều thời gian implement một graph nặng nề trong khi `create_react_agent` kèm tool calling đã giải quyết được bài toán gọn hơn nhiều. Bài học: AI giỏi gợi ý giải pháp "đúng sách" nhưng không nhất thiết là giải pháp tối ưu cho scope và deadline của hackathon.