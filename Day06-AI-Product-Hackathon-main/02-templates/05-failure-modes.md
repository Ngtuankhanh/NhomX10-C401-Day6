# Top 3 failure modes

Liệt kê cách product có thể fail — không phải list features.

> **"Failure mode nào user KHÔNG BIẾT bị sai? Đó là cái nguy hiểm nhất."**

---

## Template

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 |   |   |   |
| 2 |   |   |   |
| 3 |   |   |   |

---

## Ví dụ

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | **Chatbot y tế:** bệnh nhân hỏi triệu chứng hiếm, ngoài training data | AI trả lời tự tin nhưng sai — **user không biết bị sai**, tin và tự điều trị | Detect domain ngoài scope → trả lời "Tôi không đủ thông tin, hãy hỏi bác sĩ" thay vì đoán |
| 2 | **Recommendation engine:** user mua quà cho người khác, pattern khác hẳn lịch sử | AI gợi ý sản phẩm hoàn toàn sai domain, user mất thời gian lọc | Cho user chọn context ("mua cho ai?") trước khi gợi ý. Reset recommendation khi detect mua ngoài pattern |
| 3 | **AI agent gửi email:** user duyệt nhanh, không đọc kỹ draft AI viết | Email gửi đi có thông tin sai hoặc tone không phù hợp — **đã gửi rồi, không recall được** | Highlight phần AI thay đổi so với template. Delay gửi 30 giây + nút undo |

---

## Cách nghĩ failure modes

1. Failure mode nào user THẤY ngay? → ít nguy hiểm (user tự sửa)
2. Failure mode nào user KHÔNG BIẾT? → nguy hiểm nhất (thiệt hại âm thầm)
3. Failure mode nào ĐÃ XẢY RA rồi mới biết? → cần prevention, không chỉ detection
4. Nghĩ từ góc automation/augmentation: automation → failure ngầm nhiều hơn

---

## Mở rộng (optional — bonus)

### Severity × likelihood matrix

Xếp failure modes vào ma trận để ưu tiên mitigation:

```
            Likelihood thấp          Likelihood cao
          ┌────────────────────┬────────────────────┐
Severity  │                    │                    │
cao       │   Monitor + plan   │   FIX NGAY         │
          │                    │   (top priority)   │
          ├────────────────────┼────────────────────┤
Severity  │                    │                    │
thấp      │   Accept           │   Fix khi có       │
          │   (không ưu tiên)  │   thời gian        │
          └────────────────────┴────────────────────┘
```

Đặt 3 failure modes của nhóm vào đâu trong ma trận? Có failure mode nào severity cao + likelihood cao mà chưa có mitigation?

### Cascade failure

Khi 1 failure gây ra failure khác:

```
VD: AI gợi ý sai khoa → bệnh nhân đặt lịch sai khoa → bác sĩ khám không đúng chuyên môn
    → bệnh nhân phải đặt lại → mất thời gian + tiền + niềm tin
```

Vẽ chuỗi hậu quả cho failure mode nguy hiểm nhất của nhóm. Chuỗi dài bao nhiêu bước trước khi có người phát hiện?

### Adversarial / misuse scenarios

User cố tình dùng sai hoặc tấn công:

| Scenario | Hậu quả | Phòng tránh |
|----------|---------|-------------|
| *VD: User nhập prompt injection vào input* |   |   |
| *VD: User spam request để tăng cost* |   |   |
| *VD: User dùng AI output làm bằng chứng sai* |   |   |

Không cần giải quyết hết — liệt kê và chọn 1-2 cái đáng phòng nhất.

### Câu hỏi mở rộng

- Failure mode nào sẽ xuất hiện ở scale lớn mà ở prototype không thấy?
- Nếu product chạy 6 tháng không ai theo dõi, failure nào sẽ tệ dần theo thời gian (model drift)?
- Automation → augmentation (hoặc ngược lại) có giảm được failure mode nào không?
