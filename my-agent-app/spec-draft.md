# Đặc Tả Sản Phẩm
# Medical Symptom Chatbot – Gợi ý Chuyên khoa & Đặt lịch khám

**Ngày tạo:** 08/04/2026

---

## 0. Bản đính chính triển khai MVP (Source of Truth)

Phần này **override cho MVP** nếu có khác biệt với các section tổng quan bên dưới. Mục tiêu là đưa tài liệu về mức có thể implement ngay với monorepo hiện tại.

### 0.1 Quyết định kiến trúc cho MVP

- **Kiến trúc khuyến nghị:** `Agent A orchestrator + Agent B as tool/subgraph`
- **Agent A** là agent duy nhất nói chuyện với người dùng, quản lý state hội thoại, hỏi thêm thông tin, chọn thời điểm gọi tools và điều phối đặt lịch.
- **Agent B** không giao tiếp trực tiếp với user. Agent B nhận input JSON chuẩn hoá từ Agent A và trả về output JSON chuẩn hoá để Agent A xử lý tiếp.
- **Knowledge Graph** ở MVP chỉ là **mock data local** (`kg.json`, `symptoms.csv`, `specialties.csv`, `facilities.csv`, `doctors.csv`). Không cần dựng graph database thật.
- **Các tool** được define rõ schema trước, triển khai dần theo từng phase. Với Agent B, hiện tại chỉ cần define interface và để comment `TODO` ở phần logic nội bộ nếu đó là phần việc của người khác.
- **Booking** tách thành 2 bước:
  1. Tạo yêu cầu booking ban đầu để nhận `verif_id`
  2. Nhận OTP từ user rồi confirm booking
- **UI/UX** phải phản ánh trạng thái hệ thống theo từng bước: đang phân tích triệu chứng, đang kiểm tra lịch, đang gửi OTP, đang xác nhận lịch.

### 0.2 Điều chỉnh quan trọng so với spec hiện tại

- Không xem MVP này là hệ thống tư vấn y khoa hoàn chỉnh. Đây là chatbot **gợi ý chuyên khoa và hỗ trợ đặt lịch**, không chẩn đoán bệnh.
- Không đưa vào MVP các hạng mục sau nếu chưa thật cần:
  - Redis/session store riêng
  - Dashboard admin
  - Giao diện quản trị KG
  - Email service riêng
  - KPI production như `500 concurrent sessions`, `99.5% uptime`
- Dữ liệu bác sĩ/chuyên khoa/cơ sở trước mắt lấy từ mock CSV hoặc API có sẵn; LLM không được tự bịa thông tin bác sĩ hay slot.

### 0.3 Mismatch cần xử lý ngay trong repo hiện tại

- Frontend hiện tại được scaffold từ `create-agent-chat-app`, đang kỳ vọng nói chuyện với **LangGraph server API** (`/info`, thread, stream, tool events).
- Backend hiện tại mới chỉ là **FastAPI thường** với endpoint `/agent/invoke`, chưa tương thích với frontend streaming hiện tại.
- Vì vậy cần chốt một trong hai hướng:
  - **Hướng khuyến nghị:** dùng **Python LangGraph runtime** làm backend chính để frontend giữ nguyên mô hình streaming/tool events; FastAPI chỉ giữ vai trò health/internal adapters khi cần.
  - **Hướng thay thế:** giữ FastAPI làm backend chính và refactor frontend sang client chat custom. Hướng này tốn công frontend hơn.
- Với yêu cầu hiện tại, nên chọn **Hướng khuyến nghị** để tận dụng tối đa UI starter và trạng thái tool/loading sẵn có.

### 0.4 Kiến trúc triển khai đề xuất

```text
Next.js Chat UI
  -> LangGraph stream API
  -> Agent A Orchestrator Graph (Python)
      -> emergency_guard node
      -> intake/parse node
      -> specialist_agent_tool (Agent B)
      -> facility/doctor/slot tools
      -> booking_init tool
      -> booking_confirm_otp tool
      -> fallback/support node
  -> Mock Data Layer
      -> kg.json
      -> specialties.csv
      -> facilities.csv
      -> doctors.csv
```

### 0.5 Trách nhiệm của từng agent

#### Agent A - Conversation Orchestrator

**Mục tiêu:**
- Duy trì hội thoại tự nhiên với người dùng
- Thu thập triệu chứng và thông tin booking theo từng bước
- Parse dữ liệu hội thoại thành JSON chuẩn
- Gọi Agent B đúng thời điểm
- Xử lý uncertainty, retry, fallback và UX messaging

**Không làm:**
- Không tự chẩn đoán bệnh
- Không tự sinh thông tin bác sĩ/cơ sở/slot nếu chưa có từ data source
- Không suy đoán chuyên khoa khi đã có structured result từ Agent B trừ khi rơi vào luồng fallback

#### Agent B - Specialist Classifier

**Mục tiêu:**
- Nhận `symptom payload` đã chuẩn hoá
- Phân tích mock KG
- Trả về `specialty suggestion result` dạng JSON

**Phạm vi MVP:**
- Chỉ cần define interface, output contract, retry/failure contract
- Logic nội bộ có thể để `TODO` nếu thuộc task owner khác

### 0.6 State machine thực tế cho Agent A

| State | Ý nghĩa | Điều kiện vào | Điều kiện ra |
|---|---|---|---|
| `GREETING` | Chào user, giải thích phạm vi hỗ trợ | Bắt đầu session | User mô tả vấn đề |
| `COLLECTING_SYMPTOMS` | Thu triệu chứng, thời gian, mức độ | Chưa đủ symptom payload | Có đủ tối thiểu để parse |
| `ANALYZING_SPECIALTY` | Gọi Agent B | Có payload hợp lệ | Có kết quả / lỗi |
| `ASKING_FOLLOWUP` | Hỏi thêm khi Agent B chưa chắc chắn | Agent B trả về `question` | User trả lời hoặc từ chối |
| `SHOWING_SPECIALTY_RESULT` | Hiển thị khoa gợi ý + disclaimer | Có kết quả | User muốn đặt lịch |
| `COLLECTING_BOOKING_PREFS` | Lấy cơ sở, chuyên khoa, bác sĩ, ngày | User đồng ý đặt lịch | Có đủ thông tin tìm slot |
| `SHOWING_SLOTS` | Hiển thị slot khám | Có doctor/date/place | User chọn slot |
| `COLLECTING_PATIENT_INFO` | Họ tên, giới tính, DOB, phone, email | Slot đã chọn | Đủ thông tin submit |
| `CONFIRMING_BOOKING` | Hiển thị summary | Có booking draft | User xác nhận |
| `WAITING_OTP` | Chờ user nhập OTP | Submit step 1 thành công | User nhập OTP hoặc huỷ |
| `BOOKING_COMPLETED` | Booking thành công | OTP hợp lệ | Kết thúc |
| `FALLBACK_SUPPORT` | Lỗi/failure/out-of-scope | Tool lỗi hoặc flow không xử lý được | Kết thúc hoặc quay lại |

### 0.7 State dữ liệu tối thiểu nên có

```json
{
  "conversation_state": "COLLECTING_SYMPTOMS",
  "triage_attempt_count": 1,
  "symptom_payload": {
    "chief_complaint": "đau đầu",
    "symptoms": ["đau đầu", "buồn nôn"],
    "duration": "3 ngày",
    "severity": null,
    "body_parts": ["đầu"],
    "risk_factors": [],
    "demographics": {
      "age": 31,
      "gender": "female"
    }
  },
  "specialty_assessment": {
    "status": "uncertain",
    "specialty_name": "Nội thần kinh",
    "description": "Triệu chứng hướng nhiều tới nhóm thần kinh",
    "question": "Bạn có chóng mặt hoặc ù tai không?",
    "confidence": 0.68
  },
  "booking_context": {
    "place_id": null,
    "facility_name": null,
    "speciality_id": null,
    "speciality_name": null,
    "doctor_id": null,
    "doctor_name": null,
    "booking_date": null,
    "booking_time": null
  },
  "patient_info": {
    "name": null,
    "gender": null,
    "phone_number": null,
    "date_of_birth": null,
    "email": null,
    "inquiry_info": null
  },
  "booking_verification": {
    "verif_id": null,
    "otp_required": false
  },
  "failure_state": {
    "agent_b_failures": 0,
    "slot_lookup_failures": 0,
    "booking_failures": 0,
    "last_error_code": null
  }
}
```

### 0.8 Input contract từ Agent A sang Agent B

```json
{
  "conversation_summary": "User bị đau đầu và buồn nôn 3 ngày nay",
  "patient_profile": {
    "age": 31,
    "gender": "female"
  },
  "symptoms": [
    {
      "name": "đau đầu",
      "duration": "3 ngày",
      "severity": null,
      "body_part": "đầu"
    },
    {
      "name": "buồn nôn",
      "duration": "3 ngày",
      "severity": null,
      "body_part": null
    }
  ],
  "triage_attempt_count": 1
}
```

### 0.9 Output contract từ Agent B về Agent A

`question` chỉ xuất hiện khi thật sự cần hỏi thêm để tăng độ chắc chắn.

```json
{
  "specialty_name": "Nội thần kinh",
  "description": "Đau đầu kèm buồn nôn kéo dài vài ngày phù hợp nhóm thần kinh hơn các nhóm khác",
  "confidence": 0.78,
  "question": "Bạn có chóng mặt hoặc nhìn mờ không?"
}
```

Nếu Agent B đã đủ chắc chắn:

```json
{
  "specialty_name": "Da liễu",
  "description": "Triệu chứng tập trung ở vùng da, phù hợp chuyên khoa da liễu",
  "confidence": 0.89
}
```

Nếu Agent B lỗi:

```json
{
  "error": {
    "code": "AGENT_B_TIMEOUT",
    "message": "Specialist classifier timed out"
  }
}
```

### 0.10 Danh sách tool cần define trước

#### Tool nhóm symptom / triage

1. `parse_symptom_payload`
   - Input: chat history + latest user message
   - Output: structured symptom payload
   - Ghi chú: có thể implement bằng LLM structured output hoặc rule-based hybrid

2. `specialist_agent_tool`
   - Input: `SpecialistAgentInput`
   - Output: `SpecialistAgentOutput`
   - Ghi chú: phần nội bộ Agent B để `TODO`

3. `fallback_specialty_tool`
   - Input: symptom payload
   - Output: specialty tạm thời theo rule/keyword map
   - Dùng khi Agent B fail hoặc user không muốn trả lời thêm

#### Tool nhóm data mock

4. `list_facilities_tool`
   - Data source: `facilities.csv`

5. `list_specialties_tool`
   - Data source: `specialties.csv`

6. `list_doctors_tool`
   - Data source: `doctors.csv`
   - Có filter theo `place_id`, `speciality_id`

7. `get_doctor_slots_tool`
   - API:
     `GET https://api2.vinmec.com/api/v1/auto-booking/vinmec/ab-time-slot/?doctor_id=...&doctor_speciality_id=...&vinmec_place_id=...&date=YYYY-MM-DD`
   - Output: danh sách slot chuẩn hoá để render

#### Tool nhóm booking

8. `create_booking_request_tool`
   - API: `POST https://www.vinmec.com/api/v3/booking`
   - Output: `verif_id`, masked username
   - Hành vi: chỉ gọi khi đã đủ patient info + slot/doctor

9. `confirm_booking_otp_tool`
   - API: `POST https://www.vinmec.com/api/v3/booking`
   - Input bổ sung: `otp_code`, `verif_id`
   - Output: booking confirmation payload

### 0.11 Nguyên tắc orchestration của Agent A

1. Luôn parse message user thành structured state trước khi quyết định bước tiếp theo.
2. Chỉ gọi Agent B khi đã có ít nhất triệu chứng chính.
3. Nếu Agent B trả về `question`, Agent A hỏi lại user bằng ngôn ngữ tự nhiên và chỉ hỏi **một câu rõ ràng mỗi lượt**.
4. Nếu user trả lời hữu ích, cập nhật `symptom_payload` rồi gọi lại Agent B.
5. Nếu user không muốn trả lời thêm hoặc thông tin mới không hữu ích, dùng kết quả tốt nhất hiện tại.
6. Nếu Agent B fail:
   - Retry 1 lần với payload rút gọn
   - Nếu vẫn fail, dùng `fallback_specialty_tool`
   - Nếu fallback cũng không chắc, chuyển `Chưa xác định chuyên khoa` + hỗ trợ đặt lịch đa khoa hoặc hotline
7. Không để loop hỏi symptom quá 3 lần.

### 0.12 Failure handling bắt buộc

| Failure | Cách xử lý ở Agent A | UX cần hiển thị |
|---|---|---|
| Agent B timeout | Retry 1 lần, sau đó fallback | "Hệ thống đang phân tích lại triệu chứng của bạn..." |
| Agent B trả JSON lỗi | Kill flow hiện tại của Agent B, ghi log, fallback | "Tôi đang thử một cách phân loại khác để tránh bỏ sót thông tin." |
| Không có slot | Gợi ý ngày khác hoặc cơ sở khác | "Ngày này hiện chưa còn lịch phù hợp, tôi có thể tìm ngày/cơ sở khác." |
| Booking step 1 fail | Cho submit lại hoặc hotline | "Tôi chưa gửi được yêu cầu đặt lịch. Bạn muốn thử lại không?" |
| OTP sai | Báo lỗi và cho nhập lại | "Mã OTP chưa đúng, bạn vui lòng kiểm tra và nhập lại." |
| OTP hết hạn | Gọi lại step 1 | "Mã đã hết hạn, tôi sẽ gửi lại một mã mới." |
| User từ chối trả lời thêm triệu chứng | Dùng kết quả hiện tại | "Tôi sẽ dùng thông tin hiện có để gợi ý chuyên khoa gần nhất." |
| Triệu chứng cấp cứu | Dừng flow booking thường | "Triệu chứng này có thể cần cấp cứu. Vui lòng gọi 115 hoặc đến cơ sở y tế gần nhất ngay." |

### 0.13 Trạng thái UX nên có trong chat

- `typing`: bot đang soạn phản hồi
- `analyzing_symptoms`: đang gọi Agent B
- `finding_doctors`: đang lọc bác sĩ/cơ sở
- `loading_slots`: đang gọi API slot
- `submitting_booking`: đang gửi yêu cầu đặt lịch
- `waiting_for_otp`: đang chờ người dùng nhập OTP
- `confirming_booking`: đang xác nhận OTP
- `recovering_from_error`: đang fallback hoặc retry

Các status text nên viết theo ngôn ngữ thân thiện:
- "Đang phân tích triệu chứng..."
- "Đang tìm bác sĩ và lịch phù hợp..."
- "Đang gửi mã xác nhận..."
- "Đang xác nhận lịch hẹn..."

### 0.14 Cấu trúc mock data đề xuất

```text
backend/app/data/
  kg.json
  specialties.csv
  facilities.csv
  doctors.csv
  doctor_specialties.csv
```

Gợi ý fields tối thiểu:

- `specialties.csv`: `speciality_id`, `speciality_name`, `description`
- `facilities.csv`: `place_id`, `facility_name`, `geo_division`, `address`
- `doctors.csv`: `doctor_id`, `doctor_name`, `doctor_ad`, `place_id`
- `doctor_specialties.csv`: `doctor_id`, `speciality_id`

### 0.15 Kế hoạch triển khai đề xuất

#### Phase 0 - Chốt nền tảng kỹ thuật

1. Chốt transport backend/frontend:
   - Ưu tiên backend chạy theo LangGraph server contract để không phải phá UI starter.
2. Chốt state schema, tool contracts, folder structure dữ liệu mock.
3. Chốt danh sách chuyên khoa MVP đầu tiên và mapping dữ liệu mock.

#### Phase 1 - Dựng xương sống hội thoại

1. Tạo state model cho Agent A.
2. Tạo graph node cho:
   - intake
   - emergency guard
   - symptom parse
   - Agent B invocation
   - booking flow router
3. Cho chạy end-to-end với mock response cứng từ Agent B.

#### Phase 2 - Tích hợp Agent B theo contract

1. Define `specialist_agent_tool`.
2. Input/output strict JSON.
3. Thêm retry + timeout + fallback path.
4. Thêm counter giới hạn follow-up tối đa 3 lần.

#### Phase 3 - Tích hợp data cơ sở/bác sĩ/slot

1. Load CSV mock cho cơ sở, chuyên khoa, bác sĩ.
2. Implement tool filter bác sĩ theo cơ sở/chuyên khoa.
3. Gọi API slot thật để lấy lịch trống.
4. Chuẩn hoá response thành UI-friendly schema.

#### Phase 4 - Booking 2 bước + OTP

1. Tạo booking draft chuẩn theo payload Vinmec.
2. Validate bắt buộc:
   - họ tên
   - giới tính
   - số điện thoại
   - ngày sinh
   - lý do khám
3. Gọi booking step 1 lấy `verif_id`.
4. Thu OTP từ user.
5. Gọi booking step 2 để confirm.

#### Phase 5 - UX và reliability

1. Gắn loading state theo từng tool.
2. Render summary card trước khi submit booking.
3. Thêm error banner/retry CTA cho từng failure case chính.
4. Thêm disclaimer và emergency interruption rõ ràng.

#### Phase 6 - Test

1. Happy path: symptom -> specialty -> slot -> booking -> OTP -> success
2. Uncertain path: Agent B hỏi thêm 1-2 câu rồi mới chốt
3. User bỏ qua follow-up question
4. Agent B timeout
5. Không có slot
6. OTP sai/hết hạn
7. Emergency keyword interrupt

### 0.16 Ưu tiên build order theo team

- **Bạn phụ trách ngay:**
  - Agent A orchestration
  - state schema
  - tool contracts
  - booking flow
  - failure handling
  - UI loading/status
- **Người khác phụ trách:**
  - logic nội bộ Agent B / KG analysis
- **Cách phối hợp tốt nhất:**
  - phía bạn mock `specialist_agent_tool` bằng response JSON cố định trước
  - team Agent B chỉ cần tuân thủ đúng contract để thay vào sau

---

## 1. Tổng quan dự án

### 1.1 Bối cảnh

Bệnh nhân thường gặp khó khăn khi không biết mình cần đến chuyên khoa nào để thăm khám. Điều này dẫn đến tình trạng đi nhầm khoa, mất thời gian chờ đợi, hoặc trì hoãn điều trị không cần thiết. Hệ thống chatbot y tế này giải quyết bài toán đó bằng cách tự động phân tích triệu chứng, gợi ý chuyên khoa phù hợp và hỗ trợ đặt lịch khám – tất cả trong cùng một luồng hội thoại.

### 1.2 Mô tả sản phẩm

Một chat widget có thể nhúng vào web (embeddable), hoạt động dựa trên kiến trúc **Multi-Agent AI** với hai agent chuyên biệt:

- **Main Agent (Agent 1):** Điều phối toàn bộ luồng hội thoại – chào hỏi, thu thập thông tin, hiển thị kết quả và xác nhận đặt lịch.
- **Specialist Suggestion Agent (Agent 2):** Phân tích triệu chứng thông qua **Knowledge Graph** y tế để gợi ý chuyên khoa phù hợp.

### 1.3 Giả thuyết cốt lõi

> Nếu chatbot có thể phân tích triệu chứng chính xác ≥ 80% và rút ngắn thời gian đặt lịch xuống dưới 5 phút, người dùng sẽ ưu tiên dùng kênh này thay vì gọi tổng đài hoặc trực tiếp đến bệnh viện.

---

## 2. Mục tiêu & chỉ số thành công

### 2.1 Mục tiêu sản phẩm

| # | Mục tiêu | Chỉ số đo lường (KPI) | Mục tiêu 6 tháng |
|---|-----------|----------------------|------------------|
| 1 | Giảm tỉ lệ đến nhầm chuyên khoa | % bệnh nhân cần đổi khoa sau khám | < 15% |
| 2 | Tăng tỉ lệ đặt lịch online | % lịch hẹn tạo qua chatbot | > 30% tổng lịch hẹn |
| 3 | Tăng sự hài lòng người dùng | CSAT Score (từ emoji feedback) | ≥ 4.0 / 5.0 |
| 4 | Giảm tải tổng đài | Số cuộc gọi đặt lịch giảm | > 25% |

### 2.2 Chỉ số sản phẩm

| Chỉ số | Mô tả | Target |
|--------|-------|--------|
| Symptom-to-Specialty Accuracy | Tỉ lệ gợi ý chuyên khoa chính xác | ≥ 80% |
| Booking Completion Rate | Tỉ lệ hoàn tất đặt lịch trong một session | ≥ 65% |
| Average Session Duration | Thời gian từ chào hỏi đến đặt lịch thành công | ≤ 5 phút |
| Agent 2 Recall Rate | Tỉ lệ Agent 2 truy hồi đủ dữ liệu từ Knowledge Graph | ≥ 75% |
| Positive Feedback Rate | % phản hồi "hài lòng" từ emoji rating | ≥ 70% |

---

## 3. Đối tượng người dùng

### 3.1 Người dùng chính

**Persona 1 – Bệnh nhân tự tìm kiếm thông tin**
- Độ tuổi: 25–55
- Có triệu chứng bệnh nhưng không biết nên gặp chuyên khoa nào
- Nhu cầu: Được tư vấn nhanh, đặt lịch tiện lợi mà không cần gọi điện
- Điểm đau: Mất thời gian tìm kiếm, lo ngại đi nhầm khoa

**Persona 2 – Người chăm sóc (Caregiver)**
- Độ tuổi: 30–60
- Đặt lịch hộ cho người thân (cha mẹ, con cái)
- Nhu cầu: Đặt lịch nhanh, nhận xác nhận qua email
- Điểm đau: Khó mô tả chính xác triệu chứng của người khác

### 3.2 Người dùng thứ cấp

- **Admin bệnh viện/phòng khám:** Xem báo cáo feedback, quản lý lịch đặt
- **Bác sĩ:** Nhận thông tin lịch hẹn kèm lý do khám sơ bộ từ chatbot

---

## 4. Phạm vi dự án (Scope)

### 4.1 MVP – Trong phạm vi

- Chat widget nhúng vào web (embeddable via `<script>` tag hoặc `<iframe>`)
- Main Agent xử lý hội thoại đa lượt
- Specialist Suggestion Agent (Agent 2) tích hợp Knowledge Graph
- Vòng lặp thu thập triệu chứng bổ sung (tối đa 3 lần)
- Gợi ý bệnh viện/phòng khám theo vị trí và thời gian mong muốn
- Gợi ý bác sĩ theo chuyên khoa và lịch trống
- Xem thông tin chi tiết bác sĩ
- Thu thập thông tin đặt lịch (họ tên, ngày khám, SĐT, email)
- Xác nhận thông tin trước khi hoàn tất đặt lịch
- Gửi email xác nhận sau khi đặt lịch thành công
- Emoji feedback 3 mức (Hài lòng / Trung bình / Tệ)
- Hiển thị thông tin liên hệ hỗ trợ khi chatbot không đáp ứng được

---

## 5. Kiến trúc hệ thống

### 5.1 Sơ đồ tổng thể

```
┌─────────────────────────────────────────────────────┐
│                    WEB CLIENT                       │
│            (Chat Widget – Embeddable)               │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS / WebSocket
┌──────────────────────▼──────────────────────────────┐
│               API GATEWAY / BFF Layer               │
│         (Auth, Rate Limit, Session Management)      │
└───┬──────────────────────────────────────┬──────────┘
    │                                      │
┌───▼──────────────────┐      ┌────────────▼──────────┐
│   MAIN AGENT (LLM)   │◄────►│  SPECIALIST AGENT     │
│   - Orchestrator     │      │  (Agent 2)            │
│   - Dialog Manager   │      │  - Symptom Extractor  │
│   - Tool Caller      │      │  - KG Query Engine    │
└───┬──────────────────┘      │  - Completeness Check │
    │                         └────────────┬──────────┘
    │ Tool Calls                           │
    ▼                                      ▼
┌─────────────────────────────────────────────────────┐
│                    TOOL LAYER                       │
│  ┌──────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │ Hospital &   │  │ Doctor List │  │ Booking   │  │
│  │ Clinic Finder│  │ & Schedule  │  │ & Notify  │  │
│  └──────────────┘  └─────────────┘  └───────────┘  │
└──────────────────────────┬──────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────┐
│           KNOWLEDGE GRAPH (Medical KB)              │
│   Symptom → Disease → Specialty → ICD-10 Codes     │
│   (Thư viện đồ thị nội bộ – phù hợp quy mô nhỏ)  │
└─────────────────────────────────────────────────────┘
```

### 5.2 Công nghệ đề xuất

| Thành phần | Công nghệ | Lý do |
|------------|-----------|-------|
| LLM Core | Claude Sonnet / GPT-4o | Độ chính xác cao, hỗ trợ function calling |
| Knowledge Graph | Thư viện đồ thị nhúng (phù hợp quy mô nhỏ) | Query quan hệ triệu chứng–bệnh–chuyên khoa |
| Email Service | SendGrid / AWS SES | Gửi email xác nhận lịch hẹn |
| Session Storage | Redis | Lưu trạng thái hội thoại stateless |

---

## 6. Đặc tả Agent

### 6.1 Main Agent (Agent 1)

**Vai trò:** Điều phối toàn bộ hội thoại, giao tiếp trực tiếp với người dùng, gọi Agent 2 và các Tool.

**Hành vi cốt lõi:**

> Lắng nghe và thu thập triệu chứng từ người dùng, gợi ý chuyên khoa dựa trên kết quả phân tích, hỗ trợ đặt lịch khám phù hợp. Luôn thân thiện, rõ ràng và không bao giờ đưa ra chẩn đoán bệnh cụ thể.

**State Machine của Main Agent:**

| State | Mô tả | Điều kiện chuyển tiếp |
|-------|-------|-----------------------|
| `GREETING` | Chào hỏi người dùng | Người dùng mô tả triệu chứng |
| `COLLECTING_SYMPTOMS` | Thu thập triệu chứng | Đã có đủ triệu chứng ban đầu |
| `ANALYZING` | Gọi Agent 2 phân tích | Agent 2 trả về kết quả |
| `SHOWING_RESULT_UNCERTAIN` | Kết quả chưa chắc, gợi ý bổ sung | User chọn thêm hoặc bỏ qua |
| `SHOWING_RESULT_CONFIRMED` | Kết quả đủ chắc chắn | User xác nhận tiếp tục |
| `COLLECTING_LOCATION_TIME` | Hỏi địa điểm và thời gian | User cung cấp đủ thông tin |
| `SUGGESTING_FACILITIES` | Gợi ý bệnh viện/phòng khám | User chọn cơ sở |
| `SUGGESTING_DOCTORS` | Gợi ý bác sĩ | User chọn bác sĩ |
| `COLLECTING_BOOKING_INFO` | Thu thập họ tên, SĐT, email, ngày giờ | Đủ thông tin |
| `CONFIRMING_BOOKING` | Hiển thị thông tin xác nhận | User đồng ý hoặc yêu cầu sửa |
| `BOOKING_SUCCESS` | Đặt lịch thành công | Kết thúc luồng |
| `SHOWING_CONTACT_INFO` | Hiển thị thông tin liên hệ hỗ trợ | — |

---

### 6.2 Specialist Suggestion Agent (Agent 2)

**Vai trò:** Được gọi bởi Main Agent. Phân tích triệu chứng, truy vấn Knowledge Graph, đánh giá độ đầy đủ thông tin và trả kết quả chuẩn hoá về cho Main Agent.

**Quy trình xử lý nội bộ:**

**Bước 1 – Trích xuất thực thể y tế (Medical NER)**

Từ ngữ cảnh hội thoại và danh sách triệu chứng, Agent 2 trích xuất:
- Triệu chứng chính và triệu chứng kèm theo
- Vị trí giải phẫu liên quan
- Thời gian kéo dài và mức độ nghiêm trọng (nhẹ / vừa / nặng)
- Các yếu tố liên quan: tiền sử bệnh, thuốc đang dùng

**Bước 2 – Truy hồi Knowledge Graph**

Truy vấn đồ thị theo hướng: Triệu chứng → Bệnh → Chuyên khoa, lấy kết quả theo tần suất xuất hiện và độ liên quan.

**Bước 3 – Đánh giá độ đầy đủ thông tin (Completeness Score)**

| Tiêu chí | Trọng số |
|----------|----------|
| Có ít nhất 1 triệu chứng chính | 40% |
| Thời gian kéo dài | 20% |
| Vị trí giải phẫu | 20% |
| Mức độ nghiêm trọng | 10% |
| Yếu tố nguy cơ / tiền sử | 10% |

- **Score ≥ 70:** Thông tin đầy đủ → trả kết quả chuyên khoa
- **Score < 70:** Thông tin chưa đủ → trả kết quả + danh sách câu hỏi gợi ý bổ sung + cờ `is_complete: false`

**Ví dụ output trả về cho Main Agent:**

```json
{
  "is_complete": true,
  "completeness_score": 82,
  "suggested_specialty": {
    "primary": {
      "name": "Thần kinh",
      "code": "NEURO",
      "confidence": 0.87,
      "reason": "Triệu chứng đau đầu + chóng mặt + buồn nôn tập trung vào hệ thần kinh"
    },
    "alternatives": [
      { "name": "Tai Mũi Họng", "code": "ENT", "confidence": 0.62 },
      { "name": "Tim mạch", "code": "CARDIO", "confidence": 0.41 }
    ]
  },
  "related_diseases": ["Migraine", "Viêm mê đạo tai", "Hạ huyết áp tư thế"],
  "additional_symptoms_to_ask": [
    "Bạn có bị ù tai không?",
    "Đau đầu xuất hiện theo nhịp tim không?",
    "Triệu chứng tệ hơn khi thay đổi tư thế không?"
  ]
}
```

---

## 7. Luồng người dùng chi tiết (User Flow)

### 7.1 Luồng chính (Happy Path)

```
[BƯỚC 1 – CHÀO HỎI]
Bot: "Xin chào! Tôi là trợ lý y tế của [Tên hệ thống].
      Bạn đang gặp triệu chứng gì? Tôi có thể giúp bạn tìm
      đúng chuyên khoa và đặt lịch khám phù hợp."

[BƯỚC 2 – THU THẬP TRIỆU CHỨNG]
User: "Tôi bị đau đầu và buồn nôn mấy ngày nay."
Bot:  → Gọi Agent 2 với các triệu chứng đã thu thập

[BƯỚC 3A – KẾT QUẢ ĐẦY ĐỦ (score ≥ 70)]
Bot: "Dựa trên triệu chứng của bạn, tôi gợi ý bạn đến khoa
      THẦN KINH. Đây có thể liên quan đến Migraine hoặc rối
      loạn tiền đình.
      ⚠️ Đây chỉ là gợi ý, không phải chẩn đoán.
      Bạn muốn đặt lịch khám không?"

[BƯỚC 3B – KẾT QUẢ CHƯA ĐẦY ĐỦ (score < 70)]
Bot: "Tôi tạm gợi ý khoa THẦN KINH, nhưng chưa hoàn toàn
      chắc chắn. Bạn có thể cho biết thêm không?
      [ ] Bị ù tai
      [ ] Đau đầu theo nhịp tim
      [ ] Triệu chứng tệ hơn khi đổi tư thế
      [Bỏ qua và tiếp tục →]"

  → User chọn thêm: Gọi lại Agent 2 (tối đa 3 lần)
  → User bỏ qua: Tiếp tục với kết quả hiện tại

[BƯỚC 4 – GỢI Ý BÁC SĨ]
Bot: "Để tìm bác sĩ phù hợp, bạn muốn khám ở khu vực nào
      và dự kiến ngày giờ nào?"
  → Sau khi có đủ thông tin: tìm cơ sở và lịch bác sĩ

Bot: "Tôi tìm thấy một số bác sĩ phù hợp:
      1. BS. Nguyễn Văn A – BV Bạch Mai – Còn slot 9:00, 14:00
      2. BS. Trần Thị B – PK Đa khoa ABC – Còn slot 10:30
      Bạn muốn xem thêm thông tin bác sĩ nào không?"

[BƯỚC 5 – THU THẬP THÔNG TIN ĐẶT LỊCH]
Bot: "Để đặt lịch, tôi cần thêm một số thông tin:
      - Họ và tên: ___
      - Số điện thoại: ___
      - Email: ___
      - Ngày giờ khám mong muốn: ___"

[BƯỚC 6 – XÁC NHẬN]
Bot: "Vui lòng kiểm tra thông tin đặt lịch:
      ┌─────────────────────────────────────┐
      │ Bệnh nhân:   Nguyễn Văn C          │
      │ SĐT:         0912 345 678          │
      │ Email:       abc@email.com         │
      │ Bác sĩ:      BS. Nguyễn Văn A     │
      │ Chuyên khoa: Thần kinh             │
      │ Cơ sở:       BV Bạch Mai          │
      │ Ngày giờ:    10/04/2026 – 09:00   │
      │ Lý do:       Đau đầu, buồn nôn    │
      └─────────────────────────────────────┘
      [✓ Xác nhận đặt lịch]   [✏️ Sửa thông tin]"

[BƯỚC 7A – XÁC NHẬN THÀNH CÔNG]
Bot: "🎉 Đặt lịch thành công! Email xác nhận đã được gửi đến
      abc@email.com. Chúc bạn sức khoẻ!"

[BƯỚC 7B – YÊU CẦU SỬA]
Bot: "Thông tin nào bạn muốn sửa? Vui lòng nhập lại."
  → Quay về Bước 5 với thông tin đã điền sẵn

[BƯỚC CUỐI – THÔNG TIN LIÊN HỆ]
Bot: "Nếu bạn cần hỗ trợ thêm, vui lòng liên hệ:
      📞 Hotline: 1800 xxxx (Miễn phí, 7:00–22:00)
      📧 support@[domain].vn
      🌐 [link website]"
```

### 7.2 Vòng lặp thu thập triệu chứng

```
Lần 1: User nhập → Agent 2 → is_complete: false → Bot gợi ý thêm
Lần 2: User bổ sung → Agent 2 → is_complete: true/false
Lần 3: (nếu vẫn false) → Dùng kết quả tốt nhất hiện có + cảnh báo
        "Độ chắc chắn còn thấp, vui lòng tham khảo ý kiến bác sĩ"
```

---

## 8. Đặc tả giao diện (UI/UX)

### 8.1 Kiểu triển khai

- **Dạng:** Embeddable Web Chat Widget
- **Tích hợp:** Qua thẻ `<script>` hoặc `<iframe>` nhúng vào trang host
- **Hiển thị:** Icon chat ở góc dưới phải màn hình, click để mở cửa sổ
- **Kích thước:** Rộng 380px, cao 600px (responsive trên mobile ≥ 320px)

### 8.2 Cấu trúc Chat Widget

```
┌────────────────────────────────────────┐
│ 🏥 Trợ lý Y tế               [_] [✕] │  ← Header (AI badge)
├────────────────────────────────────────┤
│                                        │
│  [Bot] Xin chào! ...                  │  ← Vùng tin nhắn
│                                        │     (cuộn được)
│             [User] Tôi bị đau đầu...  │
│                                        │
│  [Bot] Dựa trên triệu chứng...        │
│  ┌──────────────────────────────────┐  │
│  │ [ ] Bị ù tai                    │  │  ← Multi-select chips
│  │ [ ] Đau đầu theo nhịp tim       │  │
│  │ [Bỏ qua →]                      │  │
│  └──────────────────────────────────┘  │
│                                        │
│  👍 😐 👎  ← Phản hồi tin nhắn này   │
├────────────────────────────────────────┤
│  Nhập tin nhắn...                [➤]  │  ← Ô nhập liệu
└────────────────────────────────────────┘
```

### 8.3 Các UI Component trong Chat

| Component | Mô tả | Khi nào dùng |
|-----------|-------|-------------|
| Text Bubble | Tin nhắn văn bản | Mọi lúc |
| Multi-select Chips | Nút chọn triệu chứng bổ sung | Bước thu thập triệu chứng |
| Doctor Card | Card bác sĩ (tên, ảnh, slot trống) | Bước gợi ý bác sĩ |
| Booking Summary Card | Bảng tóm tắt thông tin đặt lịch | Bước xác nhận |
| Action Buttons | Nút [Xác nhận] / [Sửa thông tin] | Bước xác nhận |
| Contact Info Card | Thông tin liên hệ hỗ trợ | Cuối luồng |
| Emoji Reaction Bar | 👍 😐 👎 | Sau tin nhắn quan trọng của bot |
| Typing Indicator | Animation "..." | Khi bot đang xử lý |
| Loading Spinner | Spinner + "Đang tìm kiếm..." | Khi gọi Tool |

### 8.4 Hệ thống Emoji Feedback

- **Vị trí:** Dưới các tin nhắn quan trọng của bot (kết quả chuyên khoa, xác nhận booking)
- **3 mức:** 👍 Hài lòng (5đ) · 😐 Trung bình (3đ) · 👎 Tệ (1đ)
- **Hành vi:** Chọn một lần, không thể thay đổi. Sau khi chọn: emoji được highlight.
- **Dữ liệu ghi nhận:** `message_id`, `rating`, `timestamp`, `session_id`
- **Nếu chọn 👎:** Hiển thị thêm ô nhập tự do "Bạn có thể nói thêm không?" (không bắt buộc)

### 8.5 Màn hình Thông tin Liên hệ Hỗ trợ

Hiển thị cuối luồng sau khi đặt lịch thành công, hoặc khi chatbot không thể trả lời:

```
╔══════════════════════════════════════╗
║  📋 Thông tin liên hệ hỗ trợ        ║
╠══════════════════════════════════════╣
║  Chatbot không thể hỗ trợ về:       ║
║  • Giải thích kết quả xét nghiệm    ║
║  • Giải thích đơn thuốc             ║
║  • Tư vấn pháp lý y tế              ║
║                                     ║
║  Vui lòng liên hệ trực tiếp:       ║
║  📞 Hotline: 1800 xxxx              ║
║     (7:00 – 22:00 tất cả các ngày)  ║
║  📧 support@[domain].vn             ║
║  🌐 [Tên website]                   ║
╚══════════════════════════════════════╝
```

---

## 9. Yêu cầu phi chức năng

### 9.1 Hiệu năng

| Chỉ số | Yêu cầu |
|--------|---------|
| Thời gian phản hồi tin nhắn bot | ≤ 3 giây (P95) |
| Thời gian Agent 2 phân tích | ≤ 3 giây (P95) |
| Thời gian gọi Tool bên ngoài | ≤ 2 giây / tool call |
| Concurrent users | ≥ 500 sessions đồng thời |
| Uptime | ≥ 99.5% / tháng |

### 9.2 Khả năng mở rộng

- Main Agent hoạt động stateless; trạng thái hội thoại lưu tại Redis
- Knowledge Graph hỗ trợ thêm chuyên khoa mới mà không cần retrain LLM
- Tool Layer có thể tích hợp thêm nguồn dữ liệu ngoài (BHYT, HIS) ở các giai đoạn sau

### 9.3 Khả năng sử dụng

- Ngôn ngữ mặc định: Tiếng Việt (hỗ trợ tiếng Anh ở Phase 2)
- Không yêu cầu đăng nhập để chat và nhận gợi ý
- Responsive trên mobile browser (viewport ≥ 320px)
- Hỗ trợ keyboard navigation và screen reader (WCAG 2.1 AA)

### 9.4 Khả năng bảo trì

- Knowledge Graph có giao diện quản trị để cập nhật dữ liệu y tế
- Logging đầy đủ mọi lệnh gọi Agent 2 và Tool để phục vụ audit
- Dashboard monitoring: uptime, latency, error rate, feedback score

---

## 10. Xử lý lỗi & Edge Cases

### 10.1 Bảng Edge Cases

| Tình huống | Hành vi mong đợi |
|------------|-----------------|
| User nhập thông tin không phải triệu chứng | Bot hỏi lại: "Bạn có thể mô tả triệu chứng đang gặp không?" |
| Agent 2 timeout / lỗi Knowledge Graph | Fallback LLM gợi ý chuyên khoa, ghi log lỗi, hiện cảnh báo "kết quả có thể chưa chính xác" |
| Không tìm thấy bác sĩ / cơ sở phù hợp | Thông báo và gợi ý mở rộng phạm vi tìm kiếm hoặc chọn ngày khác |
| Đặt lịch thất bại | Thông báo lỗi, gợi ý liên hệ hotline để đặt trực tiếp |
| User mô tả triệu chứng cấp cứu | Hiển thị ngay: "⚠️ Triệu chứng có thể cần cấp cứu. Hãy gọi 115 hoặc đến phòng cấp cứu ngay." |
| Session hết hạn (> 30 phút không hoạt động) | Lưu tóm tắt context, khi quay lại hỏi "Bạn có muốn tiếp tục không?" |
| User hỏi ngoài phạm vi (chẩn đoán, thuốc) | Bot từ chối lịch sự và hiển thị thông tin liên hệ hỗ trợ |
| Email không hợp lệ | Validate regex trước khi submit, yêu cầu nhập lại |
| SĐT sai định dạng | Validate định dạng Việt Nam (10 số, đầu 03/05/07/08/09) |
| Agent 2 vòng lặp > 3 lần | Dừng lặp, dùng kết quả có confidence cao nhất kèm cảnh báo |

### 10.2 Từ khoá kích hoạt cảnh báo cấp cứu

Khi phát hiện các cụm từ sau, hệ thống ngừng luồng thông thường và hiển thị thông báo khẩn:

> "đau ngực", "khó thở đột ngột", "liệt tay chân", "mất ý thức", "co giật", "nôn ra máu", "xuất huyết", "tai nạn"

---

## 11. Bảo mật & Tuân thủ

### 11.1 Bảo mật dữ liệu

| Yêu cầu | Chi tiết |
|---------|---------|
| Mã hoá truyền tải | HTTPS / TLS 1.3 bắt buộc |
| Mã hoá lưu trữ | AES-256 cho dữ liệu cá nhân bệnh nhân |
| Dữ liệu nhạy cảm | Không log họ tên, SĐT, email trong hệ thống log thông thường |
| Session | Token JWT, TTL 30 phút, tự refresh khi đang hoạt động |
| PII | Tuân thủ Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân |

### 11.2 Tuân thủ y tế

- Chatbot **không** được đưa ra chẩn đoán bệnh cụ thể
- Mọi kết quả gợi ý chuyên khoa phải kèm disclaimer: *"Đây là gợi ý ban đầu, không thay thế chẩn đoán của bác sĩ"*
- Dữ liệu y tế trong Knowledge Graph phải được review bởi chuyên gia định kỳ (6 tháng/lần)
- Audit log toàn bộ phiên chat để phục vụ kiểm tra sau sự cố

### 11.3 Phân quyền

| Role | Quyền |
|------|-------|
| End User | Chat, đặt lịch |
| Admin | Xem báo cáo, quản lý Knowledge Graph |
| Developer | Truy cập log, monitoring |
| Medical Reviewer | Review và cập nhật Knowledge Graph |

---

## 12. Lộ trình phát triển

### Phase 1 – MVP (Tháng 1–3)

| Sprint | Deliverable |
|--------|------------|
| Sprint 1–2 | Thiết kế kiến trúc, Knowledge Graph cơ bản (15 chuyên khoa phổ biến) |
| Sprint 3–4 | Main Agent + Agent 2 tích hợp KG, luồng thu thập triệu chứng |
| Sprint 5–6 | Tool tìm cơ sở y tế + lịch bác sĩ |
| Sprint 7–8 | Tool đặt lịch + email xác nhận |
| Sprint 9 | Chat Widget UI, Emoji Feedback, màn hình liên hệ hỗ trợ |
| Sprint 10 | QA, UAT, kiểm toán bảo mật |
| Sprint 11 | Soft launch tại 1 cơ sở y tế pilot |

### Phase 2 – Mở rộng (Tháng 4–6)

- Hỗ trợ tiếng Anh
- Tích hợp Zalo OA
- Lịch sử chat cho người dùng đã đăng nhập
- Dashboard analytics cho admin
- Mở rộng Knowledge Graph lên 30+ chuyên khoa

### Phase 3 – Nâng cao (Tháng 7–12)

- Mobile App (iOS / Android)
- Tích hợp hệ thống HIS bệnh viện
- Thanh toán online phí khám
- Multimodal: nhận ảnh triệu chứng từ người dùng

---

## 13. Rủi ro & Giải pháp

| Rủi ro | Mức độ | Giải pháp |
|--------|--------|-----------|
| Knowledge Graph thiếu dữ liệu → gợi ý sai chuyên khoa | Cao | Fallback LLM, review định kỳ bởi chuyên gia, hiện confidence score |
| LLM hallucination → thông tin bác sĩ sai | Cao | Dữ liệu bác sĩ lấy 100% từ API thực, LLM không tự sinh |
| API bác sĩ / booking bị downtime | Trung bình | Retry logic, fallback hiển thị hotline |
| Rủi ro pháp lý khi tư vấn y tế | Cao | Disclaimer rõ ràng, giới hạn chỉ gợi ý chuyên khoa, tham vấn luật sư y tế |
| Người dùng nhầm chatbot là bác sĩ thật | Trung bình | Header luôn hiển thị "Trợ lý AI – không phải bác sĩ" |

---

## Phụ lục A – Danh sách chuyên khoa hỗ trợ (MVP)

| STT | Mã | Chuyên khoa | Triệu chứng điển hình |
|-----|----|------------|----------------------|
| 1 | NEURO | Thần kinh | Đau đầu, chóng mặt, tê liệt, co giật |
| 2 | CARDIO | Tim mạch | Đau ngực, hồi hộp, khó thở khi gắng sức |
| 3 | ORTHO | Cơ xương khớp | Đau khớp, đau lưng, chấn thương |
| 4 | GASTRO | Tiêu hoá | Đau bụng, buồn nôn, tiêu chảy, táo bón |
| 5 | DERM | Da liễu | Phát ban, ngứa, mụn, rụng tóc |
| 6 | ENT | Tai Mũi Họng | Ù tai, đau họng, viêm xoang, khó nuốt |
| 7 | OPHT | Nhãn khoa | Mờ mắt, đau mắt, đỏ mắt |
| 8 | PULMO | Hô hấp | Ho kéo dài, khó thở, đau ngực khi thở |
| 9 | ENDO | Nội tiết | Mệt mỏi, tăng/giảm cân bất thường, khát nước nhiều |
| 10 | URO | Tiết niệu | Tiểu buốt, tiểu rắt, đau lưng dưới |
| 11 | GYN | Phụ sản | Rối loạn kinh nguyệt, đau bụng dưới (nữ) |
| 12 | PSYCH | Tâm thần | Lo âu, mất ngủ, trầm cảm |
| 13 | PEDI | Nhi khoa | Trẻ em sốt, ho, quấy khóc |
| 14 | ONCO | Ung bướu | Sưng hạch, sụt cân không rõ nguyên nhân |
| 15 | GENERAL | Nội tổng quát | Triệu chứng chung, không rõ ràng |

---

## Phụ lục B – Cấu trúc dữ liệu Knowledge Graph

```
Node Types:
  - Symptom    (name, icd10_code, severity_weight)
  - Disease    (name, icd10_code, prevalence)
  - Specialty  (name, code, description)
  - BodyPart   (name, anatomical_region)

Relationship Types:
  - (Symptom)  -[:INDICATES {weight}]->  (Disease)
  - (Disease)  -[:TREATED_BY]->          (Specialty)
  - (Symptom)  -[:LOCATED_IN]->          (BodyPart)
  - (BodyPart) -[:BELONGS_TO]->          (Specialty)
  - (Symptom)  -[:RELATED_TO]->          (Symptom)
```

---

## Phụ lục C – Định nghĩa thuật ngữ

| Thuật ngữ | Định nghĩa |
|-----------|-----------|
| Main Agent | Agent LLM điều phối hội thoại chính |
| Agent 2 / Specialist Agent | Agent chuyên biệt phân tích triệu chứng |
| Knowledge Graph (KG) | Cơ sở tri thức y tế dạng đồ thị quan hệ |
| Completeness Score | Điểm đánh giá mức độ đầy đủ thông tin triệu chứng (0–100) |
| Slot | Khung giờ khám còn trống của bác sĩ |
| Facility | Bệnh viện hoặc phòng khám |
| PII | Personally Identifiable Information – thông tin cá nhân nhận dạng được |
| NER | Named Entity Recognition – trích xuất thực thể từ văn bản tự nhiên |
