# Eval metrics + threshold

Chọn metrics, đặt threshold, xác định red flag. Câu hỏi quan trọng nhất: **optimize precision hay recall?**

## Precision hay recall?

☐ Precision — khi AI nói "có" thì thực sự đúng (ít false positive)
☐ Recall — tìm được hết những cái cần tìm (ít false negative)

**Tại sao?** ___ **Nếu sai ngược lại thì sao?** ___

## Metrics table

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
|   |   |   |
|   |   |   |
|   |   |   |

## Ví dụ 1: Chatbot ngân hàng (precision-first)

**Tại sao precision?** Trả lời sai về lãi suất/phí → khách mất tiền, ngân hàng mất uy tín. False positive tệ hơn false negative ("tôi không biết").

| Metric | Threshold | Red flag |
|--------|-----------|----------|
| Precision (câu trả lời đúng/tổng trả lời) | ≥95% | <90% trong 1 tuần |
| Escalation rate (chuyển nhân viên) | <30% | >50% → AI không hữu ích |
| User satisfaction | ≥4/5 | <3/5 trong 2 tuần |

## Ví dụ 2: FAQ e-commerce (recall-first)

**Tại sao recall?** Khách hỏi mà AI không tìm được → khách bỏ đi. Bỏ sót tệ hơn gợi ý sai (khách thấy ngay, hỏi lại).

| Metric | Threshold | Red flag |
|--------|-----------|----------|
| Recall (tìm được/tổng có đáp án) | ≥90% | <80% → khách không tìm được |
| Accuracy (đúng trong số đã trả lời) | ≥80% | <70% → gợi ý sai quá nhiều |
| Deflection rate (không cần nhân viên) | ≥60% | <40% → chưa tiết kiệm nhân lực |

---

## Mở rộng (optional — bonus)

### User-facing metrics vs internal metrics

Không phải metric nào cũng nên show cho user. Phân loại:

| Metric | User thấy? | Dùng để làm gì |
|--------|-----------|-----------------|
| *VD: Confidence score* | ☐ Có ☐ Không | *Show khi >70% để user tin, ẩn khi thấp để không gây hoang mang* |
| *VD: Response latency* | ☐ Có ☐ Không | *User không cần thấy số ms, nhưng >5s cần hiện loading state* |
| *VD: Correction rate* | ☐ Có ☐ Không | *Internal: theo dõi chất lượng. User chỉ cần thấy "đã cải thiện"* |

### Offline eval vs online eval

| Loại | Khi nào | Đo gì | Ví dụ |
|------|---------|-------|-------|
| **Offline** | Trước khi deploy | Accuracy trên test set | Chạy 100 câu hỏi mẫu, đo precision/recall |
| **Online** | Sau khi deploy | Hành vi user thật | User click "helpful"? User sửa kết quả? User quay lại dùng? |

- Product đang đo gì? Thiếu gì?
- Offline metric cao nhưng online metric thấp → vấn đề gì?

### A/B test design (nếu có thời gian)

Nếu đưa product ra thật, sẽ A/B test gì đầu tiên?

| Test | Variant A | Variant B | Metric theo dõi | Kết quả mong đợi |
|------|-----------|-----------|------------------|-------------------|
| *VD: Hiện confidence* | Hiện % confidence | Không hiện | Trust score, correction rate | Hiện confidence → ít correction hơn |

### Câu hỏi mở rộng

- Metric nào đo được sớm nhất (ngày 1)? Metric nào cần thời gian (tuần/tháng)?
- Nếu chỉ được chọn 1 metric duy nhất để theo dõi, chọn gì? Tại sao?
- Metric đang chọn có bị "game" được không? (VD: AI từ chối trả lời nhiều → precision cao nhưng vô dụng)
