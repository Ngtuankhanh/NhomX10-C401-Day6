# Đặc Tả Sản Phẩm — AI Product Hackathon

**Nhóm:** Nhóm X10 — C401
**Track:** ☐ VinFast · ☑ Vinmec · ☐ VinUni-VinSchool · ☐ XanhSM · ☐ Open
**Problem statement (1 câu):** Bệnh nhân thường bối rối không biết khám chuyên khoa nào, dẫn đến đi nhầm khoa và mất thời gian; AI giải quyết bằng cách phân tích triệu chứng để gợi ý đúng chuyên khoa và hỗ trợ đặt lịch ngay lập tức.

---

## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | **Bệnh nhân tự do:** Muốn biết khám gì mà không cần chờ tổng đài — AI gợi ý chuyên khoa + đặt lịch 24/7. | **Disclaimer:** AI không chẩn đoán, chỉ gợi ý. User có thể chọn lại khoa khác hoặc bỏ qua bước đặt lịch. Xác nhận lại info bác sĩ thật qua API. | **Cost:** ~$0.01/session (GPT-4o/4o-mini). **Latency:** <3s. **Risk:** AI gợi ý sai khoa nhưng đã có bác sĩ/lễ tân check lại tại viện. |

**Automation hay augmentation?** ☐ Automation · ☑ Augmentation

Justify: Sản phẩm hỗ trợ người dùng đưa ra quyết định nhanh hơn, không thay thế chẩn đoán y khoa chính thức. Người dùng luôn có quyền quyết định cuối cùng về việc đặt lịch hay không.

**Learning signal:**

1. **User correction đi vào đâu?** Khi user chọn khoa khác khoa gợi ý hoặc báo "không hài lòng" qua emoji rating -> Lưu vào `correction_log.jsonl`.
2. **Product thu signal gì để biết tốt lên hay tệ đi?** Tỷ lệ đặt lịch thành công (Booking rate) và Tỷ lệ hài lòng (Positive Feedback Rate).
3. **Data thuộc loại nào?** ☐ User-specific · ☑ Domain-specific · ☐ Real-time · ☑ Human-judgment · ☐ Khác: ___
   Có **marginal value** không? (Model đã biết cái này chưa?) Có. Dữ liệu thực tế về triệu chứng người Việt và thói quen đặt lịch tại Vinmec giúp tinh chỉnh prompt và Knowledge Graph local.

---

## 2. User Stories — 4 paths

### Feature: Phân loại triệu chứng & Gợi ý chuyên khoa (Triage)

**Trigger:** User nhập: "Tôi bị đau đầu và buồn nôn 2 ngày nay."

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | Hiển thị: "Dựa trên triệu chứng, bạn nên khám khoa **Nội thần kinh**". User thấy hợp lý, nhấn "Tìm bác sĩ". |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | Bot hỏi lại: "Bạn có bị chóng mặt hay ù tai không?". User chọn "Có" -> Bot tăng confidence và gợi ý khoa. |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | Gợi ý khoa Tim mạch khi user chỉ bị đau cơ ngực. User nhận ra sai, chọn "Tôi muốn tìm khoa khác" hoặc chat lại rõ hơn. |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | User nhấn nút "Không đúng khoa tôi cần" -> Hệ thống ghi log để Reviewer điều chỉnh map triệu chứng - khoa trong KG. |

### Feature: Đặt lịch khám tích hợp (Booking)

**Trigger:** User chọn bác sĩ và nhấn "Xác nhận đặt lịch".

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — Flow chuẩn | User thấy gì? Flow kết thúc ra sao? | User nhập info -> Nhập OTP -> Nhận thông báo "Đặt lịch thành công" + Email xác nhận. |
| Low-confidence — AI không chắc | AI không chắc info user nhập | AI parse thông tin (họ tên, SĐT) không rõ -> Hiển thị form cho user điền/sửa lại bằng tay thay vì tự động. |
| Failure — Hệ thống lỗi | Lỗi hệ thống/Hết slot | System báo: "Slot này vừa có người đặt, vui lòng chọn khung giờ khác". Gợi ý tìm ngày/cơ sở khác. |
| Correction — Sửa thông tin | User sửa thông tin sai | User nhấn "Sửa thông tin" tại màn hình Summary trước khi nhấn xác nhận cuối cùng. |

---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** ☐ Precision · ☑ Recall

Tại sao? Trong y tế, **Recall** quan trọng hơn — thà gợi ý thừa chuyên khoa/cảnh báo nhầm còn hơn bỏ sót triệu chứng nguy hiểm hoặc gợi ý sai khoa dẫn đến chậm trễ điều trị.

Nếu chọn ngược lại (optimize Precision): Sẽ bỏ sót nhiều ca bệnh cần chú ý -> user bị gửi sai khoa và không được cảnh báo kịp thời.

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| **Symptom-to-Specialty Accuracy** | ≥ 80% | < 70% trong 24h liên tục |
| **Booking Completion Rate** | ≥ 65% | < 40% (có thể do lỗi API đặt lịch) |
| **Emergency Detection Recall** | 100% | Bỏ sót bất kỳ 1 ca cấp cứu nào mà không cảnh báo 115 |

---

## 4. Top 3 failure modes

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | Triệu chứng mơ hồ (VD: "Mệt mỏi") | AI gợi ý quá nhiều khoa hoặc khoa General không ích lợi | Cài đặt "Ask-back loop": Bot chủ động hỏi 3 câu hỏi sàng lọc (Sốt? Sụt cân? Đau ở đâu?). Tối đa 3 vòng hỏi. |
| 2 | Hallucination thông tin bác sĩ/lịch | AI sinh ra tên bác sĩ không tồn tại hoặc slot giả, user đặt lịch nhầm | **Strict API Mapping:** Luôn fetch data bác sĩ/slot từ API thật của bệnh viện, LLM không được tự sinh thông tin bác sĩ hay slot. |
| 3 | Mis-interpretation triệu chứng cấp cứu | User bảo "Đau thắt ngực" nhưng AI coi là đau cơ thường, bỏ qua cảnh báo | **Emergency Guardrail:** Chạy một node check keyword/intent cấp cứu riêng biệt trước khi xử lý triage thường. Không thể bypass. |

---

## 5. ROI 3 kịch bản

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | 50 user/ngày, 50% hoàn thành booking | 200 user/ngày, 70% hoàn thành booking | 1000 user/ngày, 85% hoàn thành booking |
| **Cost** | $5/tháng (API inference) | $20/tháng (API inference) | $100/tháng (API inference) |
| **Benefit** | Tiết kiệm 10h trực tổng đài/tháng | Tiết kiệm 50h/tháng, tăng 5% lịch hẹn online | Tiết kiệm 200h/tháng, tăng 15% lịch online, giảm 25% cuộc gọi |
| **Net** | Dương (ROI > 0) | Rất tốt, payback < 3 tháng | Đột phá về vận hành |

**Kill criteria:** Dừng dự án khi tỷ lệ đặt lịch thành công < 20% liên tục trong 1 tháng (chứng tỏ user không tin tưởng chatbot) hoặc chi phí API vượt quá 30% lợi nhuận vận hành mang lại.

---

## 6. Mini AI spec (1 trang)

### Giải quyết vấn đề gì, cho ai

**Bài toán:** Bệnh nhân không biết phải khám chuyên khoa nào — dẫn đến đi nhầm khoa, mất thời gian chờ đợi và tăng tải tổng đài bệnh viện.

**Đối tượng:** Bệnh nhân tự do (25-55 tuổi) và người chăm sóc (Caregiver) đặt lịch hộ người thân, sử dụng qua web chat widget.

### Auto hay Augmentation

**Augmentation.** AI gợi ý chuyên khoa và danh sách bác sĩ, nhưng user là người quyết định cuối cùng — chọn bác sĩ, xác nhận slot, nhập OTP. AI không tự động đặt lịch mà không có sự chấp thuận rõ ràng.

### Quality (Precision / Recall)

Ưu tiên **Recall** để đảm bảo không bỏ sót triệu chứng cần cảnh báo. Chấp nhận một tỷ lệ false positive nhỏ (gợi ý thêm chuyên khoa không cần thiết) hơn là bỏ sót ca bệnh nghiêm trọng.

### Risk chính

- **Hallucination bác sĩ/slot:** Giải quyết bằng Strict API Mapping — LLM không được tự tạo thông tin.
- **Bỏ sót cấp cứu:** Giải quyết bằng Emergency Guardrail chạy song song, không thể bypass.
- **Tuân thủ y tế:** Mọi gợi ý đều kèm disclaimer "không phải chẩn đoán y khoa".

### Data flywheel

Mỗi lần user chọn khoa khác khoa AI gợi ý -> log correction -> Reviewer phân tích -> cập nhật Knowledge Graph -> AI chính xác hơn -> nhiều user tin dùng hơn -> nhiều feedback hơn -> vòng lặp tiếp tục.

---

## PHẦN CHI TIẾT KỸ THUẬT (APPENDIX)

---

### A. Kiến trúc triển khai MVP

#### A.1 Kiến trúc tổng thể

```text
Next.js Chat UI (Frontend)
  -> FastAPI Backend (Python)
       -> Agent A: Conversation Orchestrator (LangGraph ReAct)
            -> emergency_guard node
            -> specialist_agent_tool (Agent B)
            -> list_facilities_tool
            -> search_doctors_tool
            -> get_doctor_slots_tool
            -> create_booking_tool
            -> confirm_booking_tool
       -> Agent B: Specialist Classifier
            -> Medical NER
            -> Knowledge Graph Query (Mock CSV/JSON)
            -> Completeness Score Calculator
  -> Mock Data Layer
       -> specialties.csv
       -> facilities.csv
       -> doctors.csv
       -> kg.json
  -> Vinmec API (Slot & Booking thật)
```

#### A.2 Quyết định kiến trúc MVP

- **Agent A** là agent duy nhất giao tiếp với người dùng. Quản lý toàn bộ state hội thoại và điều phối các tools.
- **Agent B** không giao tiếp trực tiếp với user. Nhận input JSON chuẩn hoá từ Agent A, trả về specialty suggestion JSON.
- **Knowledge Graph** ở MVP là mock data local (CSV/JSON). Không dựng graph database thật.
- **Booking** tách thành 2 bước: (1) Tạo yêu cầu lấy `verif_id`, (2) Nhận OTP từ user và confirm.

---

### B. Trách nhiệm của từng agent

#### B.1 Agent A — Conversation Orchestrator

**Làm:**
- Duy trì hội thoại tự nhiên với người dùng
- Thu thập triệu chứng và thông tin booking theo từng bước
- Gọi Agent B đúng thời điểm (khi đã có ít nhất triệu chứng chính)
- Xử lý uncertainty, retry, fallback và UX messaging

**Không làm:**
- Không tự chẩn đoán bệnh
- Không tự sinh thông tin bác sĩ/cơ sở/slot khi chưa có từ data source
- Không gọi Agent B khi chưa có đủ thông tin triệu chứng ban đầu

#### B.2 Agent B — Specialist Classifier

**Làm:**
- Nhận `symptom payload` đã chuẩn hoá từ Agent A
- Phân tích Knowledge Graph (mock CSV/JSON)
- Tính Completeness Score
- Trả về `specialty suggestion` dạng JSON kèm confidence và follow-up question nếu cần

---

### C. State machine của Agent A

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
| `CONFIRMING_BOOKING` | Hiển thị summary để user xác nhận | Có booking draft | User xác nhận |
| `WAITING_OTP` | Chờ user nhập OTP | Submit step 1 thành công | User nhập OTP hoặc huỷ |
| `BOOKING_COMPLETED` | Booking thành công | OTP hợp lệ | Kết thúc |
| `FALLBACK_SUPPORT` | Lỗi / failure / out-of-scope | Tool lỗi hoặc flow không xử lý được | Kết thúc hoặc quay lại |

---

### D. JSON Contracts giữa Agent A và Agent B

#### D.1 Input (Agent A -> Agent B)

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

#### D.2 Output — Agent B đủ chắc chắn

```json
{
  "specialty_name": "Nội thần kinh",
  "description": "Đau đầu kèm buồn nôn kéo dài vài ngày phù hợp nhóm thần kinh hơn các nhóm khác",
  "confidence": 0.87
}
```

#### D.3 Output — Agent B chưa chắc, cần hỏi thêm

```json
{
  "specialty_name": "Nội thần kinh",
  "description": "Triệu chứng hướng nhiều tới nhóm thần kinh nhưng cần thêm thông tin",
  "confidence": 0.68,
  "question": "Bạn có chóng mặt hoặc nhìn mờ không?"
}
```

#### D.4 Output — Agent B lỗi

```json
{
  "error": {
    "code": "AGENT_B_TIMEOUT",
    "message": "Specialist classifier timed out"
  }
}
```

---

### E. Session State Schema

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

---

### F. Failure Handling

| Failure | Cách xử lý ở Agent A | UX hiển thị |
|---|---|---|
| Agent B timeout | Retry 1 lần với payload rút gọn, sau đó fallback | "Hệ thống đang phân tích lại triệu chứng của bạn..." |
| Agent B trả JSON lỗi | Ghi log, chuyển fallback specialty tool | "Tôi đang thử một cách phân loại khác để tránh bỏ sót thông tin." |
| Không có slot | Gợi ý ngày khác hoặc cơ sở khác | "Ngày này hiện chưa còn lịch phù hợp, tôi có thể tìm ngày/cơ sở khác." |
| Booking step 1 fail | Cho submit lại hoặc hotline | "Tôi chưa gửi được yêu cầu đặt lịch. Bạn muốn thử lại không?" |
| OTP sai | Báo lỗi và cho nhập lại | "Mã OTP chưa đúng, bạn vui lòng kiểm tra và nhập lại." |
| OTP hết hạn | Gọi lại booking step 1 để lấy OTP mới | "Mã đã hết hạn, tôi sẽ gửi lại một mã mới." |
| User từ chối trả lời thêm triệu chứng | Dùng kết quả tốt nhất hiện tại | "Tôi sẽ dùng thông tin hiện có để gợi ý chuyên khoa gần nhất." |
| Triệu chứng cấp cứu | Dừng flow booking, hiển thị cảnh báo | "Triệu chứng này có thể cần cấp cứu. Vui lòng gọi 115 ngay." |

---

### G. Luồng người dùng (Happy Path)

```
[BƯỚC 1 – CHÀO HỎI]
Bot: "Xin chào! Tôi là trợ lý y tế Vinmec.
      Bạn đang gặp triệu chứng gì? Tôi có thể giúp bạn tìm
      đúng chuyên khoa và đặt lịch khám phù hợp."

[BƯỚC 2 – THU THẬP TRIỆU CHỨNG]
User: "Tôi bị đau đầu và buồn nôn mấy ngày nay."
Bot:  → Gọi Agent B với các triệu chứng đã thu thập

[BƯỚC 3A – KẾT QUẢ ĐẦY ĐỦ (confidence ≥ 70%)]
Bot: "Dựa trên triệu chứng của bạn, tôi gợi ý bạn đến khoa
      THẦN KINH. Đây có thể liên quan đến Migraine hoặc rối
      loạn tiền đình.
      ⚠️ Đây chỉ là gợi ý, không phải chẩn đoán.
      Bạn muốn đặt lịch khám không?"

[BƯỚC 3B – KẾT QUẢ CHƯA ĐẦY ĐỦ (confidence < 70%)]
Bot: "Tôi tạm gợi ý khoa THẦN KINH, nhưng chưa hoàn toàn
      chắc chắn. Bạn có thể cho biết thêm không?
      [ ] Bị ù tai
      [ ] Đau đầu theo nhịp tim
      [ ] Triệu chứng tệ hơn khi đổi tư thế
      [Bỏ qua và tiếp tục →]"
  → User chọn thêm: Gọi lại Agent B (tối đa 3 lần)
  → User bỏ qua: Tiếp tục với kết quả hiện tại

[BƯỚC 4 – GỢI Ý BÁC SĨ]
Bot: "Bạn muốn khám ở khu vực nào và dự kiến ngày giờ nào?"
  → Gọi list_facilities_tool, search_doctors_tool, get_doctor_slots_tool
Bot: "Tôi tìm thấy một số bác sĩ phù hợp:
      1. BS. Nguyễn Văn A – BV Vinmec Times City – Còn slot 9:00, 14:00
      2. BS. Trần Thị B – BV Vinmec Royal City – Còn slot 10:30"

[BƯỚC 5 – THU THẬP THÔNG TIN ĐẶT LỊCH]
Bot: "Để đặt lịch, tôi cần:
      - Họ và tên / Giới tính / Ngày sinh / SĐT / Email / Lý do khám"

[BƯỚC 6 – XÁC NHẬN]
Bot: "Vui lòng kiểm tra thông tin:
      ┌─────────────────────────────────────┐
      │ Bệnh nhân:   Nguyễn Văn C          │
      │ SĐT:         0912 345 678          │
      │ Bác sĩ:      BS. Nguyễn Văn A     │
      │ Chuyên khoa: Thần kinh             │
      │ Ngày giờ:    10/04/2026 – 09:00   │
      └─────────────────────────────────────┘
      [✓ Xác nhận]   [✏️ Sửa thông tin]"
  → Gọi create_booking_tool -> nhận verif_id

[BƯỚC 7 – OTP]
Bot: "Chúng tôi đã gửi mã OTP đến SĐT của bạn. Vui lòng nhập mã:"
  → Gọi confirm_booking_tool với verif_id + otp_code

[BƯỚC 8 – THÀNH CÔNG]
Bot: "Đặt lịch thành công! Email xác nhận đã được gửi. Chúc bạn sức khoẻ!"
```

---

### H. Đặc tả UI/UX

#### H.1 Cấu trúc Chat Widget

```
┌────────────────────────────────────────┐
│ 🏥 Trợ lý Y tế Vinmec       [_] [✕] │  ← Header
├────────────────────────────────────────┤
│  [Bot] Xin chào! ...                  │
│             [User] Tôi bị đau đầu...  │
│  [Bot] Dựa trên triệu chứng...        │
│  ┌──────────────────────────────────┐  │
│  │ [ ] Bị ù tai                    │  │  ← Multi-select chips
│  │ [ ] Đau đầu theo nhịp tim       │  │
│  │ [Bỏ qua →]                      │  │
│  └──────────────────────────────────┘  │
│  👍 😐 👎                             │  ← Emoji Feedback
├────────────────────────────────────────┤
│  Nhập tin nhắn...                [➤]  │
└────────────────────────────────────────┘
```

#### H.2 UI Components

| Component | Mô tả | Khi nào dùng |
|-----------|-------|-------------|
| Text Bubble | Tin nhắn văn bản | Mọi lúc |
| Multi-select Chips | Nút chọn triệu chứng bổ sung | Bước thu thập triệu chứng |
| Doctor Card | Card bác sĩ (tên, chuyên khoa, slot trống) | Bước gợi ý bác sĩ |
| Booking Summary Card | Bảng tóm tắt thông tin đặt lịch | Bước xác nhận |
| Action Buttons | [Xác nhận] / [Sửa thông tin] | Bước xác nhận |
| Emoji Reaction Bar | 👍 😐 👎 | Sau tin nhắn quan trọng của bot |
| Typing Indicator | Animation "..." | Khi bot đang xử lý |
| Loading Spinner | Spinner + status text | Khi gọi Tool |

#### H.3 Loading Status Text

| Status Code | Text hiển thị |
|-------------|---------------|
| `analyzing_symptoms` | "Đang phân tích triệu chứng..." |
| `finding_doctors` | "Đang tìm bác sĩ và lịch phù hợp..." |
| `loading_slots` | "Đang kiểm tra lịch trống..." |
| `submitting_booking` | "Đang gửi yêu cầu đặt lịch..." |
| `waiting_for_otp` | "Đang chờ mã OTP..." |
| `confirming_booking` | "Đang xác nhận lịch hẹn..." |
| `recovering_from_error` | "Đang thử lại..." |

---

### I. Yêu cầu phi chức năng

| Chỉ số | Yêu cầu |
|--------|---------|
| Thời gian phản hồi bot | ≤ 3 giây (P95) |
| Thời gian Agent B phân tích | ≤ 3 giây (P95) |
| Thời gian gọi Tool ngoài | ≤ 2 giây / tool call |
| Uptime | ≥ 99.5% / tháng |
| Bảo mật | HTTPS / TLS 1.3, AES-256 cho dữ liệu bệnh nhân |
| Tuân thủ | Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân |

---

### J. Bảo mật & Tuân thủ y tế

- Chatbot **không** được đưa ra chẩn đoán bệnh cụ thể.
- Mọi kết quả gợi ý chuyên khoa phải kèm disclaimer: *"Đây là gợi ý ban đầu, không thay thế chẩn đoán của bác sĩ"*.
- Không log họ tên, SĐT, email trong hệ thống log thông thường.
- Audit log toàn bộ phiên chat để phục vụ kiểm tra sau sự cố.
- Header luôn hiển thị badge "Trợ lý AI – không phải bác sĩ".

---

### K. Lộ trình phát triển

#### Phase 1 — MVP (Tháng 1–3)

| Sprint | Deliverable |
|--------|------------|
| Sprint 1–2 | Kiến trúc, Knowledge Graph 15 chuyên khoa, mock data CSV |
| Sprint 3–4 | Agent A + Agent B, luồng thu thập triệu chứng e2e |
| Sprint 5–6 | Tool tìm cơ sở y tế + lịch bác sĩ (Slot API thật) |
| Sprint 7–8 | Tool đặt lịch 2 bước + OTP |
| Sprint 9 | Chat Widget UI, Emoji Feedback, màn hình liên hệ hỗ trợ |
| Sprint 10 | QA, UAT, kiểm toán bảo mật |

#### Phase 2 — Mở rộng (Tháng 4–6)

- Hỗ trợ tiếng Anh
- Tích hợp Zalo OA
- Dashboard analytics cho admin
- Mở rộng Knowledge Graph lên 30+ chuyên khoa

#### Phase 3 — Nâng cao (Tháng 7–12)

- Mobile App (iOS / Android)
- Tích hợp hệ thống HIS bệnh viện
- Multimodal: nhận ảnh triệu chứng từ người dùng

---

### L. Phụ lục

#### L.1 Danh sách chuyên khoa hỗ trợ (MVP)

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

#### L.2 Cấu trúc Knowledge Graph

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

#### L.3 Định nghĩa thuật ngữ

| Thuật ngữ | Định nghĩa |
|-----------|-----------|
| Main Agent / Agent A | Agent LLM điều phối hội thoại chính |
| Specialist Agent / Agent B | Agent chuyên biệt phân tích triệu chứng |
| Knowledge Graph (KG) | Cơ sở tri thức y tế dạng đồ thị quan hệ |
| Completeness Score | Điểm đánh giá mức độ đầy đủ thông tin triệu chứng (0–100) |
| Slot | Khung giờ khám còn trống của bác sĩ |
| verif_id | ID xác thực được trả về sau khi tạo booking draft thành công |
| OTP | Mã xác thực một lần gửi qua SĐT để confirm lịch hẹn |
| Facility | Bệnh viện hoặc phòng khám |
| PII | Personally Identifiable Information — thông tin cá nhân nhận dạng được |
| NER | Named Entity Recognition — trích xuất thực thể từ văn bản tự nhiên |

---

*Ngày 6 — VinUni A20 — AI Thực Chiến 2026*
