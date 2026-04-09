# Canvas worked example — AI Email Triage

Ví dụ đầy đủ để tham khảo. **[Annotation]** giải thích tại sao điền như vậy.

**Product:** Phân loại email → 3 nhãn (Urgent / Action-needed / FYI). AI gợi ý, user xác nhận hoặc sửa.

---

## Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Core** | **User:** NV văn phòng nhận 50-100 email/ngày. **Pain:** 30 phút/ngày phân loại. **Value:** AI gợi ý nhãn → 5 phút, không bỏ sót. | **Khi sai:** user thấy nhãn sai → sửa 1 click. **Explain:** hiện lý do ("từ sếp, chứa 'deadline'"). **Sửa:** kéo thả sang nhãn đúng. | **Cost:** ~$0.01/email. **Latency:** <2s. **Risk:** hallucinate nội dung nhạy cảm qua external API → cần redact PII. |
| **Then chốt** | **Augmentation** — cost of reject = 0. Nếu automation → email urgent bị ẩn = nguy hiểm. | **4-path:** xem User Stories dưới. | **Recall-first** — bỏ sót urgent tệ hơn gợi ý sai. |

> **[Annotation]** Value: user + pain + benefit đo được (30→5 phút). Trust: trả lời 3 câu (sai/explain/sửa), chọn aug vì cost of reject = 0. Feasibility: cost per unit ($0.01), risk cụ thể (PII).

## Learning signal

| # | Câu hỏi | Trả lời |
|---|---------|---------|
| 1 | Correction đi vào đâu? | User sửa nhãn → correction log → retrain hàng tuần |
| 2 | Thu signal gì? | Implicit: acceptance rate. Explicit: thumbs down. Correction: sửa nhãn. Alert khi acceptance giảm >10%/tuần |
| 3 | Data loại nào? | User-specific + Real-time. Marginal value cao — model chung không biết email pattern cá nhân |

> **[Annotation]** Ghi 3 loại signal. Marginal value = data có giá trị thêm so với model đã có?

## User stories — 4 paths

**Feature:** Gợi ý nhãn email. **Trigger:** email mới → AI phân tích → gợi ý nhãn.

| Path | Diễn biến |
|------|-----------|
| **Happy** | Email từ sếp "Deadline Friday" → "Urgent" (95%) → badge đỏ + lý do → user tiếp tục |
| **Low-confidence** | Newsletter "Action required" → 55% → hiện 2 nhãn + % → user chọn "FYI" |
| **Failure** | Khiếu nại viết tiếng lóng → AI gắn "FYI" (80%) → user đọc tối, sửa "Urgent". Hậu quả: trả lời chậm 4h |
| **Correction** | Kéo thả sang nhãn đúng → ghi correction → retrain cuối tuần → lần sau đúng |

> **[Annotation]** Failure nêu hậu quả cụ thể. Correction chỉ rõ data đi đâu → nguồn feedback loop.

## Eval: Recall-first — bỏ sót urgent nguy hiểm hơn gợi ý sai.

| Metric | Threshold | Red flag |
|--------|-----------|----------|
| Recall (urgent) | ≥95% | <90%/3 ngày |
| Precision (overall) | ≥80% | <70% → mất tin |
| Acceptance rate | ≥75% | <60% → vô dụng |

## Failure modes

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | Email quan trọng viết tiếng lóng | Sai + confidence cao — **user không biết** | Sender VIP → flag review |
| 2 | Thông tin nhạy cảm qua external API | Rò rỉ dữ liệu | Redact PII trước khi gửi |
| 3 | User mới, chưa có correction data | AI kém → tắt feature | Rule-based 2 tuần đầu |

## ROI: Conservative +$1350/ngày → Optimistic +$13,400/ngày

**Kill criteria:** acceptance <50% sau 1 tháng, hoặc cost > benefit 2 tháng liên tục.
