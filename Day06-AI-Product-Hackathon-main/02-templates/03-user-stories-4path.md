# User stories — 4 paths

Mỗi feature AI chính = 1 bảng. AI trả lời xong → chuyện gì xảy ra? Viết cả 4 trường hợp.

---

## Template

### Feature: [tên feature]

**Trigger:** [user làm gì → AI phản hồi → ...]

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | ___ |
| **Low-confidence** — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | ___ |
| **Failure** — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | ___ |
| **Correction** — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | ___ |

*Lặp lại cho mỗi feature chính.*

---

## Ví dụ: AI phân loại email

### Feature: Gợi ý nhãn email (Urgent / Action-needed / FYI)

**Trigger:** Email mới đến → AI phân tích subject + sender + nội dung → gợi ý nhãn.

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** | User thấy gì? Flow kết thúc ra sao? | Email từ sếp, subject "Deadline Friday" → AI gợi ý "Urgent" (confidence 95%) → hiện badge đỏ + lý do "từ sếp, chứa 'deadline'" → user thấy đúng, tiếp tục |
| **Low-confidence** | System báo bằng cách nào? | Newsletter tiêu đề "Action required" → AI không chắc Action-needed hay FYI (confidence 55%) → hiện 2 nhãn gợi ý + % → user chọn 1 |
| **Failure** | User biết sai bằng cách nào? | Email khiếu nại viết tiếng lóng → AI gắn "FYI" (confidence 80%) → user đọc inbox, thấy sai → sửa thành "Urgent" |
| **Correction** | User sửa bằng cách nào? Data đi vào đâu? | User kéo thả email sang nhãn đúng → ghi correction log (sender + pattern + nhãn sửa) → retrain cuối tuần |

---

## Lưu ý

- Viết **cả 4 path** — nhiều nhóm chỉ nghĩ happy path, bỏ quên 3 cái còn lại
- Path "Failure" quan trọng nhất: user biết AI sai bằng cách nào? Nếu không biết → nguy hiểm
- Path "Correction" = nguồn data cho feedback loop — thiết kế sớm, không để sau
- Mỗi path có câu hỏi thiết kế riêng, không copy-paste

---

## Mở rộng (optional — bonus)

### Transition flow giữa các path

Vẽ diagram hoặc mô tả: user chuyển từ path này sang path khác thế nào?

```
Happy → Failure: user ban đầu tin AI đúng, sau mới phát hiện sai (delayed failure)
Low-confidence → Happy: AI không chắc, user chọn đúng → AI học, lần sau tự tin hơn
Failure → Correction → Happy: user sửa → data mới → model cải thiện → lần sau đúng
Failure → Bỏ dùng: user sửa quá nhiều lần → mất kiên nhẫn → churn
```

- Mỗi mũi tên = 1 điểm thiết kế UX. Bao nhiêu lần failure trước khi user bỏ dùng?
- Transition nào product đang không hỗ trợ?

### Edge cases

Liệt kê 3-5 tình huống biên mà AI sẽ gặp khó:

| Edge case | Dự đoán AI sẽ xử lý thế nào | UX nên phản ứng ra sao |
|-----------|------------------------------|------------------------|
| *VD: Input bằng ngôn ngữ khác* |   |   |
| *VD: Input cố tình gây lỗi (adversarial)* |   |   |
| *VD: Input quá dài / quá ngắn* |   |   |

### Câu hỏi mở rộng

- Nếu user sửa AI 10 lần liên tiếp, UI có nên thay đổi hành vi không? (VD: tắt auto, chuyển sang gợi ý)
- User mới vs user cũ: 4 paths có cần thiết kế khác nhau không?
- Nếu 2 user sửa AI theo 2 hướng ngược nhau, hệ thống ưu tiên ai?
